from flask import Blueprint, jsonify, request
from app.database import db
from app.models.plants import Plants

# Add the correct URL prefix
plants_bp = Blueprint("plants", __name__)

@plants_bp.route("/", methods=["GET"])
def get_plants():
    plants = Plants.query.all()
    return jsonify([{"id": p.id, "nickname": p.nickname, "created_at": p.created_at} for p in plants])

@plants_bp.route("/", methods=["POST"])
def add_plant():
    data = request.get_json()
    new_plant = Plants(nickname=data["nickname"], species=data["species"])
    db.session.add(new_plant)
    db.session.commit()
    return jsonify(new_plant.to_dict()), 201
