from flask import Blueprint, jsonify, Response
from typing import Tuple
from app.services.pump_service import PumpService

controls_bp = Blueprint("controls", __name__)
pump_service = PumpService()

@controls_bp.route("/", methods=["POST"])
def pump() -> Tuple[Response, int]:
    """Activate the pump.
    
    Returns:
        JSON response with activation confirmation or error message.
    """
    try:
        response = pump_service.activate_pump()
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": "Failed to activate pump"}), 500