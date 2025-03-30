# Re-run code after execution environment reset
import pandas as pd

# Define structured representations of five marathon training plans
training_plans = [
    {
        "source": "Hal Higdon",
        "level": "Intermediate",
        "duration_weeks": 18,
        "weekly_sessions_avg": 5,
        "session_types": {
            "easy": 2,
            "tempo": 1,
            "long_run": 1,
            "pace_run": 1
        },
        "long_run_max_km": 32,
        "taper_weeks": 3,
        "intensity_guidance": {
            "easy": "65-75% max HR",
            "tempo": "85-90% max HR",
            "long": "70-80% max HR"
        },
        "notes": "Cutback week every 4th week. Long runs build progressively. Taper begins week 16."
    },
    {
        "source": "Hansons",
        "level": "Beginner",
        "duration_weeks": 18,
        "weekly_sessions_avg": 6,
        "session_types": {
            "easy": 3,
            "tempo": 1,
            "long_run": 1,
            "speed": 1
        },
        "long_run_max_km": 26,
        "taper_weeks": 2,
        "intensity_guidance": {
            "easy": "60-70% max HR",
            "tempo": "goal marathon pace",
            "long": "goal marathon pace + 10-15 sec/km"
        },
        "notes": "Emphasizes cumulative fatigue. Long runs never exceed 26 km. Tempo runs every week from week 6."
    },
    {
        "source": "Jack Daniels",
        "level": "2Q Plan",
        "duration_weeks": 18,
        "weekly_sessions_avg": 5,
        "session_types": {
            "easy": 2,
            "quality": 2,
            "long_run": 1
        },
        "long_run_max_km": 32,
        "taper_weeks": 2,
        "intensity_guidance": {
            "easy": "60-70% max HR or VDOT E pace",
            "quality": "intervals, threshold, and long sessions based on VDOT",
            "long": "VDOT L pace"
        },
        "notes": "2 hard sessions per week (Q1 + Q2). Pace guidance driven by VDOT system."
    },
    {
        "source": "Renato Canova",
        "level": "Elite",
        "duration_weeks": 12,
        "weekly_sessions_avg": 10,
        "session_types": {
            "regeneration": 3,
            "fundamental": 3,
            "special": 2,
            "specific": 2
        },
        "long_run_max_km": 40,
        "taper_weeks": 2,
        "intensity_guidance": {
            "regeneration": "low effort",
            "fundamental": "aerobic base building",
            "special": "near race pace",
            "specific": "at race pace or faster"
        },
        "notes": "Periodized: Regeneration → Fundamental → Special → Specific. High intensity and volume for elites."
    },
    {
        "source": "Nike",
        "level": "Intermediate",
        "duration_weeks": 18,
        "weekly_sessions_avg": 5,
        "session_types": {
            "easy": 2,
            "speed": 1,
            "long_run": 1,
            "recovery": 1
        },
        "long_run_max_km": 32,
        "taper_weeks": 3,
        "intensity_guidance": {
            "easy": "light conversational",
            "speed": "intervals at 5K pace",
            "long": "70-80% max HR",
            "recovery": "very light"
        },
        "notes": "Alternates between build and cutback weeks. Mobile app provides adaptive feedback based on progress."
    }
]

# Convert to DataFrame for overview
df_plans = pd.DataFrame(training_plans)
import ace_tools as tools; tools.display_dataframe_to_user(name="Structured Marathon Training Plans", dataframe=df_plans)
def get_all_plans():
    return training_plans
