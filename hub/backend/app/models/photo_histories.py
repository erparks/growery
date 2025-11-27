from app.database import db
from datetime import datetime, timezone

class PhotoHistory(db.Model):
    __tablename__ = 'photo_histories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), nullable=False)
    image_location = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

    def to_dict(self):
        return {"id": self.id, "plant_id": self.plant_id, "image_location": self.image_location, "created_at": self.created_at}
