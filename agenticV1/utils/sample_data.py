from utils.types import Rider, Driver
import random
import pandas as pd

sample_riders = pd.read_csv('Data_Generation/users.csv')
sample_drivers = pd.read_csv('Data_Generation/drivers.csv')


def get_rider_by_id_and_password(rider_id: str, password: str) -> Rider:
    for _, row in sample_riders.iterrows():
        if row['rider_id'] == rider_id and row['rider_password'] == password:
            return Rider(**row.to_dict())

    print("Invalid rider ID or password. Using default rider.")
    return Rider(**sample_riders.sample(1).iloc[0].to_dict())

def get_driver_by_id(driver_id: str) -> Driver:
    for _, row in sample_drivers.iterrows():
        if row['driver_id'] == driver_id:
            return Driver(**row.to_dict())

    print("Invalid driver ID. Using default driver.")
    return Driver(**sample_drivers.sample(1).iloc[0].to_dict())