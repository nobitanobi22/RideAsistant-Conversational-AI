import pandas as pd
import random
import numpy as np
from utils.types import DriverCancels

# Load user and driver data
sample_riders = pd.read_csv('Data_Generation/users.csv')
sample_drivers = pd.read_csv('Data_Generation/drivers.csv')

target_samples = 1000
filtered_cancellations: list[DriverCancels] = []
i = 0  # for unique cancelation_id

while len(filtered_cancellations) < target_samples:
    # Sample one rider and driver
    rider = sample_riders.sample(n=1).iloc[0]
    driver = sample_drivers.sample(n=1).iloc[0]

    rider_id = rider['rider_id']
    driver_id = driver['driver_id']
    rider_rating = rider['rider_rating']

    # Generate features
    distance_from_pin = int(np.clip(np.random.gamma(shape=2.5, scale=80), 0, 500))
    arrived = True if distance_from_pin < 20 else random.choice([True, False])
    wait_time = int(np.clip(np.random.gamma(shape=2, scale=2), 1, 10)) if arrived else None

    # Apply filter criteria
    if arrived and distance_from_pin <= 100 and wait_time is not None and wait_time > 2:
        cancelation_id = f"CD{1000 + i}"
        cancellation = DriverCancels(
            cancelation_id=cancelation_id,
            rider_id=rider_id,
            driver_id=driver_id,
            arrived=arrived,
            distance_from_pin=distance_from_pin,
            wait_time=wait_time,
            rider_rating=rider_rating
        )
        filtered_cancellations.append(cancellation)
        i += 1

# Export to CSV
df = pd.DataFrame([c.model_dump() for c in filtered_cancellations])
output_path = "Data_Generation/driver_cancellations_filtered.csv"
df.to_csv(output_path, index=False)