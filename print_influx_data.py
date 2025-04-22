import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from influxdb_client_3 import InfluxDBClient3

# Load .env
load_dotenv()

# Config
token = os.getenv("INFLUXDB_TOKEN")
org = "US East - Prod"
host = "https://us-east-1-1.aws.cloud2.influxdata.com"
database = os.getenv("INFLUXDB_BUCKET", "spy_ohlcv_1m")

print(f"Loaded INFLUXDB_TOKEN: {'Set' if token else 'Not Set'}")
print(f"Loaded INFLUXDB_BUCKET: {database}")

if not database:
    raise ValueError("Database (bucket) name is not set.")

client = InfluxDBClient3(
    host=host,
    token=token,
    org=org,
    database=database
)

def test_bucket_access():
    """
    Check if the bucket is accessible by querying one row from any table.
    """
    query = "SELECT * FROM ohlcv LIMIT 1"
    print(f"Testing access to bucket: {database}")
    try:
        results = client.query(query=query)
        for _ in results:
            print(f"Bucket '{database}' is accessible.")
            return
        print(f"Bucket '{database}' is accessible but empty.")
    except Exception as e:
        print(f"Error accessing bucket '{database}': {e}")

def print_spy_data():
    """
    Query and print OHLCV data for SPY from the last 1 day.
    """
    query = """
    SELECT *
    FROM ohlcv
    WHERE symbol = 'SPY' AND time >= now() - interval '1 day'
    ORDER BY time ASC
    """
    print(f"Executing SQL query:\n{query}")
    try:
        results = client.query(query=query)
        for record in results:
            print(record)
    except Exception as e:
        print(f"Error querying InfluxDB: {e}")

def write_sample_data():
    """
    Write one OHLCV data point with symbol=SPY.
    Ensure `volume` is written as a float.
    """
    point = {
        "measurement": "ohlcv",
        "tags": {"symbol": "SPY"},
        "fields": {
            "open": 456.2,
            "high": 457.1,
            "low": 455.8,
            "close": 456.9,
            "volume": float(900123)  # Force float
        },
        "time": datetime.now(timezone.utc)  # timezone-aware UTC
    }

    try:
        client.write(record=point)
        print("Wrote 1 OHLCV point.")
    except Exception as e:
        print(f"Write error: {e}")

if __name__ == "__main__":
    print("Fetching SPY data from InfluxDB...")
    test_bucket_access()
    print_spy_data()
    print("Writing sample SPY OHLCV data...")
    write_sample_data()