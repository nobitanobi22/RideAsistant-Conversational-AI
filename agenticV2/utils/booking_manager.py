import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from utils.types import BookingRecord

class BookingManager:
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.bookings_file = os.path.join(storage_dir, "bookings.json")
        self.bookings: Dict[str, BookingRecord] = {}
        self._load_bookings()
        
    def _load_bookings(self) -> None:
        """Load bookings from storage file."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        try:
            with open(self.bookings_file, 'r') as f:
                bookings_data = json.load(f)
                for booking_data in bookings_data:
                    booking = BookingRecord.model_validate(booking_data)
                    self.bookings[booking.booking_id] = booking
        except (json.JSONDecodeError, FileNotFoundError):
            pass
            
    def _save_bookings(self) -> None:
        """Save bookings to storage file."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        with open(self.bookings_file, 'w') as f:
            json.dump([booking.model_dump() for booking in self.bookings.values()], f)
            
    def generate_booking_id(self) -> str:
        """Generate a unique booking ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        count = len(self.bookings) + 1
        return f"B{timestamp}{count:04d}"
        
    def create_booking(self, rider_id: str, driver_id: str, pickup: str, drop: str) -> BookingRecord:
        """Create a new booking record."""
        booking_id = self.generate_booking_id()
        
        booking = BookingRecord(
            booking_id=booking_id,
            rider_id=rider_id,
            driver_id=driver_id,
            pickup=pickup,
            drop=drop
        )
        
        self.bookings[booking_id] = booking
        self._save_bookings()
        return booking
        
    def get_booking(self, booking_id: str) -> Optional[BookingRecord]:
        """Get a booking by ID."""
        return self.bookings.get(booking_id)
        
    def get_rider_bookings(self, rider_id: str) -> List[BookingRecord]:
        """Get all bookings for a rider."""
        return [booking for booking in self.bookings.values() 
                if booking.rider_id == rider_id and booking.status == "active"]
        
    def cancel_booking(self, booking_id: str) -> Optional[BookingRecord]:
        """Cancel a booking by ID."""
        booking = self.get_booking(booking_id)
        if booking and booking.status == "active":
            booking.status = "cancelled"
            self._save_bookings()
            return booking
        return None
        
    def complete_booking(self, booking_id: str) -> Optional[BookingRecord]:
        """Mark a booking as completed."""
        booking = self.get_booking(booking_id)
        if booking and booking.status == "active":
            booking.status = "completed"
            self._save_bookings()
            return booking
        return None 