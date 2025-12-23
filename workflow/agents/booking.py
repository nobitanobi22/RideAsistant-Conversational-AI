from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from utils.types import State, BookingInfo
from langchain_core.messages import AIMessage
from utils.user_manager import UserManager
from utils.booking_manager import BookingManager
from utils.input_handlers import get_booking_input
from datetime import datetime

def booking_node(state: State):
    # Get booking inputs with validation
    pickup, drop, schedule = get_booking_input()
    
    # Convert schedule to standard format if provided
    schedule_time = None
    if schedule:
        schedule_time = datetime.strptime(schedule, "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M")
    
    # Create booking info
    booking_info = BookingInfo(
        pickup=pickup,
        drop=drop,
        schedule_time=schedule_time
    )
    state["booking_info"] = booking_info
    
    # Initialize user manager for driver validation
    user_manager = UserManager()
    
    # Get and validate driver
    print("\nAssigning driver...")
    while True:
        driver_id = input("Enter driver ID for this ride: ").strip()
        if not driver_id:
            print("Driver ID is required. Please try again.")
            continue
            
        # Validate driver exists
        driver = user_manager.get_driver(driver_id)
        if not driver:
            print(f"Error: Driver with ID {driver_id} not found in the system. Please enter a valid driver ID.")
            continue
            
        break
    
    # Create booking record
    booking_manager = BookingManager()
    booking = booking_manager.create_booking(
        rider_id=state["rider"].rider_id,
        driver_id=driver_id,
        pickup=booking_info.pickup,
        drop=booking_info.drop,
        schedule_time=booking_info.schedule_time
    )
    
    # Update booking statistics for both rider and driver
    user_manager.update_rider_stats(state["rider"].rider_id, add_booking=True)
    user_manager.update_driver_stats(driver_id, add_ride=True)
    
    # Add confirmation message with booking details
    confirmation = f"""Booking confirmed!
Booking ID: {booking.booking_id}
Driver: {driver_id} (Rating: {driver.driver_rating:.1f})
Pickup: {booking_info.pickup}
Drop: {booking_info.drop}"""
    if booking_info.schedule_time:
        confirmation += f"\nScheduled for: {booking_info.schedule_time}"
    confirmation += "\n\nPlease save your booking ID for future reference."
    
    state["messages"].append(AIMessage(content=confirmation))
    return state