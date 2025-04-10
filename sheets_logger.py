# sheets_logger.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import streamlit as st

# Google Sheets credentials from secrets
def connect_to_sheet():
    creds_dict = st.secrets["gcp_service_account"]
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("MarathonLog").worksheet("weekly_log")

def log_week_result(user_id, plan_name, week_num, score, plan_norm, actual_norm):
    try:
        sheet = connect_to_sheet()
        row = [
            datetime.utcnow().isoformat(),
            str(user_id),
            plan_name,
            week_num,
            round(score, 2),
            json.dumps(plan_norm),
            json.dumps(actual_norm)
        ]
        sheet.append_row(row)
        st.success("✅ Logged to Google Sheets!")
    except Exception as e:
        st.error("❌ Failed to log to Google Sheets.")
        st.exception(e)
def load_user_logs(user_id):
    sheet = connect_to_sheet()
    records = sheet.get_all_records()
    return [r for r in records if str(r["user_id"]) == str(user_id)]
