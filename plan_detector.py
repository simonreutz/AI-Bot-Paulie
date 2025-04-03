# plan_detector.py
from typing import Dict, List, Tuple

# Example user fitness profile from recent Strava data
# profile = {
#     "weekly_distance": 42,
#     "longest_run_km": 18,
#     "session_count": 4,
#     "avg_pace": 5.4
# }


def compute_similarity(user_profile: Dict, plan_week: Dict) -> float:
    """
    Compute similarity score between user fitness profile and a training plan week.
    Lower score = better match (like Euclidean distance)
    """
    keys = ["weekly_distance", "longest_run_km", "session_count"]
    diff_sum = 0
    for key in keys:
        u = user_profile.get(key, 0)
        p = plan_week.get(key, 0)
        diff_sum += (u - p) ** 2
    return round(diff_sum ** 0.5, 2)


def detect_best_plan_and_week(user_profile: Dict, plan_library: List[Dict]) -> Tuple[str, int, float]:
    """
    Loop through all plans and all weeks, find the best match.
    """
    best_match = None
    best_score = float("inf")
    best_plan_name = ""
    best_week = 0

    for plan in plan_library:
        plan_name = plan["source"]
        if "weeks" not in plan:
            continue  # skip plans with no structure

        for week_num, week in enumerate(plan["weeks"], start=1):
            score = compute_similarity(user_profile, week)
            if score < best_score:
                best_score = score
                best_match = week
                best_plan_name = plan_name
                best_week = week_num

    return best_plan_name, best_week, best_score
