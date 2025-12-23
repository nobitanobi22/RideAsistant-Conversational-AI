"""
Features Required:
1. Cancelation_id
2. Rider_id, Driver_id
3. Driver_reached - bool
4. Rider_rating - float
5. Wait_time - int
6. Rider_cancelation_rate - float
7. Distance_to_pin, in meters - int
8. Cancelation time from booking, in mins - int
"""

import pandas as pd
import numpy as np
import random
from utils.types import RiderCancels

# Load users and drivers
sample_riders = pd.read_csv('Data_Generation/users.csv')
sample_drivers = pd.read_csv('Data_Generation/drivers.csv')

n_samples = 2000
rider_samples = sample_riders.sample(n=n_samples, replace=True).reset_index(drop=True)
driver_samples = sample_drivers.sample(n=n_samples, replace=True).reset_index(drop=True)

# Generate dataset
cancellations: list[RiderCancels] = []

for i in range(n_samples):
    cancelation_id = f"CR{1000 + i}"
    rider_id = rider_samples.loc[i, 'rider_id']
    driver_id = driver_samples.loc[i, 'driver_id']
    rider_rating = rider_samples.loc[i, 'rider_rating']
    cancel_rate = rider_samples.loc[i, 'cancelation_rate']

    distance_from_pin = int(np.clip(np.random.gamma(shape=2.5, scale=80), 0, 500))
    arrived = True if distance_from_pin < 20 else random.choice([True, False])
    wait_time = int(np.clip(np.random.gamma(shape=2, scale=2), 1, 10)) if arrived else None

    if arrived:
        cancelation_time = 0
    else:
        if random.random() < 0.2:  
            # ~20% chance to cancel under 1 minute
            cancelation_time = 1
        else:
            # Gamma-distributed for delays beyond 1 min
            cancelation_time = int(np.clip(np.random.gamma(shape=2.5, scale=4), 2, 30))

    cancellation = RiderCancels(
        cancelation_id=cancelation_id,
        rider_id=rider_id,
        driver_id=driver_id,
        arrived=arrived,
        distance_from_pin=distance_from_pin,
        wait_time=wait_time,
        rider_rating=rider_rating,
        rider_cancelation_rate=cancel_rate,
        cancelation_time=cancelation_time
    )

    cancellations.append(cancellation)

# Export to CSV
df = pd.DataFrame([c.model_dump() for c in cancellations])
output_path = "Data_Generation/rider_cancellations.csv"
df.to_csv(output_path, index=False)