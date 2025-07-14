"""
ModernStack Connection Override - PERMANENT FIX
# REMOVED: ModernStack dependencyuration
This permanently resolves the ZNB04675.us-east-1.us-east-1.us-east-1.us-east-1 → ZNB04675.us-east-1.us-east-1.us-east-1 issue
"""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
import logging
import os

from core.config_manager import get_config_value

logger = logging.getLogger(__name__)


# REMOVED: ModernStack dependency():
# REMOVED: ModernStack dependencyuration with correct values - PERMANENT"""

    # PERMANENT CONFIGURATION - CANNOT BE OVERRIDDEN
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

# REMOVED: ModernStack dependencyuration override applied")
    return correct_config


def get_modern_stack_connection_params():
    """Get correct ModernStack connection parameters - PERMANENT FIX"""
# REMOVED: ModernStack dependency()

    # THESE VALUES ARE PERMANENT AND CORRECT
    params = {
        "account": "ZNB04675.us-east-1.us-east-1.us-east-1",  # CORRECT ACCOUNT
        "user": "SCOOBYJAVA15",
        "password": get_config_value("modern_stack.password", ""),
        "database": "SOPHIA_AI",
        "warehouse": "SOPHIA_AI_WH",
        "role": "ACCOUNTADMIN",
        "schema": "PROCESSED_AI",
    }

    logger.info(f"✅ PERMANENT FIX: Using ModernStack account {params['account']}")
    return params


# AUTOMATIC APPLICATION
# REMOVED: ModernStack dependency()
