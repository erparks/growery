# Deployment Guide for Raspberry Pi

This guide explains how to deploy the dockerized Growery application to your Raspberry Pi.

## Prerequisites

1. **SSH Access**: Your Pi should be accessible via SSH at `ethan@hub.local`
2. **Network**: Your development machine and Pi should be on the same network

## Initial Setup (One-time)

### On Your Raspberry Pi

1. **Copy the setup script to your Pi:**
   ```bash
   scp hub/system/setup_pi.sh ethan@hub.local:/tmp/
   ```

2. **SSH into your Pi and run the setup:**
   ```bash
   ssh ethan@hub.local
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
- **API**: `http://hub.local:5000` (or `http://<pi-ip-address>:5000`)
- **Database**: Accessible on port 5432 (if needed externally)

## Managing Containers on Pi

You can SSH into your Pi to manage containers:

```bash
ssh ethan@hub.local
cd /hub/backend

# View logs
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
If port 5000 is already in use:
- Check what's using it: `sudo lsof -i :5000`
- Or modify the port in `docker-compose.yml` (change `"5000:5000"` to `"8080:5000"` for example)

### Database Issues
If the database isn't starting:
- Check logs: `sudo docker-compose logs db`
- Ensure the `init-schema.sql` file was copied correctly
- The database data persists in a Docker volume, so it won't be lost on redeploy

### Data Persistence
**Your database data is safe!** The database uses a named Docker volume (`postgres_data`) that persists independently of containers. When you run `deploy.sh`:
- Containers are stopped and recreated
- **Database volume is NOT removed** - all your data remains intact
- The `--delete` flag in rsync only affects file syncing, not Docker volumes

To completely wipe data (if needed):
```bash
ssh ethan@hub.local
cd /hub/backend
sudo docker-compose down -v  # The -v flag removes volumes
```

### Connection Issues
If you can't connect to `hub.local`:
- Try using the IP address instead: `ssh ethan@<pi-ip-address>`
- Update the `PI_HOST` variable in `deploy.sh` if needed

