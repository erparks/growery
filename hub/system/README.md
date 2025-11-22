# Deployment Guide for Raspberry Pi

This guide explains how to deploy the dockerized Growery application to your Raspberry Pi.

## Prerequisites

1. **SSH Access**: Your Pi should be accessible via SSH at `user@hub.local`
2. **Network**: Your development machine and Pi should be on the same network

## Initial Setup (One-time)

### On Your Raspberry Pi

1. **Copy the setup script to your Pi:**
   ```bash
   scp hub/system/setup_pi.sh user@hub.local:/tmp/
   ```

2. **SSH into your Pi and run the setup:**
   ```bash
   ssh user@hub.local
   sudo bash /tmp/setup_pi.sh
   ```

   This will:
   - Install Docker
   - Install Docker Compose
   - Create the `/hub` directory
   - Add your user to the docker group

3. **Log out and back in** (or run `newgrp docker`) to apply group changes

## Deploying Your Application

### From Your Development Machine

You have two deployment options:

#### Full Deploy (`deploy.sh`)
Use this for:
- Initial deployment
- When dependencies change (`requirements.txt`)
- When Dockerfile changes
- When `docker-compose.yml` changes

```bash
cd hub/system
./deploy.sh
```

This script will:
1. Sync all necessary files to `/hub` on your Pi (excluding venv, cache files, etc.)
2. Stop any existing containers
3. Build and start the Docker containers
4. Show you the container status and recent logs

#### Quick Deploy (`deploy-quick.sh`)
Use this for:
- **Python code changes only** (controllers, routes, models, etc.)
- Faster deployment (no rebuild needed)

```bash
cd hub/system
./deploy-quick.sh
```

This script will:
1. Sync only the `app/` directory (your Python code)
2. Restart the Flask container to pick up changes
3. Show recent logs

**Note**: Since your code is mounted as a volume in Docker, changes sync immediately. The restart ensures Flask picks up the changes.

## Accessing Your Application

After deployment, your application will be available at:
- **API**: `http://hub.local` (or `http://<pi-ip-address>`) - listening on port 80 (default HTTP port)
- **Database**: Accessible on port 5432 (if needed externally)

## Viewing Logs

### Using `logs.sh` (Recommended)

The easiest way to view logs from your development machine:

```bash
cd hub/system
./logs.sh
```

This will:
- Connect to your Pi via SSH
- Show live logs from the Flask service (default)
- Stream logs in real-time (press Ctrl+C to exit)

**Options:**
- View a specific service: `./logs.sh db` (to view database logs)
- Show more/less initial lines: `./logs.sh --tail 200` (shows last 200 lines)
- Combine options: `./logs.sh db --tail 50` (database logs, last 50 lines)

Examples:
```bash
# View Flask logs (default)
./logs.sh

# View database logs
./logs.sh db

# View last 500 lines of Flask logs
./logs.sh --tail 500

# View last 50 lines of database logs
./logs.sh db --tail 50
```

### Managing Containers on Pi

You can SSH into your Pi to manage containers directly:

```bash
ssh user@hub.local
cd /hub/backend

# View logs (alternative to logs.sh)
sudo docker-compose logs -f

# Stop containers
sudo docker-compose down

# Restart containers
sudo docker-compose restart

# View container status
sudo docker-compose ps
```

## Troubleshooting

### Permission Issues
If you get permission errors, make sure:
- Your user is in the `docker` group: `groups` should show `docker`
- You've logged out and back in after adding to docker group
- Or use `sudo` with docker commands

### Port Already in Use
If port 80 is already in use:
- Check what's using it: `sudo lsof -i :80`
- You may need to use `sudo` with docker-compose commands to bind to port 80 (privileged port)
- Or modify the port in `docker-compose.yml` (change `"80:80"` to `"8080:80"` to use port 8080 on the host instead)

### Database Issues
If the database isn't starting:
- Check logs: `sudo docker-compose logs db` or `./logs.sh db`
- Ensure the `init-schema.sql` file was copied correctly
- The database data persists in a Docker volume, so it won't be lost on redeploy

### Data Persistence
**Your database data is safe!** The database uses a named Docker volume (`postgres_data`) that persists independently of containers. When you run `deploy.sh`:
- Containers are stopped and recreated
- **Database volume is NOT removed** - all your data remains intact
- The `--delete` flag in rsync only affects file syncing, not Docker volumes

To completely wipe data (if needed):
```bash
ssh user@hub.local
cd /hub/backend
sudo docker-compose down -v  # The -v flag removes volumes
```

### Connection Issues
If you can't connect to `hub.local`:
- Try using the IP address instead: `ssh user@<pi-ip-address>`
- Update the `PI_HOST` variable in `deploy.sh` and `logs.sh` if needed

