"""Service for note-related business logic."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from werkzeug.datastructures import FileStorage

from app.database import db
from app.models.notes import Note
from app.models.photo_histories import PhotoHistory
from app.services.photo_history_service import PhotoHistoryService
from app.services.plant_service import PlantService

logger = logging.getLogger(__name__)


class NoteService:
    """Service class for note operations."""

    UTC_TIMEZONE_OFFSET = "+00:00"

    @staticmethod
    def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        if not isinstance(value, str):
            return None
        try:
            normalized = value.replace("Z", NoteService.UTC_TIMEZONE_OFFSET)
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _get_photo_history_for_plant(
        plant_id: int, photo_history_id: int
    ) -> Optional[PhotoHistory]:
        return PhotoHistory.query.filter_by(id=photo_history_id, plant_id=plant_id).first()

    @staticmethod
    def create_note(
        plant_id: int,
        content: str,
        due_date_str: Optional[str] = None,
        photo_history_id: Optional[int] = None,
        image: Optional[FileStorage] = None,
        image_date_str: Optional[str] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], int]:
        plant = PlantService.get_plant_model_by_id(plant_id)
        if not plant:
            return None, {"error": "plant not found"}, 404

        if not content or not isinstance(content, str) or not content.strip():
            return None, {"error": "content is required"}, 400

        due_date = NoteService._parse_iso_datetime(due_date_str) if due_date_str else None
        if due_date_str and due_date is None:
            return None, {"error": "due_date must be an ISO datetime string"}, 400

        resolved_photo_history_id: Optional[int] = None
        if photo_history_id is not None:
            if not isinstance(photo_history_id, int):
                return None, {"error": "photo_history_id must be an integer"}, 400
            photo = NoteService._get_photo_history_for_plant(plant_id, photo_history_id)
            if not photo:
                return None, {"error": "photo history not found"}, 404
            resolved_photo_history_id = photo.id

        if image is not None and image.filename:
            created_photo, error, status = PhotoHistoryService.create_photo_history(
                plant_id, image, image_date_str
            )
            if error:
                return None, error, status
            resolved_photo_history_id = created_photo["id"]

        try:
            note = Note(
                plant_id=plant_id,
                photo_history_id=resolved_photo_history_id,
                content=content.strip(),
                due_date=due_date,
            )
            db.session.add(note)
            db.session.commit()
            return note.to_dict(), None, 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating note for plant {plant_id}: {e}", exc_info=True)
            return None, {"error": "Failed to create note"}, 500

    @staticmethod
    def list_notes(
        plant_id: int,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
        due_from: Optional[str] = None,
        due_to: Optional[str] = None,
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]], int]:
        plant = PlantService.get_plant_model_by_id(plant_id)
        if not plant:
            return None, {"error": "plant not found"}, 404

        created_from_dt = NoteService._parse_iso_datetime(created_from)
        created_to_dt = NoteService._parse_iso_datetime(created_to)
        due_from_dt = NoteService._parse_iso_datetime(due_from)
        due_to_dt = NoteService._parse_iso_datetime(due_to)

        if created_from and created_from_dt is None:
            return None, {"error": "created_from must be an ISO datetime string"}, 400
        if created_to and created_to_dt is None:
            return None, {"error": "created_to must be an ISO datetime string"}, 400
        if due_from and due_from_dt is None:
            return None, {"error": "due_from must be an ISO datetime string"}, 400
        if due_to and due_to_dt is None:
            return None, {"error": "due_to must be an ISO datetime string"}, 400

        q = Note.query.filter_by(plant_id=plant_id)

        if created_from_dt is not None:
            q = q.filter(Note.created_at >= created_from_dt)
        if created_to_dt is not None:
            q = q.filter(Note.created_at <= created_to_dt)
        if due_from_dt is not None:
            q = q.filter(Note.due_date >= due_from_dt)
        if due_to_dt is not None:
            q = q.filter(Note.due_date <= due_to_dt)

        notes = q.order_by(Note.created_at.desc()).all()
        return [n.to_dict() for n in notes], None, 200

    @staticmethod
    def list_all_notes(
        plant_id: Optional[int] = None,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
        due_from: Optional[str] = None,
        due_to: Optional[str] = None,
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]], int]:
        created_from_dt = NoteService._parse_iso_datetime(created_from)
        created_to_dt = NoteService._parse_iso_datetime(created_to)
        due_from_dt = NoteService._parse_iso_datetime(due_from)
        due_to_dt = NoteService._parse_iso_datetime(due_to)

        if created_from and created_from_dt is None:
            return None, {"error": "created_from must be an ISO datetime string"}, 400
        if created_to and created_to_dt is None:
            return None, {"error": "created_to must be an ISO datetime string"}, 400
        if due_from and due_from_dt is None:
            return None, {"error": "due_from must be an ISO datetime string"}, 400
        if due_to and due_to_dt is None:
            return None, {"error": "due_to must be an ISO datetime string"}, 400

        q = Note.query
        if plant_id is not None:
            q = q.filter(Note.plant_id == plant_id)

        if created_from_dt is not None:
            q = q.filter(Note.created_at >= created_from_dt)
        if created_to_dt is not None:
            q = q.filter(Note.created_at <= created_to_dt)
        if due_from_dt is not None:
            q = q.filter(Note.due_date >= due_from_dt)
        if due_to_dt is not None:
            q = q.filter(Note.due_date <= due_to_dt)

        notes = q.order_by(Note.created_at.desc()).all()
        return [n.to_dict() for n in notes], None, 200

    @staticmethod
    def update_note(
        plant_id: int,
        note_id: int,
        content: Optional[str] = None,
        due_date_str: Optional[str] = None,
        photo_history_id: Optional[int] = None,
        clear_due_date: bool = False,
        clear_photo: bool = False,
        complete: bool = False,
        clear_completed_at: bool = False,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], int]:
        plant = PlantService.get_plant_model_by_id(plant_id)
        if not plant:
            return None, {"error": "plant not found"}, 404

        note = Note.query.filter_by(id=note_id, plant_id=plant_id).first()
        if not note:
            return None, {"error": "note not found"}, 404

        if content is not None:
            if not isinstance(content, str) or not content.strip():
                return None, {"error": "content must be a non-empty string"}, 400
            note.content = content.strip()

        if clear_due_date:
            note.due_date = None
        elif due_date_str is not None:
            due_date = NoteService._parse_iso_datetime(due_date_str)
            if due_date is None:
                return None, {"error": "due_date must be an ISO datetime string"}, 400
            note.due_date = due_date

        if clear_photo:
            note.photo_history_id = None
        elif photo_history_id is not None:
            if not isinstance(photo_history_id, int):
                return None, {"error": "photo_history_id must be an integer"}, 400
            photo = NoteService._get_photo_history_for_plant(plant_id, photo_history_id)
            if not photo:
                return None, {"error": "photo history not found"}, 404
            note.photo_history_id = photo.id

        if clear_completed_at:
            note.completed_at = None
        elif complete is True:
            note.completed_at = datetime.now(timezone.utc)

        try:
            db.session.commit()
            return note.to_dict(), None, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating note {note_id} for plant {plant_id}: {e}", exc_info=True)
            return None, {"error": "Failed to update note"}, 500

    @staticmethod
    def delete_note(
        plant_id: int, note_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], int]:
        plant = PlantService.get_plant_model_by_id(plant_id)
        if not plant:
            return None, {"error": "plant not found"}, 404

        note = Note.query.filter_by(id=note_id, plant_id=plant_id).first()
        if not note:
            return None, {"error": "note not found"}, 404

        try:
            db.session.delete(note)
            db.session.commit()
            return {"message": "Note deleted successfully"}, None, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting note {note_id} for plant {plant_id}: {e}", exc_info=True)
            return None, {"error": "Failed to delete note"}, 500

    @staticmethod
    def get_timeline(
        plant_id: int,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]], int]:
        plant = PlantService.get_plant_model_by_id(plant_id)
        if not plant:
            return None, {"error": "plant not found"}, 404

        created_from_dt = NoteService._parse_iso_datetime(created_from)
        created_to_dt = NoteService._parse_iso_datetime(created_to)
        if created_from and created_from_dt is None:
            return None, {"error": "created_from must be an ISO datetime string"}, 400
        if created_to and created_to_dt is None:
            return None, {"error": "created_to must be an ISO datetime string"}, 400

        photos_q = PhotoHistory.query.filter_by(plant_id=plant_id)
        if created_from_dt is not None:
            photos_q = photos_q.filter(PhotoHistory.created_at >= created_from_dt)
        if created_to_dt is not None:
            photos_q = photos_q.filter(PhotoHistory.created_at <= created_to_dt)
        photos = photos_q.order_by(PhotoHistory.created_at.desc()).all()
        photo_ids = {p.id for p in photos}

        notes_q = Note.query.filter_by(plant_id=plant_id)
        if created_from_dt is not None:
            notes_q = notes_q.filter(Note.created_at >= created_from_dt)
        if created_to_dt is not None:
            notes_q = notes_q.filter(Note.created_at <= created_to_dt)
        notes = notes_q.order_by(Note.created_at.desc()).all()

        notes_by_photo_id: Dict[int, List[Dict[str, Any]]] = {}
        standalone_notes: List[Dict[str, Any]] = []

        for note in notes:
            if note.photo_history_id and note.photo_history_id in photo_ids:
                notes_by_photo_id.setdefault(note.photo_history_id, []).append(note.to_dict())
            else:
                standalone_notes.append(note.to_dict())

        items: List[Dict[str, Any]] = []
        for photo in photos:
            items.append(
                {
                    "kind": "photo",
                    "created_at": photo.created_at,
                    "photo_history": photo.to_dict(),
                    "notes": notes_by_photo_id.get(photo.id, []),
                }
            )

        for note_dict in standalone_notes:
            items.append(
                {
                    "kind": "note",
                    "created_at": note_dict["created_at"],
                    "note": note_dict,
                    "photo_history": None,
                }
            )

        items.sort(key=lambda i: i["created_at"], reverse=True)
        return items, None, 200


