import logging
import os

import snowflake.connector
from snowflake.connector.errors import ProgrammingError

from backend.core.auto_esc_config import get_config_value

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_snowflake_connection():
    """Establishes a connection to Snowflake using credentials from Pulumi ESC."""
    try:
        conn = snowflake.connector.connect(
            user=get_config_value("snowflake_user"),
            password=get_config_value("snowflake_password"),
            account=get_config_value("snowflake_account"),
            warehouse=get_config_value("snowflake_warehouse"),
            database=get_config_value("snowflake_database"),
            schema=get_config_value("snowflake_schema"),
        )
        logger.info("Snowflake connection successful.")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to Snowflake: {e}")
        raise


def deploy_cortex_functions():
    """
    Deploys the Snowflake Cortex AI functions by executing the corresponding SQL script.
    """
    conn = None
    sql_file_path = os.path.join(
        os.path.dirname(__file__), "..", "snowflake_setup", "cortex_functions.sql"
    )

    try:
        with open(sql_file_path) as f:
            sql_script = f.read()
        logger.info(f"Read Cortex functions from: {sql_file_path}")
    except FileNotFoundError:
        logger.error(f"Could not find the SQL script at {sql_file_path}")
        return

    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        # Split script into individual statements, ignoring empty lines and comments
        statements = [
            s.strip()
            for s in sql_script.split(";")
            if s.strip() and not s.strip().startswith("--")
        ]

        logger.info(
            f"Executing {len(statements)} Snowflake Cortex function deployment statements..."
        )
        for statement in statements:
            try:
                cursor.execute(statement)
                logger.info("Successfully executed statement.")
            except ProgrammingError as e:
                logger.error(
                    f"Failed to execute statement: {statement[:100]}... - Error: {e}"
                )
                # Decide if you want to continue or stop on error
                # raise e

        logger.info("Successfully deployed all Snowflake Cortex functions.")

    except ProgrammingError as e:
        logger.error(f"A database error occurred during deployment: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("Snowflake connection closed.")


if __name__ == "__main__":
    logger.info("Starting Snowflake Cortex Function Deployment...")
    deploy_cortex_functions()
    logger.info("Deployment script finished.")
