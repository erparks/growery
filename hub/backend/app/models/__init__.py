"""
Models package - automatically imports all models for Alembic migrations.
"""
import importlib
import pkgutil
from pathlib import Path

# Get the directory containing this __init__.py file
_package_dir = Path(__file__).parent

# Automatically import all modules in this package
# This ensures all models are registered with SQLAlchemy metadata
for _, module_name, _ in pkgutil.iter_modules([str(_package_dir)]):
    # Skip this __init__.py file itself
    if module_name != '__init__':
        importlib.import_module(f'.{module_name}', __package__)

