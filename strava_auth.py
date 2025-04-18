import streamlit as st
import requests

# ✅ Load from secrets
STRAVA_CLIENT_ID = st.secrets["strava"]["client_id"]
STRAVA_CLIENT_SECRET = st.secrets["strava"]["client_secret"]
REDIRECT_URI = st.secrets["strava"]["redirect_uri"]

# ✅ Full URL with correct scopes
AUTH_URL = (
    f"https://www.strava.com/oauth/authorize?"
    f"client_id={STRAVA_CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&response_type=code"
    f"&scope=read,activity:read_all"
)

def display_strava_login():
    st.markdown("### Connect with Strava")
    st.markdown(f"[Click here to authorize]({AUTH_URL})")

def exchange_code_for_token(auth_code):
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code"
    }

    response = requests.post(token_url, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        st.error("❌ Failed to exchange code for token.")
        st.caption(f"Strava error: `{response.status_code}` — try reconnecting.")
        st.json(response.json())  # ✅ show full error message for debugging
        return None
