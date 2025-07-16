"""
Sophia AI Backend Core Module
"""

from .database import init_database, create_tables, check_database_health
from .security import check_security_health, get_api_key

try:
    from .auto_esc_config import get_config_value, validate_config_access
except ImportError:
    def get_config_value(key: str, default=None):
        import os
        return os.getenv(key, default)
    
    def validate_config_access():
        return {"status": "ok", "message": "Basic config access"}

__all__ = [
    "init_database",
    "create_tables", 
    "check_database_health",
    "check_security_health",
    "get_api_key",
    "get_config_value",
    "validate_config_access"
] 