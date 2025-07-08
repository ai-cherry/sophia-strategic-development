"""
Sophia AI Backend Package
Centralized backend services with secure secret management
"""

from .core.auto_esc_config import (
    get_config_value,
    get_integration_config,
    get_lambda_labs_config,
    get_snowflake_config,
)

__version__ = "1.0.0"
__all__ = [
    "get_config_value",
    "get_snowflake_config",
    "get_integration_config",
    "get_lambda_labs_config",
]
