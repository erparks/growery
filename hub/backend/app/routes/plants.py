from flask import Blueprint, jsonify, request
from database import db
from models.plants import Plants
from models.photo_histories import PhotoHistory

# Add the correct URL prefix
plants_bp = Blueprint("plants", __name__)

@plants_bp.route("/", methods=["GET"])
def get_plants():
    plants = Plants.query.all()
    return jsonify({"plants": [p.to_dict() for p in plants], "count": len(plants)}), 200

@plants_bp.route("/", methods=["POST"])
def create_plant():
    data = request.get_json()
    if not data or "nickname" not in data or "species" not in data:
        return jsonify({"error": "nickname and species are required"}), 400
    
    new_plant = Plants(nickname=data["nickname"], species=data["species"])
    db.session.add(new_plant)
    db.session.commit()
    return jsonify(new_plant.to_dict()), 201

@plants_bp.route("/<int:plant_id>", methods=["GET"])
def get_plant(plant_id):
    plant = Plants.query.get(plant_id)
    if not plant:
        return jsonify({"error": "plant not found"}), 404
    
    return jsonify(plant.to_dict()), 200

@plants_bp.route("/", methods=["DELETE"])
def delete_all_plants():
    """Delete all plants and their photo histories.
    
    Requires confirmation in request body: {"confirm": true}
    """
    data = request.get_json()
    
    if not data or data.get("confirm") is not True:
        return jsonify({
            "error": "confirmation required",
            "message": "Request body must contain: {\"confirm\": true}"
        }), 400
    
    # Delete photo histories first (foreign key constraint)
    PhotoHistory.query.delete()
    deleted_count = Plants.query.delete()
    db.session.commit()
    
    return jsonify({"message": f"deleted {deleted_count} plant(s)"}), 200

@plants_bp.route("/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    plant = Plants.query.get(plant_id)
    if not plant:
        return jsonify({"error": "plant not found"}), 404
    
    db.session.delete(plant)
    db.session.commit()

    return jsonify({"message": f"plant {plant_id} removed"}), 200


