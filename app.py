import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Marathon AI Coach", layout="centered")
st.title("🏃‍♂️ Marathon AI Coach")
st.markdown("Upload your Strava data and receive intelligent training insights.")

# --- Upload Section ---
file = st.file_uploader("📁 Upload your Strava CSV file", type=["csv"])

if file:
    df = pd.read_csv(file)
    df['Activity Date'] = pd.to_datetime(df['Activity Date'])
    df = df[df['Distance'] > 0]

    # --- Validate Required Columns ---
    required_columns = ['Distance', 'Elapsed Time', 'Activity Date', 'Average Heart Rate', 'Max Heart Rate']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"❗ Missing required columns in your upload: {', '.join(missing)}. Please check your Strava export settings.")
        st.stop()

    df = df.dropna(subset=['Average Heart Rate'])

    # Feature engineering
    df['Average Pace_min_per_km'] = df['Elapsed Time'] / 60 / df['Distance']

    # If Session Type not in file, classify automatically
    if 'Session Type' not in df.columns:
        def classify_run(row):
            hr = row['Average Heart Rate']
            dist = row['Distance']
            pace = row['Average Pace_min_per_km']
            if dist < 9 and pace < 4.8 and hr > 165:
                return 'Interval Run'
            elif dist > 10 and hr >= 165:
                return 'Long Run'
            elif dist >= 8 and pace < 5.5 and hr > 149:
                return 'Fast Distance Run'
            else:
                return 'Easy Run'
        df['Session Type'] = df.apply(classify_run, axis=1)

    df['Session Type_encoded'] = df['Session Type'].astype('category').cat.codes

    st.success("✅ Data uploaded and processed successfully.")

    # --- Weekly Training Gap Analysis ---
    st.header("📅 Weekly Training Overview")
    weekly_targets = {
        "Interval Run": 1,
        "Long Run": 1,
        "Easy Run": 2,
        "Fast Distance Run": 1
    }

    today = df['Activity Date'].max()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    this_week_data = df[(df['Activity Date'] >= start_of_week) & (df['Activity Date'] <= end_of_week)]
    actual_counts = this_week_data['Session Type'].value_counts().to_dict()

    # Display Weekly Gap Table
    session_gap_report = []
    for session, required in weekly_targets.items():
        actual = actual_counts.get(session, 0)
        missing = max(0, required - actual)
        session_gap_report.append({
            'Session Type': session,
            'Required': required,
            'Completed': actual,
            'Missing': missing
        })

    gap_df = pd.DataFrame(session_gap_report)
    st.dataframe(gap_df)

    # --- Recommendations ---
    st.header("🤖 Weekly Recommendations")
    for _, row in gap_df.iterrows():
        if row['Missing'] > 0:
            if row['Session Type'] == 'Interval Run':
                st.warning(f"Add {row['Missing']} interval run(s) — 8×500m @ 4:50 pace.")
            elif row['Session Type'] == 'Long Run':
                st.warning(f"Add {row['Missing']} long run(s) — 15–20 km endurance pace.")
            elif row['Session Type'] == 'Easy Run':
                st.warning(f"Add {row['Missing']} easy run(s) — >7 km, low HR recovery pace.")
            elif row['Session Type'] == 'Fast Distance Run':
                st.warning(f"Add {row['Missing']} fast run(s) — 10–15 km @ 5:00–6:00 min/km.")

    # --- Optional: Prediction Engine ---
    st.header("🔮 Predict Pace & HR for Your Next Run")
    with st.form("prediction_form"):
        dist = st.slider("Planned Distance (km)", 5.0, 30.0, 12.0)
        max_hr = st.slider("Expected Max Heart Rate", 120, 200, 160)
        session_type = st.selectbox("Session Type", df['Session Type'].unique())
        session_encoded = int(df[df['Session Type'] == session_type]['Session Type_encoded'].iloc[0])
        submitted = st.form_submit_button("Predict")

    if submitted:
        # Train models
        X_pace = df[['Distance', 'Max Heart Rate', 'Session Type_encoded']]
        y_pace = df['Average Pace_min_per_km']
        pace_model = LinearRegression().fit(X_pace, y_pace)

        X_hr = df[['Distance', 'Average Pace_min_per_km', 'Session Type_encoded']]
        y_hr = df['Average Heart Rate']
        hr_model = LinearRegression().fit(X_hr, y_hr)

        # Predict
        pace_pred = pace_model.predict([[dist, max_hr, session_encoded]])[0]
        hr_pred = hr_model.predict([[dist, pace_pred, session_encoded]])[0]

        st.subheader("📈 Prediction Results")
        st.metric("Predicted Pace", f"{pace_pred:.2f} min/km")
        st.metric("Predicted Heart Rate", f"{hr_pred:.1f} bpm")
