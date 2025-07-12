"""
Sophia AI - Apply PostgreSQL Staging Schema

This script connects to the PostgreSQL database and applies the
staging schema defined in infrastructure/postgres_setup/staging_schema.sql.

It ensures that the necessary tables, schemas, and the pgvector extension
are in place for the data ingestion pipeline.

Date: July 12, 2025
"""

import backend.utils.path_utils  # noqa: F401, must be before other imports

import asyncio
import logging
import sys
from pathlib import Path

import asyncpg

# Add project root to path for consistent imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from backend.core.auto_esc_config import get_config_value

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
)
logger = logging.getLogger(__name__)

SCHEMA_FILE = project_root / "infrastructure" / "postgres_setup" / "staging_schema.sql"


async def apply_schema():
    """
    Connects to the PostgreSQL database and applies the staging schema.
    """
    logger.info("--- Applying PostgreSQL Staging Schema ---")

    db_config = {
        "host": get_config_value("postgresql_host", "localhost"),
        "port": int(get_config_value("postgresql_port", "5432") or "5432"),
        "user": get_config_value("postgresql_user"),
        "password": get_config_value("postgresql_password"),
        "database": get_config_value("postgresql_database", "sophia_staging"),
    }

    if not all(db_config.values()):
        logger.error(
            "Database configuration is incomplete. Please check your environment/secrets."
        )
        logger.error(
            f"DB Config: { {k: (v is not None) for k,v in db_config.items()} }"
        )
        return

    conn = None
    try:
        logger.info(
            f"Connecting to database '{db_config['database']}' on host '{db_config['host']}'..."
        )
        conn = await asyncpg.connect(**db_config)
        logger.info("Database connection successful.")

        logger.info(f"Reading schema from {SCHEMA_FILE}...")
        with open(SCHEMA_FILE, "r") as f:
            schema_sql = f.read()

        logger.info("Executing schema setup script...")
        await conn.execute(schema_sql)
        logger.info("Schema script executed successfully.")

        logger.info("--- PostgreSQL Staging Schema applied successfully. ---")

    except FileNotFoundError:
        logger.exception(f"Schema file not found at {SCHEMA_FILE}")
    except asyncpg.PostgresError as e:
        logger.exception(f"A database error occurred: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            await conn.close()
            logger.info("Database connection closed.")


async def main():
    """Main entry point for the script."""
    await apply_schema()


if __name__ == "__main__":
    asyncio.run(main())
