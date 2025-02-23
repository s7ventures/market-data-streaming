FROM python:3.10

WORKDIR /app

# Install system dependencies, including TA-Lib
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libta-lib0 \
    ta-lib \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8001"]