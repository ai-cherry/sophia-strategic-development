"""
Snowflake Configuration Override
Provides correct Snowflake configuration to fix 404 connectivity issues
"""

import os
from backend.core.auto_esc_config import get_config_value

# Correct Snowflake configuration
CORRECT_SNOWFLAKE_CONFIG = {
    "account": "ZNB04675",
    "user": "SCOOBYJAVA15",
    "database": "SOPHIA_AI_PROD", 
    "warehouse": "SOPHIA_AI_WH",
    "role": "ACCOUNTADMIN",
    "schema": "PROCESSED_AI"
}

def get_snowflake_config(key: str, default: str = None) -> str:
    """
    Get Snowflake configuration with override for correct values
    
    Args:
        key: Configuration key (without snowflake_ prefix)
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    # First try environment variable override
    env_key = f"SNOWFLAKE_{key.upper()}"
    env_value = os.getenv(env_key)
    if env_value:
        return env_value
    
    # Then try correct configuration override
    if key in CORRECT_SNOWFLAKE_CONFIG:
        return CORRECT_SNOWFLAKE_CONFIG[key]
    
    # Fall back to original config
    return get_config_value(f"snowflake_{key}", default)

def get_snowflake_connection_params() -> dict:
    """
    Get complete Snowflake connection parameters
    
    Returns:
        Dictionary of connection parameters
    """
    return {
        "account": get_snowflake_config("account"),
        "user": get_snowflake_config("user"),
        "password": get_config_value("snowflake_password"),  # Keep from ESC
        "database": get_snowflake_config("database"),
        "warehouse": get_snowflake_config("warehouse"),
        "role": get_snowflake_config("role"),
        "schema": get_snowflake_config("schema", "PUBLIC")
    }

# Set environment variables for immediate use
for key, value in CORRECT_SNOWFLAKE_CONFIG.items():
    os.environ[f"SNOWFLAKE_{key.upper()}"] = value
