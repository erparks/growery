"""Service for photo history-related business logic.

This service handles photo history operations including:
- Image upload and storage
- Automatic image compression and resizing
- EXIF date extraction
- Photo history retrieval
"""
import os
import uuid
import mimetypes
import logging
import shutil
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime, timezone
from werkzeug.datastructures import FileStorage
from app.database import db
from app.models.photo_histories import PhotoHistory
from app.services.plant_service import PlantService

logger = logging.getLogger(__name__)

try:
    import piexif
except ImportError:
    piexif = None

try:
    from PIL import Image
    # Use modern resampling if available, fallback to LANCZOS constant
    try:
        RESAMPLE_METHOD = Image.Resampling.LANCZOS
    except AttributeError:
        RESAMPLE_METHOD = Image.LANCZOS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    RESAMPLE_METHOD = None


class PhotoHistoryService:
    """Service class for photo history operations.
    
    Handles image upload, compression, storage, and retrieval. All uploaded
    images are automatically compressed to reduce file size while maintaining
    reasonable quality.
    """
    
    # File validation constants
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    DEFAULT_MIMETYPE = 'image/jpeg'
    HISTORIES_DIR_NAME = 'histories'
    UTC_TIMEZONE_OFFSET = '+00:00'
    
    # Image compression constants
    MAX_FILE_SIZE_KB = 100  # Target maximum file size in KB
    MAX_DIMENSION = 1200  # Default maximum width or height in pixels
    INITIAL_QUALITY = 60  # Initial JPEG quality (0-100)
    MIN_QUALITY = 10  # Minimum JPEG quality before giving up
    MIN_DIMENSION = 200  # Minimum width or height in pixels
    
    # Compression thresholds (multiples of MAX_FILE_SIZE_KB)
    LARGE_FILE_THRESHOLD_5X = 5  # 500KB+ files
    LARGE_FILE_THRESHOLD_3X = 3  # 300KB+ files
    LARGE_FILE_THRESHOLD_2X = 2  # 200KB+ files
    
    # Dimension targets for different file sizes
    DIMENSION_FOR_5X = 800
    DIMENSION_FOR_3X = 1000
    DIMENSION_FOR_2X = 1100
    
    # Compression iteration limits
    MAX_COMPRESSION_ITERATIONS = 30
    
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
    def _calculate_target_dimension(file_size_bytes: int, max_size_kb: int) -> int:
        """Calculate target dimension based on file size.
        
        Larger files get more aggressive resizing to ensure compression.
        
        Args:
            file_size_bytes: Current file size in bytes.
            max_size_kb: Target maximum file size in KB.
            
        Returns:
            int: Target maximum dimension (width or height) in pixels.
        """
        max_size_bytes = max_size_kb * 1024
        
        if file_size_bytes > max_size_bytes * PhotoHistoryService.LARGE_FILE_THRESHOLD_5X:
            return PhotoHistoryService.DIMENSION_FOR_5X
        elif file_size_bytes > max_size_bytes * PhotoHistoryService.LARGE_FILE_THRESHOLD_3X:
            return PhotoHistoryService.DIMENSION_FOR_3X
        elif file_size_bytes > max_size_bytes * PhotoHistoryService.LARGE_FILE_THRESHOLD_2X:
            return PhotoHistoryService.DIMENSION_FOR_2X
        else:
            return PhotoHistoryService.MAX_DIMENSION
    
    @staticmethod
    def _convert_to_rgb(img: Image.Image) -> Image.Image:
        """Convert image to RGB format for JPEG compatibility.
        
        Handles RGBA, LA, P, and other modes by converting to RGB.
        Transparent images are composited onto a white background.
        
        Args:
            img: PIL Image object.
            
        Returns:
            Image.Image: RGB converted image.
        """
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background for transparent images
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            mask = img.split()[-1] if img.mode in ('RGBA', 'LA') else None
            background.paste(img, mask=mask)
            return background
        elif img.mode != 'RGB':
            return img.convert('RGB')
        return img
    
    @staticmethod
    def _calculate_new_dimensions(
        width: int, 
        height: int, 
        target_dimension: int
    ) -> Tuple[int, int]:
        """Calculate new dimensions maintaining aspect ratio.
        
        Args:
            width: Current width in pixels.
            height: Current height in pixels.
            target_dimension: Maximum dimension (width or height) in pixels.
            
        Returns:
            tuple: (new_width, new_height) maintaining aspect ratio.
        """
        if width > height:
            new_width = target_dimension
            new_height = int(height * (target_dimension / width))
        else:
            new_height = target_dimension
            new_width = int(width * (target_dimension / height))
        return new_width, new_height
    
    @staticmethod
    def _reduce_quality(current_quality: int) -> int:
        """Reduce JPEG quality for compression.
        
        Uses progressively smaller steps as quality decreases.
        
        Args:
            current_quality: Current JPEG quality (0-100).
            
        Returns:
            int: Reduced quality value.
        """
        if current_quality > 40:
            return max(40, int(current_quality * 0.75))
        elif current_quality > 25:
            return current_quality - 7
        elif current_quality > 15:
            return current_quality - 4
        elif current_quality > PhotoHistoryService.MIN_QUALITY:
            return PhotoHistoryService.MIN_QUALITY
        else:
            return current_quality
    
    @staticmethod
    def _reduce_dimensions(
        current_width: int,
        current_height: int,
        dimension_factor: float,
        reduction_needed: float
    ) -> Tuple[int, int, float]:
        """Reduce image dimensions for further compression.
        
        Args:
            current_width: Current width in pixels.
            current_height: Current height in pixels.
            dimension_factor: Current dimension reduction factor (0.0-1.0).
            reduction_needed: How much compression is needed (ratio).
            
        Returns:
            tuple: (new_width, new_height, new_dimension_factor).
        """
        dimension_reduction = min(0.85, 1.0 / (reduction_needed ** 0.5))
        new_factor = max(0.3, dimension_factor * dimension_reduction)
        new_width = int(current_width * new_factor)
        new_height = int(current_height * new_factor)
        
        # Ensure minimum size
        if new_width < PhotoHistoryService.MIN_DIMENSION:
            new_width = PhotoHistoryService.MIN_DIMENSION
        if new_height < PhotoHistoryService.MIN_DIMENSION:
            new_height = PhotoHistoryService.MIN_DIMENSION
            
        return new_width, new_height, new_factor
    
    @staticmethod
    def _resize_and_compress_image(
        input_path: str, 
        output_path: str, 
        max_size_kb: Optional[int] = None
    ) -> bool:
        """Resize and compress an image to reduce file size.
        
        Uses an iterative approach to compress images:
        1. Converts image to RGB format
        2. Resizes based on file size (larger files get more aggressive resizing)
        3. Iteratively reduces JPEG quality until target size is met
        4. If quality reduction isn't enough, further reduces dimensions
        
        Args:
            input_path: Path to the input image file.
            output_path: Path where the compressed image will be saved.
            max_size_kb: Maximum target file size in KB. Defaults to MAX_FILE_SIZE_KB.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if max_size_kb is None:
            max_size_kb = PhotoHistoryService.MAX_FILE_SIZE_KB
            
        if not PIL_AVAILABLE:
            logger.warning(
                "PIL/Pillow is not available. Image compression disabled. "
                "Install Pillow to enable compression."
            )
            shutil.copy2(input_path, output_path)
            return True
        
        try:
            initial_size = os.path.getsize(input_path)
            max_size_bytes = max_size_kb * 1024
            logger.info(f"Processing image: {initial_size / 1024:.1f}KB (target: {max_size_kb}KB)")
            
            with Image.open(input_path) as img:
                # Convert to RGB for JPEG compatibility
                img = PhotoHistoryService._convert_to_rgb(img)
                
                # Get original dimensions
                original_width, original_height = img.size
                
                # Calculate target dimension based on file size
                target_dimension = PhotoHistoryService._calculate_target_dimension(
                    initial_size, max_size_kb
                )
                
                # Determine if resizing is needed
                needs_resize = (
                    original_width > target_dimension or
                    original_height > target_dimension or
                    initial_size > max_size_bytes
                )
                
                if needs_resize:
                    new_width, new_height = PhotoHistoryService._calculate_new_dimensions(
                        original_width, original_height, target_dimension
                    )
                    img = img.resize((new_width, new_height), RESAMPLE_METHOD)
                    logger.info(
                        f"Resized from {original_width}x{original_height} "
                        f"to {new_width}x{new_height}"
                    )
                
                # Track current dimensions for further reduction if needed
                current_width, current_height = img.size
                
                # Iteratively compress to target size
                quality = PhotoHistoryService.INITIAL_QUALITY
                dimension_factor = 1.0
                iteration = 0
                
                while iteration < PhotoHistoryService.MAX_COMPRESSION_ITERATIONS:
                    iteration += 1
                    
                    # Save with current quality
                    img.save(output_path, 'JPEG', quality=quality, optimize=True)
                    file_size = os.path.getsize(output_path)
                    
                    if file_size <= max_size_bytes:
                        # Success! File is under target size
                        break
                    
                    reduction_needed = file_size / max_size_bytes
                    
                    # Reduce quality if possible
                    if quality > PhotoHistoryService.MIN_QUALITY:
                        new_quality = PhotoHistoryService._reduce_quality(quality)
                        if new_quality != quality:
                            quality = new_quality
                            continue
                    
                    # If quality is already low, reduce dimensions
                    if dimension_factor > 0.3:
                        new_width, new_height, dimension_factor = (
                            PhotoHistoryService._reduce_dimensions(
                                current_width, current_height,
                                dimension_factor, reduction_needed
                            )
                        )
                        img = img.resize((new_width, new_height), RESAMPLE_METHOD)
                        current_width, current_height = img.size
                        quality = PhotoHistoryService.INITIAL_QUALITY  # Reset quality
                    else:
                        # We've tried our best
                        break
                
                final_size = os.path.getsize(output_path)
                logger.info(
                    f"Compressed image: {initial_size / 1024:.1f}KB -> "
                    f"{final_size / 1024:.1f}KB"
                )
                return True
                
        except Exception as e:
            logger.error(
                f"Error resizing/compressing image: {e}",
                exc_info=True
            )
            # Fallback: copy original file
            shutil.copy2(input_path, output_path)
            return False
    
    @staticmethod
    def create_photo_history(
        plant_id: int, 
        file: FileStorage, 
        date_str: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], int]:
        """Create a new photo history entry.
        
        Validates the file, compresses it, saves it to disk, and creates
        a database record. The image is automatically compressed to reduce
        file size while maintaining reasonable quality.
        
        Args:
            plant_id: The ID of the plant.
            file: The uploaded file object.
            date_str: Optional date string from request (ISO format).
            
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
            
            # Generate unique filename (always use .jpg for compressed images)
            unique_filename = f"{uuid.uuid4().hex}.jpg"
            file_path = os.path.join(histories_dir, unique_filename)
            
            # Save the file temporarily first
            temp_path = os.path.join(histories_dir, f"temp_{uuid.uuid4().hex}.{file_extension}")
            file.save(temp_path)
            
            # Resize and compress the image
            PhotoHistoryService._resize_and_compress_image(temp_path, file_path)
            
            # Remove temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
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

