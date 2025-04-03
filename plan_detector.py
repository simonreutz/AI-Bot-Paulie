# plan_detector.py
def compute_similarity(user_profile, plan_week):
    """Simple Euclidean distance-based similarity."""
    return round(1 / (
        1 +
        abs(user_profile["weekly_distance"] - plan_week["weekly_distance"]) +
        abs(user_profile["longest_run_km"] - plan_week["longest_run_km"]) +
        abs(user_profile["session_count"] - plan_week["session_count"])
    ), 3)

def detect_best_plan_and_week(user_profile, training_plans):
    best_score = 0
    best_plan = None
    best_week = 0
    for plan in training_plans:
        for i, week in enumerate(plan.get("weeks", [])):
            score = compute_similarity(user_profile, week)
            if score > best_score:
                best_score = score
                best_plan = plan
                best_week = i + 1
    if not best_plan:
        return None, 0, 0.0, []

    # Get next 2 weeks (fallback to empty if at end)
    next_weeks = best_plan["weeks"][best_week-1:best_week+1]
    return best_plan, best_week, best_score, next_weeks
