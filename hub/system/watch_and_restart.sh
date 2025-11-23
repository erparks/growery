#!/bin/bash
# File watcher that runs on the host machine and restarts Flask container on file changes
# This is more reliable than Flask's built-in reloader with Docker volume mounts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$HUB_DIR/backend"
WATCH_DIR="$BACKEND_DIR/app"
COMPOSE_FILE="$BACKEND_DIR/docker-compose.yml"
DEV_COMPOSE_FILE="$BACKEND_DIR/docker-compose.dev.yml"

echo "👀 Watching $WATCH_DIR for Python file changes..."
echo "   Will restart Flask container when files change"
echo "   Press Ctrl+C to stop"
echo ""

# Function to restart Flask
restart_flask() {
    echo "🔄 Detected change, restarting Flask container..."
    cd "$BACKEND_DIR"
    docker compose -f "$COMPOSE_FILE" -f "$DEV_COMPOSE_FILE" -p growery restart flask 2>/dev/null || {
        echo "❌ Failed to restart container"
        return 1
    }
    echo "✅ Flask container restarted"
    echo ""
}

# Check if inotifywait is available (Linux)
if command -v inotifywait &> /dev/null; then
    echo "Using inotifywait for file watching..."
    inotifywait -m -r -e modify,create,delete \
        --format '%w%f' \
        --exclude '.*\.pyc$|.*__pycache__.*|.*\.swp$|.*\.swx$' \
        "$WATCH_DIR" | while read file; do
        if [[ "$file" == *.py ]]; then
            restart_flask
        fi
    done
# Check if fswatch is available (macOS)
elif command -v fswatch &> /dev/null; then
    echo "Using fswatch for file watching..."
    fswatch -o -r "$WATCH_DIR" --exclude '.*\.pyc$|.*__pycache__.*' | while read; do
        # Check if any .py files changed
        changed_files=$(fswatch -1 -r "$WATCH_DIR" --exclude '.*\.pyc$|.*__pycache__.*' 2>/dev/null | grep '\.py$' || true)
        if [ -n "$changed_files" ]; then
            restart_flask
        fi
    done
# Fallback: simple polling
else
    echo "⚠️  inotifywait or fswatch not found, using polling mode (slower)"
    echo "   Install inotify-tools (Linux) or fswatch (macOS) for better performance"
    
    LAST_CHECK=$(find "$WATCH_DIR" -name "*.py" -type f -exec stat -c %Y {} \; 2>/dev/null | sort -n | tail -1 || echo "0")
    
    while true; do
        sleep 1
        CURRENT_CHECK=$(find "$WATCH_DIR" -name "*.py" -type f -exec stat -c %Y {} \; 2>/dev/null | sort -n | tail -1 || echo "0")
        if [ "$CURRENT_CHECK" != "$LAST_CHECK" ] && [ "$CURRENT_CHECK" != "0" ]; then
            restart_flask
            LAST_CHECK="$CURRENT_CHECK"
        fi
    done
fi

