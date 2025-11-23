from flask import Blueprint, jsonify, request, send_file
from database import db
from models.photo_histories import PhotoHistory
from models.plants import Plants
import os
import uuid
import mimetypes
from datetime import datetime, timezone


try:
    import piexif
except ImportError:
    piexif = None

photo_histories_bp = Blueprint("photo_histories", __name__)

def extract_date_from_file(file_path):
    """Extract date from EXIF metadata in the image file.
    
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

@photo_histories_bp.route("/<int:plant_id>/photo_histories", methods=["POST"])
def add_photo_history(plant_id):
    # Check if plant exists
    plant = Plants.query.get(plant_id)
    if not plant:
        return jsonify({"error": "plant not found"}), 404
    
    # Check if file is present in request
    if 'image' not in request.files:
        return jsonify({"error": "no image file provided"}), 400
    
    file = request.files['image']
    
    # Check if file is actually selected
    if file.filename == '':
        return jsonify({"error": "no file selected"}), 400
    
    # Validate file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if '.' not in file.filename:
        return jsonify({"error": "invalid file type"}), 400
    
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    if file_extension not in allowed_extensions:
        return jsonify({
            "error": "invalid file type",
            "allowed": list(allowed_extensions)
        }), 400
    
    # Create histories directory if it doesn't exist
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    histories_dir = os.path.join(backend_dir, 'histories')
    os.makedirs(histories_dir, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(histories_dir, unique_filename)
    
    # Save the file
    file.save(file_path)
    
    # Store relative path in database (relative to backend directory)
    relative_path = os.path.join('histories', unique_filename)
    
    # Get date from request if provided, otherwise extract from EXIF
    if 'date' in request.form:
        try:
            date_str = request.form['date'].replace('Z', '+00:00')
            created_at = datetime.fromisoformat(date_str)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            else:
                created_at = created_at.astimezone(timezone.utc)
        except (ValueError, TypeError):
            created_at = extract_date_from_file(file_path)
    else:
        created_at = extract_date_from_file(file_path)
    
    # Create database record with the extracted or current date
    photo_history = PhotoHistory(plant_id=plant_id, image_location=relative_path, created_at=created_at)
    db.session.add(photo_history)
    db.session.commit()
    
    return jsonify(photo_history.to_dict()), 201


@photo_histories_bp.route("/<int:plant_id>/photo_histories", methods=["GET"])
def get_photo_histories(plant_id):
    plant = Plants.query.get(plant_id)
    if not plant:
        return jsonify({"error": "plant not found"}), 404
    
    photo_histories = (
        PhotoHistory.query
        .filter_by(plant_id=plant_id)
        .order_by(PhotoHistory.created_at.desc())
        .all()
    )
    return jsonify([ph.to_dict() for ph in photo_histories]), 200

@photo_histories_bp.route("/<int:plant_id>/photo_histories/<int:id>", methods=["GET"])
def get_photo_history(plant_id, id):
    # Check if plant exists
    plant = Plants.query.get(plant_id)
    if not plant:
        return jsonify({"error": "plant not found"}), 404
    
    # Check if photo history exists and belongs to the plant
    photo_history = PhotoHistory.query.filter_by(id=id, plant_id=plant_id).first()
    if not photo_history:
        return jsonify({"error": "photo history not found"}), 404
    
    # Construct absolute path to the image file
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path = os.path.join(backend_dir, photo_history.image_location)
    
    # Check if file exists
    if not os.path.exists(image_path):
        return jsonify({"error": "image file not found"}), 404
    
    # Determine mimetype
    mimetype, _ = mimetypes.guess_type(image_path)
    if not mimetype:
        mimetype = 'image/jpeg'  # Default to jpeg if cannot determine
    
    # Return the image file
    return send_file(image_path, mimetype=mimetype)

