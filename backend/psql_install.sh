#!/bin/bash

# Exit script on error
set -e

# Define PostgreSQL variables (change these as needed)
DB_NAME="flaskdb"
DB_USER="flaskuser"
DB_PASSWORD="flaskpassword"

echo "Updating system packages..."
sudo apt update -y && sudo apt upgrade -y

echo "Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

echo "Starting and enabling PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo "Creating PostgreSQL user and database..."
sudo -u postgres psql <<EOF
-- Create a new database user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Create a new database
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

echo "PostgreSQL setup complete!"
echo "Database Name: $DB_NAME"
echo "Username: $DB_USER"
echo "Password: $DB_PASSWORD"
echo "To connect: psql -U $DB_USER -d $DB_NAME -h localhost"

echo "Installing Python PostgreSQL dependency..."
pip install psycopg2-binary

echo "Setup complete! 🎉"
