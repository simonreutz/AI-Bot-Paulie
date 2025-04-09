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

def log_week_result(plan_name, week_num, score, plan_norm, actual_norm):
    sheet = connect_to_sheet()
    row = [
        datetime.utcnow().isoformat(),
        plan_name,
        week_num,
        round(score, 2),
        json.dumps(plan_norm),
        json.dumps(actual_norm)
    ]
    sheet.append_row(row)

def load_all_logs():
    sheet = connect_to_sheet()
    records = sheet.get_all_records()
    return records
