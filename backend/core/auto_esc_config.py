"""
Enhanced Auto ESC Config with ALL GitHub Secrets Mapped
This loads ALL secrets from Pulumi ESC using the correct GitHub secret names
"""

import logging
import os
import subprocess
from functools import lru_cache
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

# Configuration cache
_config_cache: Dict[str, Any] = {}
_esc_cache: Optional[Dict[str, Any]] = None

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


def get_modern_stack_config() -> Dict[str, Any]:
    """
    Get ModernStack configuration from Pulumi ESC - PERMANENT FIX

    Returns:
        ModernStack configuration dictionary with CORRECT account
    """
    # Check environment variables first (for immediate use)
    # REMOVED: ModernStack dependency_value(
    #     "postgres_host", "UHDECNO-CVB64222"
    # )
    # REMOVED: ModernStack dependency_value(
    #     "modern_stack_user", "SCOOBYJAVA15"
    # )

    # Try PAT token first, then regular password
    pat_token = os.getenv("modern_stack_PAT")
    password = (
        pat_token
        if pat_token
        else get_config_value("postgres_password")
    )

    account = get_config_value("postgres_host", "UHDECNO-CVB64222")
    user = get_config_value("modern_stack_user", "SCOOBYJAVA15")

    return {
        "account": account,
        "user": user,
        "password": password,  # Will use PAT or password from ESC/env
        "role": get_config_value("modern_stack_role", "ACCOUNTADMIN"),
        "warehouse": get_config_value("postgres_database", "SOPHIA_AI_COMPUTE_WH"),
        "database": get_config_value("postgres_database", "AI_MEMORY"),
        "schema": get_config_value("postgres_schema", "VECTORS"),
    }


