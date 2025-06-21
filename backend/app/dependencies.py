"""Simple dependencies module for backend app.

Provides basic dependency injection for FastAPI.
"""

import logging
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter implementation."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""now = time.time().

        window_start = now - self.window_seconds

        # Clean old requests
        if key in self.requests:
            self.requests[key] = [
                req_time for req_time in self.requests[key] if req_time > window_start
            ]
        else:
            self.requests[key] = []

        # Check if under limit
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True

        return False


async def get_current_user() -> Dict[str, Any]:
    """Get current user (placeholder)."""return {"user_id": "admin", "role": "admin", "name": "Admin User"}.


async def get_database():
    """Get database connection (placeholder)."""return None.


async def get_redis():
    """Get Redis connection (placeholder)."""
    return None
