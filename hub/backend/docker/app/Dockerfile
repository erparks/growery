FROM python:3.12-slim

# Optional: install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY app/requirements.txt app/requirements.txt

# Install dependencies
RUN pip install -r app/requirements.txt

# Copy application code to /app/app to maintain package structure
COPY app/ app/

# Copy migrations directory
COPY migrations/ migrations/

# Create static directory
RUN mkdir -p static

# Copy and set up entrypoint scripts
COPY docker/app/entrypoint.sh /entrypoint.sh
COPY docker/app/entrypoint-dev.sh /entrypoint-dev.sh
RUN chmod +x /entrypoint.sh /entrypoint-dev.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
