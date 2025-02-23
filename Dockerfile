FROM python:3.10

WORKDIR /app

# 1. Install system dependencies (for build + git)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    wget \
    git \
    autoconf \
    automake \
    libtool \
    && rm -rf /var/lib/apt/lists/*

# 2. Clone and build the latest TA-Lib from GitHub
RUN git clone https://github.com/TA-Lib/ta-lib.git && \
    cd ta-lib && \
    ./autogen.sh && \
    # Force ARM-based build/host detection for older config scripts
    ./configure --prefix=/usr/local --build=aarch64-unknown-linux-gnu --host=aarch64-unknown-linux-gnu && \
    make && \
    make install && \
    ldconfig && \
    cd .. && rm -rf ta-lib

# 3. Update environment variables so Python & linker can find TA-Lib
ENV LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}"
ENV CFLAGS="-I/usr/local/include"
ENV LDFLAGS="-L/usr/local/lib"

# 4. Copy your project files
COPY . .

# 5. Upgrade pip
RUN pip install --upgrade pip

# 6. Install Python dependencies (including ta-lib)
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# 7. Launch FastAPI on port 8001
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8001"]