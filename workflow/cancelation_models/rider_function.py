import joblib
import pandas as pd
from utils.types import RiderCancels

# Load trained models
model1 = joblib.load('cancelation_models/rider_cancels_model1.pkl')
model2 = joblib.load('cancelation_models/rider_cancels_model2.pkl')
model3 = joblib.load('cancelation_models/rider_cancels_model3.pkl')

# Cluster-to-decision mappings
model1_decisions = {
    0: "base fee",
    1: "fee waived",
    2: "base + variable fee"
}

model2_decisions = {
    0: "base fee",
    1: "fee waived"
}

model3_decisions = {
    0: "base + variable fee",
    1: "fee waived",
    2: "base fee"
}

def predict_rider_cancellation_decision(cancel: RiderCancels) -> str:
    """
    Predict the fee decision based on rider cancellation data using pre-trained KMeans models.
    """

    if cancel.arrived:
        X = pd.DataFrame([{
            'rider_rating': cancel.rider_rating,
            'wait_time': cancel.wait_time,
            'rider_cancelation_rate': cancel.rider_cancelation_rate,
            'distance_from_pin': cancel.distance_from_pin
        }])
        cluster = model1.predict(X)[0]
        return model1_decisions.get(cluster, "fee waived")
    
    elif not cancel.arrived and cancel.cancelation_time is not None and cancel.cancelation_time <= 1:
        X = pd.DataFrame([{
            'rider_cancelation_rate': cancel.rider_cancelation_rate
        }])
        cluster = model2.predict(X)[0]
        return model2_decisions.get(cluster, "fee waived")

    else:
        X = pd.DataFrame([{
            'rider_rating': cancel.rider_rating,
            'cancelation_time': cancel.cancelation_time,
            'rider_cancelation_rate': cancel.rider_cancelation_rate
        }])
        cluster = model3.predict(X)[0]
        return model3_decisions.get(cluster, "fee waived")
