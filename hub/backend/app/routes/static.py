from flask import Blueprint, send_from_directory, abort
import mimetypes
import os

# Get static path relative to the app directory
# In Docker: static is at /app/static (mounted as volume or copied into image)
# In dev (with volumes): static is at /app/static (mounted) or hub/backend/static (sibling)
_current_dir = os.path.dirname(os.path.abspath(__file__))
_app_dir = os.path.dirname(os.path.dirname(_current_dir))  # Go up from routes/ to app/

# Check if static exists in app/ (Docker with volume mount, or copied into image)
_static_in_app = os.path.join(_app_dir, "static")
# Also check the explicit Docker path
_static_docker = "/app/static"

# Try Docker path first, then app-relative path, then fall back
if os.path.exists(_static_docker):
    STATIC_PATH = _static_docker
elif os.path.exists(_static_in_app):
    STATIC_PATH = _static_in_app
else:
    # Fallback: try sibling path for local dev
    _backend_dir = os.path.dirname(_app_dir) if _app_dir and _app_dir != "/" else None
    _static_sibling = os.path.join(_backend_dir, "static") if _backend_dir and _backend_dir != "/" else None
    if _static_sibling and os.path.exists(_static_sibling):
        STATIC_PATH = _static_sibling
    else:
        # Default to Docker path (it should exist with volume mount)
        STATIC_PATH = _static_docker

STATIC_PATH = os.path.abspath(STATIC_PATH)
# Log the resolved path for debugging
print(f"📁 Static files path resolved to: {STATIC_PATH}")
print(f"   (Exists: {os.path.exists(STATIC_PATH)})")
if not os.path.exists(STATIC_PATH):
    print(f"   ⚠️  WARNING: Static path does not exist!")
    print(f"   Tried: {_static_docker}, {_static_in_app}")

static_bp = Blueprint("static", __name__)

@static_bp.route("/_app/<path:filename>")
def serve_static(filename):
    print('STATIC_PATH: ', STATIC_PATH)
    print('filename: ', filename)
    mimetype, _ = mimetypes.guess_type(filename)
    return send_from_directory(STATIC_PATH+"/_app/", filename, mimetype=mimetype)

@static_bp.route("/", defaults={"path": "index.html"})
@static_bp.route("<path:path>")
def serve_sveltekit(path):
    print(f"============== base path: {path}")

    if path.startswith("_app") or path.startswith("api"):
        print("❌ Skipping static or API file:", path)
        return abort(404)
    
    if path.endswith(".css") or path.endswith(".html"):
        return send_from_directory(STATIC_PATH, path)
    
    print("fallback")
    return send_from_directory(STATIC_PATH, "index.html")