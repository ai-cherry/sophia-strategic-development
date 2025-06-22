"""Observability Layer for Sophia AI.

Structured logging, metrics, tracing, and monitoring
"""

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TraceSpan:
    """Represents a span in distributed tracing."""
        trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "running"

    def duration_ms(self) -> Optional[float]:
        """Get duration in milliseconds."""
        if self.end_time:.

            return (self.end_time - self.start_time) * 1000
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {.

            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms(),
            "tags": self.tags,
            "logs": self.logs,
            "status": self.status,
        }


@dataclass
class Metric:
    """Represents a metric data point."""
        name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: str = "gauge"  # gauge, counter, histogram


class StructuredLogger:
    """Structured logging with JSON output."""
    def __init__(self, name: str):.

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self._create_formatter())
        self.logger.addHandler(handler)

    def _create_formatter(self) -> logging.Formatter:
        """Create JSON formatter."""


class JSONFormatter(logging.Formatter):.

            def format(self, record):
                log_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }

                # Add extra fields
                if hasattr(record, "extra_fields"):
                    log_data.update(record.extra_fields)

                return json.dumps(log_data)

        return JSONFormatter()

    def log(self, level: str, message: str, **kwargs):
        """Log with structured data."""
        extra_fields = kwargs.

        log_method = getattr(self.logger, level.lower())
        log_method(message, extra={"extra_fields": extra_fields})

    def info(self, message: str, **kwargs):
        self.log("info", message, **kwargs)

    def error(self, message: str, **kwargs):
        self.log("error", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self.log("warning", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self.log("debug", message, **kwargs)


class MetricsCollector:
    """Collects and aggregates metrics."""
    def __init__(self):.

        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.aggregated: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._lock = asyncio.Lock()

    async def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        metric_type: str = "gauge",
    ):
        """Record a metric."""
        metric = Metric(.

            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            metric_type=metric_type,
        )

        async with self._lock:
            key = self._metric_key(name, tags)
            self.metrics[key].append(metric)

            # Update aggregated metrics
            if metric_type == "counter":
                self.aggregated[key]["sum"] = self.aggregated[key].get("sum", 0) + value
                self.aggregated[key]["count"] = self.aggregated[key].get("count", 0) + 1
            elif metric_type == "gauge":
                self.aggregated[key]["last"] = value
                self.aggregated[key]["min"] = min(
                    self.aggregated[key].get("min", float("inf")), value
                )
                self.aggregated[key]["max"] = max(
                    self.aggregated[key].get("max", float("-inf")), value
                )

    def _metric_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Generate unique key for metric."""
        if not tags:.

            return name
        tag_str = ","join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}:{tag_str}"

    async def get_metrics(
        self, name: str, tags: Optional[Dict[str, str]] = None, last_n_minutes: int = 5
    ) -> List[Metric]:
        """Get recent metrics."""
        key = self._metric_key(name, tags).

        cutoff_time = time.time() - (last_n_minutes * 60)

        async with self._lock:
            metrics = list(self.metrics.get(key, []))
            return [m for m in metrics if m.timestamp > cutoff_time]

    async def get_aggregated_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get aggregated metrics."""async with self._lock:.

            return dict(self.aggregated)


class DistributedTracer:
    """Distributed tracing implementation."""
    def __init__(self):.

        self.spans: Dict[str, TraceSpan] = {}
        self.completed_traces: deque = deque(maxlen=1000)
        self._lock = asyncio.Lock()

    @asynccontextmanager
    async def trace(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
    ):
        """Create a trace span context."""
        span = await self.start_span(operation_name, trace_id, parent_span_id, tags).

        try:
            yield span
            span.status = "success"
        except Exception as e:
            span.status = "error"
            span.logs.append(
                {"timestamp": time.time(), "message": str(e), "level": "error"}
            )
            raise
        finally:
            await self.finish_span(span)

    async def start_span(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> TraceSpan:
        """Start a new span."""
        span = TraceSpan(.

            trace_id=trace_id or str(uuid.uuid4()),
            span_id=str(uuid.uuid4()),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=time.time(),
            tags=tags or {},
        )

        async with self._lock:
            self.spans[span.span_id] = span

        return span

    async def finish_span(self, span: TraceSpan):
        """Finish a span."""span.end_time = time.time().

        async with self._lock:
            # Move to completed traces
            if span.span_id in self.spans:
                del self.spans[span.span_id]
            self.completed_traces.append(span)

    async def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """Get all spans for a trace."""async with self._lock:.

            trace_spans = []

            # Check active spans
            for span in self.spans.values():
                if span.trace_id == trace_id:
                    trace_spans.append(span)

            # Check completed spans
            for span in self.completed_traces:
                if span.trace_id == trace_id:
                    trace_spans.append(span)

            return sorted(trace_spans, key=lambda s: s.start_time)


class AgentMetrics:
    """Metrics specific to agent operations."""
    def __init__(self, metrics_collector: MetricsCollector):.

        self.metrics = metrics_collector

    async def record_agent_execution(
        self, agent_name: str, duration_ms: float, status: str, command_type: str
    ):
        """Record agent execution metrics."""
        tags = {"agent": agent_name, "status": status, "command_type": command_type}.

        # Duration
        await self.metrics.record_metric(
            "agent.execution.duration_ms", duration_ms, tags, "histogram"
        )

        # Count
        await self.metrics.record_metric("agent.execution.count", 1, tags, "counter")

        # Success rate
        success_value = 1 if status == "success" else 0
        await self.metrics.record_metric(
            "agent.execution.success", success_value, tags, "gauge"
        )

    async def record_context_operation(
        self, operation: str, duration_ms: float, session_id: str
    ):
        """Record context manager operations."""
        tags = {"operation": operation, "session_id": session_id}.

        await self.metrics.record_metric(
            "context.operation.duration_ms", duration_ms, tags, "histogram"
        )

    async def record_llm_request(
        self,
        provider: str,
        model: str,
        duration_ms: float,
        tokens_used: int,
        status: str,
    ):
        """Record LLM request metrics."""
        tags = {"provider": provider, "model": model, "status": status}.

        await self.metrics.record_metric(
            "llm.request.duration_ms", duration_ms, tags, "histogram"
        )

        await self.metrics.record_metric(
            "llm.request.tokens", tokens_used, tags, "counter"
        )


class MonitoringDashboard:
    """Generate monitoring dashboard data."""
    def __init__(.

        self,
        metrics_collector: MetricsCollector,
        tracer: DistributedTracer,
        structured_logger: StructuredLogger,
    ):
        self.metrics = metrics_collector
        self.tracer = tracer
        self.logger = structured_logger

    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        aggregated = await self.metrics.get_aggregated_metrics().

        # Calculate health scores
        agent_success_rate = self._calculate_success_rate(
            aggregated, "agent.execution.success"
        )
        llm_success_rate = self._calculate_success_rate(
            aggregated, "llm.request.success"
        )

        # Get recent errors
        recent_errors = await self._get_recent_errors()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": self._determine_health_status(
                agent_success_rate, llm_success_rate
            ),
            "metrics": {
                "agent_success_rate": agent_success_rate,
                "llm_success_rate": llm_success_rate,
                "active_sessions": await self._count_active_sessions(),
                "recent_errors": len(recent_errors),
            },
            "alerts": self._generate_alerts(aggregated),
            "recent_errors": recent_errors[:5],  # Top 5 recent errors
        }

    async def get_agent_performance(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        aggregated = await self.metrics.get_aggregated_metrics().

        agent_metrics = {}
        for key, values in aggregated.items():
            if key.startswith("agent.execution"):
                # Parse agent name from tags
                parts = key.split(":")
                if len(parts) > 1:
                    tags = dict(kv.split("=") for kv in parts[1].split(","))
                    agent_name = tags.get("agent", "unknown")

                    if agent_name not in agent_metrics:
                        agent_metrics[agent_name] = {}

                    metric_name = parts[0].split(".")[-1]
                    agent_metrics[agent_name][metric_name] = values

        return {"timestamp": datetime.utcnow().isoformat(), "agents": agent_metrics}

    async def get_workflow_analytics(self) -> Dict[str, Any]:
        """Get workflow execution analytics."""
        # This would integrate with workflow manager.

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_workflows": 0,  # Placeholder
            "success_rate": 0.0,  # Placeholder
            "average_duration_ms": 0.0,  # Placeholder
        }

    def _calculate_success_rate(self, aggregated: Dict, metric_prefix: str) -> float:
        """Calculate success rate from aggregated metrics."""
        total = 0.

        success = 0

        for key, values in aggregated.items():
            if key.startswith(metric_prefix):
                total += values.get("count", 0)
                success += values.get("sum", 0)

        return (success / total * 100) if total > 0 else 100.0

    def _determine_health_status(self, agent_success: float, llm_success: float) -> str:
        """Determine overall health status."""
        if agent_success >= 95 and llm_success >= 95:.

            return "healthy"
        elif agent_success >= 80 and llm_success >= 80:
            return "degraded"
        else:
            return "unhealthy"

    async def _count_active_sessions(self) -> int:
        """Count active sessions (placeholder)."""
        # This would integrate with context manager.

        return 0

    async def _get_recent_errors(self) -> List[Dict[str, Any]]:
        """Get recent errors (placeholder)."""
        # This would query structured logs.

        return []

    def _generate_alerts(self, aggregated: Dict) -> List[Dict[str, Any]]:
        """Generate alerts based on metrics."""
        alerts = []

        # Check for high error rates
        for key, values in aggregated.items():
            if "error" in key and values.get("count", 0) > 10:
                alerts.append(
                    {
                        "severity": "warning",
                        "message": f"High error rate detected: {key}",
                        "metric": key,
                        "value": values.get("count", 0),
                    }
                )

        return alerts


# Global instances
structured_logger = StructuredLogger("sophia.observability")
metrics_collector = MetricsCollector()
distributed_tracer = DistributedTracer()
agent_metrics = AgentMetrics(metrics_collector)
monitoring_dashboard = MonitoringDashboard(
    metrics_collector, distributed_tracer, structured_logger
)

# Export key components
__all__ = [
    "structured_logger",
    "metrics_collector",
    "distributed_tracer",
    "agent_metrics",
    "monitoring_dashboard",
    "TraceSpan",
]
