import streamlit as st
import requests
import urllib

CLIENT_ID = st.secrets["strava"]["client_id"]
CLIENT_SECRET = st.secrets["strava"]["client_secret"]
REDIRECT_URI = st.secrets["strava"]["redirect_uri"]

def get_strava_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "approval_prompt": "force",
        "scope": "read,activity:read",
    }
    return f"https://www.strava.com/oauth/authorize?{urllib.parse.urlencode(params)}"

def exchange_code_for_token(code):
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=payload)
    return response.json()
