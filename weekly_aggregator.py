# weekly_aggregator.py
from typing import List, Dict
from adherence_model import classify_run

# Each run should have fields: distance_km, duration_min, avg_pace_min_per_km, pace_std

def aggregate_weekly_sessions(runs: List[Dict]) -> Dict[str, int]:
    """
    Classifies and counts session types from a list of runs.
    Returns a dict like: {"easy": 2, "tempo": 1, "long_run": 1, "interval": 1}
    """
    session_counts = {"easy": 0, "tempo": 0, "long_run": 0, "interval": 0}
    
    for run in runs:
        session_type = classify_run(run)
        if session_type in session_counts:
            session_counts[session_type] += 1
    
    return session_counts

# Example input:
example_week = [
    {"distance_km": 5.2, "duration_min": 30, "avg_pace_min_per_km": 5.7, "pace_std": 0.1},  # easy
    {"distance_km": 8.0, "duration_min": 44, "avg_pace_min_per_km": 5.5, "pace_std": 0.2},  # easy
    {"distance_km": 14.5, "duration_min": 80, "avg_pace_min_per_km": 5.4, "pace_std": 0.25}, # long run
    {"distance_km": 9.0, "duration_min": 45, "avg_pace_min_per_km": 4.6, "pace_std": 0.65}   # interval
]

if __name__ == "__main__":
    summary = aggregate_weekly_sessions(example_week)
    print("Weekly Session Summary:", summary)
