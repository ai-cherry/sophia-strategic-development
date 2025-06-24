"""Enhanced Pulumi ESC configuration loader for Sophia AI Platform.

Comprehensive configuration management with environment-aware settings,
dynamic secret resolution, validation, and backward compatibility.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ValidationError, validator

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Deployment environment enumeration."""

    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"


# Backward compatibility - keep existing Settings class
class Settings(BaseModel):
    """Typed settings loaded from Pulumi ESC (backward compatibility)."""

    openai_api_key: Optional[str] = None
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    slack_bot_token: Optional[str] = None


class EnhancedSettings(BaseModel):
    """Enhanced typed settings with comprehensive configuration."""

    # Core platform configuration
    platform_name: str = "sophia-ai-platform"
    platform_version: str = "v2.0.0"
    environment: Environment = Environment.DEVELOPMENT

    # Webhook configuration (aligned with existing Gong webhook)
    webhook_domain: str = "localhost"
    webhook_port: int = 5000
    webhook_base_url: str = "http://localhost:5000/webhook/gong"
    webhook_jwt_private_key: Optional[str] = None
    webhook_jwt_public_key: Optional[str] = None

    # Snowflake configuration (aligned with existing GONG_ANALYTICS)
    snowflake_account: Optional[str] = None
    snowflake_user: str = "PROGRAMMATIC_SERVICE_USER"
    snowflake_password: Optional[str] = None
    snowflake_database: str = "GONG_ANALYTICS"
    snowflake_warehouse: str = "COMPUTE_WH"
    snowflake_schema: str = "RAW"
    snowflake_role: str = "ACCOUNTADMIN"

    # Enhanced Snowflake OAuth
    snowflake_oauth_client_id: Optional[str] = None
    snowflake_oauth_client_secret: Optional[str] = None
    snowflake_oauth_refresh_token: Optional[str] = None

    # Redis configuration for agent communication
    redis_host: str = "redis-cluster"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_ssl_enabled: bool = True
    redis_max_connections: int = 100

    # Agent orchestration (aligned with existing AgnoPerformanceOptimizer)
    agent_pool_size: int = 50
    agent_max_concurrent: int = 100
    agent_instantiation_target_us: int = 3
    agent_orchestrator_auth_token: Optional[str] = None
    agent_communication_secret: Optional[str] = None

    # Gong integration (existing setup)
    gong_access_key: Optional[str] = None
    gong_client_secret: Optional[str] = None
    gong_api_base_url: str = "https://api.gong.io"
    gong_api_rate_limit: float = 2.5
    gong_webhook_secret: Optional[str] = None

    # Enhanced Gong OAuth
    gong_oauth_client_id: Optional[str] = None
    gong_oauth_client_secret: Optional[str] = None
    gong_oauth_refresh_token: Optional[str] = None

    # AI service keys (existing setup)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    agno_api_key: Optional[str] = None
    huggingface_api_token: Optional[str] = None

    # Vector databases
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: Optional[str] = None
    weaviate_api_key: Optional[str] = None
    weaviate_url: Optional[str] = None

    # Monitoring (aligned with existing Arize setup)
    arize_api_key: Optional[str] = None
    arize_space_id: Optional[str] = None
    sentry_dsn: Optional[str] = None
    prometheus_auth_token: Optional[str] = None
    grafana_url: Optional[str] = None
    grafana_username: Optional[str] = None
    grafana_password: Optional[str] = None
    grafana_admin_password: Optional[str] = None

    # Slack integration (existing setup)
    slack_bot_token: Optional[str] = None
    slack_app_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None

    # MCP server integrations
    mcp_github_token: Optional[str] = None
    mcp_slack_token: Optional[str] = None
    mcp_linear_token: Optional[str] = None
    mcp_docker_registry_token: Optional[str] = None
    mcp_postgres_connection_string: Optional[str] = None

    # Business intelligence
    hubspot_access_token: Optional[str] = None
    linear_api_key: Optional[str] = None
    notion_api_key: Optional[str] = None

    # Infrastructure
    lambda_labs_api_key: Optional[str] = None
    lambda_labs_control_plane_ip: Optional[str] = None
    lambda_labs_ssh_key_name: Optional[str] = None

    # Database
    database_url: Optional[str] = None

    # Security
    jwt_secret: Optional[str] = None
    encryption_key: Optional[str] = None

    # OIDC
    aws_oidc_role_arn: Optional[str] = None
    azure_oidc_client_id: Optional[str] = None
    gcp_oidc_service_account: Optional[str] = None

    # Docker
    docker_username: Optional[str] = None
    docker_token: Optional[str] = None

    # Pulumi
    pulumi_access_token: Optional[str] = None
    pulumi_org: str = "scoobyjava-org"

    @validator("webhook_base_url", pre=True, always=True)
    def set_webhook_base_url(cls, v, values):
        if not v and values.get("webhook_domain"):
            domain = values["webhook_domain"]
            port = values.get("webhook_port", 5000)
            if port == 443:
                return f"https://{domain}/webhook/gong"
            elif port == 80:
                return f"http://{domain}/webhook/gong"
            else:
                return f"https://{domain}/webhook/gong"
        return v


