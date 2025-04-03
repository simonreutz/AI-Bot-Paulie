import math

def classify_run(run):
    """Classifies a run into one of the 4 types."""
    distance = run["distance_km"]
    pace = run["avg_pace_min_per_km"]
    pace_std = run.get("pace_std", 0.2)

    if distance >= 15:
        return "long_run"
    elif pace_std > 0.5 and distance <= 10:
        return "interval"
    elif pace < 5.2:
        return "tempo"
    else:
        return "easy"

def normalize_vector(vec):
    total = sum(vec.values())
    return {k: round(v / total, 2) if total > 0 else 0 for k, v in vec.items()}

def weighted_score(plan_vec, actual_vec, weights=None):
    if not weights:
        weights = {"easy": 1.0, "tempo": 1.5, "long_run": 2.0, "interval": 1.5}
    score = 0
    for key in weights:
        diff = abs(plan_vec.get(key, 0) - actual_vec.get(key, 0))
        score += weights[key] * diff
    max_score = sum(weights.values())
    return round(1.0 - score / max_score, 2)

def label_adherence(score):
    if score > 0.9:
        return "Excellent"
    elif score > 0.75:
        return "Good"
    elif score > 0.5:
        return "Slightly off"
    else:
        return "Needs improvement"

def score_adherence(plan_sessions, actual_sessions):
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
