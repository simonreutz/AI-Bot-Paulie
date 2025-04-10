import streamlit as st
from datetime import datetime
import pandas as pd
from training_plans import training_plans
from adherence_model import score_adherence, classify_run
from strava_auth import display_strava_login, exchange_code_for_token
from strava_api import fetch_recent_activities, format_activities
from weekly_aggregator import aggregate_weekly_sessions
from plan_detector import detect_best_plan_and_week
from nutrition_tips import tips as nutrition_tips
from progress_tracker import log_week_result, load_all_logs
from sheets_logger import log_week_result, load_all_logs

st.set_page_config(page_title="Marathon AI Coach", layout="centered")
st.title("🏃 Marathon AI Coach – Smart Plan Detection MVP")

# --- STRAVA CONNECTION ---
query_params = st.query_params
if "code" not in query_params:
    display_strava_login()
    st.stop()

code = query_params["code"]
token_data = exchange_code_for_token(code)

if not token_data or "access_token" not in token_data:
    st.error("❌ Failed to exchange code for token. Please reconnect to Strava.")
    st.stop()

access_token = token_data["access_token"]

# --- FETCH & PROCESS STRAVA DATA ---
st.subheader("📈 Weekly Training Analysis from Strava")
activities = fetch_recent_activities(access_token)
formatted_runs = format_activities(activities)

if not formatted_runs:
    st.warning("No recent Strava runs found.")
    st.stop()

st.write("**Detected Runs This Week:**", len(formatted_runs))
st.dataframe(pd.DataFrame(formatted_runs))

# --- SESSION CLASSIFICATION ---
classified = []
for run in formatted_runs:
    category = classify_run(run)
    run["type"] = category
    classified.append(run)

# --- AGGREGATE + FITNESS PROFILE ---
actual_sessions = aggregate_weekly_sessions(classified)
session_count = sum(actual_sessions.values())
longest = max(run["distance_km"] for run in classified)
weekly_km = sum(run["distance_km"] for run in classified)
avg_pace = sum(run["avg_pace_min_per_km"] for run in classified) / len(classified)

fitness_profile = {
    "weekly_distance": weekly_km,
    "session_count": session_count,
    "longest_run_km": longest,
    "avg_pace": avg_pace
}

# --- PLAN DETECTION ---
best_plan, best_week, match_score, next_weeks = detect_best_plan_and_week(fitness_profile, training_plans)

if not best_plan:
    st.warning("Could not match your recent training to a known plan. Try again next week or check your data.")
    st.stop()

# --- RECOMMENDED PLAN DISPLAY ---
st.subheader("🧠 Recommended Training Plan")
st.markdown(f"**{best_plan['source']}** — Start in **Week {best_week}** (Match Score: `{match_score}`)")
# Contextual description for Week 0 or very low fitness
if best_week == 1 and fitness_profile["weekly_distance"] < 5:
    st.info("This week seems to be a **rest or recovery phase**. Week 0 is a great time to rebuild base fitness or return after injury.")
elif best_week == 1:
    st.info("🏁 You're at the **start of a structured training plan**. Let’s build up gradually from here!")
st.caption("Based on your current fitness profile from the past week.")

# --- UPCOMING TRAINING BLOCK ---
st.subheader("📅 Upcoming Sessions")
for i, week in enumerate(next_weeks):
    st.markdown(f"**Week {best_week + i}**: {week}")

# --- ADHERENCE SCORING ---
st.subheader("📊 Weekly Plan Adherence")
plan_sessions = best_plan["session_types"]
result = score_adherence(plan_sessions, actual_sessions)

st.metric("Score", f"{result['adherence_score']*100:.0f}%")
st.markdown(f"**Assessment:** {result['label']}")

# --- Score Explanation ---
st.caption("Your adherence score compares your actual sessions (by type and frequency) with your expected plan structure. 100% = full alignment.")

# --- Named Breakdown ---
st.markdown("**Plan Weekly Distribution:**")
for k, v in result["plan_norm"].items():
    st.markdown(f"- {k.replace('_', ' ').title()}: {v}")

st.markdown("**Your Week’s Sessions:**")
for k, v in result["actual_norm"].items():
    st.markdown(f"- {k.replace('_', ' ').title()}: {v}")

# --- AI Coach Feedback ---
st.subheader("🤖 AI Coach Feedback")
feedback = ""

if result["label"] == "Excellent":
    feedback += "🔥 You're right on track! Keep it up.\n"
elif result["label"] == "Slightly off":
    feedback += "⚠️ You missed some planned sessions — watch your intensity and consistency.\n"
elif result["label"] == "Needs improvement":
    feedback += "❗ You're missing key workouts. Let’s refocus this week."

if actual_sessions.get("interval", 0) == 0 and plan_sessions.get("interval", 0) > 0:
    feedback += "\nTry to complete your intervals next week — they’re important for speed and VO₂ max."

st.success(feedback)

# --- LOG WEEKLY RESULT ---
st.write("📤 Logging to sheet:", best_plan["source"], best_week, result["adherence_score"])
log_week_result(
    best_plan["source"],
    best_week,
    result["adherence_score"],
    result["plan_norm"],
    result["actual_norm"]
)

# --- NUTRITION TIPS ---
st.subheader("🍝 Nutrition Tips for Upcoming Key Sessions")

# Count types across both weeks
upcoming_counts = {}
for week in next_weeks:
    for session_type, count in week.items():
        upcoming_counts[session_type] = upcoming_counts.get(session_type, 0) + count

# Show tips for relevant session types
for session_type, count in upcoming_counts.items():
    if session_type in nutrition_tips:
        st.markdown(f"### {session_type.replace('_', ' ').title()} ({count}x)")
        st.markdown(f"- **Before**: {nutrition_tips[session_type]['pre']}")
        st.markdown(f"- **After**: {nutrition_tips[session_type]['post']}")

# --- WEEKLY HISTORY VISUALIZATION ---
st.subheader("📈 Your Weekly Progress")

logs = load_all_logs()
if logs:
    df = pd.DataFrame(logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["week_label"] = df["plan"] + " - W" + df["week"].astype(str)

    st.line_chart(df.set_index("timestamp")["score"])

    st.dataframe(df[["timestamp", "plan", "week", "score"]].sort_values("timestamp", ascending=False))
else:
    st.info("No weekly history yet. Complete at least one week to begin tracking.")