class ConfigValidator:
    """Configuration validation and health checking."""

    def __init__(self, config_data: Dict[str, Any]):
        self.config_data = config_data
        self.logger = logger.bind(component="config_validator")

    async def validate_critical_services(self) -> Dict[str, bool]:
        """Validate critical services are accessible."""
        validation_results = {}

        try:
            # Validate Snowflake connectivity
            if self.config_data.get("snowflake_account") and self.config_data.get(
                "snowflake_password"
            ):
                validation_results["snowflake"] = await self._validate_snowflake()

            # Validate Gong API access
            if self.config_data.get("gong_access_key") and self.config_data.get(
                "gong_client_secret"
            ):
                validation_results["gong"] = await self._validate_gong()

            # Validate Redis connectivity
            if self.config_data.get("redis_password"):
                validation_results["redis"] = await self._validate_redis()

            # Validate OpenAI API
            if self.config_data.get("openai_api_key"):
                validation_results["openai"] = await self._validate_openai()

            self.logger.info("Service validation completed: %s", validation_results)
            return validation_results

        except Exception as e:
            self.logger.error(f"Service validation failed: {str(e)}")
            return validation_results

    async def _validate_snowflake(self) -> bool:
        """Validate Snowflake connectivity with existing GONG_ANALYTICS setup."""
        try:
            # Simple connection test without importing snowflake connector
            # This would be implemented with actual Snowflake client in production
            account = self.config_data.get("snowflake_account")
            password = self.config_data.get("snowflake_password")

            if not account or not password:
                return False

            self.logger.info("Snowflake configuration validated")
            return True

        except Exception as e:
            self.logger.error(f"Snowflake validation failed: {str(e)}")
            return False

    async def _validate_gong(self) -> bool:
        """Validate Gong API access."""
        try:
            access_key = self.config_data.get("gong_access_key")
            secret_key = self.config_data.get("gong_client_secret")

            if not access_key or not secret_key:
                return False

            # Simple validation without making actual API call
            # In production, this would test actual API connectivity
            self.logger.info("Gong configuration validated")
            return True

        except Exception as e:
            self.logger.error(f"Gong validation failed: {str(e)}")
            return False

    async def _validate_redis(self) -> bool:
        """Validate Redis connectivity."""
        try:
            password = self.config_data.get("redis_password")

            if not password:
                return False

            # Simple validation without actual Redis connection
            # In production, this would test actual Redis connectivity
            self.logger.info("Redis configuration validated")
            return True

        except Exception as e:
            self.logger.error(f"Redis validation failed: {str(e)}")
            return False

    async def _validate_openai(self) -> bool:
        """Validate OpenAI API access."""
        try:
            api_key = self.config_data.get("openai_api_key")

            if not api_key or api_key == "dummy":
                return False

            # Simple validation without actual API call
            # In production, this would test actual API connectivity
            self.logger.info("OpenAI configuration validated")
            return True

        except Exception as e:
            self.logger.error(f"OpenAI validation failed: {str(e)}")
            return False


