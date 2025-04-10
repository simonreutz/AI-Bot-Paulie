# plan_detector.py
from sheets_logger import load_user_logs

def analyze_adherence_trend(logs_for_plan):
    # Sort logs by date
    sorted_logs = sorted(logs_for_plan, key=lambda x: x["timestamp"])
    last_logs = sorted_logs[-3:]  # use last 2–3 weeks

    scores = [float(log["score"]) for log in last_logs]
    last_week = int(last_logs[-1]["week"])

    if len(scores) >= 2 and all(s >= 0.85 for s in scores[-2:]):
        return last_week + 2
    elif len(scores) >= 2 and all(s < 0.6 for s in scores[-2:]):
        return max(1, last_week - 1)
    else:
        return last_week
def compute_similarity(user_profile, plan_week):
    return round(1 / (
        1 +
        abs(user_profile["weekly_distance"] - plan_week["weekly_distance"]) +
        abs(user_profile["longest_run_km"] - plan_week["longest_run_km"]) +
        abs(user_profile["session_count"] - plan_week["session_count"])
    ), 3)

def detect_best_plan_and_week(user_profile, training_plans, user_id=None):
    # Step 1: Default best match by similarity
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

    # Step 2: Adaptive adjustment from user log
    if user_id:
        logs = load_user_logs(user_id)
        user_logs_for_plan = [l for l in logs if l["plan"] == best_plan["source"]]
        if user_logs_for_plan:
            last_entry = user_logs_for_plan[-1]
            last_week = int(last_entry["week"])
            last_score = float(last_entry["score"])

            if last_score >= 0.85:
                best_week = last_week + 1
            elif last_score < 0.6 and last_week > 1:
                best_week = last_week - 1
            else:
                best_week = last_week  # repeat current week

    # Step 3: Next 2 weeks of content
    next_weeks = best_plan["weeks"][best_week - 1:best_week + 1]
    return best_plan, best_week, best_score, next_weeks
