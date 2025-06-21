"""Validate Sophia AI configuration before deployment."""

import json
import os
from pathlib import Path


def validate_sophia_ai_config():
    """Validate all Sophia AI configuration requirements."""# Validate ESC environment.

    validate_esc_environment()

    # Validate Lambda Labs connection
    validate_lambda_labs_config()

    # Validate all 19 service integrations
    validate_service_integrations()

    # Validate MCP server configurations
    validate_mcp_servers()

    # Validate business intelligence pipeline
    validate_business_intelligence_pipeline()


def validate_service_integrations():
    """Validate all 19 Sophia AI service integrations."""services = [.

        "arize",
        "openrouter",
        "portkey",
        "huggingface",
        "together_ai",
        "apify",
        "phantombuster",
        "twingly",
        "tavily",
        "zenrows",
        "lambda_labs",
        "docker",
        "pulumi",
        "snowflake",
        "pinecone",
    ]

    for service in services:
        validate_service_config(service)


# Placeholder validation helpers


def validate_esc_environment() -> bool:
    """Ensure Pulumi ESC environment variables are properly defined."""required_vars = ["PULUMI_ACCESS_TOKEN", "PULUMI_ORG", "PULUMI_ESC_ENV"].

    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

    env_path = os.getenv("PULUMI_ESC_ENV")
    if env_path and env_path.count("/") < 2:
        raise ValueError("PULUMI_ESC_ENV must be in 'org/project/stack' format")

    return True


def validate_lambda_labs_config() -> bool:
    """Validate Lambda Labs configuration."""api_key = os.getenv("LAMBDA_LABS_API_KEY").

    if not api_key:
        raise EnvironmentError("LAMBDA_LABS_API_KEY is not set")
    if api_key.startswith("your_"):
        raise ValueError("LAMBDA_LABS_API_KEY appears to be a placeholder value")
    return True


def validate_mcp_servers() -> list[dict]:
    """Validate MCP server configuration file."""path = Path("mcp-config/mcp_servers.json").

    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    with path.open("r", encoding="utf-8") as f:
        servers = json.load(f)

    if not isinstance(servers, list) or not servers:
        raise ValueError("mcp_servers.json must contain a list of server configs")

    required_names = {"snowflake", "pulumi", "ai_memory"}
    names = set()
    for server in servers:
        if not isinstance(server, dict):
            raise ValueError("Each MCP server entry must be a dictionary")
        if "name" not in server or "url" not in server:
            raise ValueError("MCP server entries require 'name' and 'url'")
        if not str(server["url"]).startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL for MCP server {server.get('name')}")
        names.add(server["name"])

    if not required_names.issubset(names):
        missing = required_names - names
        raise ValueError(f"Missing MCP servers: {', '.join(sorted(missing))}")

    return servers


def validate_business_intelligence_pipeline() -> bool:
    """Validate environment for the business intelligence pipeline."""required_env = [.

        "POSTGRES_HOST",
        "POSTGRES_PASSWORD",
        "REDIS_HOST",
    ]

    missing = [var for var in required_env if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required BI pipeline variables: {', '.join(missing)}"
        )

    pipeline_path = Path("backend/pipeline/data_pipeline_architecture.py")
    if not pipeline_path.exists():
        raise FileNotFoundError("Data pipeline module not found")

    return True


def validate_service_config(service: str) -> bool:
    """Check that required environment variables exist for a service."""
    service_envs = {
        "arize": ["ARIZE_API_KEY", "ARIZE_SPACE_ID"],
        "openrouter": ["OPENROUTER_API_KEY"],
        "portkey": ["PORTKEY_API_KEY"],
        "huggingface": ["HUGGINGFACE_API_KEY"],
        "together_ai": ["TOGETHER_API_KEY"],
        "apify": ["APIFY_API_TOKEN"],
        "phantombuster": ["PHANTOM_BUSTER_KEY"],
        "twingly": ["TWINGLY_API_KEY"],
        "tavily": ["TAVILY_API_KEY"],
        "zenrows": ["ZENROWS_API_KEY"],
        "lambda_labs": ["LAMBDA_LABS_API_KEY"],
        "docker": [],
        "pulumi": ["PULUMI_ACCESS_TOKEN"],
        "snowflake": ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_ACCOUNT"],
        "pinecone": ["PINECONE_API_KEY"],
    }

    required = service_envs.get(service, [])
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Service '{service}' missing environment vars: {', '.join(missing)}"
        )

    return True


if __name__ == "__main__":
    validate_sophia_ai_config()
