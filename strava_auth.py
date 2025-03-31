import streamlit as st
import requests
import urllib

# Set your Strava app credentials (store these securely later)
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "https://YOUR-STREAMLIT-APP.streamlit.app"  # ← match what you registered in Strava API

def get_strava_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "approval_prompt": "force",
        "scope": "read,activity:read",
    }
    url = f"https://www.strava.com/oauth/authorize?{urllib.parse.urlencode(params)}"
    return url

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
