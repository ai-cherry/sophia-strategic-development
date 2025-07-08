"""
Centralized secret mapping configuration
Maps GitHub Organization Secrets to internal key names
"""

GITHUB_TO_INTERNAL_MAPPING = {
    # AI Services
    "OPENAI_API_KEY": "openai_api_key",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "PORTKEY_API_KEY": "portkey_api_key",
    "OPENROUTER_API_KEY": "openrouter_api_key",
    "MEM0_API_KEY": "mem0_api_key",
    # Data Infrastructure
    "SNOWFLAKE_ACCOUNT": "snowflake_account",
    "SNOWFLAKE_USERNAME": "snowflake_user",
    "SNOWFLAKE_PASSWORD": "snowflake_password",
    "SNOWFLAKE_WAREHOUSE": "snowflake_warehouse",
    "SNOWFLAKE_DATABASE": "snowflake_database",
    "SNOWFLAKE_ROLE": "snowflake_role",
    "PINECONE_API_KEY": "pinecone_api_key",
    "PINECONE_ENVIRONMENT": "pinecone_environment",
    # Business Intelligence
    "GONG_ACCESS_KEY": "gong_access_key",
    "GONG_ACCESS_KEY_SECRET": "gong_access_key_secret",
    "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
    "LINEAR_API_KEY": "linear_api_key",
    "NOTION_API_TOKEN": "notion_api_token",
    # Infrastructure
    "LAMBDA_LABS_API_KEY": "lambda_labs_api_key",
    "DOCKER_TOKEN": "docker_token",
    "DOCKER_HUB_ACCESS_TOKEN": "docker_hub_access_token",
    # Communication
    "SLACK_BOT_TOKEN": "slack_bot_token",
    "SLACK_APP_TOKEN": "slack_app_token",
    "SLACK_SIGNING_SECRET": "slack_signing_secret",
}

# Backwards-compatibility alias: map old internal key to new canonical key
ALIAS_INTERNAL_MAPPING = {
    "lambda_api_key": "lambda_labs_api_key",
}


def get_internal_key(github_key: str) -> str:
    """Convert GitHub secret name to internal key name"""
    return GITHUB_TO_INTERNAL_MAPPING.get(github_key, github_key.lower())


def get_github_key(internal_key: str) -> str:
    """Convert internal key name to GitHub secret name"""
    for github_key, internal in GITHUB_TO_INTERNAL_MAPPING.items():
        if internal == internal_key:
            return github_key
    return ALIAS_INTERNAL_MAPPING.get(internal_key, internal_key.upper())
