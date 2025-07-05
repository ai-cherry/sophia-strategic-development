import pulumi

# Configuration
config = pulumi.Config()
env = config.get("environment") or "prod"

# Tags
tags = {
    "Project": "sophia-ai",
    "Environment": env,
    "ManagedBy": "pulumi",
    "CostCenter": "ai-platform",
}

# Lambda Labs Integration
lambda_labs_config = {
    "api_key": config.require_secret("lambda_labs_api_key"),
    "instances": [
        {"name": "sophia-mcp-gateway", "type": "gpu_1x_a10"},
        {"name": "sophia-ai-memory", "type": "gpu_1x_a10"},
        {"name": "sophia-orchestrator", "type": "gpu_2x_a10"},
    ],
}

# Snowflake Configuration
snowflake_config = {
    "account": config.require("snowflake_account"),
    "user": config.require("snowflake_user"),
    "password": config.require_secret("snowflake_password"),
    "warehouses": {
        "compute": "SOPHIA_AI_COMPUTE_WH",
        "analytics": "SOPHIA_AI_ANALYTICS_WH",
    },
}

# Export configurations
pulumi.export("lambda_labs_config", lambda_labs_config)
pulumi.export("snowflake_config", snowflake_config)
pulumi.export("environment", env)
