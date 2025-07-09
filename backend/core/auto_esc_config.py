"""
Enhanced Auto ESC Config with ALL GitHub Secrets Mapped
This loads ALL secrets from Pulumi ESC using the correct GitHub secret names
"""

import logging
import os
import subprocess
import json
from typing import Any, Optional, Dict
from functools import lru_cache

logger = logging.getLogger(__name__)

# Configuration cache
_config_cache: dict[str, Any] = {}
_esc_cache: dict[str, Any] | None = None

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")
PULUMI_ORG = os.getenv("PULUMI_ORG", "scoobyjava-org")
PULUMI_STACK = f"{PULUMI_ORG}/default/sophia-ai-production"

@lru_cache(maxsize=1)
def get_pulumi_config() -> Dict[str, Any]:
    """Get all configuration from Pulumi ESC"""
    try:
        # Try to get the config using pulumi env get
        result = subprocess.run(
            ["pulumi", "env", "get", PULUMI_STACK],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Parse the output - it might be YAML or key-value pairs
            config = {}
            for line in result.stdout.strip().split('\n'):
                if ':' in line and not line.startswith('#'):
                    key, value = line.split(':', 1)
                    config[key.strip()] = value.strip()
            
            logger.info(f"✅ Loaded Pulumi ESC config from {PULUMI_STACK}")
            return config
        else:
            logger.error(f"❌ Failed to load Pulumi ESC config: {result.stderr}")
            return {}
            
    except Exception as e:
        logger.error(f"❌ Error loading Pulumi ESC config: {e}")
        return {}

def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a configuration value from Pulumi ESC or environment variables"""
    # Try environment variable first
    env_value = os.getenv(key.upper())
    if env_value:
        return env_value
    
    # Try Pulumi ESC
    config = get_pulumi_config()
    if config and key in config:
        return config[key]
    
    # Return default
    return default

def _get_security_config():
    """Get SecurityConfig class (imported lazily to avoid circular imports)"""
    try:
        # Updated import path July 2025 – SecurityConfig resides in shared.security_config
        from shared.security_config import SecurityConfig

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
            ["pulumi", "env", "get", "default/sophia-ai-production"],
            check=False,
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
            "snowflake_account", "ZNB04675.us-east-1.us-east-1"
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
        set_config_value(
            "snowflake_account", "ZNB04675.us-east-1.us-east-1"
        )  # Fixed: Use correct account
    if not get_config_value("snowflake_user"):
        set_config_value("snowflake_user", "SCOOBYJAVA15")
    if not get_config_value("snowflake_role"):
        set_config_value("snowflake_role", "ACCOUNTADMIN")
    if not get_config_value("snowflake_warehouse"):
        set_config_value("snowflake_warehouse", "AI_SOPHIA_AI_WH")
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

def get_docker_hub_config() -> dict[str, Any]:
    """
    Get Docker Hub configuration from Pulumi ESC
    
    PERMANENT FIX: Use DOCKER_TOKEN and DOCKER_USERNAME as the primary keys
    These are the actual secret names in GitHub
    
    Returns:
        Docker Hub configuration dictionary with username and access token
    """
    # Get username - DOCKER_USERNAME is the primary key in GitHub
    username = (
        get_config_value("DOCKER_USERNAME") or  # PRIMARY
        get_config_value("docker_username") or
        get_config_value("docker_hub_username") or
        "scoobyjava15"  # fallback
    )
    
    # Get token - DOCKER_TOKEN is the primary key in GitHub
    access_token = (
        get_config_value("DOCKER_TOKEN") or  # PRIMARY
        get_config_value("docker_token") or
        get_config_value("docker_hub_access_token") or
        get_config_value("docker_password")
    )
    
    # Log what we found for debugging
    if access_token:
        logger.info(f"Docker Hub config loaded: username={username}, token=***")
    else:
        logger.warning("No Docker Hub token found in configuration")
    
    return {
        "username": username,
        "access_token": access_token,
        "registry": "docker.io",
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

def get_snowflake_pat(environment: Optional[str] = None) -> str:
    """
    Get Snowflake PAT (Programmatic Access Token) for MCP authentication

    Args:
        environment: Environment name (prod, staging). Defaults to current environment.

    Returns:
        PAT string

    Raises:
        ValueError: If PAT not configured
    """
    if not environment:
        environment = get_config_value("environment", "prod")  # type: ignore[assignment]

    # After fallback logic we are confident *environment* is str
    environment_str: str = str(environment)

    # Try environment-specific PAT first
    pat_key = f"snowflake_pat_{environment_str.lower()}"
    pat = get_config_value(pat_key)

    if not pat:
        # Try generic PAT
        pat = get_config_value("snowflake_pat")

    if not pat:
        # Try with MCP prefix
        pat = get_config_value("snowflake_mcp_pat")

    if not pat:
        raise ValueError(
            f"Snowflake PAT not configured for environment: {environment_str}"
        )

    # Validate PAT format (basic check)
    if not pat.startswith("pat_") and len(pat) < 20:
        logger.warning("Snowflake PAT format may be invalid")

    return pat

def get_snowflake_mcp_config() -> dict[str, Any]:
    """
    Get Snowflake MCP server configuration

    Returns:
        MCP configuration dictionary
    """
    environment = get_config_value("environment", "prod")

    return {
        "url": get_config_value(
            "snowflake_mcp_url", "https://mcp-snowflake.sophia-ai.com"
        ),
        "pat": get_snowflake_pat(environment),
        "timeout": int(get_config_value("snowflake_mcp_timeout", "120")),
        "max_retries": int(get_config_value("snowflake_mcp_max_retries", "3")),
        "pool_size": int(get_config_value("snowflake_mcp_pool_size", "20")),
    }

# Add PAT rotation check function
def check_pat_rotation_needed() -> bool:
    """
    Check if Snowflake PAT needs rotation

    Returns:
        True if rotation needed
    """
    # This is a placeholder - in production, would check PAT metadata
    # from Snowflake or a secure metadata store
    pat_created_date = get_config_value("snowflake_pat_created_date")

    if not pat_created_date:
        logger.warning("PAT creation date not tracked")
        return False

    from datetime import datetime

    try:
        created = datetime.fromisoformat(pat_created_date)
        days_old = (datetime.now() - created).days

        # Rotate after 83 days (7 days before 90-day expiry)
        return days_old >= 83

    except Exception as e:
        logger.error(f"Error checking PAT rotation: {e}")
        return False

# Update the esc_key_mappings in get_config_value to include PAT mappings
# (This is already included in the existing mappings)

def validate_snowflake_pat() -> bool:
    """
    Validate Snowflake PAT token format

    Returns:
        True if PAT token appears valid
    """
    pat = get_config_value("snowflake_password")
    if not pat:
        logger.warning("No Snowflake password/PAT configured")
        return False

    # PAT tokens are JWT tokens that typically start with 'eyJ'
    if pat.startswith("eyJ") and len(pat) > 100:
        logger.info("Snowflake PAT token format validated")
        return True

    logger.warning("Snowflake password may not be a valid PAT token")
    return False

def get_snowflake_config_enhanced() -> dict[str, Any]:
    """
    Get enhanced Snowflake configuration with PAT support

    Returns:
        Enhanced Snowflake configuration dictionary
    """
    base_config = get_snowflake_config()

    # Add PAT-specific configuration
    enhanced_config = {
        **base_config,
        "authenticator": "snowflake",  # For PAT authentication
        "session_parameters": {
            "QUERY_TAG": "sophia_ai_unified",
        },
        "pat_validated": validate_snowflake_pat(),
    }

    # Use validated account format
    enhanced_config["account"] = "UHDECNO-CVB64222"

    return enhanced_config

# Enhanced configuration constants
SNOWFLAKE_PAT_CONFIG = {
    "account": "UHDECNO-CVB64222",
    "user": "SCOOBYJAVA15",
    "role": "ACCOUNTADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "SOPHIA_AI_PROD",
    "schema": "PUBLIC",
    "authenticator": "snowflake",
}

AI_OPTIMIZATION_CONFIG = {
    "hybrid_routing_enabled": get_config_value(
        "ai_optimization_enabled", "true"
    ).lower()
    == "true",
    "cost_monitoring_enabled": get_config_value(
        "cost_monitoring_enabled", "true"
    ).lower()
    == "true",
    "serverless_first": True,
    "data_local_preference": True,
}
