from typing import Dict, Optional
import json
import os
from utils.types import Rider, Driver

class UserManager:
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.riders_file = os.path.join(storage_dir, "riders.json")
        self.drivers_file = os.path.join(storage_dir, "drivers.json")
        self.riders: Dict[str, Rider] = {}
        self.drivers: Dict[str, Driver] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Load riders and drivers from storage files."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Load riders
        self.riders = {}
        try:
            if os.path.exists(self.riders_file):
                with open(self.riders_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        riders_data = json.loads(content)
                        for rider_data in riders_data:
                            try:
                                rider = Rider.model_validate(rider_data)
                                self.riders[rider.rider_id] = rider
                            except Exception:
                                continue
        except (json.JSONDecodeError, Exception):
            self.riders = {}

        # Load drivers
        self.drivers = {}
        try:
            if os.path.exists(self.drivers_file):
                with open(self.drivers_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        drivers_data = json.loads(content)
                        for driver_data in drivers_data:
                            try:
                                driver = Driver.model_validate(driver_data)
                                self.drivers[driver.driver_id] = driver
                            except Exception:
                                continue
        except (json.JSONDecodeError, Exception):
            self.drivers = {}

    def _save_data(self) -> None:
        """Save riders and drivers to storage files."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        try:
            # Save riders
            riders_data = [rider.model_dump() for rider in self.riders.values()]
            temp_riders_file = self.riders_file + '.tmp'
            with open(temp_riders_file, 'w') as f:
                json.dump(riders_data, f, indent=2)
            os.replace(temp_riders_file, self.riders_file)

            # Save drivers
            drivers_data = [driver.model_dump() for driver in self.drivers.values()]
            temp_drivers_file = self.drivers_file + '.tmp'
            with open(temp_drivers_file, 'w') as f:
                json.dump(drivers_data, f, indent=2)
            os.replace(temp_drivers_file, self.drivers_file)
            
        except Exception:
            # Clean up temporary files if they exist
            temp_riders = self.riders_file + '.tmp'
            temp_drivers = self.drivers_file + '.tmp'
            if os.path.exists(temp_riders):
                os.remove(temp_riders)
            if os.path.exists(temp_drivers):
                os.remove(temp_drivers)

    def create_rider(self, rider_id: str, password: str, *,
                    rating: float = 5.0,
                    total_rides: int = 0,
                    prior_cancels: int = 0,
                    cancel_rate: float = 0.0) -> Rider:
        """Create a new rider account with optional initial statistics."""
        if rider_id in self.riders:
            raise ValueError(f"Rider with ID {rider_id} already exists")
        
        rider = Rider(
            rider_id=rider_id,
            rider_password=password,
            rider_rating=rating,
            prior_cancellations=prior_cancels,
            total_rides_booked=total_rides,
            cancelation_rate=cancel_rate
        )

        self.riders[rider_id] = rider
        self._save_data()
        return rider

    def create_driver(self, driver_id: str, *,
                     rating: float = 5.0,
                     total_rides: int = 0,
                     prior_cancels: int = 0,
                     cancel_rate: float = 0.0) -> Driver:
        """Create a new driver account with optional initial statistics."""
        if driver_id in self.drivers:
            raise ValueError(f"Driver with ID {driver_id} already exists")
        
        driver = Driver(
            driver_id=driver_id,
            driver_rating=rating,
            total_rides_accepted=total_rides,
            prior_cancellations=prior_cancels,
            cancelation_rate=cancel_rate
        )

        self.drivers[driver_id] = driver
        self._save_data()
        return driver

    def get_rider(self, rider_id: str) -> Optional[Rider]:
        """Get rider by ID."""
        return self.riders.get(rider_id)

    def get_driver(self, driver_id: str) -> Optional[Driver]:
        """Get driver by ID."""
        return self.drivers.get(driver_id)

    def authenticate_rider(self, rider_id: str, password: str) -> Optional[Rider]:
        """Authenticate a rider with their ID and password."""
        try:
            rider = self.riders.get(rider_id)
            if not rider:
                return None
            
            if rider.rider_password == password:
                return rider
            else:
                return None
                
        except Exception:
            return None

    def update_rider_stats(self, rider_id: str, *, 
                         new_rating: Optional[float] = None,
                         add_cancellation: bool = False,
                         add_booking: bool = False) -> Optional[Rider]:
        """Update rider statistics."""
        rider = self.get_rider(rider_id)
        if not rider:
            return None

        if new_rating is not None:
            rider.rider_rating = new_rating
        
        if add_cancellation:
            rider.prior_cancellations += 1
        
        if add_booking:
            rider.total_rides_booked += 1

        if rider.total_rides_booked > 0:
            rider.cancelation_rate = (rider.prior_cancellations / rider.total_rides_booked) * 100

        self._save_data()
        return rider

    def update_driver_stats(self, driver_id: str, *,
                          new_rating: Optional[float] = None,
                          add_cancellation: bool = False,
                          add_ride: bool = False) -> Optional[Driver]:
        """Update driver statistics."""
        driver = self.get_driver(driver_id)
        if not driver:
            return None

        if new_rating is not None:
            driver.driver_rating = new_rating
        
        if add_cancellation:
            driver.prior_cancellations += 1
        
        if add_ride:
            driver.total_rides_accepted += 1

        if driver.total_rides_accepted > 0:
            driver.cancelation_rate = (driver.prior_cancellations / driver.total_rides_accepted) * 100

        self._save_data()
        return driver