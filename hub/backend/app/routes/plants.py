from flask import Blueprint, jsonify, request
from app.database import db
from app.models.plants import Plants

# Add the correct URL prefix
plants_bp = Blueprint("plants", __name__)

@plants_bp.route("/", methods=["GET"])
def get_plants():
    plants = Plants.query.all()
    return jsonify([p.to_dict() for p in plants])

@plants_bp.route("/", methods=["POST"])
def create_plant():
    data = request.get_json()
    new_plant = Plants(nickname=data["nickname"], species=data["species"])
    db.session.add(new_plant)
    db.session.commit()
    return jsonify(new_plant.to_dict()), 201

@plants_bp.route("/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    plant = Plants.query.get(plant_id)
    if not plant:
        return jsonify({"error": "plant not found"}), 404
    
    db.session.delete(plant)
    db.session.commit()

    return jsonify({"message": f"pant {plant_id} removed"}), 204