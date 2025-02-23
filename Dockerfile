FROM python:3.10

WORKDIR /app

# 1. Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 2. Download, build, and install TA-Lib to /usr/local
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr/local --build=aarch64-unknown-linux-gnu --host=aarch64-unknown-linux-gnu && \
    make && \
    make install && \
    ldconfig && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# 3. Set LD_LIBRARY_PATH so Python sees the TA-Lib shared library
ENV LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}"

# 4. Copy project files
COPY . .

# 5. Upgrade pip
RUN pip install --upgrade pip

# 6. Install Python dependencies (including ta-lib)
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# 7. Start the FastAPI service on port 8001
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8001"]