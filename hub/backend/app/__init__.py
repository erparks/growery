import logging
from flask import Flask, request, jsonify
from app.database import db, migrate
from app.config import Config
# Import models to ensure they're registered with SQLAlchemy for migrations
from app.models import Plants, PhotoHistory  # noqa: F401
from app.routes.plants import plants_bp
from app.routes.photo_histories import photo_histories_bp
from app.routes.static import static_bp
from app.routes.controls import controls_bp
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Application factory pattern - standard Flask best practice."""
    app = Flask(__name__, static_url_path=None, static_folder=None)
    app.config.from_object(config_class)
    CORS(app)

    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    # Register photo_histories first so more specific routes are matched before generic plant routes
    app.register_blueprint(photo_histories_bp, url_prefix="/api/plants")
    app.register_blueprint(plants_bp, url_prefix="/api/plants")
    app.register_blueprint(controls_bp, url_prefix="/api/pumps")
    app.register_blueprint(static_bp, url_prefix="/")

    @app.before_request
    def log_request():
        """Log incoming requests for debugging."""
        rule = request.url_rule.rule if request.url_rule else "NO MATCHING ROUTE"
        logger.debug(f"Received request: {request.method} {request.path} → Matched route: {rule}")

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors with consistent JSON response."""
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors with rollback and consistent JSON response."""
        db.session.rollback()
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors with consistent JSON response."""
        return jsonify({"error": "Bad request"}), 400

    return app


# Create app instance for backward compatibility
app = create_app()