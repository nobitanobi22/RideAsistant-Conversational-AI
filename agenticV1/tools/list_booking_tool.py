from langchain.tools import tool
from typing import List, Optional
from utils.booking_manager import BookingManager
from utils.types import BookingRecord

@tool
def list_bookings(state: dict) -> Optional[List[BookingRecord]]:
    """List the current user's active bookings.

    Args:
        state: Agent state dict

    Returns:
        List of active BookingRecord objects for the current user, or None if not logged in.
    """
    rider = state.get('rider')
    if not rider or not hasattr(rider, 'rider_id'):
        return None
    booking_manager = BookingManager()
    active_bookings = booking_manager.get_rider_bookings(rider.rider_id)
    return active_bookings if active_bookings else [] 

 