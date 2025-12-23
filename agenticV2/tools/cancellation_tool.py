from langchain.tools import tool
from typing import Optional
from langchain_core.messages import ToolMessage
from utils.user_manager import UserManager
from utils.booking_manager import BookingManager
from utils.cancellation_manager import CancellationManager
from utils.types import CancellationRecord, DriverCancels, RiderCancels
from cancelation_models.driver_function import predict_driver_cancellation_decision
from cancelation_models.rider_function import predict_rider_cancellation_decision

@tool
def cancel_ride(
    booking_id: str,
    state: dict
) -> Optional[CancellationRecord]:
    """Use this tool to cancel a ride/booking/trip. Only booking_id is required as input; all other details are collected interactively as needed.

    Args:
        booking_id: Booking ID to cancel
        state: Conversation state dict with a 'messages' list

    Returns:
        Cancellation details if successful, None if booking not found or invalid input
    """
    user_manager = UserManager()
    booking_manager = BookingManager()
    cancellation_manager = CancellationManager()

    # Get and validate booking
    booking = booking_manager.get_booking(booking_id)
    if not booking or booking.status != "active":
        # state["messages"].append(ToolMessage(content="Invalid booking ID or booking is not active."))
        return None

    # Validate driver exists
    driver = user_manager.get_driver(booking.driver_id)
    if not driver:
        # state["messages"].append(ToolMessage(content=f"Error: Driver with ID {booking.driver_id} not found in the system. Please contact support."))
        return None

    # Get rider
    rider = user_manager.get_rider(booking.rider_id)
    if not rider:
        # state["messages"].append(ToolMessage(content=f"Error: Rider with ID {booking.rider_id} not found in the system. Please contact support."))
        return None

    # Prompt for who cancelled
    while True:
        who_cancelled = input("Who is cancelling? [driver/rider]: ").strip().lower()
        if who_cancelled in ["driver", "rider"]:
            break
        # state["messages"].append(ToolMessage(content="Please enter 'driver' or 'rider'"))

    # --- DRIVER CANCELS ---
    if who_cancelled == "driver":
        # 1. Ask if arrived
        while True:
            arrived_input = input("Has the driver arrived? [y/n]: ").strip().lower()
            if arrived_input in ["y", "n"]:
                arrived = arrived_input == "y"
                break
            # state["messages"].append(ToolMessage(content="Please enter 'y' or 'n'"))
        # If not arrived, decision is fee waived
        if not arrived:
            decision = "fee waived"
            # state["messages"].append(ToolMessage(content="Fee Waived, since driver did not arrive."))
            cancellation_record = cancellation_manager.create_cancellation(
                booking_id=booking_id,
                rider_id=booking.rider_id,
                driver_id=booking.driver_id,
                cancelled_by=who_cancelled,
                arrived=arrived,
                distance_from_pin=None,
                wait_time=None,
                rider_rating=rider.rider_rating,
                rider_cancellation_rate=rider.cancelation_rate,
                cancellation_time=None,
                decision=decision
            )
            booking_manager.cancel_booking(booking_id)
            # state["messages"].append(ToolMessage(content=f"Cancellation processed for booking {booking_id}."))
            user_manager.update_driver_stats(booking.driver_id, add_cancellation=True)
            return cancellation_record
        # 2. Ask distance from pin
        while True:
            try:
                distance_from_pin = int(input("Distance from pickup location (in meters): "))
                if distance_from_pin < 0:
                    # state["messages"].append(ToolMessage(content="Distance cannot be negative"))
                    return None
                break
            except ValueError:
                # state["messages"].append(ToolMessage(content="Please enter a valid number for distance."))
                pass
        # If distance > 100, decision is fee waived
        if distance_from_pin > 100:
            decision = "fee waived"
            # state["messages"].append(ToolMessage(content="Fee Waived, since distance from pin is greater than 100 meters."))
            cancellation_record = cancellation_manager.create_cancellation(
                booking_id=booking_id,
                rider_id=booking.rider_id,
                driver_id=booking.driver_id,
                cancelled_by=who_cancelled,
                arrived=arrived,
                distance_from_pin=distance_from_pin,
                wait_time=None,
                rider_rating=rider.rider_rating,
                rider_cancellation_rate=rider.cancelation_rate,
                cancellation_time=None,
                decision=decision
            )
            booking_manager.cancel_booking(booking_id)
            # state["messages"].append(ToolMessage(content=f"Cancellation processed for booking {booking_id}."))
            user_manager.update_driver_stats(booking.driver_id, add_cancellation=True)
            return cancellation_record
        # 3. Ask wait time
        while True:
            try:
                wait_time = int(input("How many minutes did the driver wait at the pickup? "))
                if wait_time < 0:
                    # state["messages"].append(ToolMessage(content="Wait time cannot be negative"))
                    return None
                break
            except ValueError:
                # state["messages"].append(ToolMessage(content="Please enter a valid number for wait time."))
                pass
        # If wait_time <= 2, decision is fee waived
        if wait_time <= 2:
            decision = "fee waived"
            # state["messages"].append(ToolMessage(content="Fee Waived, since wait time is less than or equal to 2 minutes."))
            cancellation_record = cancellation_manager.create_cancellation(
                booking_id=booking_id,
                rider_id=booking.rider_id,
                driver_id=booking.driver_id,
                cancelled_by=who_cancelled,
                arrived=arrived,
                distance_from_pin=distance_from_pin,
                wait_time=wait_time,
                rider_rating=rider.rider_rating,
                rider_cancellation_rate=rider.cancelation_rate,
                cancellation_time=None,
                decision=decision
            )
            booking_manager.cancel_booking(booking_id)
            # state["messages"].append(ToolMessage(content=f"Cancellation processed for booking {booking_id}."))
            user_manager.update_driver_stats(booking.driver_id, add_cancellation=True)
            return cancellation_record
        # Otherwise, use ML model
        cancel = DriverCancels(
            cancelation_id=booking_id,
            rider_id=booking.rider_id,
            driver_id=booking.driver_id,
            arrived=arrived,
            distance_from_pin=distance_from_pin,
            wait_time=wait_time,
            rider_rating=rider.rider_rating
        )
        decision = predict_driver_cancellation_decision(cancel)
        user_manager.update_driver_stats(booking.driver_id, add_cancellation=True)
        cancellation_record = cancellation_manager.create_cancellation(
            booking_id=booking_id,
            rider_id=booking.rider_id,
            driver_id=booking.driver_id,
            cancelled_by=who_cancelled,
            arrived=arrived,
            distance_from_pin=distance_from_pin,
            wait_time=wait_time,
            rider_rating=rider.rider_rating,
            rider_cancellation_rate=rider.cancelation_rate,
            cancellation_time=None,
            decision=decision
        )
        booking_manager.cancel_booking(booking_id)
        # state["messages"].append(ToolMessage(content=f"Cancellation processed for booking {booking_id}. Fee applied: {decision}"))
        return cancellation_record

    # --- RIDER CANCELS ---
    if who_cancelled == "rider":
        # 1. Ask if driver arrived
        while True:
            arrived_input = input("Has the driver arrived? [y/n]: ").strip().lower()
            if arrived_input in ["y", "n"]:
                arrived = arrived_input == "y"
                break
            # state["messages"].append(ToolMessage(content="Please enter 'y' or 'n'"))
        # If not arrived, ask cancellation_time
        if not arrived:
            while True:
                try:
                    cancellation_time = int(input("How many minutes since booking was made? "))
                    if cancellation_time < 0:
                        # state["messages"].append(ToolMessage(content="Time cannot be negative"))
                        return None
                    break
                except ValueError:
                    # state["messages"].append(ToolMessage(content="Please enter a valid number for cancellation time."))
                    pass
            # If cancellation_time <= 1, use model2 (needs only rider_cancelation_rate)
            # Otherwise, use model3 (needs rider_rating, cancellation_time, rider_cancelation_rate)
            if cancellation_time <= 1:
                # Only rider_cancelation_rate needed
                cancel = RiderCancels(
                    cancelation_id=booking_id,
                    rider_id=booking.rider_id,
                    driver_id=booking.driver_id,
                    arrived=arrived,
                    distance_from_pin=None,
                    wait_time=None,
                    rider_rating=rider.rider_rating,
                    rider_cancelation_rate=rider.cancelation_rate,
                    cancelation_time=cancellation_time
                )
            else:
                # rider_rating, cancellation_time, rider_cancelation_rate needed
                cancel = RiderCancels(
                    cancelation_id=booking_id,
                    rider_id=booking.rider_id,
                    driver_id=booking.driver_id,
                    arrived=arrived,
                    distance_from_pin=None,
                    wait_time=None,
                    rider_rating=rider.rider_rating,
                    rider_cancelation_rate=rider.cancelation_rate,
                    cancelation_time=cancellation_time
                )
            decision = predict_rider_cancellation_decision(cancel)
            user_manager.update_rider_stats(booking.rider_id, add_cancellation=True)
            cancellation_record = cancellation_manager.create_cancellation(
                booking_id=booking_id,
                rider_id=booking.rider_id,
                driver_id=booking.driver_id,
                cancelled_by=who_cancelled,
                arrived=arrived,
                distance_from_pin=None,
                wait_time=None,
                rider_rating=rider.rider_rating,
                rider_cancellation_rate=rider.cancelation_rate,
                cancellation_time=cancellation_time,
                decision=decision
            )
            booking_manager.cancel_booking(booking_id)
            # state["messages"].append(ToolMessage(content=f"Cancellation processed for booking {booking_id}."))
            return cancellation_record
        # If arrived, ask wait_time and distance_from_pin
        while True:
            try:
                wait_time = int(input("How many minutes did the driver wait at the pickup? "))
                if wait_time < 0:
                    # state["messages"].append(ToolMessage(content="Wait time cannot be negative"))
                    return None
                break
            except ValueError:
                # state["messages"].append(ToolMessage(content="Please enter a valid number for wait time."))
                pass
        while True:
            try:
                distance_from_pin = int(input("Distance from pickup location (in meters): "))
                if distance_from_pin < 0:
                    # state["messages"].append(ToolMessage(content="Distance cannot be negative"))
                    return None
                break
            except ValueError:
                # state["messages"].append(ToolMessage(content="Please enter a valid number for distance."))
                pass
        # Use model1 (needs rider_rating, wait_time, rider_cancelation_rate, distance_from_pin)
        cancel = RiderCancels(
            cancelation_id=booking_id,
            rider_id=booking.rider_id,
            driver_id=booking.driver_id,
            arrived=arrived,
            distance_from_pin=distance_from_pin,
            wait_time=wait_time,
            rider_rating=rider.rider_rating,
            rider_cancelation_rate=rider.cancelation_rate,
            cancelation_time=None
        )
        decision = predict_rider_cancellation_decision(cancel)
        user_manager.update_rider_stats(booking.rider_id, add_cancellation=True)
        cancellation_record = cancellation_manager.create_cancellation(
            booking_id=booking_id,
            rider_id=booking.rider_id,
            driver_id=booking.driver_id,
            cancelled_by=who_cancelled,
            arrived=arrived,
            distance_from_pin=distance_from_pin,
            wait_time=wait_time,
            rider_rating=rider.rider_rating,
            rider_cancellation_rate=rider.cancelation_rate,
            cancellation_time=None,
            decision=decision
        )
        booking_manager.cancel_booking(booking_id)
        # state["messages"].append(ToolMessage(content=f"Cancellation processed for booking {booking_id}."))
        return cancellation_record

    # Should not reach here, but return None for safety
    # state["messages"].append(ToolMessage(content="Unexpected error in cancellation flow."))
    return None