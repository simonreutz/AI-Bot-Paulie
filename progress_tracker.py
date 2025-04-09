# progress_tracker.py
import json
from datetime import datetime
import os

LOG_PATH = "weekly_log.json"

def log_week_result(plan_name, week_num, score, plan_norm, actual_norm):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "plan": plan_name,
        "week": week_num,
        "score": score,
        "plan_norm": plan_norm,
        "actual_norm": actual_norm
    }

    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_entry)

    with open(LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)

def load_all_logs():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r") as f:
        return json.load(f)
