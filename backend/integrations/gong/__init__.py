"""
Gong.io Integration Package

This package contains all Gong.io API integration components for Sophia AI.
Implements REAL integration using GitHub Organization Secrets.
"""

from .gong_api_client import GongAPIClient
from .gong_data_models import *
from .gong_integration_manager import GongIntegrationManager

__version__ = "1.0.0"
__all__ = [
    "GongAPIClient",
    "GongIntegrationManager",
] 