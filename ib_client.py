import os
from ib_insync import IB, Stock
from dotenv import load_dotenv
import logging

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
    try:
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='TRADES',
            useRTH=True
        )
        if not bars:
            logging.warning(f"No data returned for symbol: {symbol}, duration: {duration}, bar_size: {bar_size}")
            return []
        return bars
    except Exception as e:
        logging.error(f"Error fetching data for symbol: {symbol}: {e}", exc_info=True)
        return []

def fetch_options(symbol):
    """
    Fetch the 20 closest call/put options for a given symbol.

    Args:
        symbol (str): The stock symbol to fetch options for.

    Returns:
        list: A list of options data dictionaries.
    """
    try:
        logging.debug(f"Fetching options data for symbol: {symbol}")
        
        # Fetch options contracts
        connect_ibkr()
        contract = Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        chains = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contract.conId)
        
        # Filter and sort options
        chain = next(c for c in chains if c.exchange == 'SMART')
        options = []
        for strike in sorted(chain.strikes)[:10]:  # Closest 10 strikes
            for right in ['C', 'P']:  # Call and Put
                options.append({
                    "symbol": symbol,
                    "strike": strike,
                    "right": right,
                    "expiry": sorted(chain.expirations)[0]  # Closest expiration
                })

        print(f"Options data for {symbol}: {options}")
        logging.debug(f"Fetched {len(options)} options for symbol: {symbol}")
        return options

    except Exception as e:
        logging.error(f"Failed to fetch options data for {symbol}: {e}", exc_info=True)
        return []

    finally:
        # Ensure IBKR connection is closed
        disconnect_ibkr()

def get_symbols():
    """
    Return a list of stock symbols to process.
    """
    # return [
    #     "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NFLX", "NVDA", "BABA",
    #     "INTC", "AMD", "ADBE", "ORCL", "CSCO", "CRM", "SPY", "PYPL", "SQ", "SHOP", "UBER"
    # ]
    return [
        "SPY"
    ]

def get_symbols_for_frontend():
    """
    Return a list of stock symbols formatted for the frontend, including a default "Please select" option.
    """
    symbols = [{"value": "", "label": "Please select"}]
    symbols += [{"value": symbol, "label": symbol} for symbol in get_symbols()]
    return symbols
