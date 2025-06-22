"""Snowflake Integration for Sophia AI.

Provides a secure and efficient way to connect to and query the Snowflake data warehouse:
    """

import asyncio
import json
import logging
from typing import Any, Dict, List

import snowflake.connector
from snowflake.connector.errors import ProgrammingError

from infrastructure.esc.snowflake_secrets import snowflake_secret_manager

logger = logging.getLogger(__name__)


class SnowflakeIntegration:
    """Handles the connection and querying logic for Snowflake."""

    def __init__(self):
        self.connection = None
        self.credentials = None

    async def initialize(self):
        """Initializes the connection to Snowflake using credentials from the secret manager."""
        if self.connection:
            return

        logger.info("Initializing Snowflake integration...")
        try:
            self.credentials = (
                await snowflake_secret_manager.get_snowflake_credentials()
            )

            # The Snowflake connector's connect method is synchronous,
            # so we run it in an executor to avoid blocking the asyncio event loop.
            loop = asyncio.get_running_loop()
            self.connection = await loop.run_in_executor(
                None,  # Uses the default ThreadPoolExecutor
                snowflake.connector.connect,
                user=self.credentials.user,
                password=self.credentials.password,
                account=self.credentials.account,
                warehouse=self.credentials.warehouse,
                database=self.credentials.database,
                schema=self.credentials.schema,
                role=self.credentials.role,
            )
            logger.info("Successfully connected to Snowflake.")
        except ProgrammingError as e:
            logger.error(f"Snowflake authentication error: {e}")
            raise ConnectionError(
                "Snowflake authentication failed. Please check your credentials."
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize Snowflake connection: {e}", exc_info=True
            )
            raise

    async def close(self):
        """Closes the Snowflake connection."""
        if self.connection and not self.connection.is_closed():
            logger.info("Closing Snowflake connection.")
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self.connection.close)

    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Executes a SQL query against the Snowflake database.

        Args:
            query: The SQL query string to execute.

        Returns:
            A list of dictionaries, where each dictionary represents a row."""
        """
        if not self.connection:
            await self.initialize()
"""
        logger.info(f"Executing Snowflake query: {query[:100]}...")

        try:
            # Run the synchronous database call in a thread pool
            loop = asyncio.get_running_loop()
            cursor = await loop.run_in_executor(None, self.connection.cursor)

            await loop.run_in_executor(None, cursor.execute, query)

            # Fetch results
            column_names = [desc[0] for desc in cursor.description]
            rows = await loop.run_in_executor(None, cursor.fetchall)

            # Format results as a list of dictionaries
            results = [dict(zip(column_names, row)) for row in rows]

            logger.info(f"Query executed successfully, fetched {len(results)} rows.")
            return results

        except ProgrammingError as e:
            logger.error(f"Error executing Snowflake query: {e}")
            raise ValueError(f"Invalid SQL query: {e}")
        finally:
            if "cursor" in locals() and cursor:
                await loop.run_in_executor(None, cursor.close)

    async def upsert_gong_call(self, analytics_data: Dict[str, Any]):
        """Upserts a single processed Gong call and its related analytics.

        into all the relevant Snowflake tables in a single transaction.

        Args:
            analytics_data: The dictionary returned by `process_call_for_analytics`."""
        """
        if not self.connection:
            await self.initialize()
"""
        call_id = analytics_data.get("call_id")
        if not call_id:
            raise ValueError("Cannot upsert Gong call without a call_id.")

        loop = asyncio.get_running_loop()
        cursor = await loop.run_in_executor(None, self.connection.cursor)

        try:
            logger.info(f"Beginning upsert transaction for call_id: {call_id}")

            await loop.run_in_executor(None, cursor.execute, "BEGIN")

            # 1. Upsert into gong_calls
            raw_call = analytics_data.get("raw_call_data", {})
            call_sql = """
                INSERT INTO gong_calls (call_id, title, url, started_at, duration_seconds, apartment_relevance_score)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (call_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    url = EXCLUDED.url,
                    started_at = EXCLUDED.started_at,
                    duration_seconds = EXCLUDED.duration_seconds,
                    apartment_relevance_score = EXCLUDED.apartment_relevance_score,
                    updated_at = CURRENT_TIMESTAMP();"""
            """
            await loop.run_in_executor(
                None,
                cursor.execute,
                call_sql,
                (
                    call_id,"""
                    raw_call.get("title"),
                    raw_call.get("url"),
                    raw_call.get("started"),
                    raw_call.get("duration"),
                    analytics_data.get("apartment_relevance_score"),
                ),
            )

            # 2. Upsert into sophia_deal_signals
            deal_signals = analytics_data.get("deal_signals", {})
            signals_sql = """
                INSERT INTO sophia_deal_signals (call_id, positive_signals, negative_signals, deal_progression_stage, win_probability)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (call_id) DO UPDATE SET
                    positive_signals = EXCLUDED.positive_signals,
                    negative_signals = EXCLUDED.negative_signals,
                    deal_progression_stage = EXCLUDED.deal_progression_stage,
                    win_probability = EXCLUDED.win_probability,
                    updated_at = CURRENT_TIMESTAMP();"""
            """
            await loop.run_in_executor(
                None,
                cursor.execute,
                signals_sql,
                (
                    call_id,"""
                    json.dumps(deal_signals.get("positive_signals")),
                    json.dumps(deal_signals.get("negative_signals")),
                    deal_signals.get("deal_progression_stage"),
                    deal_signals.get("win_probability"),
                ),
            )

            # 3. Upsert into sophia_competitive_intelligence
            comp_intel = analytics_data.get("competitive_intelligence", {})
            comp_sql = """
                INSERT INTO sophia_competitive_intelligence (call_id, competitors_mentioned, competitive_threat_level)
                VALUES (%s, %s, %s)
                ON CONFLICT (call_id) DO UPDATE SET
                    competitors_mentioned = EXCLUDED.competitors_mentioned,
                    competitive_threat_level = EXCLUDED.competitive_threat_level,
                    updated_at = CURRENT_TIMESTAMP();"""
            """
            await loop.run_in_executor(
                None,
                cursor.execute,
                comp_sql,
                (
                    call_id,"""
                    json.dumps(comp_intel.get("competitors_mentioned")),
                    comp_intel.get("competitive_threat_level"),
                ),
            )

            await loop.run_in_executor(None, cursor.execute, "COMMIT")
            logger.info(f"Successfully committed transaction for call_id: {call_id}")

        except Exception as e:
            logger.error(
                f"Transaction failed for call_id {call_id}: {e}", exc_info=True
            )
            await loop.run_in_executor(None, cursor.execute, "ROLLBACK")
            raise
        finally:
            if cursor:
                await loop.run_in_executor(None, cursor.close)


# Global instance for easy, shared access
snowflake_integration = SnowflakeIntegration()

"""