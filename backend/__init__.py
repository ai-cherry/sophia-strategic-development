"""Backend package for Sophia AI."""

# Sophia AI Backend Package
# Conditional imports to prevent environment disruption

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Only import the app when explicitly requested or when running as main application
# This prevents import chain issues when other tools import backend modules
def get_app():
    """Lazy import of the FastAPI app to prevent import chain issues."""
    try:
        from .app.fastapi_app import app
        return app
    except ImportError as e:
        print(f"Warning: Could not import FastAPI app: {e}")
        return None

# Conditional import based on environment context
if __name__ == "__main__" or os.getenv("SOPHIA_IMPORT_APP", "false").lower() == "true":
    try:
        from .app import app
    except ImportError:
        # Graceful fallback when dependencies are missing
        app = None
else:
    # Don't automatically import the app when this package is imported
    app = None

__version__ = "2.0.0"
__all__ = ["get_app", "app"]
