"""
Prometheus metrics for LLM Router
Provides comprehensive observability for all LLM operations
"""

from prometheus_client import Counter, Gauge, Histogram, Summary

# Request metrics
llm_requests_total = Counter(
    "llm_requests_total",
    "Total number of LLM requests",
    ["provider", "model", "task_type", "status"],
)

llm_request_duration = Histogram(
    "llm_request_duration_seconds",
    "LLM request duration in seconds",
    ["provider", "model", "task_type"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
)

# Cost metrics
llm_cost_usd_total = Counter(
    "llm_cost_usd_total",
    "Total cost in USD for LLM requests",
    ["provider", "model", "task_type"],
)

llm_tokens_total = Counter(
    "llm_tokens_total",
    "Total tokens processed",
    ["provider", "model", "direction"],  # direction: input/output
)

# Cache metrics
llm_cache_hit_rate = Gauge(
    "llm_cache_hit_rate", "Cache hit rate percentage", ["cache_type"]
)

llm_cache_operations = Counter(
    "llm_cache_operations_total",
    "Total cache operations",
    ["operation", "status"],  # operation: get/set, status: hit/miss/error
)

# Fallback metrics
llm_fallback_level = Gauge(
    "llm_fallback_level",
    "Current fallback level (0 = primary, higher = deeper fallback)",
    ["provider"],
)

llm_fallback_attempts = Counter(
    "llm_fallback_attempts_total",
    "Total fallback attempts",
    ["from_provider", "to_provider", "reason"],
)

# Router metrics
llm_router_version = Counter(
    "llm_router_version_total", "LLM Router version indicator", ["version"]
)

llm_routing_decisions = Counter(
    "llm_routing_decisions_total",
    "Routing decisions made",
    ["task_type", "complexity", "selected_model"],
)

# Performance metrics
llm_model_performance = Summary(
    "llm_model_performance",
    "Model performance characteristics",
    ["model", "metric"],  # metric: latency/throughput/quality
)

# Error metrics
llm_errors_total = Counter(
    "llm_errors_total", "Total LLM errors", ["provider", "model", "error_type"]
)

# Budget metrics
llm_budget_remaining = Gauge(
    "llm_budget_remaining_usd",
    "Remaining budget in USD",
    ["budget_type"],  # daily/monthly/per_request
)

llm_budget_usage_ratio = Gauge(
    "llm_budget_usage_ratio", "Budget usage ratio (0-1)", ["budget_type"]
)
