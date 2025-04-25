import os
from influxdb_client import InfluxDBClient
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# InfluxDB configuration
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_HOST = os.getenv("INFLUXDB_HOST")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "spy_ohlcv_1m")

# Initialize InfluxDB client
client = InfluxDBClient(
    url=INFLUXDB_HOST,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

# Validate InfluxDB client initialization
if not INFLUXDB_HOST or not INFLUXDB_TOKEN or not INFLUXDB_ORG or not INFLUXDB_BUCKET:
    logging.error("InfluxDB configuration is incomplete. Please check your environment variables.")
    raise ValueError("InfluxDB configuration is incomplete.")

logging.info(f"InfluxDB client initialized with host: {INFLUXDB_HOST}, org: {INFLUXDB_ORG}, bucket: {INFLUXDB_BUCKET}")

def query_stock_data(symbol, range_start='-7d'):
    """
    Query historical stock data for a given symbol from InfluxDB.

    Args:
        symbol (str): The stock symbol to query data for.
        range_start (str): The start of the time range for the query (e.g., '-7d').

    Returns:
        list: A list of dictionaries containing stock data.
    """
    logging.debug(f"Querying stock data for symbol: {symbol}, range_start: {range_start}")
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
    |> range(start: {range_start})
    |> filter(fn: (r) => r["_measurement"] == "ohlcv" and r["symbol"] == "{symbol}")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    |> sort(columns: ["_time"])
    '''
    try:
        query_api = client.query_api()
        result = query_api.query(org=INFLUXDB_ORG, query=query)
        data = [
            {
                "time": record["_time"],
                "open": record["open"],
                "high": record["high"],
                "low": record["low"],
                "close": record["close"],
                "volume": record["volume"]
            }
            for table in result for record in table.records
        ]
        logging.info(f"Queried {len(data)} records for symbol: {symbol}")
        return data
    except Exception as e:
        logging.error(f"Unexpected error querying stock data for symbol: {symbol}: {e}", exc_info=True)
        raise

def write_points(points):
    """
    Write data points to the InfluxDB bucket.
    """
    try:
        logging.debug(f"Attempting to write points to InfluxDB bucket '{INFLUXDB_BUCKET}' in org '{INFLUXDB_ORG}'.")
        logging.debug(f"Points to write: {points}")
        write_api = client.write_api()
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)
        logging.info(f"Successfully wrote {len(points)} points to InfluxDB.")
    except Exception as e:
        logging.error(f"Failed to write points to InfluxDB: {e}", exc_info=True)
    finally:
        write_api.__del__()  # Ensure the write API is closed properly

def clear_bucket():
    """
    Clear all data from the InfluxDB bucket.
    """
    try:
        logging.info(f"Clearing all data from bucket: {INFLUXDB_BUCKET}")
        delete_api = client.delete_api()
        delete_api.delete(
            start="1970-01-01T00:00:00Z",
            stop="2100-01-01T00:00:00Z",
            bucket=INFLUXDB_BUCKET,
            org=INFLUXDB_ORG,
            predicate=''
        )
        logging.info("All data cleared from the bucket successfully.")
    except Exception as e:
        logging.error(f"Failed to clear data from the bucket: {e}", exc_info=True)
