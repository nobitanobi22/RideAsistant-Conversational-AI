import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from utils.types import CancellationRecord

class CancellationManager:
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.cancellations_file = os.path.join(storage_dir, "cancellations.json")
        self.cancellations: Dict[str, CancellationRecord] = {}
        self._load_cancellations()
        
    def _load_cancellations(self) -> None:
        """Load cancellations from storage file."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        try:
            with open(self.cancellations_file, 'r') as f:
                cancellations_data = json.load(f)
                for cancel_data in cancellations_data:
                    cancellation = CancellationRecord.model_validate(cancel_data)
                    self.cancellations[cancellation.cancellation_id] = cancellation
        except (json.JSONDecodeError, FileNotFoundError):
            pass
            
    def _save_cancellations(self) -> None:
        """Save cancellations to storage file."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        with open(self.cancellations_file, 'w') as f:
            json.dump([cancel.model_dump() for cancel in self.cancellations.values()], f)
            
    def generate_cancellation_id(self) -> str:
        """Generate a unique cancellation ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        count = len(self.cancellations) + 1
        return f"C{timestamp}{count:04d}"
        
    def create_cancellation(self,
                          booking_id: str,
                          rider_id: str,
                          driver_id: str,
                          cancelled_by: str,
                          arrived: bool,
                          distance_from_pin: int,
                          wait_time: Optional[int],
                          rider_rating: float,
                          rider_cancellation_rate: Optional[float] = None,
                          cancellation_time: Optional[int] = None,
                          decision: str = "pending") -> CancellationRecord:
        """Create a new cancellation record."""
        cancellation_id = self.generate_cancellation_id()
        
        cancellation = CancellationRecord(
            cancellation_id=cancellation_id,
            booking_id=booking_id,
            rider_id=rider_id,
            driver_id=driver_id,
            cancelled_by=cancelled_by,
            arrived=arrived,
            distance_from_pin=distance_from_pin,
            wait_time=wait_time,
            rider_rating=rider_rating,
            rider_cancellation_rate=rider_cancellation_rate,
            cancellation_time=cancellation_time,
            decision=decision
        )
        
        self.cancellations[cancellation_id] = cancellation
        self._save_cancellations()
        return cancellation
        
    def get_cancellation(self, cancellation_id: str) -> Optional[CancellationRecord]:
        """Get a cancellation by ID."""
        return self.cancellations.get(cancellation_id)
        
    def get_booking_cancellation(self, booking_id: str) -> Optional[CancellationRecord]:
        """Get cancellation record for a specific booking."""
        for cancellation in self.cancellations.values():
            if cancellation.booking_id == booking_id:
                return cancellation
        return None
        
    def get_rider_cancellations(self, rider_id: str) -> List[CancellationRecord]:
        """Get all cancellations for a rider."""
        return [cancel for cancel in self.cancellations.values() 
                if cancel.rider_id == rider_id]
        
    def get_driver_cancellations(self, driver_id: str) -> List[CancellationRecord]:
        """Get all cancellations for a driver."""
        return [cancel for cancel in self.cancellations.values() 
                if cancel.driver_id == driver_id]
        
    def update_cancellation_decision(self, cancellation_id: str, decision: str) -> Optional[CancellationRecord]:
        """Update the decision for a cancellation."""
        cancellation = self.get_cancellation(cancellation_id)
        if cancellation:
            cancellation.decision = decision
            self._save_cancellations()
            return cancellation
        return None 