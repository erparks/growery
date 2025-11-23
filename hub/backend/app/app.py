# Flask app entry point for migrations and CLI commands
# This file makes the app available to Flask CLI commands like 'flask db upgrade'
import sys
import os

# Ensure current directory is in Python path for relative imports to work
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Import app from __init__.py
# Using absolute import from current directory
from __init__ import app

__all__ = ['app']

