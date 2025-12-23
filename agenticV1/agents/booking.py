from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from utils.types import State, BookingRecord
from langchain_core.messages import AIMessage
from utils.user_manager import UserManager
from utils.booking_manager import BookingManager
from utils.input_handlers import get_booking_input
from datetime import datetime
import random

def booking_node(state: State):
    # Get booking inputs with validation
    pickup, drop = get_booking_input()
    
    # Initialize managers
    user_manager = UserManager()
    booking_manager = BookingManager()
    
    # Get all available drivers
    available_drivers = list(user_manager.drivers.values())
    if not available_drivers:
        state["messages"].append(AIMessage(content="Sorry, no drivers are available at the moment. Please try again later."))
        return state
    
    # Randomly select a driver
    selected_driver = random.choice(available_drivers)
    print(f"\nAssigning driver... Driver {selected_driver.driver_id} has been assigned to your ride.")
    
    # Create booking record
    booking = booking_manager.create_booking(
        rider_id=state["rider"].rider_id,
        driver_id=selected_driver.driver_id,
        pickup=pickup,
        drop=drop
    )
    
    # Update booking statistics for both rider and driver
    user_manager.update_rider_stats(state["rider"].rider_id, add_booking=True)
    user_manager.update_driver_stats(selected_driver.driver_id, add_ride=True)
    
    # Add confirmation message with booking details
    confirmation = f"""Booking confirmed!
Booking ID: {booking.booking_id}
Driver: {selected_driver.driver_id} (Rating: {selected_driver.driver_rating:.1f})
Pickup: {booking.pickup}
Drop: {booking.drop}

Please save your booking ID for future reference."""
    
    state["messages"].append(AIMessage(content=confirmation))
    return state