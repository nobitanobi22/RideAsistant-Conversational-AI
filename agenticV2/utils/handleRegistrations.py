from utils.user_manager import UserManager

user_manager = UserManager()

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

def handle_user_registration():
    while True:
        print("\n=== User Registration ===")
        print("1. Create Rider Account")
        print("2. Create Driver Account")
        print("3. Back to Login")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n--- Create Rider Account ---")
            rider_id = input("Enter desired Rider ID (max 10 characters): ").strip()
            if len(rider_id) > 10:
                print("Error: Rider ID must be 10 characters or less")
                continue
                
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
                print(f"\nRider account created successfully!")
                print(f"Your ID: {rider.rider_id}")
                print(f"Rating: {rider.rider_rating:.1f}")
                print(f"Total Rides: {rider.total_rides_booked}")
                print(f"Cancellation Rate: {rider.cancelation_rate:.1f}%")
                return
            except ValueError as e:
                print(f"Error: {e}")
                
        elif choice == "2":
            print("\n--- Create Driver Account ---")
            driver_id = input("Enter desired Driver ID (max 10 characters): ").strip()
            if len(driver_id) > 10:
                print("Error: Driver ID must be 10 characters or less")
                continue
            
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