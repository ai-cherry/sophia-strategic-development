"""
Simple, Working Configuration System for Sophia AI
Replaces the broken enhanced_config.py with a bulletproof system.
"""

import json
import logging
import os
import subprocess
from datetime import UTC, datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SophiaConfig:
    """Simple, bulletproof configuration loader."""

    _instance: Optional["SophiaConfig"] = None
    _config: dict[str, Any] | None = None
    _last_loaded: datetime | None = None
    _cache_ttl: int = 300  # 5 minutes

    def __new__(cls) -> "SophiaConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._load_config()

    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed."""
        if self._last_loaded is None:
            return True

        now = datetime.now(UTC)
        elapsed = (now - self._last_loaded).total_seconds()
        return elapsed > self._cache_ttl

    def _load_config(self) -> None:
        """Load configuration from Pulumi ESC with fallback to environment variables."""
        logger.info("🔧 Loading Sophia AI configuration...")

        # Try Pulumi ESC first
        pulumi_config = self._load_from_pulumi_esc()
        if pulumi_config:
            self._config = self._flatten_config(pulumi_config)
            self._last_loaded = datetime.now(UTC)
            logger.info(
                f"✅ Loaded {len(self._config)} configuration values from Pulumi ESC"
            )
            return

        # Fallback to environment variables
        logger.warning("⚠️ Pulumi ESC unavailable, using environment variables")
        self._config = self._load_from_environment()
        logger.info(
            f"✅ Loaded {len(self._config)} configuration values from environment"
        )

    def _load_from_pulumi_esc(self) -> dict[str, Any] | None:
        """Load from Pulumi ESC."""
        token = os.getenv("PULUMI_ACCESS_TOKEN")
        if not token or not token.startswith("pul-"):
            logger.warning(
                "PULUMI_ACCESS_TOKEN is missing or invalid. Skipping Pulumi ESC."
            )
            return None

        try:
            org = os.getenv("PULUMI_ORG", "scoobyjava-org")
            stack = "sophia-ai-production"

            cmd = [
                "pulumi",
                "env",
                "open",
                f"{org}/default/{stack}",
                "--format",
                "json",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,  # Reduced timeout
                check=False,
            )

            if result.returncode == 0:
                config = json.loads(result.stdout)
                logger.debug(f"Successfully loaded from Pulumi ESC: {stack}")
                return config
            else:
                error_message = result.stderr.strip()
                logger.warning(f"Pulumi ESC command failed. Error: {error_message}")
                if "invalid access token" in error_message:
                    logger.error(
                        "CRITICAL: The Pulumi Access Token is invalid. Please run 'source scripts/fix_environment_permanently.sh'"
                    )
                return None

        except FileNotFoundError:
            logger.error(
                "Pulumi command not found. Please ensure Pulumi is installed and in your PATH."
            )
            return None
        except subprocess.TimeoutExpired:
            logger.warning(
                "Pulumi ESC command timed out. Check network connection and Pulumi status."
            )
            return None
        except Exception as e:
            logger.warning(
                f"An unexpected error occurred while loading from Pulumi ESC: {e}"
            )
            return None

    def _flatten_config(
        self, config: dict[str, Any], prefix: str = ""
    ) -> dict[str, Any]:
        """Flatten nested config for easy access."""
        flattened = {}

        for key, value in config.items():
            new_key = f"{prefix}_{key}" if prefix else key

            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                flattened.update(self._flatten_config(value, new_key))
            else:
                flattened[new_key] = value

        return flattened

    def _load_from_environment(self) -> dict[str, Any]:
        """Load from environment variables as fallback."""
        env_mappings = {
            # AI Services
            "values_sophia_ai_openai_api_key": "OPENAI_API_KEY",
            "values_sophia_ai_anthropic_api_key": "ANTHROPIC_API_KEY",
            # Business Intelligence
            "values_sophia_business_gong_access_key": "GONG_ACCESS_KEY",
            "values_sophia_business_gong_client_secret": "GONG_CLIENT_SECRET",
            # Data Infrastructure
            "values_sophia_data_pinecone_api_key": "PINECONE_API_KEY",
            # Communication
            "values_sophia_communication_slack_bot_token": "SLACK_BOT_TOKEN",
            # Development Tools
            "values_sophia_development_linear_api_key": "LINEAR_API_KEY",
            "values_sophia_development_notion_api_key": "NOTION_API_KEY",
            # Infrastructure
            "values_sophia_infrastructure_snowflake_account": "SNOWFLAKE_ACCOUNT",
            "values_sophia_infrastructure_snowflake_user": "SNOWFLAKE_USER",
            "values_sophia_infrastructure_snowflake_password": "SNOWFLAKE_PASSWORD",
        }

        fallback_config = {}
        for config_key, env_key in env_mappings.items():
            value = os.getenv(env_key)
            if value:
                fallback_config[config_key] = value

        return fallback_config

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with cache refresh logic."""
        if self._should_refresh_cache():
            self._load_config()

        if self._config is None:
            return default

        return self._config.get(key, default)

    def get_openai_api_key(self) -> str | None:
        """Get OpenAI API key."""
        return self.get("values_sophia_ai_openai_api_key")

    def get_anthropic_api_key(self) -> str | None:
        """Get Anthropic API key."""
        return self.get("values_sophia_ai_anthropic_api_key")

    def get_gong_access_key(self) -> str | None:
        """Get Gong access key."""
        return self.get("values_sophia_business_gong_access_key")

    def get_gong_client_secret(self) -> str | None:
        """Get Gong client secret."""
        return self.get("values_sophia_business_gong_client_secret")

    def get_pinecone_api_key(self) -> str | None:
        """Get Pinecone API key."""
        return self.get("values_sophia_data_pinecone_api_key")

    def get_snowflake_config(self) -> dict[str, Any]:
        """Get Snowflake configuration."""
        return {
            "account": self.get(
                "values_sophia_infrastructure_snowflake_account", "ZNB04675.us-east-1"
            ),
            "user": self.get(
                "values_sophia_infrastructure_snowflake_user", "SCOOBYJAVA15"
            ),
            "password": self.get("values_sophia_infrastructure_snowflake_password"),
            "role": "ACCOUNTADMIN",
            "warehouse": "AI_SOPHIA_AI_WH",
            "database": "SOPHIA_AI_ADVANCED",
            "schema": "PROCESSED_AI",
        }

    def get_all_config(self) -> dict[str, Any]:
        """Get all configuration for debugging."""
        if self._should_refresh_cache():
            self._load_config()
        return self._config or {}

    def validate_critical_secrets(self) -> dict[str, bool]:
        """Validate that critical secrets are available."""
        critical_keys = [
            "values_sophia_ai_openai_api_key",
            "values_sophia_business_gong_access_key",
            "values_sophia_data_pinecone_api_key",
            "values_sophia_ai_anthropic_api_key",
        ]

        validation_results = {}
        for key in critical_keys:
            value = self.get(key)
            validation_results[key] = bool(value and len(str(value)) > 10)

        return validation_results


# Global instance
config = SophiaConfig()


# Backward compatibility functions
def get_config_value(key: str, default: Any = None) -> Any:
    """Backward compatibility function."""
    return config.get(key, default)


def get_openai_api_key() -> str | None:
    """Get OpenAI API key."""
    return config.get_openai_api_key()


def get_gong_access_key() -> str | None:
    """Get Gong access key."""
    return config.get_gong_access_key()


def get_snowflake_config() -> dict[str, Any]:
    """Get Snowflake configuration."""
    return config.get_snowflake_config()


if __name__ == "__main__":
    # Test the configuration

    # Test critical secrets
    validation = config.validate_critical_secrets()
    for _key, valid in validation.items():
        status = "✅" if valid else "❌"
