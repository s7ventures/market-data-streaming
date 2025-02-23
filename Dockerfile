FROM python:3.10

WORKDIR /app

# Ensure TA-Lib is available inside the container (macOS workaround)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib manually inside the container
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && make && make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Copy project files
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies (TA-Lib should now install properly)
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8001"]