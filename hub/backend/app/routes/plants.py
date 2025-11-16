from flask import Blueprint, jsonify, request, send_file
from database import db
from models.photo_histories import PhotoHistory
from models.plants import Plants
import os
import uuid
from werkzeug.utils import secure_filename
import mimetypes

# Add the correct URL prefix
plants_bp = Blueprint("plants", __name__)

@plants_bp.route("/", methods=["GET"])
def get_plants():
    plants = Plants.query.all()
    return jsonify({"plants": [p.to_dict() for p in plants]})

@plants_bp.route("/", methods=["POST"])
def create_plant():
    data = request.get_json()
    new_plant = Plants(nickname=data["nickname"], species=data["species"])
    db.session.add(new_plant)
    db.session.commit()
    return jsonify(new_plant.to_dict()), 201

@plants_bp.route("/<int:plant_id>", methods=["GET"])
def get_plan(plant_id):
    plant = Plants.query.get(plant_id)
    if not plant:
        return jsonify({"error": "plant not found"}), 404
    
    return jsonify(plant.to_dict())

@plants_bp.route("/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    plant = Plants.query.get(plant_id)
    if not plant:
        return jsonify({"error": "plant not found"}), 404
    
    db.session.delete(plant)
    db.session.commit()

    return jsonify({"message": f"pant {plant_id} removed"}), 204

@plants_bp.route("/<int:plant_id>/photo_histories", methods=["POST"])
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
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({"error": "invalid file type. allowed: png, jpg, jpeg, gif, webp"}), 400
    
    # Create histories directory if it doesn't exist
    # Use absolute path based on backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    histories_dir = os.path.join(backend_dir, 'histories')
    os.makedirs(histories_dir, exist_ok=True)
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(histories_dir, unique_filename)
    
    # Save the file
    file.save(file_path)
    
    # Store relative path in database (relative to backend directory)
    relative_path = os.path.join('histories', unique_filename)
    
    # Create database record
    photo_history = PhotoHistory(plant_id=plant_id, image_location=relative_path)
    db.session.add(photo_history)
    db.session.commit()
    
    return jsonify(photo_history.to_dict()), 201

@plants_bp.route("/<int:plant_id>/photo_histories/<int:id>", methods=["GET"])
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


