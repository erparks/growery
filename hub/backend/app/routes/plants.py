from flask import Blueprint, jsonify, request, Response
from typing import Tuple, Dict, Any, Optional
from app.services.plant_service import PlantService
from app.exceptions import ValidationError

# Add the correct URL prefix
plants_bp = Blueprint("plants", __name__)
plant_service = PlantService()

@plants_bp.route("/", methods=["GET"])
def get_plants() -> Tuple[Response, int]:
    """Get all plants.
    
    Returns:
        JSON response with list of plants and count.
    """
    plants, count = plant_service.get_all_plants()
    return jsonify({"plants": plants, "count": count}), 200

@plants_bp.route("/", methods=["POST"])
def create_plant() -> Tuple[Response, int]:
    """Create a new plant.
    
    Request body must contain:
        - nickname (str): The plant's nickname
        - species (str): The plant's species
    
    Returns:
        JSON response with created plant data or error message.
    """
    data = request.get_json()
    
    # Input validation
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    if "nickname" not in data or not isinstance(data["nickname"], str) or not data["nickname"].strip():
        return jsonify({"error": "nickname is required and must be a non-empty string"}), 400
    
    if "species" not in data or not isinstance(data["species"], str) or not data["species"].strip():
        return jsonify({"error": "species is required and must be a non-empty string"}), 400
    
    try:
        new_plant = plant_service.create_plant(data["nickname"].strip(), data["species"].strip())
        return jsonify(new_plant), 201
    except Exception as e:
        return jsonify({"error": "Failed to create plant"}), 500

@plants_bp.route("/<int:plant_id>", methods=["GET"])
def get_plant(plant_id: int) -> Tuple[Response, int]:
    """Get a plant by ID.
    
    Args:
        plant_id: The ID of the plant to retrieve.
    
    Returns:
        JSON response with plant data or error message.
    """
    plant = plant_service.get_plant_by_id(plant_id)
    if not plant:
        return jsonify({"error": "plant not found"}), 404
    
    return jsonify(plant), 200

@plants_bp.route("/", methods=["DELETE"])
def delete_all_plants() -> Tuple[Response, int]:
    """Delete all plants and their photo histories.
    
    Requires confirmation in request body: {"confirm": true}
    
    Returns:
        JSON response with deletion confirmation or error message.
    """
    data = request.get_json()
    
    if not data or data.get("confirm") is not True:
        return jsonify({
            "error": "confirmation required",
            "message": "Request body must contain: {\"confirm\": true}"
        }), 400
    
    try:
        deleted_count = plant_service.delete_all_plants()
        return jsonify({"message": f"deleted {deleted_count} plant(s)"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to delete plants"}), 500

@plants_bp.route("/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id: int) -> Tuple[Response, int]:
    """Delete a plant by ID.
    
    Args:
        plant_id: The ID of the plant to delete.
    
    Returns:
        JSON response with deletion confirmation or error message.
    """
    try:
        deleted = plant_service.delete_plant(plant_id)
        if not deleted:
            return jsonify({"error": "plant not found"}), 404

        return jsonify({"message": f"plant {plant_id} removed"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to delete plant"}), 500


