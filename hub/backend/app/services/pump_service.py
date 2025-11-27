"""Service for pump control-related business logic."""
import logging
from typing import Dict, Any
from app.controllers.pump_controller import PumpController

logger = logging.getLogger(__name__)


class PumpService:
    """Service class for pump operations."""
    
    def __init__(self) -> None:
        """Initialize the pump service with a pump controller."""
        self.pump_controller = PumpController()
    
    def activate_pump(self) -> Dict[str, Any]:
        """Activate the pump.
        
        Returns:
            dict: Response message.
        """
        try:
            self.pump_controller.on()
            logger.info("Pump activated")
            return {"message": "roger roger"}
        except Exception as e:
            logger.error(f"Error activating pump: {e}", exc_info=True)
            raise

