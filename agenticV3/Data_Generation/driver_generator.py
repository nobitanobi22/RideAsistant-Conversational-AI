import random
import numpy as np
from utils.types import Driver  # Update this import path as needed
from Data_Generation.ratings import left_samples, right_samples, main_samples
import pandas as pd

"""
The rider-to-driver ratio on the Uber platform is approximately 20:1. This means for every 20 riders, there is roughly one driver available on the platform, according to Earnest Analytics. In more detail, Uber reported 161 million monthly active users and 7.8 million drivers, which translates to about 20.6 riders per driver. 
"""

n_samples = 100
drivers: dict[str, Driver] = {}

# Segmentation: high, medium, low cancel drivers
high_cancel_drivers = int(0.25 * n_samples)
medium_cancel_drivers = int(0.5 * n_samples)
low_cancel_drivers = n_samples - high_cancel_drivers - medium_cancel_drivers

cancel_rate_distribution = (
    ['high'] * high_cancel_drivers +
    ['medium'] * medium_cancel_drivers +
    ['low'] * low_cancel_drivers
)
random.shuffle(cancel_rate_distribution)

for idx, i in enumerate(range(100, 200)):
    driver_id = f"D{i}"
    total_rides = random.randint(0, 500)

    cancel_band = cancel_rate_distribution[idx]
    if cancel_band == 'high':
        cancel_rate = random.uniform(0.4, 1)
        rating = float(np.random.choice(left_samples))
    elif cancel_band == 'medium':
        cancel_rate = random.uniform(0.2, 0.4)
        rating = float(np.random.choice(main_samples))
    else:  # 'low'
        cancel_rate = random.uniform(0.0, 0.2)
        rating = float(np.random.choice(right_samples))

    prior_cancellations = int(total_rides * cancel_rate)
    if total_rides:
        cancelation_rate = prior_cancellations*100/total_rides
    else:
        cancelation_rate = 0

    driver = Driver(
        driver_id=driver_id,
        total_rides_accepted=total_rides,
        prior_cancellations=prior_cancellations,
        driver_rating=round(rating, 2),
        cancelation_rate=round(cancelation_rate,2)
    )
    drivers[driver_id] = driver

# Convert to list of dicts
driver_dicts = [driver.model_dump() for driver in drivers.values()]

# Create DataFrame and export
df = pd.DataFrame(driver_dicts)
output_path = "Data_Generation/drivers.csv"
df.to_csv(output_path, index=False)