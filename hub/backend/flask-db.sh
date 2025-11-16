#!/bin/bash
# Helper script to run Flask database commands inside the Docker container
# Usage: ./flask-db.sh <command> [args...]
# Examples:
#   ./flask-db.sh migrate -m "add new column"
#   ./flask-db.sh upgrade
#   ./flask-db.sh current
#   ./flask-db.sh history

CONTAINER_NAME="growery_flask"

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Error: Container '${CONTAINER_NAME}' is not running."
    echo "Please start it first with: ./run_dev.sh"
    exit 1
fi

# Run the Flask command in the container
# Set the working directory and environment variables to match the container setup
docker exec -it \
    -e PYTHONPATH=/app \
    -e FLASK_APP=app.py \
    -e DATABASE_URL="${DATABASE_URL:-postgresql://growery_user:growery_password@db:5432/growery}" \
    -w /app \
    "${CONTAINER_NAME}" \
    flask db "$@"
