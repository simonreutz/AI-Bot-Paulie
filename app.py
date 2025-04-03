# app.py - Marathon AI Coach (Universal Version + Plan Detection)
import streamlit as st
from datetime import datetime
import pandas as pd
from training_plans import training_plans
from adherence_model import score_adherence
from strava_auth import display_strava_login, exchange_code_for_token
from strava_api import fetch_recent_activities, format_activities
from weekly_aggregator import aggregate_weekly_sessions
from plan_detector import detect_best_plan_and_week

st.set_page_config(page_title="Marathon AI Coach", layout="centered")
st.title("🏃 Marathon AI Coach - Universal MVP")

# --- MODE TOGGLE ---
input_mode = st.radio("Choose input method", ["Strava Connect", "Manual Entry"])
session_data = None
formatted_runs = []

# --- STRAVA FLOW ---
if input_mode == "Strava Connect":
    query_params = st.query_params
    if "code" not in query_params:
        display_strava_login()
        st.stop()

    code = query_params["code"]
    token_data = exchange_code_for_token(code)
    access_token = token_data["access_token"]

    # --- FETCH & PROCESS STRAVA DATA ---
    st.subheader("📈 Weekly Training Analysis from Strava")
    activities = fetch_recent_activities(access_token)
    formatted_runs = format_activities(activities)

    if not formatted_runs:
        st.warning("No recent Strava runs found. Do a workout and check back!")
        st.stop()

    st.write("**Detected Runs This Week:**", len(formatted_runs))
    st.dataframe(pd.DataFrame(formatted_runs))

else:
    # --- MANUAL SESSION ENTRY ---
    st.header("📋 Log Your Training Session")
    session_date = st.date_input("Date", value=datetime.today())
    distance_km = st.number_input("Distance (km)", step=0.1)
    duration_min = st.number_input("Duration (min)", step=1)
    avg_pace = st.text_input("Average Pace (min/km)")
    run_type = st.selectbox("Type", ["Easy Run", "Tempo", "Long Run", "Interval"])
    submit = st.button("Submit Training")

    if submit:
        session_data = {
            "date": str(session_date),
            "distance_km": distance_km,
            "duration_min": duration_min,
            "avg_pace_min_per_km": float(avg_pace) if avg_pace else 5.5,
            "pace_std": 0.2,
            "type": run_type
        }
        formatted_runs = [session_data]

# --- DETECT PLAN ---
if formatted_runs:
    # Build user fitness profile
    total_km = sum(run["distance_km"] for run in formatted_runs)
    max_long = max(run["distance_km"] for run in formatted_runs)
    avg_sessions = len(formatted_runs)
    avg_pace = round(sum(run["avg_pace_min_per_km"] for run in formatted_runs) / len(formatted_runs), 2)

    user_profile = {
        "weekly_distance": total_km,
        "longest_run_km": max_long,
        "session_count": avg_sessions,
        "avg_pace": avg_pace
    }

    best_plan, best_week, match_score, next_weeks = detect_best_plan_and_week(user_profile, training_plans)

    st.subheader("📋 Plan Recommendation")
    st.success(f"🏅 Recommended Plan: {best_plan}  |  Start at Week {best_week}")
    st.caption(f"Matching Score: {match_score}")

    st.markdown("### 🔮 Your Next 2 Weeks of Training")
    for i, week in enumerate(next_weeks, start=best_week):
        st.markdown(f"**Week {i}:** {week}")

    actual_sessions = aggregate_weekly_sessions(formatted_runs)
    plan_sessions = training_plans[[p["source"] for p in training_plans].index(best_plan)]["session_distribution"]

    # --- SCORING ---
    st.subheader("📊 Weekly Plan Adherence")
    result = score_adherence(plan_sessions, actual_sessions)

    st.metric("Score", f"{result['adherence_score']*100:.0f}%")
    st.write(f"**Assessment:** {result['label'].capitalize()}")
    st.caption(f"Planned → {result['plan_norm']}")
    st.caption(f"Actual  → {result['actual_norm']}")

    st.subheader("🤖 AI Coach Feedback")
    st.success("You’re building up consistently. Great job!")

else:
    st.info("Submit a session or connect to Strava to get started.")

st.caption("🚧 Nutrition engine coming soon.")
