"""
Models package - imports all models for Alembic migrations.
"""
# Import all models explicitly to ensure they're registered with SQLAlchemy
# Import order matters: import base models before models that reference them
from app.models.photo_histories import PhotoHistory  # noqa: F401
from app.models.plants import Plants  # noqa: F401

__all__ = ['Plants', 'PhotoHistory']

