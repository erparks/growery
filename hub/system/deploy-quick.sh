#!/bin/bash

# Quick deploy for code changes only (no rebuild)
# Use this when you only changed Python code and don't need to rebuild images
# Usage: ./deploy-quick.sh

set -e

PI_USER="ethan"
PI_HOST="hub.local"
PI_PATH="/hub"

echo "🚀 Quick deploy (code sync + restart) to ${PI_USER}@${PI_HOST}..."

# Sync only app code (faster than full sync)
echo "📦 Syncing code files..."
rsync -av \
    --exclude='hub_env' \
    --exclude='docker_env' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='.vscode' \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='.env' \
    ../backend/app/ ${PI_USER}@${PI_HOST}:${PI_PATH}/backend/app/ \
    --rsync-path="sudo rsync"

# Also sync migrations if they changed
rsync -av \
    ../backend/migrations/ ${PI_USER}@${PI_HOST}:${PI_PATH}/backend/migrations/ \
    --rsync-path="sudo rsync" || true

echo "✅ Files synced!"

# Restart Flask container to pick up changes
echo "🔄 Restarting Flask container..."
ssh ${PI_USER}@${PI_HOST} << 'DEPLOY_EOF'
    set -e
    cd /hub/backend
    
    # Detect docker compose command
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        DOCKER_COMPOSE="docker compose"
    fi
    
    echo "Restarting Flask container..."
    sudo $DOCKER_COMPOSE restart flask
    
    echo "✅ Container restarted!"
    echo "📊 Recent logs:"
    sudo $DOCKER_COMPOSE logs --tail=10 flask
DEPLOY_EOF

echo "🎉 Quick deploy complete! Changes should be live."

