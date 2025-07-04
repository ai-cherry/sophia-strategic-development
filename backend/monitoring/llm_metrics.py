"""LLM-specific metrics for monitoring"""

from prometheus_client import Counter, Histogram

# Request metrics
llm_requests_total = Counter(
    "llm_requests_total",
    "Total number of LLM requests",
    ["provider", "model", "task_type", "status"],
)

llm_request_duration = Histogram(
    "llm_request_duration_seconds",
    "LLM request duration in seconds",
    ["provider", "model"],
)

# Cache metrics
llm_cache_hit_rate = Counter(
    "llm_cache_hits_total", "Total number of cache hits", ["provider"]
)

# Cost metrics
llm_cost_per_request = Histogram(
    "llm_cost_per_request_usd", "Cost per LLM request in USD", ["provider", "model"]
)

# Data locality metrics
data_movement_avoided = Counter(
    "data_movement_avoided_kb",
    "Amount of data movement avoided by using Snowflake Cortex (KB)",
    ["operation_type"],
)
