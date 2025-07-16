"""Error classes for Sophia AI."""

class APIError(Exception):
    """Base API error."""
    pass

class RateLimitError(APIError):
    """Rate limit exceeded error."""
    pass

class AuthenticationError(APIError):
    """Authentication failed error."""
    pass
