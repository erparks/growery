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
# Use app.py which imports the configured app from __init__.py
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

echo "Running database migrations..."
flask db upgrade

echo "Starting Flask application in development mode..."
# Flask's built-in reloader doesn't work reliably with Docker volume mounts
# Use the host-based watcher (watch_and_restart.sh) instead for auto-reload
flask run --host=0.0.0.0 --port=80 --debugger

