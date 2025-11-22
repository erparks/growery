#!/bin/bash
# Helper script to run Docker containers with UI watch mode
# This will start the Flask container and rebuild the UI on file changes

echo "Starting development environment with UI auto-rebuild..."
echo ""
echo "This will:"
echo "  1. Start Docker containers in development mode"
echo "  2. Start UI build watcher (rebuilds on changes)"
echo ""
echo "Press Ctrl+C to stop both processes"
echo ""

# Get the project directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$HUB_DIR/backend"
VIEW_DIR="$HUB_DIR/view"
STATIC_DIR="$BACKEND_DIR/static"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping processes..."
    kill $FLASK_PID $WATCH_PID 2>/dev/null
    docker-compose -f "$BACKEND_DIR/docker-compose.yml" -f "$BACKEND_DIR/docker-compose.dev.yml" -p growery --project-directory "$BACKEND_DIR" down 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

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

# Start Docker containers in background
echo ""
echo "Starting Docker containers..."

# Clean up any old containers/images that might cause issues
echo "Cleaning up old containers..."
docker-compose -f "$BACKEND_DIR/docker-compose.yml" -f "$BACKEND_DIR/docker-compose.dev.yml" -p growery --project-directory "$BACKEND_DIR" down 2>/dev/null || true

docker-compose -f "$BACKEND_DIR/docker-compose.yml" -f "$BACKEND_DIR/docker-compose.dev.yml" -p growery --project-directory "$BACKEND_DIR" up --build &
FLASK_PID=$!

# Wait a moment for Docker to start
sleep 3

# Start UI watch build in background
echo "Starting UI build watcher..."
if [ ! -d "$VIEW_DIR" ]; then
    echo "❌ Error: View directory not found at $VIEW_DIR"
    echo "   Please check that hub/view exists"
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

cd "$VIEW_DIR"
# Start UI watcher that rebuilds and restarts Flask container after each build
# This ensures Docker bind mount sees the updated files
npm run watch:dev &
WATCH_PID=$!

echo ""
echo "✅ Development environment started!"
echo "   - Flask running at http://localhost"
echo "   - UI will rebuild automatically on file changes"
echo ""
echo "Press Ctrl+C to stop"

# Wait for both processes
wait $FLASK_PID $WATCH_PID

