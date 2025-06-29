"""
Sophia AI Startup Configuration
Ensures correct configuration is loaded at application startup
"""

import os
import logging

logger = logging.getLogger(__name__)

def configure_snowflake_environment():
    """Configure Snowflake environment variables at startup"""
    
    # Set correct Snowflake configuration
    snowflake_config = {
        'SNOWFLAKE_ACCOUNT': 'ZNB04675',
        'SNOWFLAKE_USER': 'SCOOBYJAVA15',
        'SNOWFLAKE_DATABASE': 'SOPHIA_AI',
        'SNOWFLAKE_WAREHOUSE': 'SOPHIA_AI_WH',
        'SNOWFLAKE_ROLE': 'ACCOUNTADMIN',
        'SNOWFLAKE_SCHEMA': 'PROCESSED_AI'
    }
    
    for key, value in snowflake_config.items():
        os.environ[key] = value
        logger.info(f"✅ Set {key}: {value}")
    
    logger.info("🔧 Snowflake environment configuration applied")

def apply_startup_configuration():
    """Apply all startup configuration"""
    logger.info("🚀 Applying Sophia AI startup configuration")
    
    # Configure Snowflake
    configure_snowflake_environment()
    
    # Set other environment variables
    os.environ['ENVIRONMENT'] = 'prod'
    os.environ['PULUMI_ORG'] = 'scoobyjava-org'
    
    logger.info("✅ Startup configuration complete")

# Auto-apply configuration when module is imported
apply_startup_configuration()
