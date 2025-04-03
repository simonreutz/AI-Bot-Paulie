# strava_api.py
import requests
from datetime import datetime, timedelta

def fetch_recent_activities(access_token: str, days: int = 7):
    """Fetch activities from the last X days."""
    after_timestamp = int((datetime.utcnow() - timedelta(days=days)).timestamp())
    url = f"https://www.strava.com/api/v3/athlete/activities?after={after_timestamp}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching activities:", response.text)
        return []

def format_activities(raw_activities):
    runs = []
    for act in raw_activities:
        if act["type"] != "Run":
            continue

        distance_km = act["distance"] / 1000
        duration_min = act["elapsed_time"] / 60
        avg_pace = (duration_min / distance_km) if distance_km else 10
        # Placeholder for pace variability
        run = {
            "distance_km": round(distance_km, 2),
            "duration_min": round(duration_min, 1),
            "avg_pace_min_per_km": round(avg_pace, 2),
            "pace_std": 0.2  # stub value until pace samples available
        }
        runs.append(run)
    return runs
