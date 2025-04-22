# IBKR Stock Data Pipeline

This project is a stock data pipeline that integrates **Interactive Brokers (IBKR)** and **InfluxDB** to fetch, store, and visualize stock data. It includes components for fetching historical stock data from IBKR, storing it in InfluxDB, and displaying it in a web-based chart using Flask and Chart.js.

## Features

1. **Fetch Historical Stock Data**: 
   - Uses the `ib_insync` library to fetch historical stock data from IBKR.
   - Supports configurable duration and bar size for data retrieval.

2. **Store Data in InfluxDB**:
   - Writes the fetched stock data to an InfluxDB database.
   - Data is stored in the `ohlcv` measurement with fields for open, high, low, close, and volume.

3. **Visualize Data**:
   - A Flask web application serves a frontend that allows users to select a stock and view its historical data on a line chart.
   - The chart is powered by Chart.js and dynamically updates based on user selection.

4. **Automated Data Fetching**:
   - A cron job is configured to periodically fetch and store stock data.

## Components

### 1. **`ib_client.py`**
   - Handles the connection to IBKR and fetches historical stock data.
   - Key function: `fetch_historical_data(symbol, duration, bar_size)`.

### 2. **`influx_client.py`**
   - Manages the connection to InfluxDB and provides functions to query and write data.
   - Key functions:
     - `query_stock_data(symbol, range_start)`: Queries stock data from InfluxDB.
     - `write_points(points)`: Writes data points to InfluxDB.

### 3. **`fetch_and_write.py`**
   - Combines the functionality of `ib_client.py` and `influx_client.py` to fetch data from IBKR and write it to InfluxDB.
   - Configured to run periodically via a cron job.

### 4. **`app.py`**
   - A Flask web application that serves the frontend and provides an API endpoint to fetch stock data.
   - Routes:
     - `/`: Renders the main page with the stock chart.
     - `/api/data`: API endpoint to fetch stock data for a specific symbol.

### 5. **Frontend (`templates/index.html`)**
   - A simple HTML page with a dropdown to select stocks and a Chart.js-powered line chart to display stock data.

### 6. **Docker Integration**
   - The project is containerized using Docker.
   - The `Dockerfile` sets up the environment, installs dependencies, and configures the cron job.
   - The `docker-compose.yml` file defines the service configuration.

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed.
- An IBKR account with TWS or IB Gateway running.
- An InfluxDB instance (cloud or local).

### Steps

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd NEWIBKR
   ```

2. **Configure Environment Variables**:
   - Use the `.env.example` file as a template to create a `.env` file in the project root (already included in `.gitignore`).
   - Set the following variables:
     ```
     INFLUXDB_TOKEN=<your-influxdb-token>
     INFLUXDB_BUCKET=<your-bucket-name>
     INFLUXDB_ORG=<your-org-name>
     IBKR_HOST=127.0.0.1
     IBKR_PORT=7497
     IBKR_CLIENT_ID=1
     ```

3. **Build and Run the Docker Container**:
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**:
   - Open your browser and navigate to `http://localhost:5000`.

5. **Verify Cron Job**:
   - The cron job fetches and writes stock data every minute. Logs are stored in `/var/log/cron.log` inside the container.

## Usage

- **View Stock Data**:
  - Select a stock from the dropdown on the main page.
  - The chart will update with the selected stock's historical data.

- **API Endpoint**:
  - Fetch stock data programmatically using the `/api/data` endpoint:
    ```
    GET /api/data?symbol=<stock-symbol>
    ```

## Dependencies

- **Python Libraries**:
  - `ib_insync`
  - `influxdb-client`
  - `python-dotenv`
  - `flask`

- **System Dependencies**:
  - `cron` (for scheduling periodic tasks)

## File Structure

```
/NEWIBKR
├── app.py                # Flask application
├── ib_client.py          # IBKR client for fetching stock data
├── influx_client.py      # InfluxDB client for querying and writing data
├── fetch_and_write.py    # Script to fetch and write data
├── templates/
│   └── index.html        # Frontend template
├── requirements.txt      # Python dependencies
├── Dockerfile            # Dockerfile for containerization
├── docker-compose.yml    # Docker Compose configuration
└── .env                  # Environment variables (excluded from version control)
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.
