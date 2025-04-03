# strava_auth.py
import streamlit as st
import requests
import os

STRAVA_CLIENT_ID = st.secrets["strava"]["client_id"]
STRAVA_CLIENT_SECRET = st.secrets["strava"]["client_secret"]
REDIRECT_URI = st.secrets["strava"]["redirect_uri"]

AUTH_URL = (
    f"https://www.strava.com/oauth/authorize?client_id={STRAVA_CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=activity:read_all"
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
        st.error("Failed to exchange code for token")
        return None
