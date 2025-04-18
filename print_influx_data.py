import os
from influxdb_client_3 import InfluxDBClient3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load InfluxDB configuration
token = os.getenv("INFLUXDB_TOKEN")
org = "US East - Prod"
host = "https://us-east-1-1.aws.cloud2.influxdata.com"
database = os.getenv("INFLUXDB_BUCKET", "spy_ohlcv_1m")  # Default to "spy_ohlcv_1m" if not set

# Debug: Print loaded environment variables
print(f"Loaded INFLUXDB_TOKEN: {'Set' if token else 'Not Set'}")
print(f"Loaded INFLUXDB_BUCKET: {database}")

# Validate database configuration
if not database:
    raise ValueError("Database (bucket) name is not set. Please check the 'INFLUXDB_BUCKET' environment variable.")

# Initialize InfluxDB client
client = InfluxDBClient3(host=host, token=token, org=org)

def test_bucket_access():
    """
    Test if the bucket is accessible.
    """
    query = f"""
    from(bucket: "{database}")
        |> range(start: -1m)
        |> limit(n: 1)
    """
    print(f"Testing access to bucket: {database}")
    try:
        result = client.query(query=query)
        if not result:
            print(f"Bucket '{database}' is accessible but contains no data.")
        else:
            print(f"Bucket '{database}' is accessible.")
    except Exception as e:
        print(f"Error accessing bucket '{database}': {e}")

def print_spy_data():
    """
    Query and print SPY data from the InfluxDB database.
    """
    query = f"""
    from(bucket: "{database}")
        |> range(start: -1d)
        |> filter(fn: (r) => r._measurement == "ohlcv" and r.symbol == "SPY")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> sort(columns: ["_time"])
    """
    print(f"Executing query: {query}")
    print("Fetching SPY data...")
    try:
        result = client.query(query=query)
        if not result:
            print("No data found for SPY in the specified time range.")
        for record in result:
            print(record)
    except Exception as e:
        print(f"Error querying InfluxDB: {e}")

if __name__ == "__main__":
    print("Fetching SPY data from InfluxDB...")
    test_bucket_access()  # Test bucket access
    print_spy_data()
