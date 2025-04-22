from flask import Flask, render_template, request, jsonify
from influx_client import query_stock_data  # Correct import for query_stock_data
from ib_client import get_symbols_for_frontend  # Import get_symbols_for_frontend
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask app initialization
app = Flask(__name__)  # Ensure the app instance is named 'app'

@app.route('/')
def index():
    """
    Render the main page with the dropdown and chart.
    """
    logging.info("Rendering index page.")
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    """
    API endpoint to fetch data for a specific stock symbol.

    Query Parameters:
        symbol (str): The stock symbol to fetch data for.

    Returns:
        JSON response containing stock data or an error message.
    """
    symbol = request.args.get('symbol')
    if not symbol:
        logging.warning("Symbol parameter is missing in the request.")
        return jsonify({"error": "Symbol is required"}), 400

    try:
        logging.info(f"Fetching data for symbol: {symbol}")
        data = query_stock_data(symbol)  # Use the function from influx_client
        return jsonify(data)
    except Exception as e:
        logging.error(f"Failed to fetch data for symbol: {symbol}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/symbols', methods=['GET'])
def get_symbols():
    """
    API endpoint to fetch the list of available stock symbols.
    """
    try:
        symbols = get_symbols_for_frontend()
        return jsonify(symbols)
    except Exception as e:
        logging.error(f"Failed to fetch symbols: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/grafana')
def grafana():
    """
    Render a page with an embedded Grafana dashboard.
    """
    logging.info("Rendering Grafana dashboard page.")
    return render_template('grafana.html')

if __name__ == '__main__':
    logging.info("Starting Flask application.")
    app.run(debug=True, host='0.0.0.0', port=5000)  # Ensure the app listens on all interfaces
