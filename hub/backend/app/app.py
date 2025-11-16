# Flask app entry point for migrations and CLI commands
# This file makes the app available to Flask CLI commands like 'flask db upgrade'
import sys
import os
import importlib.util

# Ensure current directory is in Python path for relative imports to work
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Load __init__.py as a module - this will execute it and set up the Flask app
_init_file = os.path.join(_current_dir, "__init__.py")
spec = importlib.util.spec_from_file_location("app_init", _init_file)
if spec is None or spec.loader is None:
    raise ImportError(f"Could not load __init__.py from {_current_dir}")

app_init = importlib.util.module_from_spec(spec)
# Execute the module - this runs all the imports and setup code in __init__.py
spec.loader.exec_module(app_init)
app = app_init.app

__all__ = ['app']

