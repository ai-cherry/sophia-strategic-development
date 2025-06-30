#!/usr/bin/env python3
"""
Fix Snowflake Connection Script
Clear cache and test connection with corrected configuration
"""

import os
import sys
import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clear_python_cache():
    """Clear all Python cache files"""
    logger.info("🧹 Clearing Python cache files...")

    # Clear __pycache__ directories
    for cache_dir in Path(".").rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
            logger.info(f"   Removed: {cache_dir}")

    # Clear .pyc files
    pyc_count = 0
    for pyc_file in Path(".").rglob("*.pyc"):
        pyc_file.unlink()
        pyc_count += 1

    logger.info(f"✅ Cleared {pyc_count} .pyc files and cache directories")


def set_environment_variables():
    """Set correct environment variables"""
    logger.info("🔧 Setting correct environment variables...")

    # Set correct Snowflake configuration
    os.environ["SNOWFLAKE_ACCOUNT"] = "ZNB04675"
    os.environ["SNOWFLAKE_USER"] = "SCOOBYJAVA15"
    os.environ["SNOWFLAKE_ROLE"] = "ACCOUNTADMIN"
    os.environ["SNOWFLAKE_WAREHOUSE"] = "SOPHIA_AI_WH"
    os.environ["SNOWFLAKE_DATABASE"] = "SOPHIA_AI"
    os.environ["SNOWFLAKE_SCHEMA"] = "PROCESSED_AI"

    logger.info("✅ Environment variables set:")
    logger.info(f"   SNOWFLAKE_ACCOUNT: {os.environ['SNOWFLAKE_ACCOUNT']}")
    logger.info(f"   SNOWFLAKE_DATABASE: {os.environ['SNOWFLAKE_DATABASE']}")
    logger.info(f"   SNOWFLAKE_WAREHOUSE: {os.environ['SNOWFLAKE_WAREHOUSE']}")


def test_configuration():
    """Test the Snowflake configuration"""
    logger.info("🔍 Testing Snowflake configuration...")

    try:
        # Import after clearing cache
        from backend.core.auto_esc_config import get_snowflake_config

        config = get_snowflake_config()
        logger.info("✅ Configuration loaded successfully:")
        logger.info(f"   Account: {config['account']}")
        logger.info(f"   User: {config['user']}")
        logger.info(f"   Database: {config['database']}")
        logger.info(f"   Warehouse: {config['warehouse']}")

        return config

    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return None


def test_connection():
    """Test the actual Snowflake connection"""
    logger.info("🔗 Testing Snowflake connection...")

    try:
        import asyncio
        from backend.core.optimized_connection_manager import (
            OptimizedConnectionManager,
            ConnectionType,
        )

        async def test_async_connection():
            manager = OptimizedConnectionManager()
            try:
                conn = await manager.get_connection(ConnectionType.SNOWFLAKE)
                if conn:
                    logger.info("✅ Snowflake connection successful!")
                    return True
                else:
                    logger.error("❌ Snowflake connection returned None")
                    return False
            except Exception as e:
                logger.error(f"❌ Snowflake connection failed: {e}")
                return False

        return asyncio.run(test_async_connection())

    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False


def main():
    """Main fix function"""
    logger.info("🚀 Starting Snowflake connection fix...")

    # Step 1: Clear Python cache
    clear_python_cache()

    # Step 2: Set environment variables
    set_environment_variables()

    # Step 3: Test configuration
    config = test_configuration()
    if not config:
        logger.error("❌ Configuration test failed - aborting")
        return False

    # Step 4: Test connection
    success = test_connection()

    if success:
        logger.info("🎉 Snowflake connection fix completed successfully!")
        logger.info("✅ System ready for Cursor AI implementation")
    else:
        logger.error("❌ Connection test failed - manual investigation required")
        logger.error("   Check Pulumi ESC secret availability")
        logger.error("   Verify PAT token is not expired")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
