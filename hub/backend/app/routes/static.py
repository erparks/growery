from flask import Blueprint, send_from_directory, abort
import mimetypes
import os

# Static files path - Docker volume mount in development/production
STATIC_PATH = "/app/static"

static_bp = Blueprint("static", __name__)

@static_bp.route("/_app/<path:filename>")
def serve_static(filename):
    """Serve SvelteKit static assets."""
    mimetype, _ = mimetypes.guess_type(filename)
    return send_from_directory(os.path.join(STATIC_PATH, "_app"), filename, mimetype=mimetype)

@static_bp.route("/", defaults={"path": "index.html"})
@static_bp.route("<path:path>")
def serve_sveltekit(path):
    """Serve SvelteKit pages and static assets."""
    # Skip internal routes
    if path.startswith("_app") or path.startswith("api"):
        return abort(404)
    
    # Serve CSS and HTML files directly
    if path.endswith((".css", ".html")):
        return send_from_directory(STATIC_PATH, path)
    
    # Fallback: serve index.html for all other routes (SPA routing)
    return send_from_directory(STATIC_PATH, "index.html")