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

For manual database operations:
```bash
docker exec -it growery_db psql -U growery_user -d growery
```

## Deployment

For deployment instructions, see [../system/DEPLOYMENT.md](../system/DEPLOYMENT.md).

Quick deployment commands:

- **Full deploy** (for initial setup or when dependencies/Dockerfiles change):
  ```bash
  cd hub/system
  ./deploy.sh
  ```
  (Run from project root, or use `cd ../system` if already in `hub/backend/`)

- **Quick deploy** (for Python code changes only):
  ```bash
  cd hub/system
  ./deploy-quick.sh
  ```
  (Run from project root, or use `cd ../system` if already in `hub/backend/`)