"""
Shared utilities for Sophia AI
Centralized location for common patterns and utilities
"""

from backend.utils.errors import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    DataValidationError,
    IntegrationError,
    RateLimitError,
    SecurityError,
    ValidationError,
)
from backend.utils.http_client import APIClient, HTTPClient
from backend.utils.monitoring import (
    HealthCheck,
    HealthMonitor,
    HealthStatus,
    MetricsCollector,
    get_health_monitor,
    get_logger,
    get_metrics_collector,
    log_execution_time,
)
from backend.utils.rate_limiting import (
    MultiServiceRateLimiter,
    RateLimitConfig,
    RateLimiter,
    TokenBucketRateLimiter,
    get_global_rate_limiter,
    rate_limit,
)

__all__ = [
    # Errors
    "APIError",
    "AuthenticationError",
    "ConfigurationError",
    "ConnectionError",
    "DataValidationError",
    "IntegrationError",
    "RateLimitError",
    "SecurityError",
    "ValidationError",
    # HTTP Client
    "HTTPClient",
    "APIClient",
    # Monitoring
    "HealthStatus",
    "HealthCheck",
    "HealthMonitor",
    "MetricsCollector",
    "get_logger",
    "log_execution_time",
    "get_metrics_collector",
    "get_health_monitor",
    # Rate Limiting
    "RateLimitConfig",
    "RateLimiter",
    "MultiServiceRateLimiter",
    "TokenBucketRateLimiter",
    "rate_limit",
    "get_global_rate_limiter",
]
