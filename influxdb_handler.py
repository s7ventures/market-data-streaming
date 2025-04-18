import os
import time
import requests  # Import requests to fetch live data
from datetime import datetime
from influxdb_client_3 import InfluxDBClient3, Point
from dotenv import load_dotenv  # Import dotenv to load environment variables

# Load environment variables from .env file
load_dotenv()

# Load environment variables
token = os.getenv("INFLUXDB_TOKEN")
if not token:
    raise EnvironmentError("INFLUXDB_TOKEN is not set. Please check your environment variables.")

org = "US East - Prod"
host = "https://us-east-1-1.aws.cloud2.influxdata.com"
database = "spy_ohlcv_1m"

# Initialize InfluxDB client
try:
    client = InfluxDBClient3(host=host, token=token, org=org)
    database = "spy_ohlcv_1m"  # Ensure this is consistent across the project
except Exception as e:
    raise ConnectionError(f"Failed to connect to InfluxDB: {e}")

def delete_mock_data():
    """
    Deletes all data from the InfluxDB database.
    """
    print("Warning: The 'delete' method is not supported by InfluxDBClient3.")
    print("Consider dropping and recreating the database manually if needed.")

def write_new_data(data):
    """
    Writes new data points to the InfluxDB database.
    """
    for key in data:
        point = (
            Point("census")
            .tag("location", data[key]["location"])
            .field(data[key]["species"], data[key]["count"])
        )
        try:
            client.write(database=database, record=point)
        except Exception as e:
            raise RuntimeError(f"Failed to write data to InfluxDB: {e}")
        time.sleep(1)  # Separate points by 1 second
    print("New data written to InfluxDB.")

def fetch_live_data():
    """
    Fetches live SPY data from a market data API.
    Replace 'YOUR_API_ENDPOINT' and 'YOUR_API_KEY' with actual values.
    """
    url = "https://api.example.com/spy-live-data"  # Replace with actual API endpoint
    headers = {"Authorization": "Bearer YOUR_API_KEY"}  # Replace with actual API key
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch live data: {e}")

def aggregate_to_daily(data):
    """
    Aggregates minute-level data into daily candles.
    """
    daily_data = {}
    for point in data:
        date = datetime.fromisoformat(point["timestamp"]).date()
        if date not in daily_data:
            daily_data[date] = {
                "open": point["open"],
                "high": point["high"],
                "low": point["low"],
                "close": point["close"],
                "volume": point["volume"],
            }
        else:
            daily_data[date]["high"] = max(daily_data[date]["high"], point["high"])
            daily_data[date]["low"] = min(daily_data[date]["low"], point["low"])
            daily_data[date]["close"] = point["close"]
            daily_data[date]["volume"] += point["volume"]
    return daily_data

def write_daily_data(daily_data):
    """
    Writes daily candle data to the InfluxDB database.
    """
    for date, candle in daily_data.items():
        point = (
            Point("daily_candles")
            .tag("symbol", "SPY")
            .field("open", candle["open"])
            .field("high", candle["high"])
            .field("low", candle["low"])
            .field("close", candle["close"])
            .field("volume", candle["volume"])
            .time(datetime.combine(date, datetime.min.time()))
        )
        try:
            client.write(database=database, record=point)
        except Exception as e:
            raise RuntimeError(f"Failed to write daily data to InfluxDB: {e}")
    print("Daily data written to InfluxDB.")

if __name__ == "__main__":
    # Fetch live data
    live_data = fetch_live_data()

    # Aggregate to daily candles
    daily_candles = aggregate_to_daily(live_data)

    # Write daily candles to InfluxDB
    write_daily_data(daily_candles)

    # Example usage
    delete_mock_data()

    new_data = {
        "point1": {"location": "Klamath", "species": "bees", "count": 23},
        "point2": {"location": "Portland", "species": "ants", "count": 30},
        "point3": {"location": "Klamath", "species": "bees", "count": 28},
        "point4": {"location": "Portland", "species": "ants", "count": 32},
        "point5": {"location": "Klamath", "species": "bees", "count": 29},
        "point6": {"location": "Portland", "species": "ants", "count": 40},
    }

    write_new_data(new_data)
