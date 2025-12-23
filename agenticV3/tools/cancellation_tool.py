from langchain.tools import tool
from typing import Optional
from langchain_core.messages import ToolMessage
from utils.user_manager import UserManager
from utils.booking_manager import BookingManager
from utils.cancellation_manager import CancellationManager
from utils.types import CancellationRecord, DriverCancels, RiderCancels
from cancelation_models.driver_function import predict_driver_cancellation_decision
from cancelation_models.rider_function import predict_rider_cancellation_decision
import random

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
        return None

    # Validate driver exists
    driver = user_manager.get_driver(booking.driver_id)
    if not driver:
        return None

    # Get rider
    rider = user_manager.get_rider(booking.rider_id)
    if not rider:
        return None

    # Prompt for who cancelled
    while True:
        who_cancelled = input("Who is cancelling? [driver/rider]: ").strip().lower()
        if who_cancelled in ["driver", "rider"]:
            break

    # --- DRIVER CANCELS ---
    if who_cancelled == "driver":
        # 1. Ask if arrived
        while True:
            arrived_input = random.choice(["y","n"])
            if arrived_input in ["y", "n"]:
                arrived = arrived_input == "y"
                break

        # If not arrived, decision is fee waived
        if not arrived:
            decision = "fee waived"
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
            user_manager.update_driver_stats(booking.driver_id, add_cancellation=True)
            return cancellation_record
        
        # 2. Ask distance from pin
        distance_from_pin = random.randint(1,15)

        # If distance > 100, decision is fee waived
        if distance_from_pin > 100:
            decision = "fee waived"
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
            user_manager.update_driver_stats(booking.driver_id, add_cancellation=True)
            return cancellation_record
        
        # 3. Ask wait time
        wait_time = random.randint(1,15)

        # If wait_time <= 2, decision is fee waived
        if wait_time <= 2:
            decision = "fee waived"
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
        return cancellation_record

    # --- RIDER CANCELS ---
    if who_cancelled == "rider":
        # 1. Ask if driver arrived
        while True:
            arrived_input = random.choice(["y","n"])
            if arrived_input in ["y", "n"]:
                arrived = arrived_input == "y"
                break

        # If not arrived, ask cancellation_time
        if not arrived:
            cancellation_time = random.randint(1, 20)

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
            return cancellation_record
        
        # If arrived, ask wait_time and distance_from_pin
        wait_time = random.randint(1, 15)
        distance_from_pin = random.randint(20, 200)

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
        return cancellation_record

    return None