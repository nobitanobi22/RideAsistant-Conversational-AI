import random
import numpy as np
from utils.types import Rider
from Data_Generation.ratings import left_samples, right_samples, main_samples
import pandas as pd

n_samples = 2000
riders: dict[str, Rider] = {}

# Segmentation: high, medium, low cancel users
high_cancel_users = int(0.25 * n_samples)
medium_cancel_users = int(0.5 * n_samples)
low_cancel_users = n_samples - high_cancel_users - medium_cancel_users

cancel_rate_distribution = (
    ['high'] * high_cancel_users +
    ['medium'] * medium_cancel_users +
    ['low'] * low_cancel_users
)
random.shuffle(cancel_rate_distribution)

for idx, i in enumerate(range(1000, 3000)):
    rider_id = f"U{i}"
    rider_password = f"pass{i}"
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

    rider = Rider(
        rider_id=rider_id,
        rider_password=rider_password,
        total_rides_booked=total_rides,
        prior_cancellations=prior_cancellations,
        rider_rating=round(rating, 2),
        cancelation_rate=round(cancelation_rate,2)
    )
    riders[rider_id] = rider

# Convert to list of dicts
rider_dicts = [rider.model_dump() for rider in riders.values()]

# Create DataFrame
df = pd.DataFrame(rider_dicts)

# Export to CSV
output_path = "Data_Generation/users.csv"
df.to_csv(output_path, index=False)

##Optional Preview
# for k, v in list(riders.items())[:5]:
#     print(k, v)

