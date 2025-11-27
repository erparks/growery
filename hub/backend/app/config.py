import os

class Config:
    """Base configuration class."""
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "postgresql://flaskuser:flaskpassword@localhost:5432/flaskdb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
