"""
Sophia AI Startup Configuration - PERMANENT SNOWFLAKE FIX
Ensures correct configuration is loaded at application startup
This file permanently fixes the ZNB04675.us-east-1.us-east-1.us-east-1.us-east-1 → ZNB04675.us-east-1.us-east-1.us-east-1 issue
"""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
import logging
import os

logger = logging.getLogger(__name__)


def configure_modern_stack_environment():
    """Configure ModernStack environment variables at startup - PERMANENT FIX"""

# REMOVED: ModernStack dependencyURATION - DO NOT MODIFY
    correct_config = {
        "SNOWFLAKE_ACCOUNT": "ZNB04675.us-east-1.us-east-1.us-east-1",
        "SNOWFLAKE_USER": "SCOOBYJAVA15",
        "SNOWFLAKE_DATABASE": "SOPHIA_AI",
        "SNOWFLAKE_WAREHOUSE": "SOPHIA_AI_WH",
        "SNOWFLAKE_ROLE": "ACCOUNTADMIN",
        "SNOWFLAKE_SCHEMA": "PROCESSED_AI",
    }

    for key, value in correct_config.items():
        os.environ[key] = value
        logger.info(f"✅ PERMANENT FIX: Set {key}: {value}")

# REMOVED: ModernStack dependencyuration applied")
    logger.info(
        "   This permanently fixes the ZNB04675.us-east-1.us-east-1.us-east-1.us-east-1 → ZNB04675.us-east-1.us-east-1.us-east-1 issue"
    )


def apply_startup_configuration():
    """Apply all startup configuration - CALLED AUTOMATICALLY"""
    logger.info("🚀 Applying Sophia AI startup configuration (PERMANENT SNOWFLAKE FIX)")

    # Configure ModernStack with correct account
    configure_modern_stack_environment()

    # Set other environment variables
    os.environ["ENVIRONMENT"] = "prod"
    os.environ["PULUMI_ORG"] = "scoobyjava-org"

    logger.info("✅ Startup configuration complete - ModernStack fix applied")


# AUTOMATIC APPLICATION - This runs when module is imported
apply_startup_configuration()
