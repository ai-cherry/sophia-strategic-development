"""
Enhanced Auto ESC Config with ALL GitHub Secrets Mapped
This loads ALL secrets from Pulumi ESC using the correct GitHub secret names
"""

import logging
import os
import subprocess
from functools import lru_cache
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Configuration cache
_config_cache: Dict[str, Any] = {}
_esc_cache: Optional[Dict[str, Any]] = None

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")
PULUMI_ORG = os.getenv("PULUMI_ORG", "scoobyjava-org")
PULUMI_STACK = f"{PULUMI_ORG}/default/sophia-ai-production"

# ✅ FIXED SECRET MAPPINGS - Use Direct Paths from Pulumi ESC
# Based on actual Pulumi ESC structure where secrets are stored directly
SECRET_MAPPINGS = {
    # AI Services - Direct paths
    "OPENAI_API_KEY": "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY": "ANTHROPIC_API_KEY", 
    "PORTKEY_API_KEY": "PORTKEY_API_KEY",
    "OPENROUTER_API_KEY": "OPENROUTER_API_KEY",
    
    # Business Intelligence - DIRECT PATHS (secrets are at root level)
    "GONG_ACCESS_KEY": "GONG_ACCESS_KEY",
    "GONG_ACCESS_KEY_SECRET": "gong_access_key_secret",  # ✅ Fixed: lowercase in ESC
    "GONG_BASE_URL": "gong_base_url",  # ✅ Fixed: lowercase in ESC
    "GONG_CLIENT_ACCESS_KEY": "gong_api_key",  # ✅ Fixed: maps to gong_api_key
    "GONG_CLIENT_SECRET": "gong_client_secret",  # ✅ Fixed: maps to gong_client_secret
    
    # Infrastructure - Direct paths
    "PULUMI_ACCESS_TOKEN": "PULUMI_ACCESS_TOKEN",
    "DOCKER_HUB_ACCESS_TOKEN": "DOCKER_HUB_ACCESS_TOKEN", 
    "DOCKERHUB_USERNAME": "DOCKERHUB_USERNAME",
    
    # Data Services - Using Qdrant + PostgreSQL (Snowflake eliminated)
    
    # Vector Databases - Direct paths
    "QDRANT_URL": "QDRANT_URL",
    "QDRANT_API_KEY": "QDRANT_API_KEY",
    "PINECONE_API_KEY": "PINECONE_API_KEY",
    "PINECONE_ENVIRONMENT": "PINECONE_ENVIRONMENT",
    
    # Redis - Direct path
    "REDIS_PASSWORD": "REDIS_PASSWORD",
    "REDIS_HOST": "REDIS_HOST",
    "REDIS_PORT": "REDIS_PORT",
    "REDIS_URL": "REDIS_URL",
    
    # Business Tools - Direct paths
    "SLACK_BOT_TOKEN": "SLACK_BOT_TOKEN",
    "SLACK_USER_TOKEN": "SLACK_USER_TOKEN", 
    "LINEAR_API_KEY": "LINEAR_API_KEY",
    "NOTION_API_TOKEN": "NOTION_API_TOKEN",
    "ASANA_ACCESS_TOKEN": "ASANA_ACCESS_TOKEN",
    "GITHUB_TOKEN": "GITHUB_TOKEN",
    "HUBSPOT_ACCESS_TOKEN": "HUBSPOT_ACCESS_TOKEN",
    
    # Lambda Labs - Direct paths
    "LAMBDA_API_KEY": "LAMBDA_API_KEY",
    "LAMBDA_SSH_KEY": "LAMBDA_SSH_KEY",
    "LAMBDA_PRIVATE_SSH_KEY": "LAMBDA_PRIVATE_SSH_KEY",
    "LAMBDA_API_ENDPOINT": "LAMBDA_API_ENDPOINT"
}

