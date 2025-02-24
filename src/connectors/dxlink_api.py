#!/usr/bin/env python3
"""
dxlink_api.py

Handles WebSocket connections to DXLink for real-time market data streaming.

This script:
1. Authenticates using the API quote token from Tastytrade.
2. Maintains a persistent WebSocket connection.
3. Subscribes to market events (Quotes, Trades, Greeks).
4. Keeps the connection alive with periodic keep-alive messages.

Requirements:
  - websocket-client
  - tastytrade_api.py
"""

import json
import time
import threading
import websocket
from tastytrade_api import get_api_quote_token

# DXLink WebSocket URL (provided by Tastytrade API)
DXLINK_URL = "wss://tasty-openapi-ws.dxfeed.com/realtime"

# Subscription channels (You can modify this based on your needs)
SUBSCRIBE_SYMBOLS = ["NVDA", "TSLA"]  # Example symbols

# API quote token (retrieved via Tastytrade authentication)
API_QUOTE_TOKEN = None  # To be fetched dynamically

# WebSocket Connection
ws = None

# Keep-alive interval in seconds
KEEPALIVE_INTERVAL = 30


def on_message(ws, message):
    """Handles incoming WebSocket messages (market data updates)."""
    data = json.loads(message)
    print(f"[DATA] {data}")  # Print received data (for debugging)
    # TODO: Implement processing logic for received market data


def on_error(ws, error):
    """Handles WebSocket errors."""
    print(f"[ERROR] {error}")


def on_close(ws, close_status_code, close_msg):
    """Handles WebSocket disconnections and attempts reconnection."""
    print(f"[CLOSED] Connection closed: {close_status_code}, {close_msg}")
    print("[INFO] Reconnecting in 5 seconds...")
    time.sleep(5)
    start_websocket()  # Restart connection


def on_open(ws):
    """Handles authentication and subscriptions after connection opens."""
    global API_QUOTE_TOKEN

    print("[INFO] WebSocket connected. Authenticating...")

    # Fetch the latest API Quote Token
    API_QUOTE_TOKEN = get_api_quote_token()

    # Step 1: Send SETUP Message
    setup_msg = {
        "type": "SETUP",
        "channel": 0,
        "version": "0.1-DXF-JS/0.3.0",
        "keepaliveTimeout": 60,
        "acceptKeepaliveTimeout": 60
    }
    ws.send(json.dumps(setup_msg))

    # Step 2: Authorize with API Quote Token
    auth_msg = {
        "type": "AUTH",
        "channel": 0,
        "token": API_QUOTE_TOKEN
    }
    ws.send(json.dumps(auth_msg))

    # Step 3: Open Market Data Channel
    channel_request_msg = {
        "type": "CHANNEL_REQUEST",
        "channel": 3,
        "service": "FEED",
        "parameters": {"contract": "AUTO"}
    }
    ws.send(json.dumps(channel_request_msg))

    # Step 4: Configure Market Data Feed
    feed_setup_msg = {
        "type": "FEED_SETUP",
        "channel": 3,
        "acceptAggregationPeriod": 0.1,
        "acceptDataFormat": "COMPACT",
        "acceptEventFields": {
            "Trade": ["eventType", "eventSymbol", "price", "dayVolume", "size"],
            "Quote": ["eventType", "eventSymbol", "bidPrice", "askPrice", "bidSize", "askSize"],
            "Greeks": ["eventType", "eventSymbol", "volatility", "delta", "gamma", "theta", "rho", "vega"],
            "Profile": ["eventType", "eventSymbol", "description", "tradingStatus"],
            "Summary": ["eventType", "eventSymbol", "openInterest", "dayOpenPrice", "dayHighPrice", "dayLowPrice"]
        }
    }
    ws.send(json.dumps(feed_setup_msg))

    # Step 5: Subscribe to Market Events for Selected Symbols
    feed_subscription_msg = {
        "type": "FEED_SUBSCRIPTION",
        "channel": 3,
        "reset": True,
        "add": [
            {"type": "Trade", "symbol": symbol} for symbol in SUBSCRIBE_SYMBOLS
        ] + [
            {"type": "Quote", "symbol": symbol} for symbol in SUBSCRIBE_SYMBOLS
        ] + [
            {"type": "Greeks", "symbol": symbol} for symbol in SUBSCRIBE_SYMBOLS
        ]
    }
    ws.send(json.dumps(feed_subscription_msg))

    print("[INFO] Subscribed to real-time market data for:", SUBSCRIBE_SYMBOLS)


def send_keepalive():
    """Sends keep-alive messages every KEEPALIVE_INTERVAL seconds."""
    global ws
    while True:
        if ws:
            keepalive_msg = {"type": "KEEPALIVE", "channel": 0}
            ws.send(json.dumps(keepalive_msg))
            print("[INFO] Sent keep-alive message.")
        time.sleep(KEEPALIVE_INTERVAL)


def start_websocket():
    """Initializes and starts the WebSocket connection."""
    global ws
    print("[INFO] Connecting to DXLink WebSocket...")

    ws = websocket.WebSocketApp(
        DXLINK_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    # Start the WebSocket in a separate thread
    ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
    ws_thread.start()

    # Start keep-alive mechanism
    keepalive_thread = threading.Thread(target=send_keepalive, daemon=True)
    keepalive_thread.start()


if __name__ == "__main__":
    start_websocket()
    while True:
        time.sleep(1)  # Keep the script running