"""
Simple Authentication Module for Sophia AI Development

This module provides basic authentication for development and testing.
In production, this would be replaced with proper OAuth/JWT authentication.
"""

from typing import Any


def get_current_user() -> dict[str, Any]:
    """
    Simple auth function that returns a default user for development.

    In production, this would validate JWT tokens and return actual user data.
    """
    return {
        "id": "dev_user_001",
        "role": "ceo",  # Default to Unified role for testing
        "department": "executive",
        "name": "Development User",
        "email": "dev@sophia-ai.com",
    }
