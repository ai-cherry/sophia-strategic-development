"""
Lambda GPU Metrics
Comprehensive Prometheus metrics for monitoring Cortex operations.
"""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Info

# Create a registry for Cortex-specific metrics
cortex_registry = CollectorRegistry()

# ===================================================================
# Execution Metrics
# ===================================================================

cortex_calls_total = Counter(
    "cortex_calls_total",
    "Total Cortex API calls",
    ["mode", "task", "status", "model"],
    registry=cortex_registry,
)

cortex_latency_seconds = Histogram(
    "cortex_latency_seconds",
    "Cortex call latency in seconds",
    ["mode", "task", "model"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
    registry=cortex_registry,
)

cortex_tokens_used = Counter(
    "cortex_tokens_used",
    "Total tokens consumed by Cortex",
    ["task", "model"],
    registry=cortex_registry,
)

cortex_credits_used = Counter(
    "cortex_credits_used",
    "Qdrant credits consumed by Cortex",
    ["task", "model"],
    registry=cortex_registry,
)

# ===================================================================
# Pool Metrics
# ===================================================================

qdrant_pool_size = Gauge(
    "qdrant_pool_size",
    "Current connection pool size",
    ["mode"],
    registry=cortex_registry,
)

qdrant_pool_in_use = Gauge(
    "qdrant_pool_in_use",
    "Connections currently in use",
    ["mode"],
    registry=cortex_registry,
)

qdrant_pool_wait_time_ms = Gauge(
    "qdrant_pool_wait_time_ms",
    "Average wait time for connection acquisition in milliseconds",
    ["mode"],
    registry=cortex_registry,
)

qdrant_pool_timeouts = Counter(
    "qdrant_pool_timeouts",
    "Number of pool timeout errors",
    ["mode"],
    registry=cortex_registry,
)

# ===================================================================
# MCP Health Metrics
# ===================================================================

mcp_server_health_score = Gauge(
    "mcp_server_health_score",
    "MCP server health score (0-1)",
    ["server_id", "tier"],
    registry=cortex_registry,
)

mcp_server_latency_ms = Gauge(
    "mcp_server_latency_ms",
    "MCP server response latency in milliseconds",
    ["server_id"],
    registry=cortex_registry,
)

mcp_server_error_rate = Gauge(
    "mcp_server_error_rate",
    "MCP server error rate (errors per minute)",
    ["server_id"],
    registry=cortex_registry,
)

# ===================================================================
# Circuit Breaker Metrics
# ===================================================================

cortex_circuit_breaker_state = Gauge(
    "cortex_circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 2=half-open)",
    ["mode"],
    registry=cortex_registry,
)

cortex_circuit_breaker_failures = Counter(
    "cortex_circuit_breaker_failures",
    "Number of failures tracked by circuit breaker",
    ["mode"],
    registry=cortex_registry,
)

# ===================================================================
# Fallback Metrics
# ===================================================================

cortex_fallback_total = Counter(
    "cortex_fallback_total",
    "Number of fallbacks from MCP to DIRECT mode",
    registry=cortex_registry,
)

cortex_fallback_success = Counter(
    "cortex_fallback_success",
    "Number of successful fallbacks",
    registry=cortex_registry,
)

# ===================================================================
# Cache Metrics (for future semantic cache)
# ===================================================================

cortex_cache_hits = Counter(
    "cortex_cache_hits",
    "Number of cache hits",
    ["cache_type", "task"],
    registry=cortex_registry,
)

cortex_cache_misses = Counter(
    "cortex_cache_misses",
    "Number of cache misses",
    ["cache_type", "task"],
    registry=cortex_registry,
)

cortex_cache_size = Gauge(
    "cortex_cache_size",
    "Current cache size in entries",
    ["cache_type"],
    registry=cortex_registry,
)

# ===================================================================
# Cost Tracking Metrics
# ===================================================================

cortex_daily_credits = Gauge(
    "cortex_daily_credits", "Credits used today", ["task"], registry=cortex_registry
)

cortex_monthly_credits = Gauge(
    "cortex_monthly_credits",
    "Credits used this month",
    ["task"],
    registry=cortex_registry,
)

cortex_credit_limit_percentage = Gauge(
    "cortex_credit_limit_percentage",
    "Percentage of daily credit limit used",
    registry=cortex_registry,
)

# ===================================================================
# Model Performance Metrics
# ===================================================================

cortex_model_performance = Histogram(
    "cortex_model_performance",
    "Model performance metrics (quality score)",
    ["model", "task"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    registry=cortex_registry,
)

cortex_model_errors = Counter(
    "cortex_model_errors",
    "Model-specific errors",
    ["model", "error_type"],
    registry=cortex_registry,
)

# ===================================================================
# PAT Metrics
# ===================================================================

qdrant_pat_days_until_expiry = Counter(
    "qdrant_pat_days_until_expiry",
    "Days until PAT expiration",
    ["environment"],
    registry=cortex_registry,
)

qdrant_pat_rotation_alerts = Counter(
    "qdrant_pat_rotation_alerts",
    "Number of PATs needing rotation",
    ["severity"],
    registry=cortex_registry,
)

# ===================================================================
# System Info
# ===================================================================

cortex_info = Info("cortex", "Cortex integration information", registry=cortex_registry)

# Set initial info
cortex_info.info(
    {
        "version": "1.0.0",
        "integration": "qdrant_cortex_mcp",
        "adapter_modes": "direct,mcp,auto",
    }
)

# ===================================================================
# Helper Functions
# ===================================================================

def record_cortex_call(
    mode: str,
    task: str,
    model: str,
    status: str,
    latency_seconds: float,
    tokens: int | None = None,
):
    """Record metrics for a Cortex call"""
    cortex_calls_total.labels(mode=mode, task=task, status=status, model=model).inc()
    cortex_latency_seconds.labels(mode=mode, task=task, model=model).observe(
        latency_seconds
    )

    if tokens:
        cortex_tokens_used.labels(task=task, model=model).inc(tokens)
        # Estimate credits (rough approximation - adjust based on actual pricing)
        credits = tokens / 1000 * 0.001  # Example rate
        cortex_credits_used.labels(task=task, model=model).inc(credits)

def record_pool_metrics(mode: str, size: int, in_use: int, avg_wait_ms: float):
    """Record connection pool metrics"""
    
    qdrant_pool_size.labels(mode=mode).set(size)
    qdrant_pool_in_use.labels(mode=mode).set(in_use)
    qdrant_pool_wait_time_ms.labels(mode=mode).set(avg_wait_ms)

def record_mcp_health(
    server_id: str, tier: str, health_score: float, latency_ms: float, error_rate: float
):
    """Record MCP server health metrics"""
    mcp_server_health_score.labels(server_id=server_id, tier=tier).set(health_score)
    mcp_server_latency_ms.labels(server_id=server_id).set(latency_ms)
    mcp_server_error_rate.labels(server_id=server_id).set(error_rate)

def set_circuit_breaker_state(mode: str, state: str):
    """Set circuit breaker state"""
    state_map = {"closed": 0, "open": 1, "half-open": 2}
    cortex_circuit_breaker_state.labels(mode=mode).set(state_map.get(state, -1))

def record_cache_access(cache_type: str, task: str, hit: bool):
    """Record cache access"""
    if hit:
        cortex_cache_hits.labels(cache_type=cache_type, task=task).inc()
    else:
        cortex_cache_misses.labels(cache_type=cache_type, task=task).inc()

# ===================================================================
# Export all metrics
# ===================================================================

__all__ = [
    "cortex_cache_hits",
    "cortex_cache_misses",
    "cortex_cache_size",
    "cortex_calls_total",
    "cortex_circuit_breaker_failures",
    "cortex_circuit_breaker_state",
    "cortex_credit_limit_percentage",
    "cortex_credits_used",
    "cortex_daily_credits",
    "cortex_fallback_success",
    "cortex_fallback_total",
    "cortex_info",
    "cortex_latency_seconds",
    "cortex_model_errors",
    "cortex_model_performance",
    "cortex_monthly_credits",
    "cortex_registry",
    "cortex_tokens_used",
    "mcp_server_error_rate",
    "mcp_server_health_score",
    "mcp_server_latency_ms",
    "record_cache_access",
    "record_cortex_call",
    "record_mcp_health",
    "record_pool_metrics",
    "set_circuit_breaker_state",
    "qdrant_pat_days_until_expiry",
    "qdrant_pat_rotation_alerts",
    "qdrant_pool_in_use",
    "qdrant_pool_size",
    "qdrant_pool_timeouts",
    "qdrant_pool_wait_time_ms",
]
