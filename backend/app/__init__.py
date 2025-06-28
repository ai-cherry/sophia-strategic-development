"""FastAPI application for Sophia AI."""

import os

def get_app():
    """Lazy import of the FastAPI app to prevent import chain issues."""
    try:
        # from .fastapi_app import app
        return None
    except ImportError as e:
        print(f"Warning: Could not import FastAPI app: {e}")
        return None

# Only import the app when explicitly requested
if os.getenv("SOPHIA_IMPORT_APP", "false").lower() == "true":
    try:
        # from .fastapi_app import app
    except ImportError:
        app = None
else:
    app = None

# All logic related to fastapi_app.py is now deprecated and should be removed.
pass
