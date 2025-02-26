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

# Create a non-root user
RUN useradd -m -u 1000 scraper

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories and files with proper permissions
RUN mkdir -p /app/logs /app/data /app/data/scraper_status && \
    echo '{}' > /app/data/last_run_times.json && \
    touch /app/data/houses.csv && \
    chown -R scraper:scraper /app && \
    chmod -R 777 /app/logs /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV CHROME_BINARY_LOCATION=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PYTHONUNBUFFERED=1

# Create the run_scraper.sh script in /usr/local/bin
RUN echo '#!/bin/bash\nwhile true; do\n    cd /app && PYTHONPATH=/app python /app/src/main.py --all > /dev/null 2>&1\n    sleep 3600\ndone' > /usr/local/bin/run_scraper.sh

RUN chmod +x /usr/local/bin/run_scraper.sh && \
    chown scraper:scraper /usr/local/bin/run_scraper.sh

# Switch to non-root user
USER scraper 