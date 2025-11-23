#!/bin/bash
# Force Flask to reload by touching watched files
# Usage: ./force_reload.sh

echo "Forcing Flask reload..."
docker exec growery_flask touch /app/app.py /app/__init__.py 2>/dev/null || echo "Container not running or file touch failed"
echo "Reload triggered. Wait a few seconds for Flask to restart."

