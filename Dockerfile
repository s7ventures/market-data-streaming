FROM python:3.10

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Manually download and build TA-Lib, specifying build/host for aarch64
ENV TA_BUILD_OPTS="--prefix=/usr --build=aarch64-unknown-linux-gnu --host=aarch64-unknown-linux-gnu"

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure $TA_BUILD_OPTS && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Copy project files into the container
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies (ta-lib, etc.)
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Run your FastAPI service
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8001"]