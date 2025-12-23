from langchain.tools import tool
from typing import Optional
import random
from utils.user_manager import UserManager
from utils.booking_manager import BookingManager
from utils.types import BookingRecord, AgentState

@tool
def book_ride(pickup: str, drop: str, state: AgentState) -> Optional[BookingRecord]:
    """This tool books a ride from pickup to drop location.

    Args:
        pickup: Starting location
        drop: Destination location
        state: Agent state dict

    Returns:
        Will return a BookingRecord if successful otherwise None. Append this BookingRecord to state under booking_info
    """
    # Initialize managers
    user_manager = UserManager()
    booking_manager = BookingManager()

    # Extract rider_id from state
    rider = state.get('rider')
    if not rider or not hasattr(rider, 'rider_id'):
        return None
    rider_id = rider.rider_id

    # Get all available drivers
    available_drivers = list(user_manager.drivers.values())
    if not available_drivers:
        return None

    # Randomly select a driver
    selected_driver = random.choice(available_drivers)

    # Create booking record
    booking = booking_manager.create_booking(
        rider_id=rider_id,
        driver_id=selected_driver.driver_id,
        pickup=pickup,
        drop=drop
    )

    # Update booking statistics for both rider and driver
    user_manager.update_rider_stats(rider_id, add_booking=True)
    user_manager.update_driver_stats(selected_driver.driver_id, add_ride=True)

    return booking 