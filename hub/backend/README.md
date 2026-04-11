# backend

## Development Mode

Run the application in development mode with auto-reload on code changes:

From the `hub/backend/` directory:

```bash
./run_dev.sh
```

Or manually:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

In development mode:
- The Flask server automatically restarts when you make changes to Python code files
- Code is mounted as a volume, so changes are immediately reflected
- You'll see reload messages in the console when files change

To clean up Docker containers and images (from `hub/backend/`):
```bash
./cleanup_docker.sh
```

## Database

The database is automatically initialized when using Docker Compose. The schema is loaded from `init-schema.sql` on first startup.

### Database Migrations

Since the local environment doesn't have Python dependencies, use the helper script to run Flask migration commands inside the Docker container:

```bash
# Generate a new migration
./flask-db.sh migrate -m "description of changes"

# Apply migrations
./flask-db.sh upgrade

# Check current migration version
./flask-db.sh current

# View migration history
./flask-db.sh history
```

The migrations directory is mounted as a volume, so any migrations created in the container will appear in your local `migrations/` directory.

### Manual Database Operations

For direct database access:
```bash
docker exec -it growery_db psql -U growery_user -d growery
```

## Deployment

For deployment details, see [../system/README.md](../system/README.md).

- **Full deploy** (initial setup, Docker/Compose/requirements changes, or anything beyond UI assets):
  ```bash
  cd hub/system
  ./deploy.sh
  ```

- **Frontend only** (Svelte build → `backend/static`, fast rsync + Flask restart):
  ```bash
  cd hub/system
  ./deploy-frontend.sh
  ```