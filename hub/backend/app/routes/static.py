from flask import Blueprint, send_from_directory, abort
import mimetypes
import os

STATIC_PATH = os.path.abspath("static")

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