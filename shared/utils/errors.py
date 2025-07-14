"""
Centralized error classes for Sophia AI
All common exceptions should be defined here to avoid duplication
"""

from typing import Any, Optional


class RateLimitError(Exception):
    """Exception raised when API rate limits are exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        service: Optional[str] = None,
    ):
        self.retry_after = retry_after
        self.service = service

        if retry_after:
            message = f"{message}. Retry after {retry_after} seconds"
        if service:
            message = f"[{service}] {message}"

        super().__init__(message)


class APIError(Exception):
    """Base exception for API-related errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        service: Optional[str] = None,
    ):
        self.status_code = status_code
        self.service = service

        if status_code:
            message = f"HTTP {status_code}: {message}"
        if service:
            message = f"[{service}] {message}"

        super().__init__(message)


class AuthenticationError(APIError):
    """Exception raised for authentication failures"""

    def __init__(
        self, message: str = "Authentication failed", service: Optional[str] = None
    ):
        super().__init__(message, status_code=401, service=service)


class ConfigurationError(Exception):
    """Exception raised for configuration issues"""

    pass


class ValidationError(Exception):
    """Exception raised for data validation failures"""

    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        if field:
            message = f"{field}: {message}"
        super().__init__(message)


class ConnectionError(Exception):
    """Exception raised for connection failures"""

    def __init__(
        self,
        message: str = "Connection failed",
        service: Optional[str] = None,
        retry_count: int = 0,
    ):
        self.service = service
        self.retry_count = retry_count

        if retry_count > 0:
            message = f"{message} after {retry_count} retries"
        if service:
            message = f"[{service}] {message}"

        super().__init__(message)


class DataValidationError(ValidationError):
    """Exception raised for data validation errors"""

    pass


class IntegrationError(Exception):
    """Exception raised for third-party integration errors"""

    def __init__(
        self,
        message: str,
        service: str,
        operation: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.service = service
        self.operation = operation
        self.details = details or {}

        if operation:
            message = f"[{service}:{operation}] {message}"
        else:
            message = f"[{service}] {message}"

        super().__init__(message)


class SecurityError(Exception):
    """Exception raised for security-related errors"""

    def __init__(
        self,
        message: str,
        severity: str = "high",
        context: Optional[dict[str, Any]] = None,
    ):
        self.severity = severity
        self.context = context or {}

        message = f"[Security:{severity.upper()}] {message}"
        super().__init__(message)
