#!/bin/bash
set -e

echo "Waiting for database to be ready..."
# Wait for database to be ready (it's already health-checked by docker-compose, but this is a safety check)
until python -c "import psycopg2; psycopg2.connect('${DATABASE_URL}')" 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is ready!"

# Set PYTHONPATH to include current directory so imports work
export PYTHONPATH=/app:$PYTHONPATH
# Use app.app which imports the configured app from __init__.py
export FLASK_APP=app.app

echo "Running database migrations..."
flask db upgrade

echo "Starting Flask application..."
exec python -m app.main

