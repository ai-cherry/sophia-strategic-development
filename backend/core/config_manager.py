"""
Configuration Manager for Sophia AI
Handles database connections and configuration management
"""

import logging

import snowflake.connector

from backend.core.auto_esc_config import get_snowflake_config

logger = logging.getLogger(__name__)


def get_snowflake_connection() -> snowflake.connector.SnowflakeConnection:
    """
    Get Snowflake database connection

    Returns:
        Snowflake connection object
    """
    config = get_snowflake_config()

    try:
        connection = snowflake.connector.connect(
            account=config["account"],
            user=config["user"],
            password=config["password"],
            role=config["role"],
            warehouse=config["warehouse"],
            database=config["database"],
            schema=config["schema"],
        )

        logger.info(f"Connected to Snowflake: {config['account']}")
        return connection

    except Exception as e:
        logger.error(f"Failed to connect to Snowflake: {e}")
        raise


def test_snowflake_connection() -> bool:
    """
    Test Snowflake connection

    Returns:
        True if connection successful, False otherwise
    """
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        logger.info(f"Snowflake connection test successful: {result[0]}")
        return True

    except Exception as e:
        logger.error(f"Snowflake connection test failed: {e}")
        return False
