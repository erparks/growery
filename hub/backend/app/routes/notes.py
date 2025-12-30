from __future__ import annotations

from flask import Blueprint, Response, jsonify, request
from typing import Any, Dict, Optional, Tuple

from app.services.note_service import NoteService


notes_bp = Blueprint("notes", __name__)
note_service = NoteService()


@notes_bp.route("/notes", methods=["GET"])
def list_all_notes() -> Tuple[Response, int]:
    raw_plant_id = request.args.get("plant_id")
    plant_id: Optional[int] = None
    if raw_plant_id:
        try:
            plant_id = int(raw_plant_id)
        except ValueError:
            return jsonify({"error": "plant_id must be an integer"}), 400

    result, error, status_code = note_service.list_all_notes(
        plant_id=plant_id,
        created_from=request.args.get("created_from"),
        created_to=request.args.get("created_to"),
        due_from=request.args.get("due_from"),
        due_to=request.args.get("due_to"),
    )
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code


@notes_bp.route("/plants/<int:plant_id>/notes", methods=["POST"])
def create_note(plant_id: int) -> Tuple[Response, int]:
    content: Optional[str] = None
    due_date: Optional[str] = None
    photo_history_id: Optional[int] = None

    image = None
    image_date: Optional[str] = None

    if request.is_json:
        data: Optional[Dict[str, Any]] = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "request body required"}), 400
        content = data.get("content")
        due_date = data.get("due_date")
        photo_history_id = data.get("photo_history_id")
    else:
        content = request.form.get("content")
        due_date = request.form.get("due_date")
        image_date = request.form.get("image_date")
        raw_photo_history_id = request.form.get("photo_history_id")
        if raw_photo_history_id:
            try:
                photo_history_id = int(raw_photo_history_id)
            except ValueError:
                return jsonify({"error": "photo_history_id must be an integer"}), 400
        if "image" in request.files:
            image = request.files["image"]

    result, error, status_code = note_service.create_note(
        plant_id=plant_id,
        content=content or "",
        due_date_str=due_date,
        photo_history_id=photo_history_id,
        image=image,
        image_date_str=image_date,
    )
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code


@notes_bp.route("/plants/<int:plant_id>/notes", methods=["GET"])
def list_notes(plant_id: int) -> Tuple[Response, int]:
    result, error, status_code = note_service.list_notes(
        plant_id=plant_id,
        created_from=request.args.get("created_from"),
        created_to=request.args.get("created_to"),
        due_from=request.args.get("due_from"),
        due_to=request.args.get("due_to"),
    )
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code


@notes_bp.route("/plants/<int:plant_id>/notes/<int:note_id>", methods=["PATCH"])
def update_note(plant_id: int, note_id: int) -> Tuple[Response, int]:
    if not request.is_json:
        return jsonify({"error": "JSON body required"}), 400

    data: Optional[Dict[str, Any]] = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "request body required"}), 400

    clear_due_date = data.get("clear_due_date") is True
    clear_photo = data.get("clear_photo") is True

    result, error, status_code = note_service.update_note(
        plant_id=plant_id,
        note_id=note_id,
        content=data.get("content"),
        due_date_str=data.get("due_date"),
        photo_history_id=data.get("photo_history_id"),
        clear_due_date=clear_due_date,
        clear_photo=clear_photo,
    )
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code


@notes_bp.route("/plants/<int:plant_id>/notes/<int:note_id>", methods=["DELETE"])
def delete_note(plant_id: int, note_id: int) -> Tuple[Response, int]:
    result, error, status_code = note_service.delete_note(plant_id, note_id)
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code


@notes_bp.route("/plants/<int:plant_id>/timeline", methods=["GET"])
def plant_timeline(plant_id: int) -> Tuple[Response, int]:
    result, error, status_code = note_service.get_timeline(
        plant_id=plant_id,
        created_from=request.args.get("created_from"),
        created_to=request.args.get("created_to"),
    )
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code


