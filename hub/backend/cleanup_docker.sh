#!/bin/bash

# Script to clean up stale Docker containers and images

echo "Stopping and removing containers..."
docker-compose down -v 2>/dev/null || true

echo "Removing old containers..."
docker rm -f growery_flask growery_db 2>/dev/null || true
docker rm -f backend_flask_1 backend_db_1 2>/dev/null || true
docker rm -f $(docker ps -a | grep -E "(backend|growery)" | awk '{print $1}') 2>/dev/null || true

echo "Removing old images..."
docker rmi $(docker images | grep -E "(backend|growery|postgres)" | awk '{print $3}') 2>/dev/null || true

echo "Cleaning up..."
docker system prune -f

echo "Cleanup complete! Now run: docker-compose up --build"

