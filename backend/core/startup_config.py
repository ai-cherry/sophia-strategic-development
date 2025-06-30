"""
Sophia AI Startup Configuration - PERMANENT SNOWFLAKE FIX
Ensures correct configuration is loaded at application startup
This file permanently fixes the scoobyjava-vw02766 → ZNB04675 issue
"""

import logging
import os

logger = logging.getLogger(__name__)


def configure_snowflake_environment():
    """Configure Snowflake environment variables at startup - PERMANENT FIX"""

    # PERMANENT SNOWFLAKE CONFIGURATION - DO NOT MODIFY
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
        logger.info(f"✅ PERMANENT FIX: Set {key}: {value}")

    logger.info("🔧 PERMANENT Snowflake environment configuration applied")
    logger.info("   This permanently fixes the scoobyjava-vw02766 → ZNB04675 issue")


def apply_startup_configuration():
    """Apply all startup configuration - CALLED AUTOMATICALLY"""
    logger.info("🚀 Applying Sophia AI startup configuration (PERMANENT SNOWFLAKE FIX)")

    # Configure Snowflake with correct account
    configure_snowflake_environment()

    # Set other environment variables
    os.environ["ENVIRONMENT"] = "prod"
    os.environ["PULUMI_ORG"] = "scoobyjava-org"

    logger.info("✅ Startup configuration complete - Snowflake fix applied")


# AUTOMATIC APPLICATION - This runs when module is imported
apply_startup_configuration()
