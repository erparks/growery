FROM python:3.12-slim

# Optional: install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better layer caching
COPY app/requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY app/ .

# Copy migrations directory (if it exists at the backend root level)
# Note: Adjust based on your actual project structure
COPY migrations/ ./migrations/

# Copy and set up entrypoint scripts
COPY docker/app/entrypoint.sh /entrypoint.sh
COPY docker/app/entrypoint-dev.sh /entrypoint-dev.sh
RUN chmod +x /entrypoint.sh /entrypoint-dev.sh

EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
