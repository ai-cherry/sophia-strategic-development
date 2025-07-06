from prometheus_client import Counter, Gauge, Histogram

# -----------------------------------------
# Data Source & Pipeline Metrics
# -----------------------------------------

DATA_FETCH_DURATION = Histogram(
    "sophia_data_fetch_duration_seconds",
    "Time taken to fetch data from a source",
    ["source", "query_type"],
)

DATA_FETCH_ERRORS = Counter(
    "sophia_data_fetch_errors_total",
    "Total errors encountered while fetching data",
    ["source", "error_type"],
)

DATA_FRESHNESS = Gauge(
    "sophia_data_freshness_seconds",
    "Age of the data in seconds, reported upon fetch",
    ["source", "data_type"],
)

CACHE_OPERATIONS = Counter(
    "sophia_cache_operations_total",
    "Total cache operations",
    ["cache_type", "operation"],  # operation can be 'hit' or 'miss'
)

# -----------------------------------------
# LLM & AI Service Metrics
# -----------------------------------------

LLM_RESPONSE_TIME = Histogram(
    "sophia_llm_response_seconds",
    "Time for LLM to generate a response",
    ["provider", "model"],
)

LLM_TOKEN_USAGE = Counter(
    "sophia_llm_tokens_total",
    "Total number of LLM tokens used",
    ["provider", "model", "token_type"],  # token_type can be 'prompt' or 'completion'
)

CONSTITUTIONAL_AI_ACTIONS = Counter(
    "sophia_constitutional_ai_actions_total",
    "Actions taken by Constitutional AI",
    ["action"],  # action can be 'reviewed', 'violation_found', 'revised'
)

# -----------------------------------------
# Data Quality & Validation Metrics
# -----------------------------------------

DATA_VALIDATION_FAILURES = Counter(
    "sophia_data_validation_failures_total",
    "Total data validation failures",
    ["source", "validation_type"],
)

EMPTY_RESULTS_QUERIES = Counter(
    "sophia_empty_results_queries_total",
    "Number of queries that returned empty results from a data source",
    ["source", "query_type"],
)

# -----------------------------------------
# Business & Application Metrics
# -----------------------------------------

USER_QUERIES = Counter(
    "sophia_user_queries_total",
    "Total number of user queries processed",
    ["intent", "user_id"],
)

ACTIVE_SESSIONS = Gauge(
    "sophia_active_sessions", "Number of currently active user sessions"
)


def register_metrics():
    """
    This function can be used to initialize any metrics that need it.
    For now, it's a placeholder. In a real application, you might use this
    to register multi-process metrics collectors.
    """
    pass