def get_postgres_config() -> Dict[str, Any]:
    """
    Get PostgreSQL configuration

    Returns:
        PostgreSQL configuration dictionary
    """
    return {
        "host": get_config_value("postgres_host", "postgres"),
        "port": int(get_config_value("postgres_port", "5432")),
        "database": get_config_value("postgres_database", "sophia_ai"),
        "user": get_config_value("postgres_user", "postgres"),
        "password": get_config_value(
            "postgres_password"
        ),  # Separate password from ModernStack
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
    if not get_config_value("modern_stack_user"):
        set_config_value("modern_stack_user", "SCOOBYJAVA15")
    if not get_config_value("modern_stack_role"):
        set_config_value("modern_stack_role", "ACCOUNTADMIN")
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
    ssh_private_key = get_config_value("LAMBDA_PRIVATE_SSH_KEY") or """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAsctiuxhwWHR6Vw2MCEKFQTo0fDd0cDE4G2S7AexGvQZvTyqy
Vl/bBqVE8k3ToTO1VzVynbX4UIv4jmtZ+f85uAkCfkW9xIhfrdMGLVIoMs7UN0rS
iuFdyUD7pf41RDGah35+FfpxQWq+gL0ac9LCFwhE66YyeB2MzG6hrabsKVAAK7Tv
GSYH2ApULQdSowZP0niIshBEy9Sq3px1Vylyon7RsY3UWwEgcrEpQens4s3aJDMe
o/du4cUhbtMJf3RqcDrva9aL3ub0n1Xq5o57lju7umtqlfsJXP776Vyg2oobviaf
LeLg3ZkRHNFgkUz6nWXSZkEyeeM0nSaKIbBoawIDAQABAoIBABvsIbbZeTdjH52R
Wpcnf08FqZ2Chg5ipHmk4bvFFDz2iD+qKHTpO/g4t3HIaD6uZMHr+nKrU/KucNxJ
Hsnk2/c7rwEOyeVWN5SQii1O9FI6ali+rv8xsq17P6pLmKj7k1XJN1sTSHsqHP4R
9NgQ1vuQCGbr5Iw5s9WdYFXp27gG/cwCPcRmtbDwxWypNqBJXCuzryTcj12mXWxx
KXyR1D2i64kYJvfX4XpdO2fHqCwy9OQe6XXCgfO8EmY16GEBA9OYFz7TWD05g/ag
e4C3PhO/OJ8wdd6EUA8/DS8ycN8iAxrqJJ4O8ZRKhPWVTIWG++2b9AJlc+vy+lCo
4PbAWKECgYEA4SZhKQnDAHzt6xuHkVZCxcFGDQPtEhdPc3B23SIFgRtCCss4h5NC
20WoxjsULv+CWG6rlTxNojUS3dKwS/xZs7RZRVleV6Rd3nWikuRDTZTDXQBsxRfr
mgrfdnRKhCkqBfvxEsiRz/dewUL4owkZYyr3B8T6NRDXuCNeWKHHlgsCgYEAyifp
VmQ9aCS3PrZTVo9CwCz7vh0NHjrZ1LQpJzGWld/BKzwmqZeOe3EKlNI0BaYH43sb
38uTq5A0TnjfD16hqeWhy7oIgAabnKUU894PkMZNt4xjk9iRFKvsJiCZxv4vN5MY
MraJRj61jH/9BtXnLAhqsnH7tJYN2uAzufjB0yECgYAyalipStFKg672zWRO7ATp
qTyZX36vZV7aF53WKG8ZGNRx/E19NkFrPi7rrID5gSdby/RJ54Xuw3mlCC+H5Erl
zYWL3NYeQ+TtEmREBi736U7RvW2duJx+Et809BdXfqw1SNQTg6v66IZkOi3YvAne
Rdmo+LeaOFpFlk3jBN7fPwKBgAhMLxWus56Ms0DNtwn8g17j+clJ4/nzrHFAm9fR
/z5TmtgtdeDMKbsDXs3Q+vWoZPZ/XRuIfZ0zJBJ8f5tf5P7WQBfeoO6wVr7NP9jq
qnTkztfT2Vp+LyZMEDtYZzd1w3ZigUHDoErT1BvaPQaEzSJPjiGY8B3vcs4jGbxu
a3ZBAoGARVeKJRgiPHQTxguouBYLSpKr5kuF+sYp0TB3XvOPlMPjKMLIryOajRpd
3ot+NheIx7IOO8nbRBjcdr1CsxvKVrC6K1iEyV1cOwrGo2JednJr5cY92oE3Q3BZ
Si02dEz1jsNZT5IObnR+EZU3x3tUPVwobDfLiVIhf5iOHg48b/w=
-----END RSA PRIVATE KEY-----"""
    
    # SSH public key
    ssh_public_key = get_config_value("LAMBDA_SSH_KEY") or "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5"
    
    return {
        "api_key": api_key,
        "api_endpoint": "https://cloud.lambda.ai/api/v1/instances",
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
    """
    Get Docker Hub configuration from Pulumi ESC

    PERMANENT FIX: Use DOCKER_TOKEN and DOCKERHUB_USERNAME as the primary keys
    These are the actual secret names in GitHub

    Returns:
        Docker Hub configuration dictionary with username and access token
    """
    # Get username - DOCKERHUB_USERNAME is the primary key in GitHub
    username = (
        get_config_value("DOCKERHUB_USERNAME")
        or get_config_value("docker_username")  # PRIMARY
        or get_config_value("docker_hub_username")
        or "scoobyjava15"  # fallback
    )

    # Get token - DOCKER_TOKEN is the primary key in GitHub
    access_token = (
        get_config_value("DOCKER_TOKEN")
        or get_config_value("docker_token")  # PRIMARY
        or get_config_value("docker_hub_access_token")
        or get_config_value("docker_token")
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

# Enhanced ModernStack connection optimization
MODERN_STACK_CONNECTION_CONFIG = {
    "connection_pool_size": 10,
    "connection_timeout": 30,
    "query_timeout": 300,
    "retry_attempts": 3,
    "auto_commit": True,
    "warehouse_auto_suspend": 60,
    "warehouse_auto_resume": True,
}


def get_modern_stack_pat(default: Optional[str] = None) -> str:
    """
    Get ModernStack PAT (Programmatic Access Token) for MCP authentication

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
    pat_key = f"modern_stack_pat_{environment_str.lower()}"
    pat = get_config_value(pat_key)

    if not pat:
        # Try generic PAT
        pat = get_config_value("modern_stack_pat")

    if not pat:
        # Try with MCP prefix
        pat = get_config_value("modern_stack_mcp_pat")

    if not pat:
        raise ValueError(
# REMOVED: ModernStack dependencyured for environment: {environment_str}"
        )

    # Validate PAT format (basic check)
    if not pat.startswith("pat_") and len(pat) < 20:
        logger.warning("ModernStack PAT format may be invalid")

    return pat


# REMOVED: ModernStack dependency() -> Dict[str, Any]:
    """
# REMOVED: ModernStack dependencyuration

    Returns:
        MCP configuration dictionary
    """
    environment = get_config_value("environment", "prod")

    return {
        "url": get_config_value(
            "modern_stack_mcp_url", "https://mcp-modern_stack.sophia-ai.com"
        ),
        "pat": get_modern_stack_pat(environment),
        "timeout": int(get_config_value("modern_stack_mcp_timeout", "120")),
        "max_retries": int(get_config_value("modern_stack_mcp_max_retries", "3")),
        "pool_size": int(get_config_value("modern_stack_mcp_pool_size", "20")),
    }


# Add PAT rotation check function
def check_pat_rotation_needed() -> bool:
    """
    Check if ModernStack PAT needs rotation

    Returns:
        True if rotation needed
    """
    # This is a placeholder - in production, would check PAT metadata
    # from ModernStack or a secure metadata store
    pat_created_date = get_config_value("modern_stack_pat_created_date")

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


def validate_modern_stack_pat() -> bool:
    """
    Validate ModernStack PAT token format

    Returns:
        True if PAT token appears valid
    """
    pat = get_config_value("postgres_password")
    if not pat:
# REMOVED: ModernStack dependencyured")
        return False

    # PAT tokens are JWT tokens that typically start with 'eyJ'
    if pat.startswith("eyJ") and len(pat) > 100:
        logger.info("ModernStack PAT token format validated")
        return True

    logger.warning("ModernStack password may not be a valid PAT token")
    return False


# REMOVED: ModernStack dependency_enhanced() -> Dict[str, Any]:
    """
# REMOVED: ModernStack dependencyuration with PAT support

    Returns:
# REMOVED: ModernStack dependencyuration dictionary
    """
# REMOVED: ModernStack dependency()

    # Add PAT-specific configuration
    enhanced_config = {
        **base_config,
        "authenticator": "modern_stack",  # For PAT authentication
        "session_parameters": {
            "QUERY_TAG": "sophia_ai_unified",
        },
        "pat_validated": validate_modern_stack_pat(),
    }

    # Use validated account format
    enhanced_config["account"] = "UHDECNO-CVB64222"

    return enhanced_config


# Enhanced configuration constants
MODERN_STACK_DEFAULT_CONFIG = {
    "account": "UHDECNO-CVB64222",
    "user": "SCOOBYJAVA15",
    "role": "ACCOUNTADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "SOPHIA_AI_PROD",
    "schema": "PUBLIC",
    "authenticator": "modern_stack",
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
            "modern_stack_cortex": 2,
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
