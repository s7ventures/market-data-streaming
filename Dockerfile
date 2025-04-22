# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app_ibkr

# Install cron and other dependencies
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Add the cron job
RUN echo "* * * * * python /app_ibkr/fetch_and_write.py >> /var/log/cron.log 2>&1" > /etc/cron.d/fetch_and_write_cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/fetch_and_write_cron

# Apply the cron job
RUN crontab /etc/cron.d/fetch_and_write_cron

# Expose the port the app runs on
EXPOSE 5000

# Start cron and Flask
CMD ["sh", "-c", "cron && flask run --host=0.0.0.0 --port=5000"]
