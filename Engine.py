import time
import random
from pyexpat import features

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from sklearn.ensemble import IsolationForest


class TransactionStreamSimulator:
    def __init__(self):
        self.user_pool = [f"USER_{i:04d}" for i in range(1, 15)]
        self.locations = ["BLR_IN", "DEL_IN", "MUM_IN", "MEX_MX", "SGP_SG"]

    def generate_event(self, force_fraud=False):
        user_id = random.choice(self.user_pool)
        if force_fraud:
            amount = round(random.uniform(45000.0, 95000.0), 2)
            location = "MEX_MX"
        else:
            amount = round(random.uniform(150.0, 4500.0), 2)
            location = random.choice(self.locations[:3])

        return {
            "transaction_id": f"TXN_{int(time.time() * 1000)}",
            "user_id": user_id,
            "amount": amount,
            "location": location,
            "timestamp": datetime.utcnow().isoformat()
        }


class VelocityFeatureEngine:
    def __init__(self, window_minutes=5):
        self.window_minutes = window_minutes
        self.user_state = defaultdict(list)

    def _clean_expired_events(self, user_id, current_time):
        cutoff_time = current_time - timedelta(minutes=self.window_minutes)
        self.user_state[user_id] = [
            tx for tx in self.user_state[user_id]
            if tx['timestamp_dt'] > cutoff_time
        ]

    def update_and_extract_features(self, event):
        current_time = datetime.fromisoformat(event['timestamp'])
        user_id = event['user_id']

        self._clean_expired_events(user_id, current_time)
        history = self.user_state[user_id]

        velocity_count_5m = len(history)
        velocity_sum_5m = sum(tx['amount'] for tx in history)

        last_location = history[-1]['location'] if history else event['location']
        location_jump = 1 if (history and last_location != event['location']) else 0

        self.user_state[user_id].append({
            'amount': event['amount'],
            'location': event['location'],
            'timestamp_dt': current_time
        })

        return {
            "txn_amount": event['amount'],
            "velocity_count_5m": velocity_count_5m,
            "velocity_sum_5m": velocity_sum_5m,
            "location_jump": location_jump
        }


class FraudRiskEvaluator:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self._bootstrap_ml_model()

    def _bootstrap_ml_model(self):
        normal_data = pd.DataFrame({
            "txn_amount": np.random.uniform(100, 5000, 500),
            "velocity_count_5m": np.random.poisson(lam=1.5, size=500),
            "velocity_sum_5m": np.random.uniform(100, 10000, 500),
            "location_jump": np.random.choice([0, 1], size=500, p=[0.95, 0.05])
        })
        self.model.fit(normal_data)

    def evaluate_risk(self, event, features):
        start_time = time.perf_counter()
        triggered_rules = []
        risk_score = 0.0

        if features['velocity_count_5m'] >= 3:
            triggered_rules.append("HIGH_VELOCITY_BURST")
            risk_score += 40.0

        if features['location_jump'] == 1:
            triggered_rules.append("GEOLOCATION_JUMP")
            risk_score += 35.0

        feature_vector = pd.DataFrame([features])
        is_anomaly = self.model.predict(feature_vector)[0]

        if is_anomaly == -1:
            triggered_rules.append("ML_ANOMALY_DETECTED")
            risk_score += 25.0

        final_risk_score = min(100.0, risk_score)

        if final_risk_score >= 70.0:
            decision = "REJECT"
        elif final_risk_score >= 35.0:
            decision = "FLAG_FOR_REVIEW"
        else:
            decision = "APPROVE"
        latency_ms = (time.perf_counter() - start_time) * 1000

        return {
            "transaction_id": event['transaction_id'],
            "user_id": event['user_id'],
            "amount": event['amount'],
            "location": event['location'],
            "risk_score": final_risk_score,
            "decision": decision,
            "triggered_rules": ", ".join(triggered_rules) if triggered_rules else "NONE",
            "latency_ms": latency_ms
        }


if __name__ == '__main__':
    data = TransactionStreamSimulator()
    velocity = VelocityFeatureEngine()
    fraud = FraudRiskEvaluator()

    for i in range(30):
        trigger = (i+1)%5 == 0
        event = data.generate_event(force_fraud=trigger)
        features = velocity.update_and_extract_features(event)
        final_output = fraud.evaluate_risk(event,features)
        print(
            f"Txn: {final_output['transaction_id']} | "
            f"User: {final_output['user_id']} | "
            f"Amount: ₹{final_output['amount']:.2f} | "
            f"Risk: {final_output['risk_score']:.0f} | "
            f"Decision: {final_output['decision']} | "
            f"Rules: {final_output['triggered_rules']} |"
            f"latency: {final_output['latency_ms']} |"
            f"location: {final_output['location']}"
        )
        time.sleep(0.5)

