#!/usr/bin/env python3
"""
tastytrade_api.py

Handles authentication, session management, and fetching option chains 
from the Tastytrade API.

Requirements:
  - requests
"""

import os
import json
import requests

# Base API URL for Tastytrade
TASTYTRADE_API_URL = "https://api.tastytrade.com"

# Local session storage file
SESSION_FILE = "session_token.json"

def save_session_token(token):
    """Saves session token to a local file."""
    with open(SESSION_FILE, "w") as f:
        json.dump({"session_token": token}, f)

def load_session_token():
    """Loads session token from a local file."""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f).get("session_token")
    return None

def login(username, password, otp=""):
    """
    Logs into Tastytrade and saves session token.
    
    Args:
        username (str): Tastytrade username
        password (str): Tastytrade password
        otp (str): One-time password for 2FA (optional)
    
    Returns:
        str: Session token if successful, None otherwise
    """
    url = f"{TASTYTRADE_API_URL}/sessions"
    headers = {
        "Content-Type": "application/json",
        "X-Tastyworks-OTP": otp
    }
    payload = json.dumps({
        "login": username,
        "password": password,
        "remember-me": True
    })

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code < 300:
        data = response.json()
        session_token = data["data"]["session-token"]
        save_session_token(session_token)
        print(f"[INFO] Successfully logged in. Session Token: {session_token}")
        return session_token
    else:
        print(f"[ERROR] Login failed. Status Code: {response.status_code}")
        return None

def fetch_option_chain(ticker):
    """
    Fetches the option chain for a given ticker symbol.
    
    Args:
        ticker (str): Stock symbol (e.g., "NVDA")
    
    Returns:
        list: Option chain data if successful, None otherwise
    """
    session_token = load_session_token()
    if not session_token:
        print("[ERROR] No session token found. Please log in first.")
        return None

    url = f"{TASTYTRADE_API_URL}/option-chains/{ticker}"
    headers = {"Authorization": session_token}

    response = requests.get(url, headers=headers)

    if response.status_code < 300:
        data = response.json()
        return data["data"]["items"]
    else:
        print(f"[ERROR] Failed to fetch option chain. Status Code: {response.status_code}")
        return None

def get_api_quote_token():
    """
    Retrieves an API quote token from Tastytrade.
    
    Returns:
        str: API quote token if successful
    """
    session_token = load_session_token()
    if not session_token:
        raise Exception("[ERROR] No session token found. Please log in first.")

    url = f"{TASTYTRADE_API_URL}/api-quote-tokens"
    headers = {"Authorization": session_token}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()["data"]
            print(f"[INFO] API Quote Token: {data['token']}")
            return data["token"]
        elif response.status_code == 401:
            raise Exception("[ERROR] Unauthorized: Invalid session token.")
        else:
            raise Exception(f"[ERROR] Failed to fetch API quote token. Status Code: {response.status_code}")

    except Exception as e:
        print(f"[ERROR] Error fetching API quote token: {e}")
        raise

if __name__ == "__main__":
    # Example usage:
    USERNAME = "your_username"
    PASSWORD = "your_password"
    OTP = "123456"  # Replace with actual OTP if enabled
    
    # Log in and fetch tokens
    session_token = login(USERNAME, PASSWORD, OTP)
    if session_token:
        quote_token = get_api_quote_token()
        print(f"Fetched API Quote Token: {quote_token}")

        # Fetch NVDA option chain as an example
        option_chain = fetch_option_chain("NVDA")
        if option_chain:
            print(f"Option Chain Sample: {option_chain[:3]}")  # Print first 3 options