#!/bin/bash
# Helper script to run Docker containers in development mode with auto-reload

echo "Starting Docker containers in development mode..."
echo "Code changes will automatically trigger server restarts."
echo ""

# Clean up any old containers that might cause ContainerConfig errors
echo "Cleaning up old containers..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down 2>/dev/null || true
docker rm -f growery_flask growery_db 2>/dev/null || true

echo ""
echo "Starting containers..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build "$@"

