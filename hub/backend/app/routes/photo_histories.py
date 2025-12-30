from flask import Blueprint, jsonify, request, send_file, Response
from typing import Tuple
from app.services.photo_history_service import PhotoHistoryService

photo_histories_bp = Blueprint("photo_histories", __name__)
photo_history_service = PhotoHistoryService()

@photo_histories_bp.route("/<int:plant_id>/photo_histories", methods=["POST"])
def add_photo_history(plant_id: int) -> Tuple[Response, int]:
    """Add a photo history entry for a plant.
    
    Args:
        plant_id: The ID of the plant.
    
    Request form must contain:
        - image (file): The image file to upload
        - date (str, optional): ISO format date string
    
    Returns:
        JSON response with photo history data or error message.
    """
    # Input validation
    if 'image' not in request.files:
        return jsonify({"error": "no image file provided"}), 400
    
    file = request.files['image']
    date_str = request.form.get('date')
    
    # Validate date format if provided
    if date_str and not isinstance(date_str, str):
        return jsonify({"error": "date must be a string"}), 400
    
    result, error, status_code = photo_history_service.create_photo_history(
        plant_id, file, date_str
    )
    
    if error:
        return jsonify(error), status_code
    
    return jsonify(result), status_code


@photo_histories_bp.route("/<int:plant_id>/photo_histories", methods=["GET"])
def get_photo_histories(plant_id: int) -> Tuple[Response, int]:
    """Get all photo histories for a plant.
    
    Args:
        plant_id: The ID of the plant.
    
    Returns:
        JSON response with list of photo histories or error message.
    """
    result, error, status_code = photo_history_service.get_photo_histories_by_plant_id(plant_id)
    
    if error:
        return jsonify(error), status_code
    
    return jsonify(result), status_code

@photo_histories_bp.route("/<int:plant_id>/photo_histories/<int:id>", methods=["GET"])
def get_photo_history(plant_id: int, id: int) -> Tuple[Response, int]:
    """Get an image file for a photo history entry.
    
    Args:
        plant_id: The ID of the plant.
        id: The ID of the photo history.
    
    Returns:
        Image file or JSON error response.
    """
    image_path, mimetype, error, status_code = photo_history_service.get_photo_history_image(
        plant_id, id
    )
    
    if error:
        return jsonify(error), status_code
    
    return send_file(image_path, mimetype=mimetype)


@photo_histories_bp.route("/<int:plant_id>/photo_histories/<int:id>", methods=["DELETE"])
def delete_photo_history(plant_id: int, id: int) -> Tuple[Response, int]:
    """Delete a photo history entry.
    
    Args:
        plant_id: The ID of the plant.
        id: The ID of the photo history.
    
    Returns:
        JSON response with success message or error.
    """
    result, error, status_code = photo_history_service.delete_photo_history(
        plant_id, id
    )
    
    if error:
        return jsonify(error), status_code
    
    return jsonify(result), status_code

