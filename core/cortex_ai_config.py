"""
Cortex AI Configuration for Sophia AI
Generated: 2025-07-04T18:37:38.754393
This configuration enables native AI capabilities in Snowflake
"""

CORTEX_CONFIG = {
    "warehouse": "SOPHIA_AI_CORTEX_WH",
    "database": "SOPHIA_AI_PRODUCTION",
    "schema": "CORTEX_AI",
    "models": {
        "completion": {
            "primary": "mistral-7b",
            "alternatives": ["mixtral-8x7b", "llama2-70b-chat", "gemma-7b"],
        },
        "embeddings": {"primary": "e5-base-v2", "dimension": 768},
    },
    "functions": {
        "complete": "SNOWFLAKE.CORTEX.COMPLETE",
        "sentiment": "SNOWFLAKE.CORTEX.SENTIMENT",
        "summarize": "SNOWFLAKE.CORTEX.SUMMARIZE",
        "embed": "SNOWFLAKE.CORTEX.EMBED_TEXT_768",
        "extract": "SNOWFLAKE.CORTEX.EXTRACT_ANSWER",
        "translate": "SNOWFLAKE.CORTEX.TRANSLATE",
    },
    "tables": {
        "ai_memory": "CORTEX_AI.AI_MEMORY_ENHANCED",
        "business_insights": "CORTEX_AI.BUSINESS_INSIGHTS",
    },
    "search_services": {"business_search": "SOPHIA_BUSINESS_SEARCH"},
}

# Test results from setup
TEST_RESULTS = {
    "timestamp": "2025-07-04T18:37:14.122947",
    "connection": {
        "account": "ZNB04675",
        "user": "SCOOBYJAVA15",
        "role": "ACCOUNTADMIN",
        "version": "9.18.0",
        "status": "connected",
    },
    "warehouses": {"cortex_warehouse": "created"},
    "cortex_functions": {
        "mistral-7b": "working",
        "mixtral-8x7b": "working",
        "llama2-70b-chat": "working",
        "gemma-7b": "working",
        "sentiment": 0.88996166,
        "summarize": "working",
    },
    "embeddings": {
        "e5-base-v2": {
            "error": "the JSON object must be str, bytes or bytearray, not list"
        },
        "multilingual-e5-large": {
            "error": "220000 (22000): 01bd79a1-0105-e249-000b-d85f000ab00a: Array-like value being cast to a vector has incorrect dimension"
        },
    },
    "search_services": {
        "error": "000904 (42000): 01bd79a1-0105-de4f-000b-d85f000901d2: SQL compilation error: error line 0 at position -1\ninvalid identifier 'AI_MEMORY_ENHANCED'"
    },
    "recommendations": ["Review Cortex Search Service syntax and permissions"],
}
