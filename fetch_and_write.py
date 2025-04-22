import os
import logging
from dotenv import load_dotenv
from ib_client import fetch_historical_data, connect_ibkr, disconnect_ibkr, get_symbols  # Import get_symbols
from influx_client import write_points  # Import write_points from influx_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "volume": bar.volume,
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

if __name__ == "__main__":
    # Fetch the symbols dynamically
    symbols = get_symbols()  # Use get_symbols from ib_client.py
    logging.info("Starting data fetch and write process.")

    # Fetch and write data for each symbol
    for symbol in symbols:
        logging.info(f"Processing symbol: {symbol}")
        fetch_and_write_data(symbol)

    logging.info("Data fetch and write process completed.")
