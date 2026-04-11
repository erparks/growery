#!/bin/bash

# Fast deploy: Svelte UI only (build + rsync backend/static + restart Flask).
# Skips full-tree rsync and does not rebuild Postgres or Docker images.
#
# Requires a prior full deploy so /hub/backend and docker-compose exist on the Pi.
# Usage: ./deploy-frontend.sh

set -e

PI_USER="ethan"
PI_HOST="hub.local"
PI_PATH="/hub"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIEW_DIR="${SCRIPT_DIR}/../view"
BACKEND_STATIC_DIR="${SCRIPT_DIR}/../backend/static"

echo "🎨 Frontend-only deploy to ${PI_USER}@${PI_HOST}..."

if [ ! -d "$VIEW_DIR" ]; then
    echo "❌ Error: View directory not found at $VIEW_DIR"
    exit 1
fi

cd "$VIEW_DIR"

if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

echo "🔨 Building frontend..."
npm run build

if [ ! -d "$BACKEND_STATIC_DIR" ] || [ ! -f "$BACKEND_STATIC_DIR/index.html" ]; then
    echo "❌ Error: Frontend build output not found at $BACKEND_STATIC_DIR"
    echo "Expected index.html in static directory"
    exit 1
fi

echo "✅ Frontend built: $BACKEND_STATIC_DIR"

echo "🔍 Resolving static path on Pi..."
REMOTE_STATIC=$(ssh "${PI_USER}@${PI_HOST}" "if [ -d '${PI_PATH}/backend/static' ]; then echo '${PI_PATH}/backend/static'; elif [ -d '${PI_PATH}/hub/backend/static' ]; then echo '${PI_PATH}/hub/backend/static'; else echo 'ERROR' >&2; exit 1; fi")

if [ -z "$REMOTE_STATIC" ] || [ "$REMOTE_STATIC" = "ERROR" ]; then
    echo "❌ Could not find backend/static on the Pi under ${PI_PATH}"
    exit 1
fi

echo "📦 Syncing static assets to ${REMOTE_STATIC} ..."
rsync -av --delete \
    "${BACKEND_STATIC_DIR}/" \
    "${PI_USER}@${PI_HOST}:${REMOTE_STATIC}/" \
    --rsync-path="sudo rsync"

echo "✅ Static files synced"

echo "🔄 Restarting Flask container (picks up volume-mounted static)..."
ssh "${PI_USER}@${PI_HOST}" bash -s <<DEPLOY_EOF
set -e
if [ -d "${PI_PATH}/backend" ]; then
    BACKEND_DIR="${PI_PATH}/backend"
elif [ -d "${PI_PATH}/hub/backend" ]; then
    BACKEND_DIR="${PI_PATH}/hub/backend"
else
    echo "❌ Could not find backend directory under ${PI_PATH}"
    exit 1
fi
cd "\$BACKEND_DIR"
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi
sudo \$DOCKER_COMPOSE restart flask
echo "✅ Flask restarted"
DEPLOY_EOF

echo "🎉 Frontend deploy finished — http://${PI_HOST}"
