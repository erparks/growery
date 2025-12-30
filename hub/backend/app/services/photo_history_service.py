"""Service for photo history-related business logic."""
import os
import uuid
import mimetypes
import logging
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime, timezone
from werkzeug.datastructures import FileStorage
from app.database import db
from app.models.photo_histories import PhotoHistory
from app.services.plant_service import PlantService
from app.exceptions import PlantNotFoundError, PhotoHistoryNotFoundError, InvalidFileTypeError

logger = logging.getLogger(__name__)

try:
    import piexif
except ImportError:
    piexif = None

try:
    from PIL import Image
except ImportError:
    Image = None
    logger.error("PIL (Pillow) not found. Image compression will be disabled.")


class PhotoHistoryService:
    """Service class for photo history operations."""
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    DEFAULT_MIMETYPE = 'image/jpeg'
    HISTORIES_DIR_NAME = 'histories'
    UTC_TIMEZONE_OFFSET = '+00:00'
    
    @staticmethod
    def _get_backend_directory() -> str:
        """Get the path to the backend directory.
        
        Returns:
            str: Absolute path to the backend directory.
        """
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @staticmethod
    def _get_histories_directory() -> str:
        """Get the path to the histories directory.
        
        Returns:
            str: Absolute path to the histories directory.
        """
        backend_dir = PhotoHistoryService._get_backend_directory()
        return os.path.join(backend_dir, PhotoHistoryService.HISTORIES_DIR_NAME)
    
    @staticmethod
    def _extract_date_from_file(file_path: str) -> datetime:
        """Extract date from EXIF metadata in the image file.
        
        Args:
            file_path: Path to the image file.
            
        Returns:
            datetime: Extracted date in UTC, or current time if extraction fails.
        """
        if not piexif:
            return datetime.now(timezone.utc)
        
        try:
            exif_dict = piexif.load(file_path)
            
            # Priority order for date fields
            date_fields = [
                (piexif.ExifIFD.DateTimeOriginal, 'Exif'),
                (piexif.ImageIFD.DateTime, '0th'),
                (piexif.ExifIFD.DateTimeDigitized, 'Exif'),
            ]
            
            for field_tag, exif_section in date_fields:
                if exif_section not in exif_dict or field_tag not in exif_dict[exif_section]:
                    continue
                    
                date_str = exif_dict[exif_section][field_tag]
                if isinstance(date_str, bytes):
                    date_str = date_str.decode('utf-8')
                
                try:
                    # EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    date_obj = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                    return date_obj.replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue
        except Exception:
            pass
        
        return datetime.now(timezone.utc)
    
    @staticmethod
    def _parse_date_from_request(date_str: str) -> Optional[datetime]:
        """Parse date string from request.
        
        Args:
            date_str: Date string from request form.
            
        Returns:
            datetime: Parsed datetime in UTC, or None if parsing fails.
        """
        try:
            date_str = date_str.replace('Z', PhotoHistoryService.UTC_TIMEZONE_OFFSET)
            created_at = datetime.fromisoformat(date_str)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            else:
                created_at = created_at.astimezone(timezone.utc)
            return created_at
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _validate_file_extension(filename: str) -> Tuple[bool, Optional[str]]:
        """Validate that the file has an allowed extension.
        
        Args:
            filename: The filename to validate.
            
        Returns:
            tuple: (is_valid, extension) where is_valid is bool and extension is str or None.
        """
        if '.' not in filename:
            return False, None
        
        file_extension = filename.rsplit('.', 1)[1].lower()
        is_valid = file_extension in PhotoHistoryService.ALLOWED_EXTENSIONS
        return is_valid, file_extension
    
    @staticmethod
    def _compress_image(file_path: str, target_size_kb: int = 500) -> None:
        """Compress image to be under target size.
        
        Args:
            file_path: Path to the image file.
            target_size_kb: Target size in KB.
        """
        if not Image:
            return

        try:
            file_size = os.path.getsize(file_path)
            target_size_bytes = target_size_kb * 1024
            
            if file_size <= target_size_bytes:
                return

            with Image.open(file_path) as img:
                # Convert to RGB if necessary (e.g. for PNG to JPEG conversion)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                    
                # Iterative compression settings
                quality = 85
                min_quality = 20
                step = 10
                
                temp_path = file_path + ".temp"
                
                # First attempt with standard optimization
                save_kwargs = {'quality': quality, 'optimize': True}
                if 'exif' in img.info:
                    save_kwargs['exif'] = img.info['exif']
                    
                img.save(temp_path, format='JPEG', **save_kwargs)
                
                # If still too big, iterate down quality
                while os.path.getsize(temp_path) > target_size_bytes and quality > min_quality:
                    quality -= step
                    save_kwargs['quality'] = quality
                    img.save(temp_path, format='JPEG', **save_kwargs)

                # If still too big after quality drop, resize
                if os.path.getsize(temp_path) > target_size_bytes:
                    # Reset quality for resize
                    quality = 80
                    save_kwargs['quality'] = quality
                    
                    # Calculate new dimensions maintaining aspect ratio
                    factor = 0.9
                    while os.path.getsize(temp_path) > target_size_bytes and factor > 0.1:
                        width, height = img.size
                        new_size = (int(width * factor), int(height * factor))
                        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                        resized_img.save(temp_path, format='JPEG', **save_kwargs)
                        factor -= 0.1

                # If compressed file is smaller than original, replace
                temp_size = os.path.getsize(temp_path)
                if temp_size < file_size:
                    os.replace(temp_path, file_path)
                    logger.info(f"Compressed image: {file_size/1024:.1f}KB -> {temp_size/1024:.1f}KB")
                else:
                    os.remove(temp_path)
        except Exception as e:
            logger.warning(f"Failed to compress image {os.path.basename(file_path)}: {e}", exc_info=True)

    @staticmethod
    def create_photo_history(
        plant_id: int, 
        file: FileStorage, 
        date_str: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], int]:
        """Create a new photo history entry.
        
        Args:
            plant_id: The ID of the plant.
            file: The uploaded file object.
            date_str: Optional date string from request.
            
        Returns:
            tuple: (photo_history_dict, error_dict, status_code)
                   If successful: (dict, None, 201)
                   If error: (None, error_dict, error_code)
        """
        # Check if plant exists
        plant = PlantService.get_plant_model_by_id(plant_id)
        if not plant:
            return None, {"error": "plant not found"}, 404
        
        # Validate file
        if not file or file.filename == '':
            return None, {"error": "no file selected"}, 400
        
        # Validate file extension
        is_valid, file_extension = PhotoHistoryService._validate_file_extension(file.filename)
        if not is_valid:
            return None, {
                "error": "invalid file type",
                "allowed": list(PhotoHistoryService.ALLOWED_EXTENSIONS)
            }, 400
        
        try:
            # Create histories directory if it doesn't exist
            histories_dir = PhotoHistoryService._get_histories_directory()
            os.makedirs(histories_dir, exist_ok=True)
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(histories_dir, unique_filename)
            
            # Save the file
            file.save(file_path)

            # Compress image
            PhotoHistoryService._compress_image(file_path, target_size_kb=500)
            
            # Store relative path in database (relative to backend directory)
            relative_path = os.path.join(PhotoHistoryService.HISTORIES_DIR_NAME, unique_filename)
            
            # Get date from request if provided, otherwise extract from EXIF
            if date_str:
                created_at = PhotoHistoryService._parse_date_from_request(date_str)
                if created_at is None:
                    created_at = PhotoHistoryService._extract_date_from_file(file_path)
            else:
                created_at = PhotoHistoryService._extract_date_from_file(file_path)
            
            # Create database record
            photo_history = PhotoHistory(
                plant_id=plant_id,
                image_location=relative_path,
                created_at=created_at
            )
            db.session.add(photo_history)
            db.session.commit()
            logger.info(f"Created photo history for plant {plant_id}: {unique_filename}")
            return photo_history.to_dict(), None, 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating photo history for plant {plant_id}: {e}", exc_info=True)
            return None, {"error": "Failed to create photo history"}, 500
    
    @staticmethod
    def get_photo_histories_by_plant_id(
        plant_id: int
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]], int]:
        """Get all photo histories for a plant.
        
        Args:
            plant_id: The ID of the plant.
            
        Returns:
            tuple: (list of photo history dictionaries, error_dict, status_code)
                   If successful: (list, None, 200)
                   If error: (None, error_dict, error_code)
        """
        plant = PlantService.get_plant_model_by_id(plant_id)
        if not plant:
            return None, {"error": "plant not found"}, 404
        
        photo_histories = (
            PhotoHistory.query
            .filter_by(plant_id=plant_id)
            .order_by(PhotoHistory.created_at.desc())
            .all()
        )
        return [ph.to_dict() for ph in photo_histories], None, 200
    
    @staticmethod
    def get_photo_history_image(
        plant_id: int, 
        photo_id: int
    ) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]], int]:
        """Get the image file for a photo history entry.
        
        Args:
            plant_id: The ID of the plant.
            photo_id: The ID of the photo history.
            
        Returns:
            tuple: (file_path, mimetype, error_dict, status_code)
                   If successful: (file_path, mimetype, None, 200)
                   If error: (None, None, error_dict, error_code)
        """
        # Check if plant exists
        plant = PlantService.get_plant_model_by_id(plant_id)
        if not plant:
            return None, None, {"error": "plant not found"}, 404
        
        # Check if photo history exists and belongs to the plant
        photo_history = PhotoHistory.query.filter_by(id=photo_id, plant_id=plant_id).first()
        if not photo_history:
            return None, None, {"error": "photo history not found"}, 404
        
        # Construct absolute path to the image file
        backend_dir = PhotoHistoryService._get_backend_directory()
        image_path = os.path.join(backend_dir, photo_history.image_location)
        
        # Check if file exists
        if not os.path.exists(image_path):
            return None, None, {"error": "image file not found"}, 404
        
        # Determine mimetype
        mimetype, _ = mimetypes.guess_type(image_path)
        if not mimetype:
            mimetype = PhotoHistoryService.DEFAULT_MIMETYPE
        
        return image_path, mimetype, None, 200

    @staticmethod
    def delete_photo_history(
        plant_id: int, 
        photo_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], int]:
        """Delete a photo history entry and its associated file.
        
        Args:
            plant_id: The ID of the plant.
            photo_id: The ID of the photo history.
            
        Returns:
            tuple: (result_dict, error_dict, status_code)
                   If successful: ({"message": "deleted"}, None, 200)
                   If error: (None, error_dict, error_code)
        """
        # Check if plant exists
        plant = PlantService.get_plant_model_by_id(plant_id)
        if not plant:
            return None, {"error": "plant not found"}, 404
        
        # Check if photo history exists and belongs to the plant
        photo_history = PhotoHistory.query.filter_by(id=photo_id, plant_id=plant_id).first()
        if not photo_history:
            return None, {"error": "photo history not found"}, 404
        
        try:
            # Construct absolute path to the image file
            backend_dir = PhotoHistoryService._get_backend_directory()
            image_path = os.path.join(backend_dir, photo_history.image_location)
            
            # Delete from database first
            db.session.delete(photo_history)
            db.session.commit()
            
            # Delete file if it exists
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    logger.info(f"Deleted photo file: {image_path}")
                except Exception as e:
                    logger.error(f"Failed to delete file {image_path}: {e}")
                    # We don't fail the request if file deletion fails, as the DB record is gone
            
            return {"message": "Photo history deleted successfully"}, None, 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting photo history {photo_id}: {e}", exc_info=True)
            return None, {"error": "Failed to delete photo history"}, 500

