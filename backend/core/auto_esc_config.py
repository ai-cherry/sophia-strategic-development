"""
Auto ESC Configuration Module for Sophia AI
Handles environment variable and configuration management with Pulumi ESC integration
Integrated with SecurityConfig for centralized secret management
"""

import logging
import os
import subprocess
from typing import Any

logger = logging.getLogger(__name__)

# Configuration cache
_config_cache: dict[str, Any] = {}
_esc_cache: dict[str, Any] | None = None


def _get_security_config():
    """Get SecurityConfig class (imported lazily to avoid circular imports)"""
    try:
        from backend.core.security_config import SecurityConfig

        return SecurityConfig
    except ImportError:
        logger.warning("SecurityConfig not available, using fallback mappings")
        return None


def _load_esc_environment() -> dict[str, Any]:
    """
    Load configuration from Pulumi ESC environment

    Returns:
        ESC environment configuration
    """
    global _esc_cache

    if _esc_cache is not None:
        return _esc_cache

    try:
        # Get the ESC environment using pulumi env get
        result = subprocess.run(
            ["pulumi", "env", "get", "scoobyjava-org/default/sophia-ai-production"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            # Parse the output to extract the values
            output_lines = result.stdout.strip().split("\n")
            esc_data = {}

            for line in output_lines:
                if ":" in line and not line.strip().startswith("#"):
                    # Parse key-value pairs
                    if "[secret]" in line:
                        # This is a secret, we'll need to get it differently
                        key = line.split(":")[0].strip()
                        esc_data[key] = "[secret]"
                    elif "data_infrastructure:" in line:
                        # Skip structural lines
                        continue
                    else:
                        try:
                            parts = line.split(":", 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip()
                                esc_data[key] = value
                        except Exception:
                            continue

            _esc_cache = esc_data
            logger.info(f"Loaded {len(esc_data)} configuration items from Pulumi ESC")
            return esc_data

    except subprocess.TimeoutExpired:
        logger.warning("Timeout loading Pulumi ESC environment")
    except FileNotFoundError:
        logger.warning("Pulumi CLI not found, using fallback configuration")
    except Exception as e:
        logger.warning(f"Failed to load Pulumi ESC environment: {e}")

    # Fallback to empty dict
    _esc_cache = {}
    return _esc_cache


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get configuration value from Pulumi ESC, environment variables, or cache

    Args:
        key: Configuration key
        default: Default value if key not found

    Returns:
        Configuration value
    """
    # Check cache first
    if key in _config_cache:
        return _config_cache[key]

    # Check environment variables first (highest priority)
    env_value = os.getenv(key.upper())
    if env_value is not None:
        _config_cache[key] = env_value
        return env_value

    # Check with original case
    env_value = os.getenv(key)
    if env_value is not None:
        _config_cache[key] = env_value
        return env_value

    # Try to load from Pulumi ESC
    esc_data = _load_esc_environment()

    # Enhanced key mappings for GitHub Organization Secrets compatibility
    # Updated June 30, 2025 to match GitHub → Pulumi ESC sync patterns
    esc_key_mappings = {
        # Core AI Services (working)
        "openai_api_key": "openai_api_key",
        "anthropic_api_key": "anthropic_api_key",
        "pinecone_api_key": "pinecone_api_key",
        "gong_access_key": "gong_access_key",
        # Gateway Services (missing - fixed by sync)
        "portkey_api_key": "portkey_api_key",
        "openrouter_api_key": "openrouter_api_key",
        # Business Intelligence (missing - fixed by sync)
        "hubspot_access_token": "hubspot_access_token",
        "linear_api_key": "linear_api_key",
        "asana_access_token": "asana_access_token",  # Note: GitHub has ASANA_API_TOKEN
        # Communication (missing - fixed by sync)
        "slack_bot_token": "slack_bot_token",
        "slack_app_token": "slack_app_token",
        "slack_client_id": "slack_client_id",
        "slack_client_secret": "slack_client_secret",
        "slack_signing_secret": "slack_signing_secret",
        # Development Tools (missing - fixed by sync)
        "github_token": "github_token",  # Note: GitHub has GH_API_TOKEN
        "figma_pat": "figma_pat",
        "notion_api_token": "notion_api_token",  # Note: GitHub has NOTION_API_KEY
        # Infrastructure (missing - fixed by sync)
        "lambda_api_key": "lambda_api_key",
        "lambda_ip_address": "lambda_ip_address",
        "lambda_ssh_private_key": "lambda_ssh_private_key",
        # Snowflake (working)
        "snowflake_account": "snowflake_account",
        "snowflake_user": "snowflake_user",
        "snowflake_password": "snowflake_password",
        "snowflake_role": "snowflake_role",
        "snowflake_warehouse": "snowflake_warehouse",
        "snowflake_database": "snowflake_database",
        "snowflake_schema": "snowflake_schema",
        # Additional mappings for comprehensive coverage
        "codacy_api_token": "codacy_api_token",
        "estuary_access_token": "estuary_access_token",
        "vercel_access_token": "vercel_access_token",
        "docker_token": "docker_token",
        "npm_api_token": "npm_api_token",
    }

    # Use mapped key or original key
    esc_key = esc_key_mappings.get(key, key)

    # Get key mappings from SecurityConfig if available
    security_config = _get_security_config()
    if security_config:
        # Use SecurityConfig for key validation and mapping
        if (
            not security_config.validate_secret_key(key)
            and key not in security_config.NON_SECRET_CONFIG
        ):
            # Check if this is a known non-secret config key
            pass

    # Try to get from ESC using mapped key (handle quoted keys)
    quoted_esc_key = f'"{esc_key}"'

    # Check both quoted and unquoted versions
    esc_value = esc_data.get(esc_key) or esc_data.get(quoted_esc_key)

    if esc_value and esc_value != "[secret]":
        _config_cache[key] = esc_value
        return esc_value

    # For secrets, try to get them directly from ESC with --show-secrets
    if esc_value == "[secret]":
        try:
            # Get secret value directly using --show-secrets
            result = subprocess.run(
                [
                    "pulumi",
                    "env",
                    "get",
                    "scoobyjava-org/default/sophia-ai-production",
                    "--show-secrets",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                # Parse the JSON output to get the secret value
                import json

                try:
                    esc_secrets = json.loads(result.stdout)
                    if esc_key in esc_secrets:
                        secret_value = esc_secrets[esc_key]
                        _config_cache[key] = secret_value
                        return secret_value
                except json.JSONDecodeError:
                    # Fallback to line-by-line parsing
                    for line in result.stdout.split("\n"):
                        if f'"{esc_key}":' in line and "PLACEHOLDER" not in line:
                            try:
                                # Extract the value from the JSON line
                                value_part = line.split(":", 1)[1].strip()
                                if value_part.endswith(","):
                                    value_part = value_part[:-1]
                                secret_value = value_part.strip('"')
                                _config_cache[key] = secret_value
                                return secret_value
                            except Exception:
                                continue
        except Exception as e:
            logger.debug(f"Failed to get secret {esc_key}: {e}")

    # Return default
    _config_cache[key] = default
    return default


def set_config_value(key: str, value: Any) -> None:
    """
    Set configuration value in cache

    Args:
        key: Configuration key
        value: Configuration value
    """
    _config_cache[key] = value


def get_snowflake_config() -> dict[str, Any]:
    """
    Get Snowflake configuration from Pulumi ESC - PERMANENT FIX

    Returns:
        Snowflake configuration dictionary with CORRECT account
    """
    return {
        "account": get_config_value(
            "snowflake_account", "ZNB04675"
        ),  # PERMANENT FIX: Correct account
        "user": get_config_value("snowflake_user", "SCOOBYJAVA15"),
        "password": get_config_value("snowflake_password"),  # Will load PAT from ESC
        "role": get_config_value("snowflake_role", "ACCOUNTADMIN"),
        "warehouse": get_config_value(
            "snowflake_warehouse", "SOPHIA_AI_WH"
        ),  # PERMANENT FIX: Correct warehouse
        "database": get_config_value(
            "snowflake_database", "SOPHIA_AI"
        ),  # PERMANENT FIX: Correct database
        "schema": get_config_value("snowflake_schema", "PROCESSED_AI"),
    }


def get_estuary_config() -> dict[str, Any]:
    """
    Get Estuary configuration

    Returns:
        Estuary configuration dictionary
    """
    return {
        "access_token": get_config_value("estuary_access_token"),
        "tenant": get_config_value("estuary_tenant", "Pay_Ready"),
        "endpoint": get_config_value("estuary_endpoint", "https://api.estuary.dev"),
    }


def get_integration_config() -> dict[str, Any]:
    """
    Get integration configuration for external services

    Returns:
        Integration configuration dictionary
    """
    return {
        "gong": {
            "access_key": get_config_value("gong_access_key"),
            "access_key_secret": get_config_value("gong_access_key_secret"),
            "endpoint": get_config_value("gong_endpoint", "https://api.gong.io"),
        },
        "slack": {
            "bot_token": get_config_value("slack_bot_token"),
            "app_token": get_config_value("slack_app_token"),
            "signing_secret": get_config_value("slack_signing_secret"),
        },
        "hubspot": {
            "access_token": get_config_value("hubspot_access_token"),
            "portal_id": get_config_value("hubspot_portal_id"),
            "endpoint": get_config_value("hubspot_endpoint", "https://api.hubapi.com"),
        },
        "intercom": {
            "access_token": get_config_value("intercom_access_token"),
            "app_id": get_config_value("intercom_app_id"),
            "endpoint": get_config_value(
                "intercom_endpoint", "https://api.intercom.io"
            ),
        },
    }


def initialize_default_config():
    """Initialize default configuration values"""

    # Try to load from Pulumi ESC first
    logger.info("Loading configuration from Pulumi ESC...")

    # Load ESC environment to populate cache
    _load_esc_environment()

    # Set fallback defaults only if not available from ESC
    if not get_config_value("snowflake_account"):
        set_config_value("snowflake_account", "ZNB04675")  # Fixed: Use correct account
    if not get_config_value("snowflake_user"):
        set_config_value("snowflake_user", "SCOOBYJAVA15")
    if not get_config_value("snowflake_role"):
        set_config_value("snowflake_role", "ACCOUNTADMIN")
    if not get_config_value("snowflake_warehouse"):
        set_config_value("snowflake_warehouse", "AI_COMPUTE_WH")
    if not get_config_value("snowflake_database"):
        set_config_value("snowflake_database", "SOPHIA_AI_ADVANCED")
    if not get_config_value("snowflake_schema"):
        set_config_value("snowflake_schema", "PROCESSED_AI")

    # Estuary defaults
    if not get_config_value("estuary_tenant"):
        set_config_value("estuary_tenant", "Pay_Ready")
    if not get_config_value("estuary_endpoint"):
        set_config_value("estuary_endpoint", "https://api.estuary.dev")

    # JWT defaults
    if not get_config_value("jwt_secret"):
        set_config_value("jwt_secret", "sophia-ai-cortex-secret-key-2025")
    if not get_config_value("jwt_algorithm"):
        set_config_value("jwt_algorithm", "HS256")
    if not get_config_value("jwt_expiration_hours"):
        set_config_value("jwt_expiration_hours", "24")

    logger.info("Configuration initialized with Pulumi ESC integration")


# Initialize defaults on import
initialize_default_config()


def get_lambda_labs_config() -> dict[str, Any]:
    """
    Get Lambda Labs configuration from Pulumi ESC

    Returns:
        Lambda Labs configuration dictionary
    """
    return {
        "api_key": get_config_value("lambda_api_key")
        or get_config_value("LAMBDA_API_KEY"),
        "ip_address": get_config_value("lambda_ip_address")
        or get_config_value("LAMBDA_IP_ADDRESS"),
        "ssh_private_key": get_config_value("lambda_ssh_private_key")
        or get_config_value("LAMBDA_SSH_PRIVATE_KEY"),
    }


# Backward compatibility - create a config object that mimics the old interface
class ConfigObject:
    """Backward compatibility object for legacy config access patterns"""

    def get(self, key: str, default: Any = None) -> Any:
        """Dictionary-style get method for backward compatibility"""
        return get_config_value(key, default)

    def __getitem__(self, key: str) -> Any:
        """Dictionary-style access for backward compatibility"""
        return get_config_value(key)

    def __getattr__(self, name):
        return get_config_value(name)

    @property
    def redis_url(self):
        return get_config_value("redis_url", "redis://localhost:6379")

    @property
    def gong_api_base_url(self):
        return get_config_value("gong_api_base_url", "https://api.gong.io")

    @property
    def hubspot_api_base_url(self):
        return get_config_value("hubspot_api_base_url", "https://api.hubapi.com")

    @property
    def slack_webhook_url(self):
        return get_config_value("slack_webhook_url", "")

    @property
    def linear_api_base_url(self):
        return get_config_value("linear_api_base_url", "https://api.linear.app")

    @property
    def github_webhook_url(self):
        return get_config_value("github_webhook_url", "")

    @property
    def costar_api_base_url(self):
        return get_config_value("costar_api_base_url", "")

    @property
    def apollo_api_base_url(self):
        return get_config_value("apollo_api_base_url", "https://api.apollo.io")


# Create backward compatibility config object
config = ConfigObject()


# Enhanced Snowflake connection optimization
SNOWFLAKE_OPTIMIZATION_CONFIG = {
    "connection_pool_size": 10,
    "connection_timeout": 30,
    "query_timeout": 300,
    "retry_attempts": 3,
    "auto_commit": True,
    "warehouse_auto_suspend": 60,
    "warehouse_auto_resume": True,
}
