from database import db
from datetime import datetime, timezone
from models.photo_histories import PhotoHistory

class Plants(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(255), unique=True)
    species = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

    def to_dict(self):
        # Query the related PhotoHistory records each time to ensure up-to-date data
        histories = PhotoHistory.query.filter_by(plant_id=self.id).all()
        return {
            "id": self.id,
            "nickname": self.nickname,
            "species": self.species,
            "created_at": self.created_at,
            "photo_histories": [ph.to_dict() for ph in histories]
        }