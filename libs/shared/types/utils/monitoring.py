"""
Centralized monitoring utilities for Sophia AI
Provides common patterns for metrics, logging, and health checks
"""

import asyncio
import functools
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import structlog
from prometheus_client import Counter, Gauge, Histogram

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.contextvars.merge_contextvars,
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


class HealthStatus(Enum):
    """Health status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check result"""

    name: str
    status: HealthStatus
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ServiceMetrics:
    """Service-specific metrics"""

    service_name: str
    request_count: Counter
    request_duration: Histogram
    error_count: Counter
    active_connections: Gauge

    @classmethod
    def create(cls, service_name: str) -> "ServiceMetrics":
        """Create metrics for a service"""
        return cls(
            service_name=service_name,
            request_count=Counter(
                f"{service_name}_requests_total",
                f"Total requests for {service_name}",
                ["method", "endpoint", "status"],
            ),
            request_duration=Histogram(
                f"{service_name}_request_duration_seconds",
                f"Request duration for {service_name}",
                ["method", "endpoint"],
            ),
            error_count=Counter(
                f"{service_name}_errors_total",
                f"Total errors for {service_name}",
                ["error_type"],
            ),
            active_connections=Gauge(
                f"{service_name}_active_connections",
                f"Active connections for {service_name}",
            ),
        )


class MetricsCollector:
    """Centralized metrics collection"""

    def __init__(self):
        self.services: dict[str, ServiceMetrics] = {}

        # Global metrics
        self.system_health = Gauge(
            "sophia_ai_system_health",
            "Overall system health (0=unhealthy, 1=degraded, 2=healthy)",
        )

        self.operation_duration = Histogram(
            "sophia_ai_operation_duration_seconds",
            "Duration of operations",
            ["operation", "service"],
        )

    def get_service_metrics(self, service_name: str) -> ServiceMetrics:
        """Get or create metrics for a service"""
        if service_name not in self.services:
            self.services[service_name] = ServiceMetrics.create(service_name)
        return self.services[service_name]

    @asynccontextmanager
    async def track_operation(self, operation: str, service: str):
        """Track operation duration"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.operation_duration.labels(
                operation=operation, service=service
            ).observe(duration)

    def record_request(
        self, service: str, method: str, endpoint: str, status: int, duration: float
    ):
        """Record HTTP request metrics"""
        metrics = self.get_service_metrics(service)
        metrics.request_count.labels(
            method=method, endpoint=endpoint, status=str(status)
        ).inc()
        metrics.request_duration.labels(method=method, endpoint=endpoint).observe(
            duration
        )

        # Count errors
        if status >= 400:
            metrics.error_count.labels(error_type="http_error").inc()

    def record_error(self, service: str, error_type: str):
        """Record an error"""
        metrics = self.get_service_metrics(service)
        metrics.error_count.labels(error_type=error_type).inc()

    def update_health_status(self, status: HealthStatus):
        """Update system health status"""
        health_value = {
            HealthStatus.HEALTHY: 2,
            HealthStatus.DEGRADED: 1,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.UNKNOWN: 0,
        }
        self.system_health.set(health_value[status])


class HealthMonitor:
    """Centralized health monitoring"""

    def __init__(self):
        self.checks: dict[str, Callable] = {}
        self.logger = structlog.get_logger(__name__)

    def register_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function"""
        self.checks[name] = check_func

    async def run_check(self, name: str, check_func: Callable) -> HealthCheck:
        """Run a single health check"""
        try:
            start_time = time.time()
            result = (
                await check_func()
                if asyncio.iscoroutinefunction(check_func)
                else check_func()
            )
            duration = time.time() - start_time

            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                return HealthCheck(
                    name=name, status=status, details={"duration": duration}
                )
            elif isinstance(result, HealthCheck):
                result.details["duration"] = duration
                return result
            else:
                return HealthCheck(
                    name=name,
                    status=HealthStatus.UNKNOWN,
                    message="Invalid health check result",
                    details={"duration": duration},
                )

        except Exception as e:
            self.logger.exception("Health check failed", check=name, error=str(e))
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {e!s}",
            )

    async def run_all_checks(self) -> dict[str, HealthCheck]:
        """Run all registered health checks"""
        results = {}

        # Run checks concurrently
        tasks = [self.run_check(name, func) for name, func in self.checks.items()]

        check_results = await asyncio.gather(*tasks, return_exceptions=True)

        for name, result in zip(self.checks.keys(), check_results, strict=False):
            if isinstance(result, Exception):
                results[name] = HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed with exception: {result!s}",
                )
            else:
                results[name] = result

        return results

    def get_overall_status(self, checks: dict[str, HealthCheck]) -> HealthStatus:
        """Determine overall health status from individual checks"""
        if not checks:
            return HealthStatus.UNKNOWN

        statuses = [check.status for check in checks.values()]

        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.DEGRADED


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger"""
    return structlog.get_logger(name)


def log_execution_time(func: Callable) -> Callable:
    """Decorator to log function execution time"""
    logger = get_logger(func.__module__)

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                "Function executed",
                function=func.__name__,
                duration=duration,
                status="success",
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.exception(
                "Function failed",
                function=func.__name__,
                duration=duration,
                status="error",
                error=str(e),
            )
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                "Function executed",
                function=func.__name__,
                duration=duration,
                status="success",
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.exception(
                "Function failed",
                function=func.__name__,
                duration=duration,
                status="error",
                error=str(e),
            )
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# Global instances
_metrics_collector: Optional[MetricsCollector] = None
_health_monitor: Optional[HealthMonitor] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_health_monitor() -> HealthMonitor:
    """Get or create the global health monitor"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor
