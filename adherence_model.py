# adherence_model.py
from typing import Dict
import numpy as np

# --- Session Classification ---
def classify_run(run):
    if run.get("distance_km", 0) > 14 and run.get("duration_min", 0) > 75:
        return "long_run"
    elif run.get("pace_std", 0) > 0.6 and run.get("distance_km", 0) < 12:
        return "interval"
    elif run.get("avg_pace_min_per_km", 10) <= 5.0:
        return "tempo"
    else:
        return "easy"

# --- Normalize session distribution ---
def normalize_vector(vec: Dict[str, int]) -> Dict[str, float]:
    total = sum(vec.values())
    return {k: round(v / total, 3) for k, v in vec.items()} if total else vec

# --- Score adherence ---
def weighted_score(plan_vec, actual_vec, weights=None):
    if weights is None:
        weights = {"easy": 1.0, "tempo": 1.5, "long_run": 2.0, "interval": 1.5}
    
    score = 0
    for k in plan_vec:
        diff = abs(plan_vec.get(k, 0) - actual_vec.get(k, 0))
        score += weights.get(k, 1.0) * diff

    return round(1.0 - score / sum(weights.values()), 2)

# --- Generate feedback label ---
def label_adherence(score: float) -> str:
    if score >= 0.9:
        return "on track"
    elif score >= 0.75:
        return "slightly off"
    elif score >= 0.5:
        return "undertrained"
    else:
        return "missed key sessions"

# --- Main function ---
def score_adherence(plan_sessions: Dict[str, int], actual_sessions: Dict[str, int]) -> Dict:
    plan_norm = normalize_vector(plan_sessions)
    actual_norm = normalize_vector(actual_sessions)
    
    score = weighted_score(plan_norm, actual_norm)
    label = label_adherence(score)

    return {
        "adherence_score": score,
        "label": label,
        "plan_norm": plan_norm,
        "actual_norm": actual_norm
    }
