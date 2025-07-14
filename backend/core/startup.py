"""
Unified startup module for Sophia AI services
Ensures proper environment loading and configuration
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def load_environment(env_file: str = "local.env", verbose: bool = True) -> bool:
    """
    Load environment variables from file

    Args:
        env_file: Path to environment file
        verbose: Whether to print loading status

    Returns:
        True if loaded successfully, False otherwise
    """
    env_path = Path(env_file)

    if not env_path.exists():
        if verbose:
            print(f"⚠️ Warning: {env_file} not found, using system environment")
        return False

    loaded_count = 0
    skipped_count = 0

    try:
        with open(env_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse key=value
                if "=" not in line:
                    logger.warning(f"Invalid line {line_num} in {env_file}: {line}")
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value and value[0] in ('"', "'") and value[0] == value[-1]:
                    value = value[1:-1]

                # Only set if not already in environment (allows overrides)
                if key not in os.environ:
                    os.environ[key] = value
                    loaded_count += 1
                else:
                    skipped_count += 1

        if verbose:
            print(f"✅ Loaded {loaded_count} environment variables from {env_file}")
            if skipped_count > 0:
                print(f"ℹ️  Skipped {skipped_count} already set variables")

        return True

    except Exception as e:
        logger.error(f"Error loading environment from {env_file}: {e}")
        return False


def validate_required_variables(required_vars: list[str]) -> tuple[bool, list[str]]:
    """
    Validate that required environment variables are set

    Args:
        required_vars: List of required variable names

    Returns:
        Tuple of (all_present, missing_vars)
    """
    missing = [var for var in required_vars if not os.getenv(var)]
    return len(missing) == 0, missing


def initialize_logging(level: str = "INFO") -> None:
    """Initialize logging configuration"""
    log_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_startup_config() -> dict[str, Any]:
    """Get startup configuration with defaults"""
    return {
        "environment": os.getenv("ENVIRONMENT", "prod"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "pulumi_org": os.getenv("PULUMI_ORG", "scoobyjava-org"),
        "service_mode": os.getenv("SERVICE_MODE", "production"),
    }


def startup_sequence(
    service_name: str,
    required_vars: Optional[list[str]] = None,
    env_file: str = "local.env",
) -> dict[str, Any]:
    """
    Standard startup sequence for all services

    Args:
        service_name: Name of the service starting up
        required_vars: List of required environment variables
        env_file: Path to environment file

    Returns:
        Startup configuration dictionary

    Raises:
        SystemExit: If required variables are missing
    """
    print(f"🚀 Starting {service_name}...")

    # Load environment
    load_environment(env_file)

    # Get config
    config = get_startup_config()

    # Initialize logging
    initialize_logging(config["log_level"])

    # Validate required variables
    if required_vars:
        valid, missing = validate_required_variables(required_vars)
        if not valid:
            logger.error(
                f"Missing required environment variables: {', '.join(missing)}"
            )
            print(f"❌ Missing required environment variables: {', '.join(missing)}")
            print(f"Please check your {env_file} file")
            sys.exit(1)

    # Log startup info
    logger.info(
        f"{service_name} starting",
        extra={
            "environment": config["environment"],
            "debug": config["debug"],
            "service_mode": config["service_mode"],
        },
    )

    print(f"✅ {service_name} initialized")
    print(f"   Environment: {config['environment']}")
    print(f"   Debug mode: {config['debug']}")
    print(f"   Service mode: {config['service_mode']}")

    return config


# Auto-load environment if this module is imported
if not os.getenv("SOPHIA_STARTUP_SKIP_AUTO_LOAD"):
    load_environment(verbose=False)
