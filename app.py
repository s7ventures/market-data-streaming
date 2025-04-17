from flask import Flask, render_template
import pandas as pd
from ib_client import IBClient
import asyncio
import plotly.graph_objects as go

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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5433)
