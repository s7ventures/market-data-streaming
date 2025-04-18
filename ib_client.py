from ib_insync import IB, Stock
import pandas as pd
import time
import logging
from aws_dynamo import MarketDataStore
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from threading import Thread
import random

# Configure logging
logging.basicConfig(level=logging.INFO)

class IBClient:
    def __init__(self, host='127.0.0.1', port=7497, client_id=1):  # Default port updated to 7496
        if client_id <= 1:
            client_id = random.randint(2, 1000)  # Ensure client_id is greater than 1
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self.data_store = MarketDataStore()

    def connect(self, retries=3, delay=5):
        if self.is_connected():
            logging.info("Already connected to IB API.")
            return
        for attempt in range(retries):
            try:
                logging.info(f"Attempting to connect to IB API at {self.host}:{self.port} with client ID {self.client_id} (Attempt {attempt + 1}/{retries})...")
                self.ib.connect(self.host, self.port, self.client_id)
                logging.info("Connection successful.")
                return
            except ConnectionRefusedError as e:
                logging.error(f"Connection failed: {e}")
                if attempt < retries - 1:
                    logging.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise RuntimeError(
                        f"Failed to connect to IB API at {self.host}:{self.port} after {retries} attempts. "
                        f"Ensure TWS/IB Gateway is running and API access is enabled."
                    ) from e
            except Exception as e:
                if "client id is already in use" in str(e).lower():
                    logging.warning(f"Client ID {self.client_id} is already in use. Incrementing client ID and retrying...")
                    self.client_id += 1
                else:
                    raise

    def disconnect(self):
        """Disconnect from the IB API."""
        if self.is_connected():
            logging.info("Disconnecting from IB API...")
            self.ib.disconnect()
            logging.info("Disconnected successfully.")
        else:
            logging.info("Already disconnected from IB API.")

    def is_connected(self):
        """Check if the client is connected to the IB API."""
        return self.ib.isConnected()

    def fetch_historical_data(self, symbol, duration='1 D', bar_size='1 min'):
        self.connect()
        contract = Stock(symbol, 'SMART', 'USD')
        self.ib.qualifyContracts(contract)
        data = self.ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='TRADES',
            useRTH=True
        )
        logging.info(f"Fetched {len(data)} bars for {symbol} with duration {duration} and bar size {bar_size}.")
        time.sleep(1)  # Handle pacing limits
        df = pd.DataFrame([{
            'timestamp': bar.date.isoformat(),
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume,
            'symbol': symbol,
            'source': 'IBKR'
        } for bar in data])
        self.data_store.batch_write(df.to_dict('records'))
        return df

    def fetch_multiple_symbols(self, symbols, duration='1 D', bar_size='1 min'):
        """
        Fetch historical data for multiple symbols and combine into a single DataFrame.
        """
        all_data = []
        for symbol in symbols:
            logging.info(f"Fetching data for {symbol}")
            data = self.fetch_historical_data(symbol, duration, bar_size)
            data['symbol'] = symbol  # Add symbol column to identify data
            all_data.append(data)
        return pd.concat(all_data, ignore_index=True)

    def fetch_live_data(self, symbol='SPY', duration='1 D', bar_size='1 min'):
        """
        Fetch live minute-level data for a symbol and write it to InfluxDB.
        """
        self.connect()
        contract = Stock(symbol, 'SMART', 'USD')
        self.ib.qualifyContracts(contract)
        data = self.ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='TRADES',
            useRTH=True
        )
        df = pd.DataFrame([{
            'timestamp': bar.date.isoformat(),
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume
        } for bar in data])

        # Write data to InfluxDB
        from influxdb_client_3 import Point
        from influxdb_handler import client, database  # Ensure influxdb_handler is imported

        for _, row in df.iterrows():
            point = (
                Point("ohlcv")
                .tag("symbol", symbol)
                .field("open", row['open'])
                .field("high", row['high'])
                .field("low", row['low'])
                .field("close", row['close'])
                .field("volume", row['volume'])
                .time(row['timestamp'])
            )
            client.write(database=database, record=point)

        return df

    def render_live_chart(self, symbol='SPY', update_interval=5):
        """
        Render a live chart for the given symbol.
        """
        def update_chart():
            fig = make_subplots(rows=1, cols=1)
            fig.add_trace(go.Candlestick(name=symbol, x=[], open=[], high=[], low=[], close=[]))

            while True:
                df = self.fetch_live_data(symbol, duration='1 D', bar_size='1 min')
                fig.data[0].x = df['timestamp']
                fig.data[0].open = df['open']
                fig.data[0].high = df['high']
                fig.data[0].low = df['low']
                fig.data[0].close = df['close']
                fig.update_layout(title=f"Live Chart for {symbol}")
                fig.show()
                time.sleep(update_interval)

        thread = Thread(target=update_chart, daemon=True)
        thread.start()
