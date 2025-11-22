from flask import Flask, request
from database import db, migrate
from config import Config
# Import models to ensure they're registered with SQLAlchemy for migrations
from models.plants import Plants  # noqa: F401
from routes.plants import plants_bp
from routes.photo_histories import photo_histories_bp
from routes.static import static_bp
from routes.controls import controls_bp
from flask_cors import CORS

app = Flask(__name__, static_url_path=None, static_folder=None)
app.config.from_object(Config)
CORS(app)

# Initialize database
db.init_app(app)
migrate.init_app(app, db)

# Register Blueprints
# Register photo_histories first so more specific routes are matched before generic plant routes
app.register_blueprint(photo_histories_bp,  url_prefix="/api/plants")
app.register_blueprint(plants_bp,  url_prefix="/api/plants")
app.register_blueprint(controls_bp,  url_prefix="/api/pumps")
app.register_blueprint(static_bp,  url_prefix="/")


@app.before_request
def log_request():
    rule = request.url_rule.rule if request.url_rule else "❌ NO MATCHING ROUTE ❌"
    print(f"🔹 Received request: {request.path} → Matched route: {rule}")

def create_app():
    return app