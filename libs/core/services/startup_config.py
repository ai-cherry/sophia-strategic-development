"""
Sophia AI Startup Configuration - PERMANENT qdrant FIX
Ensures correct configuration is loaded at application startup
This file permanently fixes the ZNB04675.us-east-1.us-east-1.us-east-1.us-east-1 → ZNB04675.us-east-1.us-east-1.us-east-1 issue
"""

import logging
import os
from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

def configure_QDRANT_environment():
    """Configure Qdrant environment variables at startup - PERMANENT FIX"""

    correct_config = {
        "QDRANT_ACCOUNT": "ZNB04675.us-east-1.us-east-1.us-east-1",
        "QDRANT_USER": "SCOOBYJAVA15",
        "QDRANT_DATABASE": "SOPHIA_AI",
        "QDRANT_WAREHOUSE": "SOPHIA_AI_WH",
        "QDRANT_ROLE": "ACCOUNTADMIN",
        "QDRANT_SCHEMA": "PROCESSED_AI",
    }

    for key, value in correct_config.items():
        os.environ[key] = value
        logger.info(f"✅ PERMANENT FIX: Set {key}: {value}")

    logger.info(
        "   This permanently fixes the ZNB04675.us-east-1.us-east-1.us-east-1.us-east-1 → ZNB04675.us-east-1.us-east-1.us-east-1 issue"
    )

def apply_startup_configuration():
    """Apply all startup configuration - CALLED AUTOMATICALLY"""
    logger.info("🚀 Applying Sophia AI startup configuration (PERMANENT qdrant FIX)")

    # Configure Qdrant with correct account
    configure_QDRANT_environment()

    # Set other environment variables
    get_config_value("ENVIRONMENT") = "prod"
    get_config_value("PULUMI_ORG") = "scoobyjava-org"

    logger.info("✅ Startup configuration complete - Qdrant fix applied")

# AUTOMATIC APPLICATION - This runs when module is imported
apply_startup_configuration()
