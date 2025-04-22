import os
from ib_insync import IB, Stock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# IBKR configuration
IBKR_HOST = os.getenv("IBKR_HOST", "127.0.0.1")
IBKR_PORT = int(os.getenv("IBKR_PORT", 7497))
IBKR_CLIENT_ID = int(os.getenv("IBKR_CLIENT_ID", 1))

# Initialize IBKR client
ib = IB()

def connect_ibkr():
    """
    Connect to IBKR TWS.
    """
    if not ib.isConnected():
        ib.connect(IBKR_HOST, IBKR_PORT, IBKR_CLIENT_ID)

def disconnect_ibkr():
    """
    Disconnect from IBKR TWS.
    """
    if ib.isConnected():
        ib.disconnect()

def fetch_historical_data(symbol, duration='1 D', bar_size='1 min'):
    """
    Fetch historical data for a given symbol from IBKR.
    """
    connect_ibkr()
    contract = Stock(symbol, 'SMART', 'USD')
    ib.qualifyContracts(contract)
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr=duration,
        barSizeSetting=bar_size,
        whatToShow='TRADES',
        useRTH=True
    )
    return bars

def get_symbols():
    """
    Return a list of stock symbols to process.
    """
    return [
        "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NFLX", "NVDA", "BABA",
        "INTC", "AMD", "ADBE", "ORCL", "CSCO", "CRM", "SPY", "PYPL", "SQ", "SHOP", "UBER"
    ]

def get_symbols_for_frontend():
    """
    Return a list of stock symbols formatted for the frontend.
    """
    return [{"value": symbol, "label": symbol} for symbol in get_symbols()]
