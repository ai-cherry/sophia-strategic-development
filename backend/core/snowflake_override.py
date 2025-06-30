"""
Snowflake Connection Override - PERMANENT FIX
Forces correct Snowflake account configuration
This permanently resolves the scoobyjava-vw02766 → ZNB04675 issue
"""

import logging
import os

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


def override_snowflake_config():
    """Override Snowflake configuration with correct values - PERMANENT"""

    # PERMANENT CONFIGURATION - CANNOT BE OVERRIDDEN
    correct_config = {
        "SNOWFLAKE_ACCOUNT": "ZNB04675",
        "SNOWFLAKE_USER": "SCOOBYJAVA15",
        "SNOWFLAKE_DATABASE": "SOPHIA_AI",
        "SNOWFLAKE_WAREHOUSE": "SOPHIA_AI_WH",
        "SNOWFLAKE_ROLE": "ACCOUNTADMIN",
        "SNOWFLAKE_SCHEMA": "PROCESSED_AI",
    }

    for key, value in correct_config.items():
        os.environ[key] = value

    logger.info("🔧 PERMANENT Snowflake configuration override applied")
    return correct_config


def get_snowflake_connection_params():
    """Get correct Snowflake connection parameters - PERMANENT FIX"""
    override_snowflake_config()

    # THESE VALUES ARE PERMANENT AND CORRECT
    params = {
        "account": "ZNB04675",  # CORRECT ACCOUNT
        "user": "SCOOBYJAVA15",
        "password": get_config_value("snowflake.password", ""),
        "database": "SOPHIA_AI",
        "warehouse": "SOPHIA_AI_WH",
        "role": "ACCOUNTADMIN",
        "schema": "PROCESSED_AI",
    }

    logger.info(f"✅ PERMANENT FIX: Using Snowflake account {params['account']}")
    return params


# AUTOMATIC APPLICATION
override_snowflake_config()
