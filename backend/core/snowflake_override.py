"""
Snowflake Connection Override
Forces correct Snowflake account configuration
"""

import os
import logging
from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

def override_snowflake_config():
    """Override Snowflake configuration with correct values"""
    
    # Force correct Snowflake account
    correct_config = {
        'SNOWFLAKE_ACCOUNT': 'ZNB04675',
        'SNOWFLAKE_USER': 'SCOOBYJAVA15',
        'SNOWFLAKE_DATABASE': 'SOPHIA_AI',
        'SNOWFLAKE_WAREHOUSE': 'SOPHIA_AI_WH',
        'SNOWFLAKE_ROLE': 'ACCOUNTADMIN',
        'SNOWFLAKE_SCHEMA': 'PROCESSED_AI'
    }
    
    for key, value in correct_config.items():
        os.environ[key] = value
    
    logger.info("🔧 Snowflake configuration override applied")
    return correct_config

def get_snowflake_connection_params():
    """Get correct Snowflake connection parameters"""
    override_snowflake_config()
    
    return {
        'account': 'ZNB04675',
        'user': 'SCOOBYJAVA15',
        'password': get_config_value('snowflake.password', ''),
        'database': 'SOPHIA_AI',
        'warehouse': 'SOPHIA_AI_WH',
        'role': 'ACCOUNTADMIN',
        'schema': 'PROCESSED_AI'
    }

# Apply override when module is imported
override_snowflake_config()
