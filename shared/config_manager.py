"""
DEPRECATED: Use backend.core.auto_esc_config instead
This module now delegates all calls to auto_esc_config for backward compatibility

Configuration Manager for Sophia AI - NOW DEPRECATED
All functionality has been moved to auto_esc_config.py
This file remains only for backward compatibility.
"""

import logging
from typing import Any

# Import everything from auto_esc_config
from core.auto_esc_config import (
    get_config_value,
    get_integration_config,
    get_snowflake_config,
    set_config_value,
)

# Try to import BaseConfig for backward compatibility
try:
    from core.base import BaseConfig
except ImportError:
    # Create a dummy BaseConfig if it doesn't exist
    BaseConfig = object  # type: Any

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    DEPRECATED: Use backend.core.auto_esc_config directly

    This class now delegates all functionality to auto_esc_config.
    It exists only for backward compatibility.
    """

    def __init__(self):
        logger.warning(
            "ConfigManager is deprecated. Use backend.core.auto_esc_config directly."
        )

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value - delegates to auto_esc_config"""
        return get_config_value(key, default)

    def set_value(self, key: str, value: Any) -> None:
        """Set a configuration value - delegates to auto_esc_config"""
        set_config_value(key, value)

    def get_snowflake_config(self) -> dict[str, Any]:
        """Get Snowflake configuration - delegates to auto_esc_config"""
        return get_snowflake_config()

    def get_integration_config(self) -> dict[str, Any]:
        """Get integration configuration - delegates to auto_esc_config"""
        return get_integration_config()


# Create global instance for backward compatibility
_config_manager = ConfigManager()

# The functions are already imported from auto_esc_config above
# No need to redefine them
