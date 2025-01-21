FROM python:3.12-slim

# Install system dependencies and Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories and files
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV CHROME_BINARY_LOCATION=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PYTHONUNBUFFERED=1 

# Add these lines before the final CMD or ENTRYPOINT
RUN apt-get update && \
    apt-get install -y cron && \
    mkdir -p /app/logs && \
    touch /app/logs/cron.log && \
    chmod 0644 /app/logs/cron.log && \
    (crontab -l 2>/dev/null; echo '0 * * * * cd /app && PYTHONPATH=/app /usr/local/bin/python /app/src/main.py --all >> /app/logs/cron.log 2>&1') | crontab - 