from flask import Flask
from app.database import db, migrate
from app.config import Config
from app.routes.plants import plants_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    
    app.register_blueprint(plants_bp,  url_prefix="/api/plants")

    return app
