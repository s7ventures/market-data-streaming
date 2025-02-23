FROM python:3.10

WORKDIR /app

# Install dependencies for macOS ARM (Apple Silicon)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables to use Homebrew TA-Lib
ENV CFLAGS="-I/opt/homebrew/include"
ENV LDFLAGS="-L/opt/homebrew/lib"

# Copy project files
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies (TA-Lib should now install properly)
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8001"]