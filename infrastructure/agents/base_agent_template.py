from datetime import UTC, datetime

#!/usr/bin/env python3
"""
Base Agent Template
Implements expert-recommended standards for all Sophia AI agents
"""

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

import structlog
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Configure structured logging
LoggingInstrumentor().instrument(set_logging_format=True)
logger = structlog.get_logger()

# OpenTelemetry setup
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)


class HealthStatus(Enum):
    """Agent health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class AgentRequest:
    """Standard agent request format"""

    def __init__(
        self,
        action: str,
        payload: dict[str, Any],
        correlation_id: str | None = None,
        priority: int = 5,
    ):
        self.action = action
        self.payload = payload
        self.correlation_id = correlation_id or self._generate_id()
        self.priority = priority
        self.timestamp = datetime.now(UTC)

    def _generate_id(self) -> str:
        import uuid

        return str(uuid.uuid4())


class AgentResponse:
    """Standard agent response format"""

    def __init__(
        self,
        status: str,
        data: dict[str, Any] | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.status = status
        self.data = data or {}
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now(UTC)


class BaseAgent(ABC):
    """
    Base class for all Sophia AI agents
    Implements expert-recommended patterns
    """

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logger.bind(agent=name)
        self._health_status = HealthStatus.HEALTHY
        self._metrics = {}
        self._setup_metrics()

    def _setup_metrics(self):
        """Initialize OpenTelemetry metrics"""
        self.request_counter = meter.create_counter(
            f"{self.name}_requests_total",
            description=f"Total requests processed by {self.name}",
        )

        self.error_counter = meter.create_counter(
            f"{self.name}_errors_total", description=f"Total errors in {self.name}"
        )

        self.latency_histogram = meter.create_histogram(
            f"{self.name}_latency_seconds",
            description=f"Request latency for {self.name}",
        )

    async def health_check(self) -> HealthStatus:
        """
        Health check implementation
        Override in subclasses for custom checks
        """
        try:
            # Basic health check - override for specific checks
            await self._perform_health_check()
            return self._health_status
        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
            self._health_status = HealthStatus.UNHEALTHY
            return self._health_status

    @abstractmethod
    async def _perform_health_check(self):
        """Implement specific health checks in subclasses"""
        pass

    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Main processing method - must be implemented by all agents
        """
        pass

    async def get_metrics(self) -> dict[str, float]:
        """
        Return current metrics
        """
        return {
            "health_status": self._health_status.value,
            "uptime_seconds": self._get_uptime(),
            **self._metrics,
        }

    def _get_uptime(self) -> float:
        """Calculate agent uptime"""
        # Implementation depends on how you track start time
        return 0.0

    async def execute_with_telemetry(self, request: AgentRequest) -> AgentResponse:
        """
        Execute request with full observability
        """
        with tracer.start_as_current_span(f"{self.name}.process") as span:
            span.set_attribute("agent.name", self.name)
            span.set_attribute("request.action", request.action)
            span.set_attribute("request.correlation_id", request.correlation_id)

            start_time = datetime.now(UTC)

            try:
                # Log request
                self.logger.info(
                    "Processing request",
                    action=request.action,
                    correlation_id=request.correlation_id,
                )

                # Process request
                response = await self.process(request)

                # Record metrics
                latency = (datetime.now(UTC) - start_time).total_seconds()
                self.latency_histogram.record(latency)
                self.request_counter.add(1, {"status": response.status})

                # Log response
                self.logger.info(
                    "Request completed",
                    action=request.action,
                    correlation_id=request.correlation_id,
                    status=response.status,
                    latency=latency,
                )

                return response

            except Exception as e:
                # Record error
                self.error_counter.add(1, {"error_type": type(e).__name__})
                span.record_exception(e)

                # Log error
                self.logger.error(
                    "Request failed",
                    action=request.action,
                    correlation_id=request.correlation_id,
                    error=str(e),
                )

                # Return error response
                return AgentResponse(
                    status="error",
                    error=str(e),
                    metadata={"correlation_id": request.correlation_id},
                )


# Example implementation
class ExampleAgent(BaseAgent):
    """
    Example agent implementation
    """

    async def _perform_health_check(self):
        """Check agent-specific health"""
        # Example: Check database connection, API availability, etc.
        pass

    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process the request"""
        # Example implementation
        action = request.action

        if action == "ping":
            return AgentResponse(status="success", data={"message": "pong"})

        # Add your agent-specific logic here
        return AgentResponse(status="success", data={"processed": True})


# Circuit breaker decorator for external calls
class CircuitBreaker:
    """
    Simple circuit breaker implementation
    Based on expert recommendation for resilience
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time
            and (datetime.now(UTC) - self.last_failure_time).seconds
            >= self.recovery_timeout
        )

    def _on_success(self):
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now(UTC)
        if self.failure_count >= self.failure_threshold:
            self.state = "open"


if __name__ == "__main__":
    # Example usage
    async def main():
        agent = ExampleAgent(name="example-agent", config={"debug": True})

        # Test request
        request = AgentRequest(action="ping", payload={})

        response = await agent.execute_with_telemetry(request)
        print(f"Response: {response.status}")

        # Check health
        health = await agent.health_check()
        print(f"Health: {health.value}")

        # Get metrics
        metrics = await agent.get_metrics()
        print(f"Metrics: {metrics}")

    asyncio.run(main())
