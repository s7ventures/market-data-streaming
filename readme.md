# IBKR Market Data Application

This project is a market data application that fetches historical stock data from Interactive Brokers (IBKR), processes it, and visualizes it using candlestick charts with moving averages and volume overlays. The application supports both local storage using TinyDB and cloud storage using AWS DynamoDB.

## Project Structure

### `main.py`
This is the entry point of the application. It initializes the `IBClient` to fetch historical data for predefined symbols and prints the number of records inserted.

### `ib_client.py`
Contains the `IBClient` class, which handles the connection to IBKR and fetches historical market data. It also integrates with the `MarketDataStore` to store the fetched data.

### `aws_dynamo.py`
Defines the `MarketDataStore` class, which abstracts the storage backend. It supports both TinyDB (local JSON-based database) and AWS DynamoDB for storing market data.

- **`create_table`**: Creates a DynamoDB table or initializes a TinyDB file.
- **`batch_write`**: Writes multiple records to the storage backend.

### `app.py`
A Flask-based web application that visualizes market data using candlestick charts. It fetches data for multiple symbols, calculates moving averages, and renders interactive charts.

### `templates/index.html`
The HTML template for rendering the candlestick charts. It uses Bootstrap for styling and integrates Plotly-generated charts.

### `market_data.json`
A sample TinyDB database file that stores market data locally in JSON format.

### `requirements.txt`
Lists the Python dependencies required for the project, including libraries for data fetching, storage, and visualization.

### `.env`
Environment variables for configuring the storage backend and AWS credentials. Example:
```
STORAGE_BACKEND=tinydb
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### `sample.env`
A sample `.env` file to demonstrate the required environment variables.

## Features
- Fetch historical market data from IBKR.
- Store data locally or in AWS DynamoDB.
- Visualize data with candlestick charts, moving averages, and volume overlays.
- Interactive web interface using Flask and Plotly.

## Setup Instructions
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the `.env` file with appropriate values.
4. Run the Flask application:
   ```bash
   python app.py
   ```
5. Access the web interface at `http://127.0.0.1:5433`.

## License
This project is licensed under the MIT License.
