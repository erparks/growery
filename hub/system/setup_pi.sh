#!/bin/bash

# Initial setup script for Raspberry Pi
# Run this once on your Pi to install Docker and Docker Compose
# Usage: Run on Pi: bash setup_pi.sh

set -e

echo "🔧 Setting up Raspberry Pi for Docker deployment..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script needs sudo privileges. Please run with sudo or as root."
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
apt-get update

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Add user to docker group (replace 'ethan' with your username)
    usermod -aG docker ethan
    
    echo "✅ Docker installed!"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    apt-get install -y docker-compose-plugin || {
        # Fallback to standalone docker-compose if plugin not available
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    }
    echo "✅ Docker Compose installed!"
else
    echo "✅ Docker Compose already installed"
fi

# Create /hub directory if it doesn't exist
if [ ! -d "/hub" ]; then
    echo "📁 Creating /hub directory..."
    mkdir -p /hub
    chown ethan:ethan /hub
    echo "✅ /hub directory created"
else
    echo "✅ /hub directory already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Log out and log back in (or run 'newgrp docker') to apply docker group changes"
echo "2. From your development machine, run: ./hub/system/deploy.sh"
echo "3. Your app will be available at http://$(hostname -I | awk '{print $1}'):5000"

