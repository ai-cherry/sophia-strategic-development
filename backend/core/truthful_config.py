"""
Truthful Configuration Module for Sophia AI
Provides consistent configuration access across all services
"""

from typing import Dict, Any
from .auto_esc_config import get_config_value, get_qdrant_config

def get_real_qdrant_config() -> Dict[str, Any]:
    """Get real Qdrant configuration - alias for standardized function"""
    return get_qdrant_config()

def get_real_config_value(key: str, default: Any = None) -> Any:
    """Get real configuration value - alias for standardized function"""
    return get_config_value(key, default)

# Legacy compatibility
get_real_QDRANT_config = get_real_qdrant_config
