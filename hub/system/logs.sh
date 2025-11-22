#!/bin/bash

# View live logs from Docker containers running on Raspberry Pi
# Usage: ./logs.sh [service] [--tail N]
#   - service: optional service name (default: flask)
#   - --tail N: show last N lines before following (default: 100)

set -e

PI_USER="ethan"
PI_HOST="hub.local"
PI_PATH="/hub"

# Parse arguments
SERVICE="flask"
TAIL_LINES=100

while [[ $# -gt 0 ]]; do
    case $1 in
        --tail)
            TAIL_LINES="$2"
            shift 2
            ;;
        *)
            SERVICE="$1"
            shift
            ;;
    esac
done

echo "📊 Fetching logs for '${SERVICE}' service on ${PI_USER}@${PI_HOST}..."
echo "   (Press Ctrl+C to exit)"
echo ""

# Connect and follow logs
ssh ${PI_USER}@${PI_HOST} << EOF
    set -e
    
    # Find the backend directory
    if [ -d "/hub/backend" ]; then
        BACKEND_DIR="/hub/backend"
    elif [ -d "/hub/hub/backend" ]; then
        BACKEND_DIR="/hub/hub/backend"
    else
        echo "❌ Error: Could not find backend directory"
        echo "Available directories in /hub:"
        ls -la /hub/
        exit 1
    fi
    
    cd "\$BACKEND_DIR"
    
    # Detect docker compose command
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        DOCKER_COMPOSE="docker compose"
    fi
    
    # Follow logs
    sudo \$DOCKER_COMPOSE logs -f --tail=${TAIL_LINES} ${SERVICE}
EOF

