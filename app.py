import streamlit as st
from datetime import datetime
import pandas as pd
import requests
from training_plans import training_plans  # ✅ This works now
from adherence_scorer import predict_adherence
from strava_auth import get_strava_auth_url, exchange_code_for_token
from strava_api import get_recent_activities
# ------------------------
# OCR Microservice API Call
# ------------------------
def parse_ocr_image_with_api(image_file):
    api_url = "https://YOUR-OCR-RENDER-URL.onrender.com/ocr"  # ⬅️ Replace with your deployed Render URL
    files = {'image': image_file}
    try:
        response = requests.post(api_url, files=files)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"OCR server error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Failed to connect to OCR server: {e}")
        return None

# ------------------------
# Streamlit UI
# ------------------------
st.set_page_config(page_title="Marathon AI Coach", layout="centered")
st.title("🏃 Marathon AI Coach - MVP")

# --- Sidebar Config ---
st.sidebar.header("🔗 Strava Connection")

# Step 1: If not connected, show login button
if "strava_token" not in st.session_state:
    auth_url = get_strava_auth_url()
    st.sidebar.markdown(f"[Connect with Strava]({auth_url})", unsafe_allow_html=True)

# Step 2: After redirect from Strava, capture ?code=...
query_params = st.experimental_get_query_params()
if "code" in query_params and "strava_token" not in st.session_state:
    with st.spinner("Connecting to Strava..."):
        auth_code = query_params["code"][0]
        token_data = exchange_code_for_token(auth_code)
        if "access_token" in token_data:
            st.session_state.strava_token = token_data["access_token"]
            st.sidebar.success("✅ Connected to Strava")
        else:
            st.sidebar.error("❌ Strava auth failed.")
elif "strava_token" in st.session_state:
    st.sidebar.success("✅ Connected to Strava")
if "strava_token" in st.session_state:
    st.header("📥 Recent Strava Runs")
    activities = get_recent_activities(st.session_state.strava_token)

    if activities:
        for a in activities:
            st.markdown(f"**{a['date']} – {a['name']}**")
            st.write(f"🛣 {a['distance_km']} km in {a['duration_min']} min, pace ≈ {round(a['duration_min'] / a['distance_km'], 2)} min/km")
            st.caption(f"🧠 Interpreted as: {a['type']}")
    else:
        st.warning("No recent running activities found.")
    activities = get_recent_activities(st.session_state.strava_token)

    if activities:
        for a in activities:
            st.markdown(f"**{a['date']} – {a['name']}**")
            st.write(f"🛣 {a['distance_km']} km in {a['duration_min']} min, pace ≈ {round(a['duration_min'] / a['distance_km'], 2)} min/km")
            st.caption(f"🧠 Interpreted as: {a['type']}")
    else:
        st.warning("No recent running activities found.")
st.sidebar.header("Training Setup")
plan_names = [plan["source"] for plan in training_plans]
selected_plan_name = st.sidebar.selectbox("Choose a Training Plan", plan_names)
selected_plan = next(plan for plan in training_plans if plan["source"] == selected_plan_name)
training_week = st.sidebar.number_input("Which week are you on?", min_value=1, max_value=24, value=1)

# --- Main Section ---
st.header("📋 Log Your Training Session")
input_method = st.radio("Input method", ["Manual Entry", "Upload Screenshot"])

session_data = None

# --- Manual Entry ---
if input_method == "Manual Entry":
    session_date = st.date_input("Date", value=datetime.today())
    distance_km = st.number_input("Distance (km)", step=0.1)
    duration_min = st.number_input("Duration (min)", step=1)
    avg_pace = st.text_input("Average Pace (min/km)")
    run_type = st.selectbox("Type", ["Easy Run", "Interval", "Long Run", "Tempo", "Recovery"])
    submit = st.button("Submit Training")
    
    if submit:
        session_data = {
            'date': str(session_date),
            'distance_km': distance_km,
            'duration_min': duration_min,
            'avg_pace': avg_pace,
            'type': run_type,
        }

# --- Screenshot Upload with OCR ---
else:
    uploaded_file = st.file_uploader("Upload Strava Screenshot", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Screenshot", use_column_width=True)
        session_data = parse_ocr_image_with_api(uploaded_file)
        if session_data:
            st.success("Parsed session data:")
            st.json(session_data)

# --- Feedback Logic ---
if session_data:
    expected = f"{selected_plan['weekly_sessions_avg']} sessions/week (e.g. {selected_plan['session_types']})"
    actual = f"{session_data.get('distance_km', '?')}km {session_data.get('type', '?')} in {session_data.get('duration_min', '?')} min"

    st.subheader("🔍 Training Plan Alignment")
    st.write(f"**Week {training_week} - {selected_plan_name}**")
    st.markdown(f"**Planned:** {expected}")
    st.markdown(f"**Your Session:** {actual}")

    st.subheader("🤖 AI Coach Feedback")
    feedback = "Looks good! Keep consistency." if "Easy" in session_data.get('type', '') else "Nice work — make sure to alternate intensity."
    if session_data.get('distance_km') and session_data['distance_km'] < 8:
        feedback += " Consider increasing long run distance gradually."
    elif session_data.get('distance_km') and session_data['distance_km'] > 15:
        feedback += " Great endurance! Monitor fatigue."

    st.success(feedback)
    st.markdown("---")
    st.caption("🚧 More advanced feedback with zones, HR, and fitness prediction coming soon.")
# --- ML-Based Plan Adherence Score ---
from adherence_scorer import predict_adherence

if isinstance(session_data, dict):
    actual_summary = {
        "sessions_completed": 1,
        "tempo_done": 1 if "tempo" in session_data.get("type", "").lower() else 0,
        "longest_run_km": session_data.get("distance_km", 0),
    }

    score = predict_adherence(selected_plan, actual_summary)

    st.subheader("📊 Plan Adherence Score")
    st.metric(label="This Week", value=f"{score} %")

    if score < 60:
        st.warning("You're falling off the plan. Try to stick to your key sessions.")
    elif score < 80:
        st.info("Decent effort! Aim to hit long runs and tempo sessions.")
    else:
        st.success("Great job following the plan!")

score = predict_adherence(selected_plan, actual_summary)

st.subheader("📊 Plan Adherence Score")
st.metric(label="This Week", value=f"{score} %")

if score < 60:
    st.warning("You're falling off the plan. Try to stick to your key sessions.")
elif score < 80:
    st.info("Decent effort! Aim to hit long runs and tempo sessions.")
else:
    st.success("Great job following the plan!")
