"""
Centralized Configuration Manager

Phase 1 Critical Stability Implementation:
- Unified configuration loading across all services
- Environment-specific configuration management
- Fallback configuration strategies
- Configuration validation and health checking
- Eliminates the 5 different configuration patterns identified in technical debt analysis
"""

import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConfigurationSource(Enum):
    """Configuration source priority order"""

    PULUMI_ESC = "pulumi_esc"
    ENVIRONMENT_VARS = "environment_vars"
    CONFIG_FILE = "config_file"
    DEFAULTS = "defaults"


@dataclass
class ConfigurationEntry:
    """Configuration entry with metadata"""

    key: str
    value: Any
    source: ConfigurationSource
    required: bool = False
    sensitive: bool = False
    description: str = ""


@dataclass
class ConfigurationReport:
    """Configuration validation report"""

    total_configs: int
    loaded_configs: int
    missing_required: list[str]
    configuration_health: str
    sources_used: list[str]
    warnings: list[str]
    errors: list[str]


class CentralizedConfigManager:
    """
    Centralized configuration manager for Sophia AI

    Addresses technical debt by:
    - Eliminating 5 different configuration patterns
    - Providing unified configuration interface
    - Supporting multiple configuration sources with fallback
    - Validating configuration completeness
    - Centralizing environment-specific logic
    """

    def __init__(self, environment: str | None = None):
        self.environment = environment or os.getenv("ENVIRONMENT", "dev")
        self.config_cache: dict[str, ConfigurationEntry] = {}
        self.config_sources = [
            ConfigurationSource.PULUMI_ESC,
            ConfigurationSource.ENVIRONMENT_VARS,
            ConfigurationSource.CONFIG_FILE,
            ConfigurationSource.DEFAULTS,
        ]

        # Configuration schema
        self.config_schema = self._initialize_config_schema()

        # Load configurations
        self._load_all_configurations()

    def _initialize_config_schema(self) -> dict[str, dict[str, Any]]:
        """Initialize the configuration schema with all known config keys"""
        return {
            # AI Services
            "openai_api_key": {
                "required": True,
                "sensitive": True,
                "description": "OpenAI API key for LLM operations",
                "env_vars": ["OPENAI_API_KEY"],
                "default": None,
            },
            "anthropic_api_key": {
                "required": False,
                "sensitive": True,
                "description": "Anthropic API key for Claude operations",
                "env_vars": ["ANTHROPIC_API_KEY"],
                "default": None,
            },
            "openrouter_api_key": {
                "required": False,
                "sensitive": True,
                "description": "OpenRouter API key for model routing",
                "env_vars": ["OPENROUTER_API_KEY"],
                "default": None,
            },
            # Data Services
            "pinecone_api_key": {
                "required": False,
                "sensitive": True,
                "description": "Pinecone API key for vector database",
                "env_vars": ["PINECONE_API_KEY"],
                "default": None,
            },
            "pinecone_environment": {
                "required": False,
                "sensitive": False,
                "description": "Pinecone environment",
                "env_vars": ["PINECONE_ENVIRONMENT"],
                "default": "us-east-1-aws",
            },
            # Snowflake Configuration
            "snowflake_account": {
                "required": False,
                "sensitive": False,
                "description": "Snowflake account identifier",
                "env_vars": ["SNOWFLAKE_ACCOUNT"],
                "default": None,
            },
            "snowflake_user": {
                "required": False,
                "sensitive": False,
                "description": "Snowflake username",
                "env_vars": ["SNOWFLAKE_USER"],
                "default": None,
            },
            "snowflake_password": {
                "required": False,
                "sensitive": True,
                "description": "Snowflake password",
                "env_vars": ["SNOWFLAKE_PASSWORD"],
                "default": None,
            },
            "snowflake_warehouse": {
                "required": False,
                "sensitive": False,
                "description": "Snowflake warehouse",
                "env_vars": ["SNOWFLAKE_WAREHOUSE"],
                "default": "COMPUTE_WH",
            },
            "snowflake_database": {
                "required": False,
                "sensitive": False,
                "description": "Snowflake database",
                "env_vars": ["SNOWFLAKE_DATABASE"],
                "default": "SOPHIA_AI",
            },
            "snowflake_schema": {
                "required": False,
                "sensitive": False,
                "description": "Snowflake schema",
                "env_vars": ["SNOWFLAKE_SCHEMA"],
                "default": "PUBLIC",
            },
            # Business Integration Services
            "gong_access_key": {
                "required": False,
                "sensitive": True,
                "description": "Gong API access key",
                "env_vars": ["GONG_ACCESS_KEY", "GONG_API_KEY"],
                "default": None,
            },
            "hubspot_access_token": {
                "required": False,
                "sensitive": True,
                "description": "HubSpot access token",
                "env_vars": ["HUBSPOT_ACCESS_TOKEN"],
                "default": None,
            },
            "slack_bot_token": {
                "required": False,
                "sensitive": True,
                "description": "Slack bot token",
                "env_vars": ["SLACK_BOT_TOKEN"],
                "default": None,
            },
            "linear_api_key": {
                "required": False,
                "sensitive": True,
                "description": "Linear API key",
                "env_vars": ["LINEAR_API_KEY"],
                "default": None,
            },
            # Infrastructure Services
            "portkey_api_key": {
                "required": False,
                "sensitive": True,
                "description": "Portkey API key for LLM gateway",
                "env_vars": ["PORTKEY_API_KEY"],
                "default": None,
            },
            "estuary_server_url": {
                "required": False,
                "sensitive": False,
                "description": "Estuary server URL",
                "env_vars": ["ESTUARY_SERVER_URL"],
                "default": "http://localhost:8000",
            },
            # Environment Configuration
            "environment": {
                "required": True,
                "sensitive": False,
                "description": "Application environment",
                "env_vars": ["ENVIRONMENT", "SOPHIA_ENVIRONMENT"],
                "default": "dev",
            },
            "log_level": {
                "required": False,
                "sensitive": False,
                "description": "Logging level",
                "env_vars": ["LOG_LEVEL"],
                "default": "INFO",
            },
        }

    def _load_all_configurations(self):
        """Load configurations from all sources"""
        logger.info(f"🔧 Loading configurations for {self.environment} environment...")

        for config_key, schema in self.config_schema.items():
            value = self._load_config_value(config_key, schema)

            if value is not None:
                self.config_cache[config_key] = ConfigurationEntry(
                    key=config_key,
                    value=value,
                    source=self._determine_source(config_key, schema),
                    required=schema.get("required", False),
                    sensitive=schema.get("sensitive", False),
                    description=schema.get("description", ""),
                )

        logger.info(f"✅ Loaded {len(self.config_cache)} configurations")

    def _load_config_value(self, config_key: str, schema: dict[str, Any]) -> Any:
        """Load configuration value from available sources"""
        # Try Pulumi ESC first (if available)
        try:
            from backend.core.auto_esc_config import get_config_value

            value = get_config_value(config_key)
            if value:
                return value
        except Exception:
            pass

        # Try environment variables
        for env_var in schema.get("env_vars", []):
            value = os.getenv(env_var)
            if value:
                return value

        # Try config file
        value = self._load_from_config_file(config_key)
        if value:
            return value

        # Use default
        return schema.get("default")

    def _determine_source(
        self, config_key: str, schema: dict[str, Any]
    ) -> ConfigurationSource:
        """Determine which source provided the configuration"""
        # Check Pulumi ESC
        try:
            from backend.core.auto_esc_config import get_config_value

            value = get_config_value(config_key)
            if value:
                return ConfigurationSource.PULUMI_ESC
        except Exception:
            pass

        # Check environment variables
        for env_var in schema.get("env_vars", []):
            if os.getenv(env_var):
                return ConfigurationSource.ENVIRONMENT_VARS

        # Check config file
        if self._load_from_config_file(config_key):
            return ConfigurationSource.CONFIG_FILE

        return ConfigurationSource.DEFAULTS

    def _load_from_config_file(self, config_key: str) -> str | None:
        """Load configuration from config file"""
        config_file = Path(f"config/environments/{self.environment}.json")

        if config_file.exists():
            try:
                with open(config_file) as f:
                    config_data = json.load(f)
                    return config_data.get(config_key)
            except Exception as e:
                logger.debug(f"Error loading config file: {e}")

        return None

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        entry = self.config_cache.get(key)
        if entry:
            return entry.value
        return default

    def get_config_entry(self, key: str) -> ConfigurationEntry | None:
        """Get full configuration entry with metadata"""
        return self.config_cache.get(key)

    def is_configured(self, key: str) -> bool:
        """Check if a configuration key is configured"""
        entry = self.config_cache.get(key)
        return entry is not None and entry.value is not None

    def get_configured_services(self) -> list[str]:
        """Get list of services that are properly configured"""
        services = []

        service_mappings = {
            "OpenAI": "openai_api_key",
            "Anthropic": "anthropic_api_key",
            "Gong": "gong_access_key",
            "HubSpot": "hubspot_access_token",
            "Slack": "slack_bot_token",
            "Linear": "linear_api_key",
            "Pinecone": "pinecone_api_key",
            "Snowflake": "snowflake_account",
            "Portkey": "portkey_api_key",
        }

        for service_name, config_key in service_mappings.items():
            if self.is_configured(config_key):
                services.append(service_name)

        return services

    def validate_configuration(self) -> ConfigurationReport:
        """Validate configuration completeness and health"""
        missing_required = []
        warnings = []
        errors = []
        sources_used = set()

        for config_key, schema in self.config_schema.items():
            entry = self.config_cache.get(config_key)

            if schema.get("required", False) and (not entry or entry.value is None):
                missing_required.append(config_key)
                errors.append(f"Required configuration missing: {config_key}")

            if entry:
                sources_used.add(entry.source.value)

        # Determine overall health
        if missing_required:
            health = "critical"
        elif len(self.config_cache) < 5:
            health = "degraded"
        else:
            health = "healthy"

        # Add warnings for common issues
        if ConfigurationSource.PULUMI_ESC.value not in sources_used:
            warnings.append("Pulumi ESC not available - using fallback configuration")

        if not self.is_configured("openai_api_key") and not self.is_configured(
            "anthropic_api_key"
        ):
            warnings.append("No AI service configured - limited functionality")

        return ConfigurationReport(
            total_configs=len(self.config_schema),
            loaded_configs=len(self.config_cache),
            missing_required=missing_required,
            configuration_health=health,
            sources_used=list(sources_used),
            warnings=warnings,
            errors=errors,
        )

    def get_configuration_summary(self) -> dict[str, Any]:
        """Get configuration summary for health checks"""
        configured_services = self.get_configured_services()
        validation_report = self.validate_configuration()

        return {
            "environment": self.environment,
            "total_configurations": len(self.config_schema),
            "loaded_configurations": len(self.config_cache),
            "configured_services": configured_services,
            "configuration_health": validation_report.configuration_health,
            "sources_used": validation_report.sources_used,
            "warnings_count": len(validation_report.warnings),
            "errors_count": len(validation_report.errors),
        }


# Global configuration manager instance
_config_manager: CentralizedConfigManager | None = None


def get_config_manager() -> CentralizedConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = CentralizedConfigManager()
    return _config_manager


def get_config(key: str, default: Any = None) -> Any:
    """Convenience function to get configuration value"""
    return get_config_manager().get_config(key, default)


def is_configured(key: str) -> bool:
    """Convenience function to check if configuration is available"""
    return get_config_manager().is_configured(key)


def get_configured_services() -> list[str]:
    """Convenience function to get list of configured services"""
    return get_config_manager().get_configured_services()


def validate_configuration() -> ConfigurationReport:
    """Convenience function to validate configuration"""
    return get_config_manager().validate_configuration()


def get_configuration_summary() -> dict[str, Any]:
    """Convenience function to get configuration summary"""
    return get_config_manager().get_configuration_summary()
