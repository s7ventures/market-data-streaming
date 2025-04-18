from flask import Flask, render_template, jsonify, redirect, url_for, request
import pandas as pd
from ib_client import IBClient
import asyncio
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from pytz import timezone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get timezone from .env
APP_TIMEZONE = os.getenv('APP_TIMEZONE', 'UTC')  # Default to UTC if not set

app = Flask(__name__)

@app.route('/')
def index():
    # Create a new asyncio event loop for the current thread
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()

    # Fetch data using IBClient
    ib_client = IBClient()
    symbols = ['SPY', 'QQQ']
    combined_data = ib_client.fetch_multiple_symbols(symbols)

    # Create candlestick charts for each symbol
    figures = []
    for symbol in symbols:
        symbol_data = combined_data[combined_data['symbol'] == symbol]

        # Calculate moving averages
        symbol_data['MA20'] = symbol_data['close'].rolling(window=20).mean()
        symbol_data['MA50'] = symbol_data['close'].rolling(window=50).mean()

        # Create candlestick chart with moving averages and volume overlay
        fig = go.Figure(data=[
            go.Candlestick(
                x=symbol_data['timestamp'],
                open=symbol_data['open'],
                high=symbol_data['high'],
                low=symbol_data['low'],
                close=symbol_data['close'],
                name='Candlestick'
            ),
            go.Scatter(
                x=symbol_data['timestamp'],
                y=symbol_data['MA20'],
                mode='lines',
                line=dict(color='blue', width=1),
                name='20-day MA'
            ),
            go.Scatter(
                x=symbol_data['timestamp'],
                y=symbol_data['MA50'],
                mode='lines',
                line=dict(color='red', width=1),
                name='50-day MA'
            )
        ])

        # Add volume as a bar chart
        fig.add_trace(go.Bar(
            x=symbol_data['timestamp'],
            y=symbol_data['volume'],
            name='Volume',
            marker_color='lightgray',
            yaxis='y2'
        ))

        # Update layout for dual y-axis and interactivity
        fig.update_layout(
            title=f'Advanced Candlestick Chart for {symbol}',
            xaxis_title='Timestamp',
            yaxis_title='Price',
            yaxis2=dict(
                title='Volume',
                overlaying='y',
                side='right'
            ),
            xaxis_rangeslider_visible=False,
            dragmode='pan'  # Enable mouse drag and zoom
        )
        figures.append(fig.to_html(full_html=False))

    # Render the HTML template with the candlestick charts
    return render_template('index.html', figures=figures)

@app.route('/api/available-symbols')
def available_symbols():
    ib_client = IBClient()
    symbols = ib_client.get_available_symbols()
    return jsonify({'symbols': symbols})

@app.route('/live')
def live_chart():
    symbol = request.args.get('symbol', 'SPY')  # Default to SPY if no symbol is provided
    return render_template('live_chart.html', symbol=symbol)

@app.route('/api/spy-data')
def spy_data():
    symbol = request.args.get('symbol', 'SPY')  # Default to SPY if no symbol is provided
    duration = request.args.get('duration', '1 D')  # Default to 1 day if no duration is provided
    if(duration != '1 D'):
        duration += ' D'  # Default to 5 days if not 1 day
    # Use timezone from .env
    app_timezone = timezone(APP_TIMEZONE)
    now = datetime.now(app_timezone)  # Current time in the specified timezone

    ib_client = IBClient()
    data = ib_client.fetch_historical_data(symbol, duration=duration, bar_size='1 min')

    if data.empty:
        return jsonify({'timestamps': [], 'prices': []})  # Return empty data if no bars are fetched

    # Convert timestamps to the specified timezone
    app_timezone = timezone(APP_TIMEZONE)
    def ensure_timezone_aware(ts):
        if ts.tzinfo is None:
            return ts.tz_localize('UTC').tz_convert(app_timezone)
        return ts.tz_convert(app_timezone)

    data['timestamp'] = pd.to_datetime(data['timestamp']).apply(ensure_timezone_aware)

    # Extract timestamps and prices
    timestamps = data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
    prices = data['close'].tolist()
    return jsonify({'timestamps': timestamps, 'prices': prices})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5433)
