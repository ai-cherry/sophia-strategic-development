import os

"""
Comprehensive Security Configuration for Sophia AI
Centralized secrets management with Pulumi ESC integration and best practices
"""

import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SecretType(Enum):
    """Types of secrets for proper categorization and handling"""

    API_KEY = "api_key"
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    JWT_SECRET = os.getenv("JWT_SECRET")
    OAUTH_TOKEN = "oauth_token"
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
    ENCRYPTION_KEY = "encryption_key"


@dataclass
class SecretConfig:
    """Configuration for a secret"""

    key: str
    secret_type: SecretType
    required: bool = True
    default: str | None = None
    description: str = ""
    rotation_enabled: bool = False
    rotation_days: int = 90


class SecurityConfig:
    """
    Centralized security configuration manager for Sophia AI
    Integrates with Pulumi ESC for secure secret management
    """

    # Define all secrets used across the platform
    SECRETS_REGISTRY: dict[str, SecretConfig] = {
        # AI/ML Service API Keys
        "openai_api_key": SecretConfig(
            key="openai_api_key",
            secret_type=SecretType.API_KEY,
            required=True,
            description="OpenAI API key for GPT models",
            rotation_enabled=True,
            rotation_days=90,
        ),
        "anthropic_api_key": SecretConfig(
            key="anthropic_api_key",
            secret_type=SecretType.API_KEY,
            required=True,
            description="Anthropic API key for Claude models",
            rotation_enabled=True,
            rotation_days=90,
        ),
        "pinecone_api_key": SecretConfig(
            key="pinecone_api_key",
            secret_type=SecretType.API_KEY,
            required=True,
            description="Pinecone API key for vector database",
            rotation_enabled=True,
            rotation_days=90,
        ),
        # Database Credentials
        "snowflake_password": SecretConfig(
            key="snowflake_password",
            secret_type=SecretType.DATABASE_PASSWORD,
            required=True,
            description="Snowflake database password/PAT",
            rotation_enabled=True,
            rotation_days=30,
        ),
        "redis_password": SecretConfig(
            key="redis_password",
            secret_type=SecretType.DATABASE_PASSWORD,
            required=False,
            description="Redis password for caching",
            rotation_enabled=True,
            rotation_days=60,
        ),
        # Business Integration API Keys
        "gong_access_key": SecretConfig(
            key="gong_access_key",
            secret_type=SecretType.API_KEY,
            required=False,
            description="Gong API access key for call analytics",
            rotation_enabled=True,
            rotation_days=90,
        ),
        "gong_client_secret": SecretConfig(
            key="gong_client_secret",
            secret_type=SecretType.API_KEY,
            required=False,
            description="Gong OAuth client secret",
            rotation_enabled=True,
            rotation_days=90,
        ),
        "hubspot_access_token": SecretConfig(
            key="hubspot_access_token",
            secret_type=SecretType.OAUTH_TOKEN,
            required=False,
            description="HubSpot API access token",
            rotation_enabled=True,
            rotation_days=60,
        ),
        "slack_bot_token": SecretConfig(
            key="slack_bot_token",
            secret_type=SecretType.OAUTH_TOKEN,
            required=False,
            description="Slack bot token for integrations",
            rotation_enabled=True,
            rotation_days=90,
        ),
        "slack_signing_secret": SecretConfig(
            key="slack_signing_secret",
            secret_type=SecretType.WEBHOOK_SECRET,
            required=False,
            description="Slack webhook signing secret",
            rotation_enabled=True,
            rotation_days=90,
        ),
        "asana_access_token": SecretConfig(
            key="asana_access_token",
            secret_type=SecretType.OAUTH_TOKEN,
            required=False,
            description="Asana API access token",
            rotation_enabled=True,
            rotation_days=90,
        ),
        # Application Security
        os.getenv("JWT_SECRET"): SecretConfig(
            key=os.getenv("JWT_SECRET"),
            secret_type=SecretType.JWT_SECRET,
            required=True,
            description="JWT signing secret for authentication",
            rotation_enabled=True,
            rotation_days=30,
        ),
        "encryption_key": SecretConfig(
            key="encryption_key",
            secret_type=SecretType.ENCRYPTION_KEY,
            required=True,
            description="Application-level encryption key",
            rotation_enabled=True,
            rotation_days=30,
        ),
        # GitHub Integration
        "github_token": SecretConfig(
            key="github_token",
            secret_type=SecretType.OAUTH_TOKEN,
            required=False,
            description="GitHub personal access token",
            rotation_enabled=True,
            rotation_days=90,
        ),
        "github_webhook_secret": SecretConfig(
            key="github_webhook_secret",
            secret_type=SecretType.WEBHOOK_SECRET,
            required=False,
            description="GitHub webhook secret for CI/CD",
            rotation_enabled=True,
            rotation_days=90,
        ),
        # Pulumi/Infrastructure
        "pulumi_access_token": SecretConfig(
            key="pulumi_access_token",
            secret_type=SecretType.OAUTH_TOKEN,
            required=True,
            description="Pulumi Cloud access token",
            rotation_enabled=True,
            rotation_days=60,
        ),
    }

    # Non-secret configuration values
    NON_SECRET_CONFIG: dict[str, str] = {
        # Snowflake Connection Details
        "snowflake_account": "ZNB04675.us-east-1",
        "snowflake_user": "SCOOBYJAVA15",
        "snowflake_role": "ACCOUNTADMIN",
        "snowflake_warehouse": "SOPHIA_AI_WH",
        "snowflake_database": "SOPHIA_AI",
        "snowflake_schema": "PROCESSED_AI",
        # Redis Configuration
        "redis_host": "localhost",
        "redis_port": "6379",
        "redis_db": "0",
        # Application Configuration
        "environment": "production",
        "log_level": "INFO",
        "debug": "false",
        # Service URLs
        "gong_base_url": "https://api.gong.io",
        "hubspot_api_base_url": "https://api.hubapi.com",
        "slack_api_base_url": "https://slack.com/api",
        "asana_api_base_url": "https://app.asana.com/api/1.0",
        # Pulumi Configuration
        "pulumi_org": "scoobyjava-org",
        "pulumi_project": "sophia-ai",
        "pulumi_stack": "production",
    }

    @classmethod
    def get_secret_keys(cls) -> list[str]:
        """Get list of all secret keys"""
        return list(cls.SECRETS_REGISTRY.keys())

    @classmethod
    def get_required_secrets(cls) -> list[str]:
        """Get list of required secret keys"""
        return [key for key, config in cls.SECRETS_REGISTRY.items() if config.required]

    @classmethod
    def get_secrets_by_type(cls, secret_type: SecretType) -> list[str]:
        """Get secrets by type"""
        return [
            key
            for key, config in cls.SECRETS_REGISTRY.items()
            if config.secret_type == secret_type
        ]

    @classmethod
    def get_rotatable_secrets(cls) -> list[str]:
        """Get secrets that support rotation"""
        return [
            key
            for key, config in cls.SECRETS_REGISTRY.items()
            if config.rotation_enabled
        ]

    @classmethod
    def validate_secret_key(cls, key: str) -> bool:
        """Validate if a key is a registered secret"""
        return key in cls.SECRETS_REGISTRY

    @classmethod
    def get_secret_config(cls, key: str) -> SecretConfig | None:
        """Get configuration for a specific secret"""
        return cls.SECRETS_REGISTRY.get(key)

    @classmethod
    def is_secret_required(cls, key: str) -> bool:
        """Check if a secret is required"""
        config = cls.get_secret_config(key)
        return config.required if config is not None else False

    @classmethod
    def get_non_secret_config(cls, key: str) -> str | None:
        """Get non-secret configuration value"""
        return cls.NON_SECRET_CONFIG.get(key)

    @classmethod
    def validate_environment_secrets(cls) -> dict[str, bool]:
        """Validate that all required secrets are available"""
        from backend.core.config_manager import get_config_value

        validation_results = {}
        for key, config in cls.SECRETS_REGISTRY.items():
            if config.required:
                value = get_config_value(key)
                validation_results[key] = value is not None and value != ""
            else:
                validation_results[key] = True  # Optional secrets always pass

        return validation_results

    @classmethod
    def get_missing_required_secrets(cls) -> list[str]:
        """Get list of missing required secrets"""
        validation_results = cls.validate_environment_secrets()
        return [key for key, is_valid in validation_results.items() if not is_valid]

    @classmethod
    def log_security_status(cls) -> None:
        """Log security configuration status"""
        logger.info("🔐 Security Configuration Status:")
        logger.info(f"   Total secrets registered: {len(cls.SECRETS_REGISTRY)}")
        logger.info(f"   Required secrets: {len(cls.get_required_secrets())}")
        logger.info(f"   Rotatable secrets: {len(cls.get_rotatable_secrets())}")

        missing_secrets = cls.get_missing_required_secrets()
        if missing_secrets:
            logger.error(f"❌ Missing required secrets: {missing_secrets}")
        else:
            logger.info("✅ All required secrets are available")

    @classmethod
    def generate_pulumi_esc_template(cls) -> str:
        """Generate a Pulumi ESC environment template"""
        template = """# Sophia AI Production Environment Template
# This template defines all secrets and configuration for Sophia AI

values:
  # AI/ML Service API Keys (SECRETS - Set via Pulumi ESC CLI)
"""

        # Add secrets by category
        categories = {
            SecretType.API_KEY: "API Keys",
            SecretType.DATABASE_PASSWORD: "Database Credentials",
            SecretType.OAUTH_TOKEN: "OAuth Tokens",
            SecretType.WEBHOOK_SECRET: "Webhook Secrets",
            SecretType.JWT_SECRET: "JWT Secrets",
            SecretType.ENCRYPTION_KEY: "Encryption Keys",
        }

        for secret_type, category_name in categories.items():
            secrets = cls.get_secrets_by_type(secret_type)
            if secrets:
                template += f"\n  # {category_name}\n"
                for secret_key in secrets:
                    config = cls.get_secret_config(secret_key)
                    template += f'  {secret_key}: ""\n'
                    if config is not None:
                        template += f"  # {config.description}\n"

        # Add non-secret configuration
        template += "\n  # Non-Secret Configuration\n"
        for key, value in cls.NON_SECRET_CONFIG.items():
            template += f'  {key}: "{value}"\n'

        # Add environment variables mapping
        template += "\n  # Environment Variables Mapping\n"
        template += "  environmentVariables:\n"
        for secret_key in cls.SECRETS_REGISTRY:
            template += f"    {secret_key.upper()}: ${{{secret_key}}}\n"

        for config_key in cls.NON_SECRET_CONFIG:
            template += f"    {config_key.upper()}: ${{{config_key}}}\n"

        return template


# Initialize security configuration on import
def initialize_security_config():
    """Initialize security configuration and log status"""
    SecurityConfig.log_security_status()


# Export commonly used functions
__all__ = ["SecurityConfig", "SecretType", "SecretConfig", "initialize_security_config"]
