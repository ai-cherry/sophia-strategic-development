"""
Auto ESC Configuration Module for Sophia AI
Handles environment variable and configuration management
"""

import os
import json
import logging
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)

# Configuration cache
_config_cache: Dict[str, Any] = {}

def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get configuration value from environment variables or cache
    
    Args:
        key: Configuration key
        default: Default value if key not found
        
    Returns:
        Configuration value
    """
    # Check cache first
    if key in _config_cache:
        return _config_cache[key]
    
    # Check environment variables
    env_value = os.getenv(key.upper())
    if env_value is not None:
        _config_cache[key] = env_value
        return env_value
    
    # Check with original case
    env_value = os.getenv(key)
    if env_value is not None:
        _config_cache[key] = env_value
        return env_value
    
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

def get_snowflake_config() -> Dict[str, Any]:
    """
    Get Snowflake configuration
    
    Returns:
        Snowflake configuration dictionary
    """
    return {
        'account': get_config_value('snowflake_account', 'UHDECNO-CVB64222'),
        'user': get_config_value('snowflake_user', 'MUSILLYNN'),
        'password': get_config_value('snowflake_password'),
        'role': get_config_value('snowflake_role', 'ACCOUNTADMIN'),
        'warehouse': get_config_value('snowflake_warehouse', 'AI_COMPUTE_WH'),
        'database': get_config_value('snowflake_database', 'SOPHIA_AI_ADVANCED'),
        'schema': get_config_value('snowflake_schema', 'PROCESSED_AI')
    }

def get_estuary_config() -> Dict[str, Any]:
    """
    Get Estuary configuration
    
    Returns:
        Estuary configuration dictionary
    """
    return {
        'access_token': get_config_value('estuary_access_token'),
        'tenant': get_config_value('estuary_tenant', 'Pay_Ready'),
        'endpoint': get_config_value('estuary_endpoint', 'https://api.estuary.dev')
    }

def get_integration_config() -> Dict[str, Any]:
    """
    Get integration configuration for external services
    
    Returns:
        Integration configuration dictionary
    """
    return {
        'gong': {
            'access_key': get_config_value('gong_access_key'),
            'access_key_secret': get_config_value('gong_access_key_secret'),
            'endpoint': get_config_value('gong_endpoint', 'https://api.gong.io')
        },
        'slack': {
            'bot_token': get_config_value('slack_bot_token'),
            'app_token': get_config_value('slack_app_token'),
            'signing_secret': get_config_value('slack_signing_secret')
        },
        'hubspot': {
            'access_token': get_config_value('hubspot_access_token'),
            'portal_id': get_config_value('hubspot_portal_id'),
            'endpoint': get_config_value('hubspot_endpoint', 'https://api.hubapi.com')
        },
        'intercom': {
            'access_token': get_config_value('intercom_access_token'),
            'app_id': get_config_value('intercom_app_id'),
            'endpoint': get_config_value('intercom_endpoint', 'https://api.intercom.io')
        }
    }

def initialize_default_config():
    """Initialize default configuration values"""
    
    # Snowflake defaults with correct PAT configuration
    set_config_value('snowflake_account', 'UHDECNO-CVB64222')
    set_config_value('snowflake_user', 'SCOOBYJAVA15')
    set_config_value('snowflake_password', 'eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A')
    set_config_value('snowflake_role', 'ACCOUNTADMIN')
    set_config_value('snowflake_warehouse', 'AI_COMPUTE_WH')
    set_config_value('snowflake_database', 'SOPHIA_AI_ADVANCED')
    set_config_value('snowflake_schema', 'PROCESSED_AI')
    
    # Estuary defaults
    set_config_value('estuary_tenant', 'Pay_Ready')
    set_config_value('estuary_endpoint', 'https://api.estuary.dev')
    
    # JWT defaults
    set_config_value('jwt_secret', 'sophia-ai-cortex-secret-key-2025')
    set_config_value('jwt_algorithm', 'HS256')
    set_config_value('jwt_expiration_hours', '24')
    
    logger.info("Default configuration initialized with PAT authentication")

# Initialize defaults on import
initialize_default_config()

