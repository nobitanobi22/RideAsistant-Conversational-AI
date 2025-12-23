from typing import Tuple
from utils.types import State, DriverCancels, RiderCancels, CancellationEvent
from langchain_core.messages import AIMessage
from cancelation_models.driver_function import predict_driver_cancellation_decision
from cancelation_models.rider_function import predict_rider_cancellation_decision
from utils.user_manager import UserManager
from utils.booking_manager import BookingManager
from utils.cancellation_manager import CancellationManager
from utils.input_handlers import get_cancellation_inputs, get_wait_time, get_cancellation_time

def cancel_node(state: State) -> State:
    user_manager = UserManager()
    booking_manager = BookingManager()
    cancellation_manager = CancellationManager()
    
    # Get active bookings for the rider
    active_bookings = booking_manager.get_rider_bookings(state["rider"].rider_id)
    
    if not active_bookings:
        state["messages"].append(AIMessage(content="You have no active bookings to cancel."))
        return state
    
    # Get initial cancellation inputs
    booking_id, who_cancelled, arrived, distance_from_pin = get_cancellation_inputs(active_bookings)
    
    if not booking_id:
        state["messages"].append(AIMessage(content="Cancellation cancelled. Please try again if needed."))
        return state
    
    # Get the booking
    booking = booking_manager.get_booking(booking_id)
    if not booking or booking.status != "active":
        state["messages"].append(AIMessage(content="Invalid booking ID or booking is not active."))
        return state
    
    # Validate driver exists in the system
    driver = user_manager.get_driver(booking.driver_id)
    if not driver:
        state["messages"].append(AIMessage(content=f"Error: Driver with ID {booking.driver_id} not found in the system. Please contact support."))
        return state
    
    rider = state["rider"]
    driver_id = booking.driver_id
    
    # Get additional inputs based on arrival status
    wait_time = get_wait_time() if arrived else None
    cancellation_time = get_cancellation_time() if who_cancelled == "rider" and not arrived else None

    # Create base cancellation event
    cancellation_event = CancellationEvent(
        cancelled_by=who_cancelled,
        rider_id=rider.rider_id,
        driver_id=driver_id,
        arrived=arrived,
        distance_from_pin=distance_from_pin,
        wait_time=wait_time,
        rider_rating=rider.rider_rating
    )

    # Calculate rider cancellation rate
    rider_cancellation_rate = (rider.prior_cancellations / rider.total_rides_booked * 100 
                             if rider.total_rides_booked else 0)
    cancellation_event.rider_cancellation_rate = rider_cancellation_rate
    cancellation_event.cancellation_time = cancellation_time

    if who_cancelled == "driver":
        # Create DriverCancels object for ML model
        cancel = DriverCancels(
            cancelation_id=booking_id,  # Use booking ID as cancellation ID
            rider_id=rider.rider_id,
            driver_id=driver_id,
            arrived=arrived,
            distance_from_pin=distance_from_pin,
            wait_time=wait_time,
            rider_rating=rider.rider_rating
        )
        decision = predict_driver_cancellation_decision(cancel)
        
        # Update driver's cancellation stats
        updated_driver = user_manager.update_driver_stats(driver_id, add_cancellation=True)
        if not updated_driver:
            state["messages"].append(AIMessage(content=f"Warning: Could not update driver statistics for ID {driver_id}."))

    else:  # rider cancelled
        # Create RiderCancels object for ML model
        cancel = RiderCancels(
            cancelation_id=booking_id,  # Use booking ID as cancellation ID
            rider_id=rider.rider_id,
            driver_id=driver_id,
            arrived=arrived,
            distance_from_pin=distance_from_pin,
            wait_time=wait_time,
            rider_rating=rider.rider_rating,
            rider_cancelation_rate=rider_cancellation_rate,
            cancelation_time=cancellation_time
        )
        decision = predict_rider_cancellation_decision(cancel)
        
        # Update rider's cancellation stats
        updated_rider = user_manager.update_rider_stats(rider.rider_id, add_cancellation=True)
        if not updated_rider:
            state["messages"].append(AIMessage(content=f"Warning: Could not update rider statistics for ID {rider.rider_id}."))

    # Save decision to cancellation event
    cancellation_event.decision = decision
    
    # Create cancellation record
    cancellation_record = cancellation_manager.create_cancellation(
        booking_id=booking_id,
        rider_id=rider.rider_id,
        driver_id=driver_id,
        cancelled_by=who_cancelled,
        arrived=arrived,
        distance_from_pin=distance_from_pin,
        wait_time=wait_time,
        rider_rating=rider.rider_rating,
        rider_cancellation_rate=rider_cancellation_rate,
        cancellation_time=cancellation_time,
        decision=decision
    )
    
    # Cancel the booking in the booking manager
    booking_manager.cancel_booking(booking_id)
    
    # Update state and provide detailed response
    state["cancellation_event"] = cancellation_event
    response = f"""Booking {booking_id} has been cancelled.
Cancellation ID: {cancellation_record.cancellation_id}
Cancelled by: {who_cancelled.title()}
Fee Decision: {decision}

Details:
- Pickup: {booking.pickup}
- Drop: {booking.drop}
- Driver: {driver_id} (Rating: {driver.driver_rating:.1f})
- Driver arrived: {'Yes' if arrived else 'No'}
- Distance from pickup: {distance_from_pin}m"""

    if wait_time:
        response += f"\n- Wait time: {wait_time} minutes"
    if cancellation_time:
        response += f"\n- Time to cancel: {cancellation_time} minutes"

    state["messages"].append(AIMessage(content=response))
    return state
