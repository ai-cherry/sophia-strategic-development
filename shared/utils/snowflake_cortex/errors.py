"""Error classes for Snowflake Cortex service."""


from .enums import ErrorSeverity


class CortexError(Exception):
    """Base exception for Cortex-related errors."""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: dict | None = None,
    ):
        super().__init__(message)
        self.severity = severity
        self.details = details or {}


class CortexConnectionError(CortexError):
    """Raised when connection to Snowflake fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, ErrorSeverity.HIGH, details)


class CortexAuthenticationError(CortexError):
    """Raised when authentication fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, ErrorSeverity.CRITICAL, details)


class CortexModelError(CortexError):
    """Raised when model operations fail."""

    def __init__(self, message: str, model: str, details: dict | None = None):
        details = details or {}
        details["model"] = model
        super().__init__(message, ErrorSeverity.MEDIUM, details)


class CortexQuotaError(CortexError):
    """Raised when quota limits are exceeded."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, ErrorSeverity.HIGH, details)


class MCPServerError(CortexError):
    """Raised when MCP server operations fail."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, ErrorSeverity.HIGH, details)
