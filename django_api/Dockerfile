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
RUN useradd -m -u 1000 apiuser

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/api/data && \
    chown -R apiuser:apiuser /app && \
    chmod -R 755 /app

# Create SSL certificates directory
RUN mkdir -p /app/api/certs && \
    chown -R apiuser:apiuser /app/api/certs && \
    chmod -R 755 /app/api/certs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=api.settings
ENV CHROME_BINARY_LOCATION=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Switch to non-root user
USER apiuser

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "api/manage.py", "runserver_plus", "--cert-file", "api/certs/cert.crt", "--key-file", "api/certs/cert.key", "0.0.0.0:8000"] 