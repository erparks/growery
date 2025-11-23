#!/bin/bash
# Helper script to run Docker containers with UI watch mode and tmux panes
# This will start the Flask container, rebuild the UI on file changes, and watch for Python changes

# Get the project directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$HUB_DIR/backend"
VIEW_DIR="$HUB_DIR/view"
STATIC_DIR="$BACKEND_DIR/static"
WATCH_SCRIPT="$SCRIPT_DIR/watch_and_restart.sh"
TMUX_SESSION="growery-dev"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping development environment..."
    # Stop tmux session if it exists
    tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true
    # Stop containers
    docker-compose -f "$BACKEND_DIR/docker-compose.yml" -f "$BACKEND_DIR/docker-compose.dev.yml" -p growery --project-directory "$BACKEND_DIR" down 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if tmux is available
if ! command -v tmux &> /dev/null; then
    echo "❌ Error: tmux is not installed"
    echo "   Install it with: sudo apt-get install tmux (Linux) or brew install tmux (macOS)"
    exit 1
fi

# Build UI first to ensure static directory exists before starting container
echo "🔨 Building UI initially to populate static directory..."
if [ ! -d "$VIEW_DIR" ]; then
    echo "❌ Error: View directory not found at $VIEW_DIR"
    exit 1
fi

cd "$VIEW_DIR"
if [ ! -f "$STATIC_DIR/index.html" ]; then
    echo "Building UI (static directory is empty or missing)..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "❌ Error: Initial UI build failed"
        exit 1
    fi
    echo "✅ Initial build complete!"
else
    echo "✅ Static files already exist, skipping initial build"
fi

# Clean up any old containers/images that might cause issues
echo ""
echo "Cleaning up old containers..."
docker-compose -f "$BACKEND_DIR/docker-compose.yml" -f "$BACKEND_DIR/docker-compose.dev.yml" -p growery --project-directory "$BACKEND_DIR" down 2>/dev/null || true

# Kill existing tmux session if it exists
tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true

# Start Docker containers in detached mode
echo "Starting Docker containers..."
docker-compose -f "$BACKEND_DIR/docker-compose.yml" -f "$BACKEND_DIR/docker-compose.dev.yml" -p growery --project-directory "$BACKEND_DIR" up --build -d

# Wait a moment for Docker to start
sleep 3

# Start UI watch build in background
echo "Starting UI build watcher..."
if [ ! -d "$VIEW_DIR" ]; then
    echo "❌ Error: View directory not found at $VIEW_DIR"
    echo "   Please check that hub/view exists"
    cleanup
    exit 1
fi

cd "$VIEW_DIR"
npm run watch:dev > /dev/null 2>&1 &
WATCH_PID=$!

# Create tmux session with two windows
echo "Starting tmux session with two windows..."
echo "   - Window 0: Docker logs (Ctrl+B then 0)"
echo "   - Window 1: File watcher (Ctrl+B then 1, or Ctrl+B then P/N to switch)"
echo ""
echo "Press Ctrl+B then D to detach, or Ctrl+C in this terminal to stop everything"

# Create new tmux session (detached) with first window for Docker logs
tmux new-session -d -s "$TMUX_SESSION" -x 120 -y 40 -n "logs"

# Start Docker logs in first window
tmux send-keys -t "$TMUX_SESSION:logs" "cd '$BACKEND_DIR' && while true; do docker-compose -f docker-compose.yml -f docker-compose.dev.yml -p growery logs -f flask 2>&1 || sleep 2; done" C-m

# Create second window for file watcher
tmux new-window -t "$TMUX_SESSION" -n "watcher"

# Start file watcher in second window
tmux send-keys -t "$TMUX_SESSION:watcher" "cd '$SCRIPT_DIR' && '$WATCH_SCRIPT'" C-m

# Switch back to first window (Docker logs)
tmux select-window -t "$TMUX_SESSION:logs"

# Attach to tmux session
tmux attach-session -t "$TMUX_SESSION"

