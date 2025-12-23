import random
import string
import json
import os

def get_float_input(prompt: str, min_val: float, max_val: float) -> float:
    while True:
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a valid number")

def get_int_input(prompt: str, min_val: int) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value >= min_val:
                return value
            print(f"Please enter a value greater than or equal to {min_val}")
        except ValueError:
            print("Please enter a valid number")

# Utility to load existing IDs from a JSON database file
def load_ids_from_json(file_path: str, key: str) -> set:
    if not os.path.exists(file_path):
        return set()
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
            return {entry[key] for entry in data}
        except json.JSONDecodeError:
            return set()

def generate_rider_id():
    prefix = "user-"
    existing_ids = load_ids_from_json("data/riders.json", "rider_id")

    while True:
        part = (
            random.choice(string.ascii_uppercase) +
            ''.join(random.choices(string.digits, k=4))
        )
        rider_id = prefix + part
        if rider_id not in existing_ids:
            return rider_id

def generate_driver_id():
    prefix = "driver-"
    existing_ids = load_ids_from_json("data/drivers.json", "driver_id")

    while True:
        part = (
            random.choice(string.ascii_uppercase) +
            ''.join(random.choices(string.digits, k=2))
        )
        driver_id = prefix + part
        if driver_id not in existing_ids:
            return driver_id


def handle_user_registration(user_manager):
    """Handle user registration using the provided user_manager instance."""
    while True:
        print("\n=== User Registration ===")
        print("1. Create Rider Account")
        print("2. Create Driver Account")
        print("3. Back to Login")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n--- Create Rider Account ---")
            rider_id = generate_rider_id()
            print(f"User ID: {rider_id}")

            password = input("Enter password (min 8 characters): ").strip()
            if len(password) < 8:
                print("Error: Password must be at least 8 characters")
                continue
            
            # Get rider statistics
            print("\nPlease provide your riding history:")
            rider_rating = get_float_input("Enter your current rating (0-5): ", 0, 5)
            total_rides = get_int_input("Enter total rides booked: ", 0)
            prior_cancels = get_int_input("Enter number of prior cancellations: ", 0)
            
            # Calculate cancellation rate
            cancel_rate = (prior_cancels / total_rides * 100) if total_rides > 0 else 0.0
                
            try:
                rider = user_manager.create_rider(
                    rider_id=rider_id,
                    password=password,
                    rating=rider_rating,
                    total_rides=total_rides,
                    prior_cancels=prior_cancels,
                    cancel_rate=cancel_rate
                )
                print(f"\nRider account created successfully! (Remember ID and Password for further logins)")
                print(f"Your ID: {rider.rider_id}")
                print(f"Rating: {rider.rider_rating:.1f}")
                print(f"Total Rides: {rider.total_rides_booked}")
                print(f"Cancellation Rate: {rider.cancelation_rate:.1f}%")
            
                return
            except ValueError as e:
                print(f"Error: {e}")
                
        elif choice == "2":
            print("\n--- Create Driver Account ---")
            driver_id = generate_driver_id()
            print(f"Driver ID: {driver_id}")
            
            # Get driver statistics
            print("\nPlease provide your driving history:")
            driver_rating = get_float_input("Enter your current rating (0-5): ", 0, 5)
            total_rides = get_int_input("Enter total rides accepted: ", 0)
            prior_cancels = get_int_input("Enter number of prior cancellations: ", 0)
            
            # Calculate cancellation rate
            cancel_rate = (prior_cancels / total_rides * 100) if total_rides > 0 else 0.0
                
            try:
                driver = user_manager.create_driver(
                    driver_id=driver_id,
                    rating=driver_rating,
                    total_rides=total_rides,
                    prior_cancels=prior_cancels,
                    cancel_rate=cancel_rate
                )
                print(f"\nDriver account created successfully!")
                print(f"Your ID: {driver.driver_id}")
                print(f"Rating: {driver.driver_rating:.1f}")
                print(f"Total Rides: {driver.total_rides_accepted}")
                print(f"Cancellation Rate: {driver.cancelation_rate:.1f}%")
                
                return
            except ValueError as e:
                print(f"Error: {e}")
                
        elif choice == "3":
            return
        
        else:
            print("Invalid choice. Please try again.")