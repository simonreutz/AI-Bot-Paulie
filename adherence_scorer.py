import joblib
import numpy as np

# Load model once
model = joblib.load("plan_adherence_model.pkl")

def extract_features(plan, actual):
    # Basic rules for feature engineering (must match training logic)
    plan_sessions = plan.get("weekly_sessions_avg", 5)
    actual_sessions = actual.get("sessions_completed", 0)
    session_ratio = actual_sessions / plan_sessions if plan_sessions else 0

    plan_long_km = plan.get("long_run_max_km", 30)
    actual_long_km = actual.get("longest_run_km", 0)
    long_ratio = actual_long_km / plan_long_km if plan_long_km else 0

    tempo_required = 1 if plan.get("session_types", {}).get("tempo", 0) > 0 else 0
    tempo_done = 1 if actual.get("tempo_done", 0) > 0 else 0
    long_done = 1 if actual_long_km >= 18 else 0

    return np.array([[session_ratio, long_ratio, tempo_required, tempo_done, long_done]])

def predict_adherence(plan, actual):
    features = extract_features(plan, actual)
    score = model.predict_proba(features)[0][1]  # probability of good adherence
    return round(score * 100, 1)