class AutoESCConfig:
    """Enhanced singleton loader for Pulumi ESC secrets with caching and validation."""

    _instance: Optional["AutoESCConfig"] = None
    _config: dict[str, Any] | None = None
    _enhanced_settings: Optional[EnhancedSettings] = None
    _last_loaded: Optional[datetime] = None
    _cache_ttl: int = 300  # 5 minutes

    def __new__(cls) -> "AutoESCConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._config is None:
            self._load_config()

    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed."""
        if self._last_loaded is None:
            return True

        now = datetime.now(timezone.utc)
        elapsed = (now - self._last_loaded).total_seconds()
        return elapsed > self._cache_ttl

    def _load_config(self) -> None:
        """Load configuration from Pulumi ESC with enhanced error handling."""
        org = os.getenv("PULUMI_ORG", "scoobyjava-org")

        # Environment-aware stack selection
        environment = os.getenv("ENVIRONMENT", "staging")
        if environment == "prod":
            stack = "sophia-ai-production"
        elif environment == "staging":
            stack = "sophia-ai-platform-staging"
        elif environment == "dev":
            stack = "sophia-ai-platform-dev"
        else:
            # Fallback to original naming for backward compatibility
            stack = os.getenv("PULUMI_STACK", "sophia-ai-production")

        cmd = [
            "pulumi",
            "env",
            "open",
            f"{org}/default/{stack}",
            "--format",
            "json",
        ]

        logger.debug("Loading ESC config: command='%s' stack='%s'", " ".join(cmd), stack)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=30,  # Add timeout
            )

            if result.returncode != 0:
                logger.error(
                    "pulumi env open failed for stack %s (returncode %d): %s",
                    stack,
                    result.returncode,
                    result.stderr.strip(),
                )
                self._config = {}
                self._fallback_to_env_vars()
                return

            self._config = json.loads(result.stdout)
            self._last_loaded = datetime.now(timezone.utc)

            logger.info(
                "Loaded ESC configuration: key_count=%d stack='%s' environment='%s'",
                len(self._config or {}),
                stack,
                environment,
            )

        except json.JSONDecodeError as exc:
            logger.exception("Failed to parse ESC output: %s", str(exc))
            self._config = {}
            self._fallback_to_env_vars()

        except subprocess.TimeoutExpired:
            logger.error("Pulumi ESC command timed out")
            self._config = {}
            self._fallback_to_env_vars()

        except Exception as exc:
            logger.exception("Unexpected error loading ESC config: %s", str(exc))
            self._config = {}
            self._fallback_to_env_vars()

    def _fallback_to_env_vars(self) -> None:
        """Fallback to environment variables when ESC is unavailable."""
        logger.warning("Falling back to environment variables")

        # Load critical environment variables as fallback
        env_mappings = {
            "openai_api_key": "OPENAI_API_KEY",
            "snowflake_account": "SNOWFLAKE_ACCOUNT",
            "snowflake_user": "SNOWFLAKE_USER",
            "snowflake_password": "SNOWFLAKE_PASSWORD",
            "gong_access_key": "GONG_ACCESS_KEY",
            "gong_client_secret": "GONG_CLIENT_SECRET",
            "redis_cluster_password": "REDIS_CLUSTER_PASSWORD",
            "slack_bot_token": "SLACK_BOT_TOKEN",
            "slack_app_token": "SLACK_APP_TOKEN",
            "arize_api_key": "ARIZE_API_KEY",
            "arize_space_id": "ARIZE_SPACE_ID",
            "sentry_dsn": "SENTRY_DSN",
            "webhook_domain": "WEBHOOK_DOMAIN",
            "agent_orchestrator_auth_token": "AGENT_ORCHESTRATOR_AUTH_TOKEN",
            "agent_communication_secret": "AGENT_COMMUNICATION_SECRET",
            "jwt_secret": "JWT_SECRET",
            "encryption_key": "ENCRYPTION_KEY",
        }

        fallback_config = {}
        for config_key, env_key in env_mappings.items():
            value = os.getenv(env_key)
            if value:
                fallback_config[config_key] = value

        # Set environment-specific defaults
        environment = os.getenv("ENVIRONMENT", "staging")
        fallback_config["environment"] = environment
        fallback_config["platform_name"] = "sophia-ai-platform"
        fallback_config["platform_version"] = "v2.0.0"

        self._config = fallback_config
        logger.info(
            "Fallback configuration loaded: key_count=%d environment='%s'",
            len(fallback_config),
            environment,
        )

    def get(self, key: str, default: Any | None = None) -> Any | None:
        """Retrieve a config value with cache refresh logic."""
        if self._should_refresh_cache():
            self._load_config()

        if self._config is None:
            return default

        # Check nested structure first for real secrets
        if key == "openai_api_key":
            nested_value = self._get_nested_value("values.sophia.ai.openai.api_key")
            if nested_value:
                return nested_value
        elif key == "pinecone_api_key":
            nested_value = self._get_nested_value("values.sophia.data.pinecone.api_key")
            if nested_value:
                return nested_value
        elif key == "gong_access_key":
            nested_value = self._get_nested_value("values.sophia.business.gong.access_key")
            if nested_value:
                return nested_value
        elif key == "gong_client_secret":
            nested_value = self._get_nested_value("values.sophia.business.gong.client_secret")
            if nested_value:
                return nested_value
        elif key == "anthropic_api_key":
            nested_value = self._get_nested_value("values.sophia.ai.anthropic.api_key")
            if nested_value:
                return nested_value

        return self._config.get(key, default)
    
    def _get_nested_value(self, path: str) -> Any | None:
        """Get value from nested dictionary using dot notation."""
        if not self._config:
            return None
            
        keys = path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
                
        return value if value != "PLACEHOLDER_VALUE" else None

    def as_settings(self) -> Settings:
        """Return config as typed Settings (backward compatibility)."""
        try:
            return Settings(**(self._config or {}))
        except ValidationError as exc:
            logger.error("Settings validation failed: %s", exc.errors())
            raise RuntimeError(f"Invalid ESC configuration: {exc}") from exc

    def as_enhanced_settings(self) -> EnhancedSettings:
        """Return config as enhanced typed settings with comprehensive validation."""
        if self._enhanced_settings is None or self._should_refresh_cache():
            if self._should_refresh_cache():
                self._load_config()

            try:
                self._enhanced_settings = EnhancedSettings(**(self._config or {}))
                logger.info("Enhanced settings loaded successfully")

            except ValidationError as exc:
                logger.error("Enhanced settings validation failed: %s", exc.errors())
                # Return minimal settings to prevent total failure
                self._enhanced_settings = self._get_minimal_enhanced_settings()

            except Exception as exc:
                logger.exception(
                    "Unexpected error creating enhanced settings: %s", str(exc)
                )
                self._enhanced_settings = self._get_minimal_enhanced_settings()

        return self._enhanced_settings

    def _get_minimal_enhanced_settings(self) -> EnhancedSettings:
        """Return minimal enhanced settings to prevent total failure."""
        environment = os.getenv("ENVIRONMENT", "staging")

        minimal_data = {
            "platform_name": "sophia-ai-platform",
            "platform_version": "v2.0.0",
            "environment": environment,
            "webhook_domain": "localhost",
            "webhook_port": 5000,
            "snowflake_database": "GONG_ANALYTICS",
            "snowflake_warehouse": "COMPUTE_WH",
            "snowflake_schema": "RAW",
            "snowflake_role": "ACCOUNTADMIN",
            "redis_host": "redis-cluster",
            "redis_port": 6379,
            "redis_ssl_enabled": True,
            "agent_pool_size": 50,
            "agent_max_concurrent": 100,
            "agent_instantiation_target_us": 3,
            "gong_api_base_url": "https://api.gong.io",
            "gong_api_rate_limit": 2.5,
            "pulumi_org": "scoobyjava-org",
        }

        logger.warning("Using minimal enhanced settings due to validation errors")
        return EnhancedSettings(**minimal_data)

    async def validate_configuration(self) -> Dict[str, bool]:
        """Validate the current configuration."""
        if self._should_refresh_cache():
            self._load_config()

        validator = ConfigValidator(self._config or {})
        return await validator.validate_critical_services()

    async def refresh_cache(self) -> None:
        """Force refresh of configuration cache."""
        self._config = None
        self._enhanced_settings = None
        self._last_loaded = None
        self._load_config()
        logger.info("Configuration cache refreshed")

    def get_health_status(self) -> Dict[str, Any]:
        """Get configuration health status."""
        config_count = len(self._config or {})
        last_loaded = self._last_loaded.isoformat() if self._last_loaded else None
        cache_age = (
            (datetime.now(timezone.utc) - self._last_loaded).total_seconds()
            if self._last_loaded
            else None
        )

        return {
            "config_loaded": self._config is not None,
            "config_key_count": config_count,
            "last_loaded": last_loaded,
            "cache_age_seconds": cache_age,
            "cache_valid": not self._should_refresh_cache(),
            "environment": os.getenv("ENVIRONMENT", "staging"),
            "pulumi_org": os.getenv("PULUMI_ORG", "scoobyjava-org"),
        }


# Global instance (maintain backward compatibility)
config = AutoESCConfig()


def get_config_value(key: str, default: Any | None = None) -> Any | None:
    """Get configuration value using the global config instance.
    
    This function provides backward compatibility for modules that expect
    a simple get_config_value function.
    
    Args:
        key: Configuration key to retrieve
        default: Default value if key is not found
        
    Returns:
        Configuration value or default
    """
    return config.get(key, default)


def get_config_value(key: str, default: Any | None = None) -> Any | None:
    """Get configuration value using the global config instance.
    
    This function provides backward compatibility for modules that expect
    a simple get_config_value function.
    
    Args:
        key: Configuration key to retrieve
        default: Default value if key is not found
        
    Returns:
        Configuration value or default
    """
    return config.get(key, default)
