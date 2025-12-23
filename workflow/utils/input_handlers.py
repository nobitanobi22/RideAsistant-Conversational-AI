from typing import Tuple, Optional, List
from utils.types import BookingRecord

def get_booking_input() -> Tuple[str, str, Optional[str]]:
    """Get booking inputs with validation."""
    while True:
        pickup = input("\nEnter pickup location: ").strip()
        if not pickup:
            print("Pickup location cannot be empty.")
            continue
            
        drop = input("Enter drop location: ").strip()
        if not drop:
            print("Drop location cannot be empty.")
            continue
            
        schedule = input("Enter schedule time (optional, format: DD/MM/YYYY HH:MM): ").strip()
        if schedule and not validate_schedule_format(schedule):
            print("Invalid schedule format. Use DD/MM/YYYY HH:MM or leave empty.")
            continue
            
        return pickup, drop, schedule if schedule else None

def get_cancellation_inputs(active_bookings: List[BookingRecord]) -> Tuple[Optional[str], Optional[str], bool, Optional[int]]:
    """Display active bookings and get cancellation inputs."""
    # Display active bookings
    print("\nYour active bookings:")
    for booking in active_bookings:
        print(f"\nBooking ID: {booking.booking_id}")
        print(f"Driver ID: {booking.driver_id}")
        print(f"Pickup: {booking.pickup}")
        print(f"Drop: {booking.drop}")
        if booking.schedule_time:
            print(f"Scheduled for: {booking.schedule_time}")
    
    # Get booking ID
    while True:
        booking_id = input("\nEnter the Booking ID you want to cancel: ").strip()
        if not booking_id:
            return None, None, False, None
        
        # Validate booking ID exists in active bookings
        if not any(b.booking_id == booking_id for b in active_bookings):
            print("Invalid booking ID. Please try again or press Enter to go back.")
            continue
        break
    
    # Get who cancelled
    while True:
        who_cancelled = input("Who cancelled the ride? [driver/rider]: ").strip().lower()
        if who_cancelled not in {"driver", "rider"}:
            print("Please enter 'driver' or 'rider'.")
            continue
        break
    
    # Get arrival status
    while True:
        arrived_input = input("Did the driver arrive? [y/n]: ").strip().lower()
        if arrived_input not in {"y", "n"}:
            print("Please enter 'y' or 'n'.")
            continue
        arrived = arrived_input == "y"
        break
    
    # Get distance from pin
    while True:
        try:
            distance = int(input("Driver distance from pin at cancellation (in meters): "))
            if distance < 0:
                print("Distance cannot be negative.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    return booking_id, who_cancelled, arrived, distance

def get_wait_time() -> Optional[int]:
    """Get wait time for arrived drivers."""
    while True:
        try:
            wait_time = int(input("Driver wait time (in minutes): "))
            if wait_time < 0:
                print("Wait time cannot be negative.")
                continue
            return wait_time
        except ValueError:
            print("Please enter a valid number.")

def get_cancellation_time() -> Optional[int]:
    """Get cancellation time for rider cancellations."""
    while True:
        try:
            cancel_time = int(input("Time taken to cancel after booking (in minutes): "))
            if cancel_time < 0:
                print("Cancellation time cannot be negative.")
                continue
            return cancel_time
        except ValueError:
            print("Please enter a valid number.")

def validate_schedule_format(schedule: str) -> bool:
    """Validate schedule time format."""
    try:
        from datetime import datetime
        datetime.strptime(schedule, "%d/%m/%Y %H:%M")
        return True
    except ValueError:
        return False 