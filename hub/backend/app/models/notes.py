from __future__ import annotations

from datetime import datetime, timezone

from app.database import db


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plant_id = db.Column(
        db.Integer, db.ForeignKey("plants.id", ondelete="CASCADE"), nullable=False
    )
    photo_history_id = db.Column(
        db.Integer,
        db.ForeignKey("photo_histories.id", ondelete="SET NULL"),
        nullable=True,
    )

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    due_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "plant_id": self.plant_id,
            "photo_history_id": self.photo_history_id,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "due_date": self.due_date,
            "completed_at": self.completed_at,
        }


