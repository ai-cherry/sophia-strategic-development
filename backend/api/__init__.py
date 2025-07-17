"""
API module for Sophia AI backend
Contains FastAPI routes and API configurations
"""

from .main import create_app, app

__all__ = ['create_app', 'app'] 