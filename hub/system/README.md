# Raspberry Pi deployment (`hub/system`)

This folder contains two scripts for deploying and operating the dockerized Growery stack on a Raspberry Pi from your development machine.

## Prerequisites

1. **SSH**: The Pi is reachable via SSH (see `PI_USER` and `PI_HOST` at the top of each script; they default to `ethan@hub.local`).
2. **Network**: Your dev machine and the Pi are on the same network.
3. **On the Pi**: Docker and Docker Compose are installed, your user can run Docker (e.g. in the `docker` group), and the deploy target path exists (the scripts use `/hub` on the Pi).

## `deploy.sh`

Full sync and container rebuild. Use for initial deployment and whenever the image or synced tree must change—not only app code (e.g. `requirements.txt`, Dockerfile, `docker-compose.yml`, frontend, or static assets).

From the repo:

```bash
cd hub/system
./deploy.sh
```

What it does:

1. **Builds the Svelte UI** under `hub/view` (`npm install` if `node_modules` is missing, then `npm run build`), producing assets in `hub/backend/static/`.
2. **Rsyncs** the contents of `hub/` to `${PI_PATH}` on the Pi (default `/hub`), excluding venvs, caches, `.git`, `node_modules`, logs, `.env`, and similar.
3. **On the Pi**, finds `backend` (supports `/hub/backend` or `/hub/hub/backend`), runs `docker compose` / `docker-compose` **down** (volumes are not removed), then **up -d --build**, prints container status and a short log tail.

Edit `PI_USER`, `PI_HOST`, and `PI_PATH` in `deploy.sh` if your Pi or paths differ.

## `logs.sh`

Stream live logs from a Compose service on the Pi over SSH.

```bash
cd hub/system
./logs.sh              # follow flask logs (default)
./logs.sh db           # follow database logs
./logs.sh --tail 200   # show last 200 lines before following
./logs.sh db --tail 50
```

Default service name is `flask`; use `db` for Postgres. Press Ctrl+C to stop.

`PI_USER` and `PI_HOST` match `deploy.sh`; change them in `logs.sh` if needed.

## Accessing the app

After a successful deploy:

- **HTTP**: `http://hub.local` (or the Pi’s IP)—Flask is published on host port **80**.
- **Postgres**: host port **5432** if you need direct access.

## Troubleshooting

**Permission / Docker on the Pi**  
Ensure your user is in the `docker` group (or use `sudo` for compose on the Pi). Log out and back in after group changes.

**Port 80 in use**  
Check with `sudo lsof -i :80` on the Pi, or change the port mapping in `hub/backend/docker-compose.yml`.

**Database**  
Inspect with `./logs.sh db`. Data lives in the `postgres_data` volume; `deploy.sh` does not remove volumes on `down`. To wipe DB data: on the Pi, in the backend directory, `sudo docker compose down -v` (destructive).

**Cannot resolve `hub.local`**  
Use the Pi’s IP for SSH and set `PI_HOST` in both scripts, or add a hosts entry.