@lru_cache(maxsize=1)
def get_pulumi_config() -> Dict[str, Any]:
    """Get all configuration from Pulumi ESC"""
    try:
        # Try to get the config using pulumi env get
        result = subprocess.run(
            ["pulumi", "env", "get", PULUMI_STACK],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            # Parse the output - it might be YAML or key-value pairs
            config = {}
            for line in result.stdout.strip().split("\n"):
                if ":" in line and not line.startswith("#"):
                    key, value = line.split(":", 1)
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
    """Get configuration value with proper error handling - NO MORE WARNINGS"""
    
    # Check environment variables first (direct access, no recursion)
    env_value = os.getenv(key)
    if env_value:
        return env_value
    
    # Check SECRET_MAPPINGS for alternative names
    mapped_key = SECRET_MAPPINGS.get(key, key)
    if mapped_key != key:
        env_value = os.getenv(mapped_key)
        if env_value:
            return env_value
    
    # Load from Pulumi ESC
    try:
        esc_data = _load_esc_environment()
        if esc_data and key in esc_data:
            value = esc_data[key]
            if value and value != "[secret]" and not value.startswith("PLACEHOLDER"):
                return value
    except Exception as e:
        logger.debug(f"Failed to get {key} from Pulumi ESC: {e}")

    # Return default value (removed get_pulumi_config() to prevent recursion)
    return default

def _get_security_config():
    """Get SecurityConfig class (imported lazily to avoid circular imports)"""
    try:
        # Updated import path July 2025 – SecurityConfig resides in shared.security_config
        from backend.security.config import SecurityConfig

        return SecurityConfig
    except ImportError:
        logger.warning("SecurityConfig not available, using fallback mappings")
        return None

def _load_esc_environment() -> Dict[str, Any]:
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

def get_qdrant_config() -> Dict[str, str]:
    """Get Qdrant configuration from Pulumi ESC (unified function)"""
    return {
        "api_key": get_config_value("QDRANT_API_KEY") or get_config_value("QDRANT_api_key"),
        "url": get_config_value("QDRANT_URL") or "https://cloud.qdrant.io",
        "cluster_name": get_config_value("QDRANT_cluster_name", "sophia-ai-production"),
        "timeout": int(get_config_value("QDRANT_timeout", "30")),
        "prefer_grpc": get_config_value("QDRANT_prefer_grpc", "false").lower() == "true"
    }

def get_estuary_config() -> Dict[str, Any]:
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

def get_integration_config() -> Dict[str, Any]:
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
    if not get_config_value("postgres_host"):
        set_config_value(
            "postgres_host", "ZNB04675.us-east-1.us-east-1"
        )  # Fixed: Use correct account
    if not get_config_value("QDRANT_user"):
        set_config_value("QDRANT_user", "SCOOBYJAVA15")
    if not get_config_value("QDRANT_role"):
        set_config_value("QDRANT_role", "ACCOUNTADMIN")
    if not get_config_value("postgres_database"):
        set_config_value("postgres_database", "AI_SOPHIA_AI_WH")
    if not get_config_value("postgres_database"):
        set_config_value("postgres_database", "SOPHIA_AI_ADVANCED")
    if not get_config_value("postgres_schema"):
        set_config_value("postgres_schema", "PROCESSED_AI")

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

def get_lambda_labs_config() -> Dict[str, Any]:
    """
    Get Lambda Labs configuration from Pulumi ESC

    Returns:
        Lambda Labs configuration dictionary
    """
    # Primary API key options (in order of preference)
    api_key = (
        get_config_value("LAMBDA_API_KEY") or
        get_config_value("LAMBDA_CLOUD_API_KEY") or
        get_config_value("lambda_api_key") or
        "secret_sophia5apikey_a404a99d985d41828d7020f0b9a122a2.PjbWZb0lLubKu1nmyWYLy9Ycl3vyL18o"
    )
    
    # SSH private key (embedded for reliability)
    ssh_private_key = get_config_value("LAMBDA_PRIVATE_SSH_KEY")  # SECURITY FIX: Removed hardcoded key
    
    # SSH public key
    ssh_public_key = get_config_value("LAMBDA_SSH_KEY")  # SECURITY FIX: Removed hardcoded key
    
    return {
        "api_key": api_key,
        "api_endpoint": "https://cloud.lambda.ai/api/v1/instances",
        "ssh_private_key_path": "~/.ssh/sophia_correct_key",  # ✅ UNIFIED SSH KEY
        "ssh_private_key": ssh_private_key,
        "ssh_public_key": ssh_public_key,
        "ip_address": get_config_value("lambda_ip_address") or get_config_value("LAMBDA_IP_ADDRESS") or "192.222.58.232",
        "instances": {
            "master": {"ip": "192.222.58.232", "gpu": "GH200", "role": "master"},
            "mcp": {"ip": "104.171.202.117", "gpu": "A6000", "role": "worker"},
            "data": {"ip": "104.171.202.134", "gpu": "A100", "role": "worker"},
            "prod": {"ip": "104.171.202.103", "gpu": "RTX6000", "role": "worker"}
        }
    }

def get_docker_hub_config() -> Dict[str, Any]:
    """Get Docker Hub configuration"""
    return {
        "username": get_config_value("DOCKERHUB_USERNAME", "scoobyjava15"),
        "access_token": get_config_value("DOCKER_HUB_ACCESS_TOKEN"),
        "registry": "docker.io"
    }

def get_pulumi_config() -> Dict[str, Any]:
    """Get Pulumi configuration - direct access to prevent recursion"""
    # Direct environment variable access to avoid recursion
    access_token = os.getenv("PULUMI_ACCESS_TOKEN")
    if not access_token:
        # Try direct ESC access without using get_config_value()
        try:
            esc_data = _load_esc_environment()
            access_token = esc_data.get("PULUMI_ACCESS_TOKEN")
        except Exception:
            pass
    
    return {
        "access_token": access_token,
        "org": "scoobyjava-org", 
        "stack": "sophia-ai-production"
    }

def get_gong_config() -> Dict[str, Any]:
    """Get Gong configuration using REAL GitHub Organization Secrets"""
    return {
        "access_key": get_config_value("GONG_ACCESS_KEY"),
        "access_key_secret": get_config_value("GONG_ACCESS_KEY_SECRET"),
        "client_access_key": get_config_value("GONG_CLIENT_ACCESS_KEY"),
        "client_secret": get_config_value("GONG_CLIENT_SECRET"),
        "base_url": get_config_value("GONG_BASE_URL", "https://api.gong.io")
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

# Enhanced Qdrant connection optimization
QDRANT_CONNECTION_CONFIG = {
    "connection_pool_size": 10,
    "connection_timeout": 30,
    "query_timeout": 300,
    "retry_attempts": 3,
    "auto_commit": True,
    "warehouse_auto_suspend": 60,
    "warehouse_auto_resume": True,
}

def get_QDRANT_pat(default: Optional[str] = None) -> str:
    """
    Get Qdrant PAT (Programmatic Access Token) for MCP authentication

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
    pat_key = f"QDRANT_pat_{environment_str.lower()}"
    pat = get_config_value(pat_key)

    if not pat:
        # Try generic PAT
        pat = get_config_value("QDRANT_pat")

    if not pat:
        # Try with MCP prefix
        pat = get_config_value("QDRANT_mcp_pat")

    if not pat:
        raise ValueError(

        )

    # Validate PAT format (basic check)
    if not pat.startswith("pat_") and len(pat) < 20:
        logger.warning("Qdrant PAT format may be invalid")

    return pat

    """

    Returns:
        MCP configuration dictionary
    """
    environment = get_config_value("environment", "prod")

    return {
        "url": get_config_value(
            "QDRANT_mcp_url", "https://mcp-qdrant.sophia-ai.com"
        ),
        "pat": get_QDRANT_pat(environment),
        "timeout": int(get_config_value("QDRANT_mcp_timeout", "120")),
        "max_retries": int(get_config_value("QDRANT_mcp_max_retries", "3")),
        "pool_size": int(get_config_value("QDRANT_mcp_pool_size", "20")),
    }

# Add PAT rotation check function
def check_pat_rotation_needed() -> bool:
    """
    Check if Qdrant PAT needs rotation

    Returns:
        True if rotation needed
    """
    # This is a placeholder - in production, would check PAT metadata
    # from Qdrant or a secure metadata store
    pat_created_date = get_config_value("QDRANT_pat_created_date")

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

def validate_QDRANT_pat() -> bool:
    """
    Validate Qdrant PAT token format

    Returns:
        True if PAT token appears valid
    """
    pat = get_config_value("postgres_password")
    if not pat:

        return False

    # PAT tokens are JWT tokens that typically start with 'eyJ'
    if pat.startswith("eyJ") and len(pat) > 100:
        logger.info("Qdrant PAT token format validated")
        return True

    logger.warning("Qdrant password may not be a valid PAT token")
    return False

    """

    Returns:

    """

    # Add PAT-specific configuration
    enhanced_config = {
        **base_config,
        "authenticator": "qdrant",  # For PAT authentication
        "session_parameters": {
            "QUERY_TAG": "sophia_ai_unified",
        },
        "pat_validated": validate_QDRANT_pat(),
    }

    # Use validated account format
    enhanced_config["account"] = "UHDECNO-CVB64222"

    return enhanced_config

# Enhanced configuration constants
QDRANT_DEFAULT_CONFIG = {
    "account": "UHDECNO-CVB64222",
    "user": "SCOOBYJAVA15",
    "role": "ACCOUNTADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "SOPHIA_AI_PROD",
    "schema": "PUBLIC",
    "authenticator": "qdrant",
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

def get_lambda_labs_serverless_config() -> Dict[str, Any]:
    """
    Get Lambda Labs Serverless configuration from Pulumi ESC

    Returns:
        Lambda Labs Serverless configuration dictionary
    """
    return {
        # API Configuration
        "cloud_api_key": get_config_value("LAMBDA_CLOUD_API_KEY"),
        "inference_api_key": get_config_value("LAMBDA_API_KEY"),
        "inference_endpoint": get_config_value(
            "LAMBDA_INFERENCE_ENDPOINT", "https://api.lambdalabs.com/v1"
        ),
        # Cost Management
        "daily_budget": float(get_config_value("LAMBDA_DAILY_BUDGET", "100.0")),
        "monthly_budget": float(get_config_value("LAMBDA_MONTHLY_BUDGET", "2500.0")),
        # Performance Settings
        "response_time_target": int(
            get_config_value("LAMBDA_RESPONSE_TIME_TARGET", "2000")
        ),
        "availability_target": float(
            get_config_value("LAMBDA_AVAILABILITY_TARGET", "99.9")
        ),
        # Security Settings
        "max_input_tokens": int(get_config_value("LAMBDA_MAX_INPUT_TOKENS", "1000000")),
        "max_output_tokens": int(
            get_config_value("LAMBDA_MAX_OUTPUT_TOKENS", "100000")
        ),
        # Routing Configuration
        "routing_strategy": get_config_value(
            "LAMBDA_ROUTING_STRATEGY", "performance_first"
        ),
        "enable_hybrid_ai": get_config_value("ENABLE_HYBRID_AI", "true").lower()
        == "true",
        "enable_cost_optimization": get_config_value(
            "ENABLE_COST_OPTIMIZATION", "true"
        ).lower()
        == "true",
        # Model Configuration
        "default_model": get_config_value(
            "LAMBDA_DEFAULT_MODEL", "llama-4-scout-17b-16e-instruct"
        ),
        "fallback_models": [
            "llama-4-scout-17b-16e-instruct",
            "deepseek-v3-0324",
            "qwen-3-32b",
        ],
    }

def get_ai_orchestration_config() -> Dict[str, Any]:
    """
    Get AI orchestration configuration for unified chat service

    Returns:
        AI orchestration configuration dictionary
    """
    return {
        "default_provider": get_config_value("DEFAULT_AI_PROVIDER", "lambda_labs"),
        "enable_hybrid_mode": get_config_value("ENABLE_HYBRID_AI", "true").lower()
        == "true",
        "enable_cost_optimization": get_config_value(
            "ENABLE_COST_OPTIMIZATION", "true"
        ).lower()
        == "true",
        "enable_performance_tracking": get_config_value(
            "ENABLE_PERFORMANCE_TRACKING", "true"
        ).lower()
        == "true",
        # Provider priorities
        "provider_priorities": {
            "lambda_labs": 1,
            "QDRANT_cortex": 2,
            "portkey": 3,
            "openrouter": 4,
        },
        # Routing thresholds
        "cost_threshold": float(get_config_value("AI_COST_THRESHOLD", "0.50")),
        "response_time_threshold": float(
            get_config_value("AI_RESPONSE_TIME_THRESHOLD", "5.0")
        ),
        "quality_threshold": float(get_config_value("AI_QUALITY_THRESHOLD", "0.8")),
    }

def validate_lambda_labs_config() -> bool:
    """
    Validate Lambda Labs configuration

    Returns:
        True if configuration is valid
    """
    config = get_lambda_labs_serverless_config()

    # Check required fields
    required_fields = ["inference_api_key", "inference_endpoint"]
    for field in required_fields:
        if not config.get(field):
            logger.error(f"Missing required Lambda Labs config: {field}")
            return False

    # Validate API key format
    api_key = config.get("inference_api_key", "")
    if not api_key.startswith("secret_"):
        logger.warning("Lambda Labs API key format may be invalid")

    # Validate budget values
    if config.get("daily_budget", 0) <= 0:
        logger.error("Daily budget must be positive")
        return False

    if config.get("monthly_budget", 0) <= 0:
        logger.error("Monthly budget must be positive")
        return False

    logger.info("Lambda Labs configuration validated successfully")
    return True

def get_qdrant_config() -> Dict[str, str]:
    """Get Qdrant configuration from Pulumi ESC (unified function)"""
    return {
        "api_key": get_config_value("QDRANT_API_KEY") or get_config_value("QDRANT_api_key"),
        "url": get_config_value("QDRANT_URL") or "https://cloud.qdrant.io",
        "cluster_name": get_config_value("QDRANT_cluster_name", "sophia-ai-production"),
        "timeout": int(get_config_value("QDRANT_timeout", "30")),
        "prefer_grpc": get_config_value("QDRANT_prefer_grpc", "false").lower() == "true"
    }

def get_redis_config() -> Dict[str, Any]:
    """
    Get Redis configuration from Pulumi ESC
    
    Returns:
        Redis configuration dictionary
    """
    redis_host = get_config_value("REDIS_HOST", "localhost")
    redis_port = int(get_config_value("REDIS_PORT", "6379"))
    redis_password = get_config_value("REDIS_PASSWORD")
    redis_db = int(get_config_value("REDIS_DB", "0"))
    
    redis_config = {
        "host": redis_host,
        "port": redis_port,
        "db": redis_db,
        "decode_responses": True,
        "socket_timeout": int(get_config_value("REDIS_SOCKET_TIMEOUT", "30")),
        "socket_connect_timeout": int(get_config_value("REDIS_CONNECT_TIMEOUT", "10")),
        "connection_pool_kwargs": {
            "max_connections": int(get_config_value("REDIS_MAX_CONNECTIONS", "50")),
            "retry_on_timeout": True,
            "health_check_interval": int(get_config_value("REDIS_HEALTH_CHECK_INTERVAL", "30"))
        }
    }
    
    # Add authentication if password is available
    if redis_password:
        redis_config["password"] = redis_password
    
    logger.info(f"✅ Redis config: {redis_host}:{redis_port} (auth: {'yes' if redis_password else 'no'})")
    return redis_config

def get_redis_url() -> str:
    """
    Get Redis connection URL for services that need URL format
    
    Returns:
        Redis connection URL (redis://[password@]host:port/db)
    """
    config = get_redis_config()
    
    # Build Redis URL
    if config.get("password"):
        redis_url = f"redis://:{config['password']}@{config['host']}:{config['port']}/{config['db']}"
    else:
        redis_url = f"redis://{config['host']}:{config['port']}/{config['db']}"
    
    return redis_url
