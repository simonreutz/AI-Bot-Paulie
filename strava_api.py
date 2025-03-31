import requests

def get_recent_activities(token, limit=10):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"per_page": limit, "page": 1}
    url = "https://www.strava.com/api/v3/athlete/activities"

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return []

    activities = response.json()
    runs = [a for a in activities if a["type"] == "Run"]
    parsed = []

    for run in runs:
        parsed.append({
            "name": run["name"],
            "date": run["start_date_local"],
            "distance_km": round(run["distance"] / 1000, 2),
            "duration_min": round(run["elapsed_time"] / 60, 1),
            "avg_speed_kmh": round(run["average_speed"] * 3.6, 2),
            "type": "Long Run" if run["distance"] > 15 else "Easy Run"  # very basic type mapping
        })

    return parsed
