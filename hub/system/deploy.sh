#!/bin/bash

# Deploy dockerized application to Raspberry Pi
# This does a full sync and rebuild - use for:
#   - Initial deployment
#   - When dependencies change (requirements.txt)
#   - When Dockerfile changes
#   - When docker-compose.yml changes
#
# For code-only changes, use deploy-quick.sh instead
# Usage: ./deploy.sh

set -e

PI_USER="ethan"
PI_HOST="hub.local"
PI_PATH="/hub"

echo "🚀 Deploying to ${PI_USER}@${PI_HOST}..."

# Build UI frontend before syncing
echo "🎨 Building UI frontend..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIEW_DIR="${SCRIPT_DIR}/../view"

if [ ! -d "$VIEW_DIR" ]; then
    echo "❌ Error: View directory not found at $VIEW_DIR"
    exit 1
fi

cd "$VIEW_DIR"

# Check if node_modules exists, install if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Build the frontend (outputs to hub/backend/static/)
echo "🔨 Building frontend..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Error: Frontend build failed"
    exit 1
fi

# Verify build output exists
BACKEND_STATIC_DIR="${SCRIPT_DIR}/../backend/static"
if [ ! -d "$BACKEND_STATIC_DIR" ] || [ ! -f "$BACKEND_STATIC_DIR/index.html" ]; then
    echo "❌ Error: Frontend build output not found at $BACKEND_STATIC_DIR"
    echo "Expected index.html in static directory"
    exit 1
fi

echo "✅ Frontend built successfully! (Output: $BACKEND_STATIC_DIR)"

# Return to original directory for rsync
cd "$SCRIPT_DIR"

# Sync files to Pi (excluding unnecessary files)
echo "📦 Syncing files..."
# Use trailing slash on source to sync contents, not the directory itself
rsync -av --delete \
    --exclude='hub_env' \
    --exclude='docker_env' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='.vscode' \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='.env' \
    --exclude='backend/app/histories' \
    ../ ${PI_USER}@${PI_HOST}:${PI_PATH}/ \
    --rsync-path="sudo rsync"

echo "✅ Files synced successfully!"

# Deploy on Pi
echo "🐳 Starting Docker containers on Pi..."
ssh ${PI_USER}@${PI_HOST} << 'DEPLOY_EOF'
    set -e
    
    # Debug: Show current directory structure
    echo "📁 Checking directory structure..."
    echo "Current directory: $(pwd)"
    echo "Contents of /hub:"
    ls -la /hub/ | head -20 || true
    echo ""
    echo "Looking for docker-compose.yml..."
    find /hub -name "docker-compose.yml" -type f 2>/dev/null || echo "docker-compose.yml not found"
    echo ""
    
    # Try to find the backend directory
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
    
    echo "✅ Found backend directory at: $BACKEND_DIR"
    cd "$BACKEND_DIR"
    
    # Verify docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        echo "❌ Error: docker-compose.yml not found in $BACKEND_DIR"
        echo "Contents of $BACKEND_DIR:"
        ls -la
        exit 1
    fi
    
    echo "✅ Found docker-compose.yml"
    
    # Detect docker compose command (supports both 'docker-compose' and 'docker compose')
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        DOCKER_COMPOSE="docker compose"
    fi
    
    echo "Stopping existing containers..."
    # Note: 'down' does NOT remove volumes, so database data is preserved
    sudo $DOCKER_COMPOSE down || true
    
    echo "Building and starting containers..."
    sudo $DOCKER_COMPOSE up -d --build
    
    echo "Checking container status..."
    sudo $DOCKER_COMPOSE ps
    
    echo "✅ Deployment complete!"
    echo "📊 Container logs:"
    sudo $DOCKER_COMPOSE logs --tail=20
DEPLOY_EOF

echo "🎉 Deployment finished! Your app should be running on http://${PI_HOST}"
