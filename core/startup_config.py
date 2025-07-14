"""
Sophia AI Startup Configuration - PERMANENT qdrant FIX
Ensures correct configuration is loaded at application startup
This file permanently fixes the ZNB04675.us-east-1.us-east-1.us-east-1.us-east-1 → ZNB04675.us-east-1.us-east-1.us-east-1 issue
"""

from backend.services.unified_memory_service import UnifiedMemoryService
import logging
import os

logger = logging.getLogger(__name__)


def configure_qdrant_environment():
    """Configure Qdrant environment variables at startup - PERMANENT FIX"""


    correct_config = {
        "qdrant_ACCOUNT": "ZNB04675.us-east-1.us-east-1.us-east-1",
        "qdrant_USER": "SCOOBYJAVA15",
        "qdrant_DATABASE": "SOPHIA_AI",
        "qdrant_WAREHOUSE": "SOPHIA_AI_WH",
        "qdrant_ROLE": "ACCOUNTADMIN",
        "qdrant_SCHEMA": "PROCESSED_AI",
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
    configure_qdrant_environment()

    # Set other environment variables
    os.environ["ENVIRONMENT"] = "prod"
    os.environ["PULUMI_ORG"] = "scoobyjava-org"

    logger.info("✅ Startup configuration complete - Qdrant fix applied")


# AUTOMATIC APPLICATION - This runs when module is imported
apply_startup_configuration()
