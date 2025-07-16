"""
Centralized Secret Mapping Configuration
Clean Lambda Labs integration with Pulumi ESC and GitHub workflows
"""

GITHUB_TO_INTERNAL_MAPPING = {
    # AI Services
    "OPENAI_API_KEY": "openai_api_key",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "PORTKEY_API_KEY": "portkey_api_key",
    "OPENROUTER_API_KEY": "openrouter_api_key",
    "MEM0_API_KEY": "mem0_api_key",
    # Data Infrastructure
    "QDRANT_ACCOUNT": "postgres_host",
    "QDRANT_USER": "QDRANT_user",
    "QDRANT_PASSWORD": "postgres_password",
    "QDRANT_WAREHOUSE": "postgres_database",
    "QDRANT_DATABASE": "postgres_database",
    "QDRANT_ROLE": "QDRANT_role",
    # Business Intelligence
    "GONG_ACCESS_KEY": "gong_access_key",
    "GONG_ACCESS_KEY_SECRET": "gong_access_key_secret",
    "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
    "LINEAR_API_KEY": "linear_api_key",
    "NOTION_API_TOKEN": "notion_api_token",
    # Lambda Labs Infrastructure (Clean Configuration)
    "LAMBDA_LABS_API_KEY": "lambda_labs_api_key",
    # Infrastructure
    "DOCKER_HUB_ACCESS_TOKEN": "docker_hub_access_token",
    "PULUMI_ACCESS_TOKEN": "pulumi_access_token",
    # Communications
    "SLACK_BOT_TOKEN": "slack_bot_token",
    "SLACK_APP_TOKEN": "slack_app_token",
    "SLACK_WEBHOOK_URL": "slack_webhook_url",
    # Security
    "JWT_SECRET_KEY": "jwt_secret_key",
    "ENCRYPTION_KEY": "encryption_key",
    # Monitoring
    "SENTRY_DSN": "sentry_dsn",
    "DATADOG_API_KEY": "datadog_api_key",
    # Deployment
    "LAMBDA_LABS_TOKEN": "LAMBDA_LABS_TOKEN",
    "GITHUB_TOKEN": "github_token",
}

# Lambda Labs specific configuration
LAMBDA_LABS_CONFIG = {
    "api_endpoint": "https://api.lambda.ai/v1",
    "supported_models": [
        "llama3.1-8b-instruct",
        "llama3.1-70b-instruct-fp8",
        "llama-4-maverick-17b-128e-instruct-fp8",
    ],
    "cost_per_million_tokens": {
        "llama3.1-8b-instruct": 0.07,
        "llama3.1-70b-instruct-fp8": 0.35,
        "llama-4-maverick-17b-128e-instruct-fp8": 0.88,
    },
    "budget_limits": {
        "daily": 50.0,
        "monthly": 1000.0,
    },
    "routing_strategy": "serverless_first",
    "gpu_fallback": True,
}

# Service dependencies
SERVICE_DEPENDENCIES = {
    "lambda_labs": ["qdrant", "redis"],
    "qdrant": ["estuary"],
    "gong": ["qdrant", "ai_memory"],
    "slack": ["qdrant", "ai_memory"],
    "ai_memory": ["qdrant"],
}

# Health check endpoints
HEALTH_CHECK_ENDPOINTS = {
    "lambda_labs": "/v1/models",
    "qdrant": "/health",
    "gong": "/v2/calls",
    "slack": "/api/test",
    "linear": "/graphql",
}

def get_secret_mapping(github_secret_name: str) -> str:
    """Get internal secret name from GitHub secret name."""
    return GITHUB_TO_INTERNAL_MAPPING.get(
        github_secret_name, github_secret_name.lower()
    )

def get_lambda_labs_model_cost(model: str) -> float:
    """Get cost per million tokens for a Lambda Labs model."""
    return LAMBDA_LABS_CONFIG["cost_per_million_tokens"].get(
        model, 0.35
    )  # Default to mid-tier

def get_service_dependencies(service: str) -> list[str]:
    """Get dependencies for a service."""
    return SERVICE_DEPENDENCIES.get(service, [])
