#!/usr/bin/env python3
"""
Prometheus Monitoring Configuration for Sophia AI
Implements comprehensive metrics collection and monitoring

NOTE: All metrics and monitoring are tuned for a user base of 5–100 users. Resource allocation, retention, and alerting thresholds are set for this scale and can be adjusted as the user base grows.
"""

import logging
import time
from contextlib import contextmanager
from functools import wraps

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
    start_http_server,
)

logger = logging.getLogger(__name__)


class SophiaMetrics:
    """Centralized metrics collection for Sophia AI"""

    def __init__(self, registry: CollectorRegistry | None = None):
        self.registry = registry or CollectorRegistry()

        # Initialize core metrics
        self._init_core_metrics()
        self._init_ai_metrics()
        self._init_business_metrics()
        self._init_infrastructure_metrics()

    def _init_core_metrics(self):
        """Initialize core application metrics"""

        # Request metrics
        self.request_count = Counter(
            "sophia_requests_total",
            "Total number of requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self.request_duration = Histogram(
            "sophia_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )

        # Error metrics
        self.error_count = Counter(
            "sophia_errors_total",
            "Total number of errors",
            ["service", "error_type"],
            registry=self.registry,
        )

        # Active connections
        self.active_connections = Gauge(
            "sophia_active_connections",
            "Number of active connections",
            ["service"],
            registry=self.registry,
        )

    def _init_ai_metrics(self):
        """Initialize AI-specific metrics"""

        # AI model performance
        self.ai_request_count = Counter(
            "sophia_ai_requests_total",
            "Total AI requests",
            ["model", "provider", "task_type"],
            registry=self.registry,
        )

        self.ai_request_duration = Histogram(
            "sophia_ai_request_duration_seconds",
            "AI request duration",
            ["model", "provider"],
            registry=self.registry,
        )

        self.ai_token_usage = Counter(
            "sophia_ai_tokens_total",
            "Total AI tokens used",
            ["model", "provider", "token_type"],
            registry=self.registry,
        )

        self.ai_cost = Counter(
            "sophia_ai_cost_dollars",
            "Total AI cost in dollars",
            ["model", "provider"],
            registry=self.registry,
        )

        # AI quality metrics
        self.ai_evaluation_scores = Histogram(
            "sophia_ai_evaluation_scores",
            "AI evaluation scores",
            ["metric", "category"],
            registry=self.registry,
        )

        self.ai_safety_violations = Counter(
            "sophia_ai_safety_violations_total",
            "AI safety violations",
            ["violation_type"],
            registry=self.registry,
        )

    def _init_business_metrics(self):
        """Initialize business intelligence metrics"""

        # Business queries
        self.business_queries = Counter(
            "sophia_business_queries_total",
            "Total business intelligence queries",
            ["query_type", "user_role"],
            registry=self.registry,
        )

        self.business_query_success = Counter(
            "sophia_business_query_success_total",
            "Successful business queries",
            ["query_type", "data_source"],
            registry=self.registry,
        )

        # Data processing
        self.data_ingestion_records = Counter(
            "sophia_data_ingestion_records_total",
            "Total records ingested",
            ["source", "table"],
            registry=self.registry,
        )

        self.data_processing_duration = Histogram(
            "sophia_data_processing_duration_seconds",
            "Data processing duration",
            ["operation", "source"],
            registry=self.registry,
        )

        # Business insights
        self.insights_generated = Counter(
            "sophia_insights_generated_total",
            "Total insights generated",
            ["insight_type", "confidence_level"],
            registry=self.registry,
        )

    def _init_infrastructure_metrics(self):
        """Initialize infrastructure metrics"""

        # Database connections
        self.db_connections_active = Gauge(
            "sophia_db_connections_active",
            "Active database connections",
            ["database", "pool"],
            registry=self.registry,
        )

        self.db_query_duration = Histogram(
            "sophia_db_query_duration_seconds",
            "Database query duration",
            ["database", "operation"],
            registry=self.registry,
        )

        # Cache metrics
        self.cache_operations = Counter(
            "sophia_cache_operations_total",
            "Cache operations",
            ["operation", "cache_type"],
            registry=self.registry,
        )

        self.cache_hit_ratio = Gauge(
            "sophia_cache_hit_ratio",
            "Cache hit ratio",
            ["cache_type"],
            registry=self.registry,
        )

        # MCP server metrics
        self.mcp_server_status = Gauge(
            "sophia_mcp_server_status",
            "MCP server status (1=up, 0=down)",
            ["server_name", "port"],
            registry=self.registry,
        )

        self.mcp_request_count = Counter(
            "sophia_mcp_requests_total",
            "MCP server requests",
            ["server_name", "tool"],
            registry=self.registry,
        )

        # System info
        self.system_info = Info(
            "sophia_system_info", "System information", registry=self.registry
        )

    @contextmanager
    def time_operation(self, metric: Histogram, **labels):
        """Context manager to time operations"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            metric.labels(**labels).observe(duration)

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        self.request_count.labels(
            method=method, endpoint=endpoint, status=str(status)
        ).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_error(self, service: str, error_type: str):
        """Record error occurrence"""
        self.error_count.labels(service=service, error_type=error_type).inc()

    def record_ai_request(
        self,
        model: str,
        provider: str,
        task_type: str,
        duration: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
    ):
        """Record AI request metrics"""
        self.ai_request_count.labels(
            model=model, provider=provider, task_type=task_type
        ).inc()

        self.ai_request_duration.labels(model=model, provider=provider).observe(
            duration
        )

        if input_tokens > 0:
            self.ai_token_usage.labels(
                model=model, provider=provider, token_type="input"
            ).inc(input_tokens)

        if output_tokens > 0:
            self.ai_token_usage.labels(
                model=model, provider=provider, token_type="output"
            ).inc(output_tokens)

        if cost > 0:
            self.ai_cost.labels(model=model, provider=provider).inc(cost)

    def record_ai_evaluation(self, metric: str, category: str, score: float):
        """Record AI evaluation metrics"""
        self.ai_evaluation_scores.labels(metric=metric, category=category).observe(
            score
        )

    def record_safety_violation(self, violation_type: str):
        """Record AI safety violation"""
        self.ai_safety_violations.labels(violation_type=violation_type).inc()

    def record_business_query(
        self,
        query_type: str,
        user_role: str,
        success: bool = True,
        data_source: str = "unknown",
    ):
        """Record business intelligence query"""
        self.business_queries.labels(query_type=query_type, user_role=user_role).inc()

        if success:
            self.business_query_success.labels(
                query_type=query_type, data_source=data_source
            ).inc()

    def record_data_ingestion(self, source: str, table: str, record_count: int):
        """Record data ingestion metrics"""
        self.data_ingestion_records.labels(source=source, table=table).inc(record_count)

    def record_insight_generation(self, insight_type: str, confidence_level: str):
        """Record insight generation"""
        self.insights_generated.labels(
            insight_type=insight_type, confidence_level=confidence_level
        ).inc()

    def update_db_connections(self, database: str, pool: str, count: int):
        """Update database connection count"""
        self.db_connections_active.labels(database=database, pool=pool).set(count)

    def record_db_query(self, database: str, operation: str, duration: float):
        """Record database query metrics"""
        self.db_query_duration.labels(database=database, operation=operation).observe(
            duration
        )

    def record_cache_operation(self, operation: str, cache_type: str):
        """Record cache operation"""
        self.cache_operations.labels(operation=operation, cache_type=cache_type).inc()

    def update_cache_hit_ratio(self, cache_type: str, ratio: float):
        """Update cache hit ratio"""
        self.cache_hit_ratio.labels(cache_type=cache_type).set(ratio)

    def update_mcp_server_status(self, server_name: str, port: int, status: bool):
        """Update MCP server status"""
        self.mcp_server_status.labels(server_name=server_name, port=str(port)).set(
            1 if status else 0
        )

    def record_mcp_request(self, server_name: str, tool: str):
        """Record MCP server request"""
        self.mcp_request_count.labels(server_name=server_name, tool=tool).inc()

    def set_system_info(self, info: dict[str, str]):
        """Set system information"""
        self.system_info.info(info)


# Global metrics instance
metrics = SophiaMetrics()


def monitor_request(endpoint: str = "unknown"):
    """Decorator to monitor HTTP requests"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            method = kwargs.get("method", "GET")
            status = 200

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 500
                metrics.record_error(service="api", error_type=type(e).__name__)
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_request(method, endpoint, status, duration)

        return wrapper

    return decorator


def monitor_ai_operation(model: str, provider: str, task_type: str):
    """Decorator to monitor AI operations"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Extract metrics from result if available
                duration = time.time() - start_time
                input_tokens = result.get("usage", {}).get("input_tokens", 0)
                output_tokens = result.get("usage", {}).get("output_tokens", 0)
                cost = result.get("cost", 0.0)

                metrics.record_ai_request(
                    model=model,
                    provider=provider,
                    task_type=task_type,
                    duration=duration,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost,
                )

                return result

            except Exception as e:
                metrics.record_error(service="ai", error_type=type(e).__name__)
                raise

        return wrapper

    return decorator


def monitor_db_operation(database: str, operation: str):
    """Decorator to monitor database operations"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                metrics.record_error(service="database", error_type=type(e).__name__)
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_db_query(database, operation, duration)

        return wrapper

    return decorator


class PrometheusServer:
    """Prometheus metrics server"""

    def __init__(self, port: int = 8090, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        self.server = None

    def start(self):
        """Start Prometheus metrics server"""
        try:
            self.server = start_http_server(
                self.port, self.host, registry=metrics.registry
            )
            logger.info(f"Prometheus metrics server started on {self.host}:{self.port}")

            # Set initial system info
            metrics.set_system_info(
                {
                    "version": "1.0.0",
                    "service": "sophia-ai",
                    "environment": "production",
                }
            )

        except Exception as e:
            logger.exception(f"Failed to start Prometheus server: {e}")
            raise

    def stop(self):
        """Stop Prometheus metrics server"""
        if self.server:
            # Prometheus client returns a tuple (server, thread)
            # We need to stop the thread
            if hasattr(self.server, "__iter__") and len(self.server) == 2:
                server, thread = self.server
                if hasattr(server, "shutdown"):
                    server.shutdown()
                if hasattr(thread, "join"):
                    thread.join()
            logger.info("Prometheus metrics server stopped")

    def get_metrics(self) -> str:
        """Get current metrics in Prometheus format"""
        return generate_latest(metrics.registry).decode("utf-8")


# Health check metrics
class HealthMetrics:
    """Health check specific metrics"""

    def __init__(self):
        self.health_check_status = Gauge(
            "sophia_health_check_status",
            "Health check status (1=healthy, 0=unhealthy)",
            ["service", "check_type"],
            registry=metrics.registry,
        )

        self.health_check_duration = Histogram(
            "sophia_health_check_duration_seconds",
            "Health check duration",
            ["service", "check_type"],
            registry=metrics.registry,
        )

    def record_health_check(
        self, service: str, check_type: str, healthy: bool, duration: float
    ):
        """Record health check result"""
        self.health_check_status.labels(service=service, check_type=check_type).set(
            1 if healthy else 0
        )

        self.health_check_duration.labels(
            service=service, check_type=check_type
        ).observe(duration)


# Global health metrics instance
health_metrics = HealthMetrics()


# Example usage and testing
async def example_usage():
    """Example usage of monitoring system"""

    # Start Prometheus server
    prometheus_server = PrometheusServer(port=8090)
    prometheus_server.start()

    # Record some example metrics
    metrics.record_request("GET", "/api/chat", 200, 0.5)
    metrics.record_ai_request("gpt-4", "openai", "chat", 1.2, 100, 150, 0.01)
    metrics.record_business_query("revenue_analysis", "manager", True, "snowflake")
    metrics.update_mcp_server_status("ai_memory", 9000, True)

    # Record health check
    health_metrics.record_health_check("database", "connection", True, 0.1)

    logger.info("Example metrics recorded")

    # Get current metrics
    current_metrics = prometheus_server.get_metrics()
    logger.info(f"Current metrics: {len(current_metrics)} bytes")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
