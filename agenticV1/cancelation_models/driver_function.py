import joblib
import pandas as pd
from utils.types import DriverCancels

# Load the trained model
pipeline = joblib.load('cancelation_models/driver_cancels.pkl')

# Cluster-to-decision mapping
cluster_label_map = {
    0: "fee waived",
    1: "base fee",
    2: "base + variable fee"
}

def predict_driver_cancellation_decision(cancelation: DriverCancels) -> str:
    """
    Predicts cancellation fee decision based on rules and clustering model.
    """

    if not cancelation.arrived:
        return "fee waived"
    
    if cancelation.distance_from_pin > 100:
        return "fee waived"
    
    if cancelation.wait_time is not None and cancelation.wait_time <= 2:
        return "fee waived"

    # If none of the rule-based conditions apply, use the ML model
    X_input = pd.DataFrame([{
        'rider_rating': cancelation.rider_rating,
        'wait_time': cancelation.wait_time
    }])
    
    cluster = pipeline.predict(X_input)[0]
    return cluster_label_map.get(cluster, "fee waived")


