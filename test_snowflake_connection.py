#!/usr/bin/env python3
"""
Snowflake Connection Test Script
Test the corrected Snowflake configuration
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_snowflake_connection():
    """Test Snowflake connection with corrected configuration."""

    try:
        # Import Snowflake connector
        import snowflake.connector

        # Import configuration
        from backend.core.auto_esc_config import get_config_value

        logger.info("🔍 Testing Snowflake connection configuration")

        # Get configuration values
        account = get_config_value("snowflake_account", "ZNB04675")
        user = get_config_value("snowflake_user", "SCOOBYJAVA15")
        password = get_config_value("snowflake_password")
        role = get_config_value("snowflake_role", "SYSADMIN")
        warehouse = get_config_value("snowflake_warehouse", "SOPHIA_AI_WH")
        database = get_config_value("snowflake_database", "SOPHIA_AI_PROD")

        logger.info(f"🔍 Account: {account}")
        logger.info(f"🔍 User: {user}")
        logger.info(f"🔍 Role: {role}")
        logger.info(f"🔍 Warehouse: {warehouse}")
        logger.info(f"🔍 Database: {database}")
        logger.info(f"🔍 Password: {'*' * len(password) if password else 'NOT SET'}")

        if not password:
            logger.error("❌ Snowflake password not found in configuration")
            return False

        # Test connection
        logger.info("🔗 Attempting Snowflake connection...")

        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            role=role,
            warehouse=warehouse,
            database=database,
        )

        logger.info("✅ Snowflake connection successful!")

        # Test basic query
        cursor = conn.cursor()
        cursor.execute(
            "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()"
        )
        result = cursor.fetchone()

        logger.info("✅ Connection details:")
        logger.info(f"   Account: {result[0]}")
        logger.info(f"   User: {result[1]}")
        logger.info(f"   Role: {result[2]}")
        logger.info(f"   Warehouse: {result[3]}")
        logger.info(f"   Database: {result[4]}")

        # Test database access
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        logger.info(f"✅ Available databases: {len(databases)}")

        # Test warehouse access
        cursor.execute("SHOW WAREHOUSES")
        warehouses = cursor.fetchall()
        logger.info(f"✅ Available warehouses: {len(warehouses)}")

        cursor.close()
        conn.close()

        logger.info("🎉 Snowflake connection test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Snowflake connection test failed: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")

        # Provide specific guidance based on error type
        if "404" in str(e):
            logger.error("💡 404 Error suggests account locator is incorrect")
            logger.error("💡 Verify account locator format: ZNB04675")
            logger.error("💡 Try with region suffix if needed: ZNB04675.us-west-2.aws")
        elif "authentication" in str(e).lower():
            logger.error("💡 Authentication error suggests username/password issue")
            logger.error("💡 Verify credentials in Pulumi ESC or environment variables")
        elif "warehouse" in str(e).lower():
            logger.error(
                "💡 Warehouse error suggests warehouse doesn't exist or no access"
            )
            logger.error("💡 Verify warehouse name and user permissions")

        return False


def test_configuration_loading():
    """Test configuration loading from various sources."""

    try:
        from backend.core.auto_esc_config import get_config_value
        from backend.core.security_config import SecurityConfig

        logger.info("🔍 Testing configuration loading")

        # Test configuration sources
        config_tests = [
            ("snowflake_account", "ZNB04675"),
            ("snowflake_user", "SCOOBYJAVA15"),
            ("snowflake_role", "SYSADMIN"),
            ("snowflake_warehouse", "SOPHIA_AI_WH"),
            ("snowflake_database", "SOPHIA_AI_PROD"),
        ]

        for key, expected in config_tests:
            value = get_config_value(key)
            logger.info(f"🔍 {key}: {value}")

            if value != expected:
                logger.warning(f"⚠️ {key} expected '{expected}', got '{value}'")

        # Test SecurityConfig
        security_config = SecurityConfig()
        non_secret_config = security_config.NON_SECRET_CONFIG

        logger.info("🔍 SecurityConfig.NON_SECRET_CONFIG:")
        for key, value in non_secret_config.items():
            if "snowflake" in key:
                logger.info(f"   {key}: {value}")

        return True

    except Exception as e:
        logger.error(f"❌ Configuration loading test failed: {e}")
        return False


def main():
    """Main test function."""
    logger.info("🚀 Starting Snowflake connection diagnostics")

    # Test configuration loading
    config_success = test_configuration_loading()

    if not config_success:
        logger.error("❌ Configuration loading failed, skipping connection test")
        return 1

    # Test Snowflake connection
    connection_success = test_snowflake_connection()

    if connection_success:
        logger.info(
            "🎉 All tests passed! Snowflake configuration is working correctly."
        )
        return 0
    else:
        logger.error(
            "❌ Connection test failed. Please check the error messages above."
        )
        return 1


if __name__ == "__main__":
    exit(main())
