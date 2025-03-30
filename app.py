from best_fit_analysis import compare_user_to_all_plans
from training_plans import get_all_plans
import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import re
from datetime import datetime, timedelta

st.set_page_config(page_title="Marathon AI Coach", page_icon="🏃")
st.title("🏃 Marathon AI Coach")
st.subheader("Upload your Strava data and receive intelligent training insights.")

uploaded_file = st.file_uploader("📂 Upload your Strava CSV or Screenshot", type=["csv", "png", "jpg", "jpeg"])

def extract_fields_from_text(text):
    fields = {
        "Distance": None,
        "Average Pace": None,
        "Elapsed Time": None,
        "Calories": None,
        "Elevation": None
    }
    dist_match = re.search(r"(\d+[.,]\d+)\s?km", text, re.IGNORECASE)
    if dist_match:
        fields["Distance"] = float(dist_match.group(1).replace(",", "."))

    pace_match = re.search(r"(\d{1,2}:\d{2})\s*/km", text)
    if pace_match:
        min, sec = map(int, pace_match.group(1).split(":"))
        fields["Average Pace"] = round(min + sec / 60, 2)

    time_match = re.search(r"(\d{1,2}:\d{2}:\d{2})", text)
    if time_match:
        h, m, s = map(int, time_match.group(1).split(":"))
        fields["Elapsed Time"] = round(h * 60 + m + s / 60, 2)

    cal_match = re.search(r"(\d+)\s*K?cal", text, re.IGNORECASE)
    if cal_match:
        fields["Calories"] = int(cal_match.group(1))

    elev_match = re.search(r"(\d+)\s?m", text)
    if elev_match:
        fields["Elevation"] = int(elev_match.group(1))

    return fields

def display_extracted_data(fields):
    st.subheader("📊 Extracted Run Summary")
    for k, v in fields.items():
        st.write(f"**{k}:** {v if v is not None else 'Not Found'}")

if uploaded_file:
    file_type = uploaded_file.type

    if "csv" in file_type:
        df = pd.read_csv(uploaded_file)
        df["Activity Date"] = pd.to_datetime(df["Activity Date"])
        st.dataframe(df.head())

        today = df["Activity Date"].max()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        this_week_data = df[(df["Activity Date"] >= start_of_week) & (df["Activity Date"] <= end_of_week)]
        session_counts = this_week_data["Session Type"].value_counts().to_dict()
        longest_run_km = this_week_data["Distance"].max()

        user_week = {
            "total_sessions": len(this_week_data),
            "session_types": session_counts,
            "long_run_distance_km": longest_run_km
        }

        st.header("🧠 Best-Fit Marathon Plan Analysis")
        plans = get_all_plans()
        plan_scores = compare_user_to_all_plans(user_week, plans)

        score_df = pd.DataFrame(plan_scores.items(), columns=["Training Plan", "Fit Score"])
        st.dataframe(score_df)
        # Identify top match
top_plan = score_df.sort_values("Fit Score", ascending=False).iloc[0]
plan_name = top_plan["Training Plan"]
fit_score = top_plan["Fit Score"]
st.markdown("### 🎯 Target Plan Guidance")
target_plan_name = st.selectbox(
    "Which training philosophy would you like to follow?",
    ["Hal Higdon", "Hansons", "Jack Daniels", "Renato Canova", "Nike"]
)
target_plan = [p for p in plans if p["source"] == target_plan_name][0]
target_sessions = target_plan["session_types"]

advice = []

# Weekly session volume
if user_week["total_sessions"] < target_plan["weekly_sessions_avg"]:
    advice.append(f"📅 Try to increase your weekly runs from {user_week['total_sessions']} to around {target_plan['weekly_sessions_avg']}.")

# Missing session types
for stype, req in target_sessions.items():
    actual = user_week["session_types"].get(stype, 0)
    if actual < req:
        advice.append(f"➕ Add more `{stype}` sessions (target: {req}/week, you did: {actual}).")

# Long run distance
if user_week["long_run_distance_km"] < target_plan["long_run_max_km"] * 0.85:
    advice.append(f"🏃‍♂️ Your long run was {user_week['long_run_distance_km']} km — aim for {target_plan['long_run_max_km']} km to match {target_plan_name}.")

# Display advice
if advice:
    st.markdown("#### 📋 Weekly Coaching Tips")
    for tip in advice:
        st.markdown(tip)
else:
    st.success("✅ You're already following this plan's structure closely!")
# Custom messages per plan
feedback_messages = {
    "Hal Higdon": "You're progressing like a classic runner — steady long runs and consistent weekly volume. Keep that rhythm going and consider mixing in some pace runs!",
    "Hansons": "Your training reflects Hansons' philosophy — shorter long runs but high weekly consistency. Great job handling the workload!",
    "Jack Daniels": "You're running with structure and variety — very Daniels-style. Stay mindful of pacing based on effort or VDOT zones.",
    "Renato Canova": "You're touching elite territory. Canova-style training demands intensity and variation — make sure recovery is in check.",
    "Nike": "You’re training smart and balanced. The Nike plan is ideal for intermediate runners — keep building mileage with purpose."
}

# Show interpretation
st.markdown(f"""
### 🧠 Recommendation
🏁 **Most aligned plan:** `{plan_name}`  
📊 **Fit Score:** `{fit_score:.2f}`  
💬 {feedback_messages.get(plan_name, "Keep it up — great structure this week!")}
""")

    elif "image" in file_type:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Screenshot", use_column_width=True)
        text = pytesseract.image_to_string(img)
        st.subheader("🔎 OCR Extracted Text")
        st.text(text)
        fields = extract_fields_from_text(text)
        display_extracted_data(fields)
