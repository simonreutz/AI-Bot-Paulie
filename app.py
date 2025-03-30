
import streamlit as st
import pandas as pd
import numpy as np
import easyocr
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Marathon AI Coach", layout="centered")
st.title("🏃‍♂️ Marathon AI Coach")
st.write("Upload your Strava data or manually input a run to receive intelligent training insights.")

# File upload section
uploaded_file = st.file_uploader("📁 Upload your Strava CSV file", type=["csv"])

# Manual KPI insertion form
with st.expander("📝 Or manually enter a single run" ):
    with st.form("manual_form"):
        manual_date = st.date_input("Activity Date")
        distance = st.number_input("Distance (km)", min_value=0.0, format="%.2f")
        time_minutes = st.number_input("Elapsed Time (min)", min_value=0.0, format="%.2f")
        pace = st.number_input("Average Pace (min/km)", min_value=0.0, format="%.2f")
        avg_hr = st.number_input("Average Heart Rate", min_value=0)
        max_hr = st.number_input("Max Heart Rate", min_value=0)
        session_type = st.selectbox("Session Type", ["Easy Run", "Interval Run", "Long Run", "Fast Distance Run"])
        submitted = st.form_submit_button("Add Run")

    if submitted:
        st.success("Run added!")
        manual_df = pd.DataFrame({
            "Activity Date": [manual_date],
            "Distance": [distance],
            "Elapsed Time": [time_minutes],
            "Pace_min_per_km": [pace],
            "Average Heart Rate": [avg_hr],
            "Max Heart Rate": [max_hr],
            "Session Type": [session_type]
        })
        st.dataframe(manual_df)

# Screenshot OCR extraction
with st.expander("🖼️ Upload a Strava Screenshot (OCR-based)"):
    screenshot = st.file_uploader("Upload PNG or JPG screenshot", type=["png", "jpg", "jpeg"], key="ocr")
    if screenshot:
        image = Image.open(BytesIO(screenshot.read()))
        st.image(image, caption="Uploaded Screenshot", use_column_width=True)

        reader = easyocr.Reader(['en'], gpu=False)
        with st.spinner("🔍 Extracting data with OCR..."):
            results = reader.readtext(np.array(image), detail=0)

        st.subheader("🔎 OCR Extracted Text")
        for line in results:
            st.write(line)

        # Placeholder: Extract structured data (e.g., regex on `results`) in future steps
        st.info("🧠 In future, we will parse these results into structured KPIs automatically.")

# If CSV uploaded, show preview
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("CSV uploaded successfully!")
    st.dataframe(df.head())
