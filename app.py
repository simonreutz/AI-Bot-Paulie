# app.py - Marathon AI Coach (Universal Version)
import streamlit as st
from datetime import datetime
import pandas as pd
from training_plans import training_plans
from adherence_model import score_adherence
from strava_auth import display_strava_login, exchange_code_for_token
from strava_api import fetch_recent_activities, format_activities
from weekly_aggregator import aggregate_weekly_sessions

st.set_page_config(page_title="Marathon AI Coach", layout="centered")
st.title("🏃 Marathon AI Coach - Universal MVP")

# --- TRAINING PLAN SETUP ---
plan_names = [plan["source"] for plan in training_plans]
selected_plan_name = st.sidebar.selectbox("Choose a Training Plan", plan_names)
selected_plan = next(plan for plan in training_plans if plan["source"] == selected_plan_name)
training_week = st.sidebar.number_input("Which week are you on?", min_value=1, max_value=24, value=1)

# --- MODE TOGGLE ---
input_mode = st.radio("Choose input method", ["Strava Connect", "Manual Entry"])
session_data = None

# --- STRAVA FLOW ---
if input_mode == "Strava Connect":
    query_params = st.experimental_get_query_params()
    if "code" not in query_params:
        display_strava_login()
        st.stop()

    code = query_params["code"][0]
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

    actual_sessions = aggregate_weekly_sessions(formatted_runs)

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

    if session_data:
        detected_type = run_type.lower().replace(" ", "_")
        actual_sessions = {t: 0 for t in ["easy", "tempo", "long_run", "interval"]}
        if detected_type in actual_sessions:
            actual_sessions[detected_type] += 1
    else:
        actual_sessions = None

# --- SCORING BLOCK ---
if actual_sessions:
    st.subheader("📊 Weekly Plan Adherence")
    plan_sessions = selected_plan["session_types"]
    result = score_adherence(plan_sessions, actual_sessions)

    st.metric("Score", f"{result['adherence_score']*100:.0f}%")
    st.write(f"**Assessment:** {result['label'].capitalize()}")
    st.caption(f"Planned → {result['plan_norm']}")
    st.caption(f"Actual  → {result['actual_norm']}")
    st.markdown("---")

    st.subheader("🤖 AI Coach Feedback")
    if input_mode == "Manual Entry" and session_data:
        feedback = "Solid run! Keep your effort steady." if "easy" in detected_type else "Good effort — keep variety in your training."
        if session_data.get("distance_km") and session_data["distance_km"] < 8:
            feedback += " Consider adding distance for endurance."
        elif session_data.get("distance_km") and session_data["distance_km"] > 15:
            feedback += " Strong volume — manage recovery well."
        st.success(feedback)
else:
    st.info("Submit a session or connect to Strava to get feedback.")

st.caption("🚧 Plan detection & nutrition engine coming soon.")
