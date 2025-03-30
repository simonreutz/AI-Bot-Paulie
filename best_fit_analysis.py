def score_user_against_plan(user, plan):
    score = 0
    total_weight = 0

    # Score for total session frequency
    freq_target = plan["weekly_sessions_avg"]
    freq_score = 1 - abs(user["total_sessions"] - freq_target) / freq_target
    score += freq_score * 0.3
    total_weight += 0.3

    # Score for matching session types
    type_score = 0
    required_types = plan["session_types"]
    for stype, req_count in required_types.items():
        actual = user["session_types"].get(stype, 0)
        match = min(actual / req_count, 1.0)
        type_score += match
    type_score = type_score / len(required_types)
    score += type_score * 0.5
    total_weight += 0.5

    # Score for long run distance
    plan_long = plan["long_run_max_km"]
    user_long = user["long_run_distance_km"]
    dist_score = min(user_long / plan_long, 1.0)
    score += dist_score * 0.2
    total_weight += 0.2

    return round(score / total_weight, 2)


def compare_user_to_all_plans(user_week, training_plans):
    scores = {
        plan["source"]: score_user_against_plan(user_week, plan)
        for plan in training_plans
    }
    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    return sorted_scores
