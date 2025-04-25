import os
import logging
from dotenv import load_dotenv
from ib_client import fetch_historical_data, connect_ibkr, disconnect_ibkr, get_symbols, fetch_options  # Import get_symbols and fetch_options
from influx_client import write_points, clear_bucket  # Import write_points and clear_bucket from influx_client
import time
# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname=s - %(message)s')

def fetch_and_write_data(symbol, duration='1 D', bar_size='1 min'):
    """
    Fetch historical data from IBKR and write it to InfluxDB.

    Args:
        symbol (str): The stock symbol to fetch data for.
        duration (str): The duration of historical data to fetch (e.g., '1 D').
        bar_size (str): The size of each data bar (e.g., '1 min').
    """
    try:
        logging.debug(f"Fetching historical data for symbol: {symbol}, duration: {duration}, bar_size: {bar_size}")
        
        # Fetch historical data
        bars = fetch_historical_data(symbol, duration, bar_size)
        logging.debug(f"Fetched {len(bars)} bars for symbol: {symbol}")

        # Prepare data for InfluxDB
        points = [
            {
                "measurement": "ohlcv",
                "tags": {"symbol": symbol},
                "time": bar.date.isoformat(),
                "fields": {
                    "open": float(bar.open),  # Ensure numeric type
                    "high": float(bar.high),  # Ensure numeric type
                    "low": float(bar.low),    # Ensure numeric type
                    "close": float(bar.close),  # Ensure numeric type
                    "volume": int(bar.volume),  # Ensure numeric type
                },
            }
            for bar in bars
        ]
        logging.debug(f"Prepared {len(points)} points for InfluxDB for symbol: {symbol}")

        # Write data to InfluxDB
        write_points(points)
        logging.info(f"{len(points)} points written to InfluxDB for {symbol}.")

    except Exception as e:
        logging.error(f"Failed to fetch/write data for {symbol}: {e}", exc_info=True)

    finally:
        # Ensure IBKR connection is closed
        disconnect_ibkr()

def fetch_and_write_options(symbol):
    """
    Fetch the 20 closest call/put options for a given symbol and write them to InfluxDB.

    Args:
        symbol (str): The stock symbol to fetch options for.
    """
    try:
        # Fetch options using ib_client's fetch_options
        options = fetch_options(symbol)

        # Prepare data for InfluxDB
        points = [
            {
                "measurement": "options",
                "tags": {
                    "symbol": symbol,
                    "option_type": option["right"],  # Call or Put
                    "strike_price": str(option["strike"]),  # Use string for better Grafana filtering
                },
                "time": option["expiry"],  # Expiry date as timestamp
                "fields": {
                    "strike_price": option["strike"],  # Numeric strike price
                    "option_type": option["right"],  # Call or Put
                    "expiry": option["expiry"],  # Expiry date
                },
            }
            for option in options
        ]
        logging.debug(f"Prepared {len(points)} points for InfluxDB for options of symbol: {symbol}")

        # Write data to InfluxDB
        write_points(points)
        logging.info(f"{len(points)} options points written to InfluxDB for {symbol}.")

    except Exception as e:
        logging.error(f"Failed to fetch/write options data for {symbol}: {e}", exc_info=True)

    finally:
        # Ensure IBKR connection is closed
        disconnect_ibkr()

if __name__ == "__main__":
    import sys

    # Check for command-line arguments
    if len(sys.argv) > 1 and sys.argv[1].lower() == "cleardb":
        logging.info("Clearing the InfluxDB bucket as requested.")
        clear_bucket()
        sys.exit(0)

    # Fetch the symbols dynamically
    symbols = get_symbols()  # Use get_symbols from ib_client.py
    logging.info("Starting data fetch and write process.")
    
    # Fetch and write data for each symbol
    for symbol in symbols:
        logging.info(f"Processing symbol: {symbol}")
        fetch_and_write_data(symbol)  # Fetch and write stock data
        fetch_and_write_options(symbol)  # Fetch and write options data
        time.sleep(1)
    # Log completion
    logging.info("Data fetch and write process completed.")
