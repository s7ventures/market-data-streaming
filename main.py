from ib_client import IBClient

def main():
    client = IBClient()
    symbols = ['SPY', 'QQQ']
    for symbol in symbols:
        data = client.fetch_historical_data(symbol, duration='5 D', bar_size='1 min')
        print(f"Inserted {len(data)} records for {symbol}")

if __name__ == '__main__':
    main()
