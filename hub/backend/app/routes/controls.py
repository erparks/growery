from flask import Blueprint, jsonify
from controllers.pump_controller import PumpController

controls_bp = Blueprint("controls", __name__)
pump_controller = PumpController()

@controls_bp.route("/", methods=["POST"])
def pump():
    pump_controller.on()
    return jsonify({"message": "roger roger"})