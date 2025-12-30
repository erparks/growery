"""Service for plant-related business logic."""
import logging
from typing import Optional, Dict, Any, Tuple, List
from app.database import db
from app.models.plants import Plants
from app.models.photo_histories import PhotoHistory
from app.models.notes import Note
from app.exceptions import PlantNotFoundError

logger = logging.getLogger(__name__)


class PlantService:
    """Service class for plant operations."""
    
    @staticmethod
    def get_all_plants() -> Tuple[List[Dict[str, Any]], int]:
        """Retrieve all plants.
        
        Returns:
            tuple: (list of plant dictionaries, count)
        """
        # Sorting requirements (DB-driven where possible):
        # 1) Plants with incomplete notes that have a due_date come first, sorted by earliest due_date.
        #    Past-due naturally comes first because earlier timestamps sort first.
        # 2) Plants without incomplete-due notes are sorted by most recent photo upload (created_at desc).
        #
        # Note: "incomplete" is defined as completed_at IS NULL.
        next_due_subq = (
            db.session.query(
                Note.plant_id.label("plant_id"),
                db.func.min(Note.due_date).label("next_due_date"),
            )
            .filter(Note.completed_at.is_(None))
            .filter(Note.due_date.isnot(None))
            .group_by(Note.plant_id)
            .subquery()
        )

        last_photo_subq = (
            db.session.query(
                PhotoHistory.plant_id.label("plant_id"),
                db.func.max(PhotoHistory.created_at).label("last_photo_at"),
            )
            .group_by(PhotoHistory.plant_id)
            .subquery()
        )

        incomplete_notes_subq = (
            db.session.query(
                Note.plant_id.label("plant_id"),
                db.func.count(Note.id).label("incomplete_note_count"),
            )
            .filter(Note.completed_at.is_(None))
            .filter(Note.due_date.isnot(None))
            .group_by(Note.plant_id)
            .subquery()
        )

        rows = (
            db.session.query(
                Plants,
                next_due_subq.c.next_due_date,
                last_photo_subq.c.last_photo_at,
                incomplete_notes_subq.c.incomplete_note_count,
            )
            .outerjoin(next_due_subq, next_due_subq.c.plant_id == Plants.id)
            .outerjoin(last_photo_subq, last_photo_subq.c.plant_id == Plants.id)
            .outerjoin(incomplete_notes_subq, incomplete_notes_subq.c.plant_id == Plants.id)
            .order_by(
                db.case((next_due_subq.c.next_due_date.is_(None), 1), else_=0),
                next_due_subq.c.next_due_date.asc(),
                db.case((last_photo_subq.c.last_photo_at.is_(None), 1), else_=0),
                last_photo_subq.c.last_photo_at.desc(),
            )
            .all()
        )

        plants: List[Dict[str, Any]] = []
        for plant, next_due_date, last_photo_at, incomplete_note_count in rows:
            plant_dict = plant.to_dict()
            plant_dict["next_due_date"] = next_due_date
            plant_dict["last_photo_at"] = last_photo_at
            plant_dict["has_incomplete_notes"] = bool((incomplete_note_count or 0) > 0)
            plants.append(plant_dict)

        return plants, len(plants)
    
    @staticmethod
    def get_plant_by_id(plant_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a plant by ID.
        
        Args:
            plant_id: The ID of the plant to retrieve.
            
        Returns:
            dict: Plant dictionary if found, None otherwise.
        """
        plant = Plants.query.get(plant_id)
        return plant.to_dict() if plant else None
    
    @staticmethod
    def get_plant_model_by_id(plant_id: int) -> Optional[Plants]:
        """Retrieve a plant model object by ID.
        
        Args:
            plant_id: The ID of the plant to retrieve.
            
        Returns:
            Plants: Plant model object if found, None otherwise.
        """
        return Plants.query.get(plant_id)
    
    @staticmethod
    def create_plant(nickname: str, species: str) -> Dict[str, Any]:
        """Create a new plant.
        
        Args:
            nickname: The nickname of the plant.
            species: The species of the plant.
            
        Returns:
            dict: The created plant dictionary.
            
        Raises:
            Exception: If database operation fails.
        """
        try:
            new_plant = Plants(nickname=nickname, species=species)
            db.session.add(new_plant)
            db.session.commit()
            logger.info(f"Created plant: {nickname} ({species})")
            return new_plant.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating plant: {e}", exc_info=True)
            raise
    
    @staticmethod
    def delete_plant(plant_id: int) -> bool:
        """Delete a plant by ID.
        
        Args:
            plant_id: The ID of the plant to delete.
            
        Returns:
            bool: True if plant was found and deleted, False otherwise.
            
        Raises:
            Exception: If database operation fails.
        """
        plant = Plants.query.get(plant_id)
        if not plant:
            return False
        
        try:
            db.session.delete(plant)
            db.session.commit()
            logger.info(f"Deleted plant: {plant_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting plant {plant_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def delete_all_plants() -> int:
        """Delete all plants and their photo histories.
        
        Returns:
            int: Number of plants deleted.
            
        Raises:
            Exception: If database operation fails.
        """
        try:
            # Delete photo histories first (foreign key constraint)
            PhotoHistory.query.delete()
            deleted_count = Plants.query.delete()
            db.session.commit()
            logger.info(f"Deleted all plants: {deleted_count} plant(s)")
            return deleted_count
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting all plants: {e}", exc_info=True)
            raise

