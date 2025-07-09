#!/usr/bin/env python3
"""
from backend.core.auto_esc_config import get_config_value
Gong API Data Extractor
Secure implementation for Sophia AI Platform
"""

import asyncio
import base64
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiohttp
import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GongConfig:
    """Gong API configuration"""

    access_key: str
    access_key_secret: str
    base_url: str = "https://api.gong.io"
    rate_limit_delay: float = 0.34  # 3 calls/second
    max_retries: int = 3


class GongAPIExtractor:
    """Secure Gong API data extraction service"""

    def __init__(self):
        self.config = self._load_config()
        self.session: aiohttp.ClientSession | None = None

    def _load_config(self) -> GongConfig:
        """Load configuration from environment variables"""
        access_key = get_config_value("gong_access_key")
        access_key_secret = get_config_value("gong_access_key_secret")

        if not access_key or not access_key_secret:
            raise ValueError("Gong API credentials not found in environment variables")

        return GongConfig(access_key=access_key, access_key_secret=access_key_secret)

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _get_auth_header(self) -> str:
        """Generate Basic Auth header"""
        credentials = f"{self.config.access_key}:{self.config.access_key_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    async def _make_request(self, endpoint: str, params: dict | None = None) -> dict:
        """Make authenticated request to Gong API with rate limiting"""
        url = f"{self.config.base_url}{endpoint}"
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json",
        }

        for attempt in range(self.config.max_retries):
            try:
                await asyncio.sleep(self.config.rate_limit_delay)

                async with self.session.get(
                    url, headers=headers, params=params
                ) as response:
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning(
                            f"Rate limited. Waiting {retry_after} seconds..."
                        )
                        await asyncio.sleep(retry_after)
                        continue

                    response.raise_for_status()
                    return await response.json()

            except Exception as e:
                logger.exception(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)

    async def extract_calls(self, days_back: int = 7) -> list[dict]:
        """Extract call data from Gong API"""
        logger.info(f"Extracting calls from last {days_back} days")

        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        params = {
            "fromDateTime": start_date,
            "contentSelector": [
                "parties",
                "content",
                "context",
                "interaction",
                "pointsOfInterest",
                "questions",
                "trackers",
                "topics",
            ],
        }

        calls = []
        cursor = None

        while True:
            if cursor:
                params["cursor"] = cursor

            response = await self._make_request("/v2/calls/extensive", params)

            if "calls" in response:
                calls.extend(response["calls"])
                logger.info(f"Extracted {len(response['calls'])} calls")

            cursor = response.get("records", {}).get("cursor")
            if not cursor:
                break

        logger.info(f"Total calls extracted: {len(calls)}")
        return calls

    async def extract_users(self) -> list[dict]:
        """Extract user data from Gong API"""
        logger.info("Extracting user data")

        response = await self._make_request("/v2/users")
        users = response.get("users", [])

        logger.info(f"Extracted {len(users)} users")
        return users

    async def extract_crm_entities(self, days_back: int = 7) -> list[dict]:
        """Extract CRM entity changes"""
        logger.info(f"Extracting CRM entities from last {days_back} days")

        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        params = {"fromDateTime": start_date}

        response = await self._make_request("/v2/crm/entities/changed", params)
        entities = response.get("entities", [])

        logger.info(f"Extracted {len(entities)} CRM entities")
        return entities


class PostgreSQLStaging:
    """PostgreSQL staging database manager"""

    def __init__(self):
        self.connection_string = os.getenv("POSTGRESQL_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("PostgreSQL connection string not found")

    async def create_tables(self):
        """Create staging tables if they don't exist"""
        conn = await asyncpg.connect(self.connection_string)

        try:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS gong_calls_staging (
                    id VARCHAR PRIMARY KEY,
                    data JSONB NOT NULL,
                    extracted_at TIMESTAMP DEFAULT NOW(),
                    processed BOOLEAN DEFAULT FALSE
                )
            """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS gong_users_staging (
                    id VARCHAR PRIMARY KEY,
                    data JSONB NOT NULL,
                    extracted_at TIMESTAMP DEFAULT NOW(),
                    processed BOOLEAN DEFAULT FALSE
                )
            """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS gong_crm_entities_staging (
                    id VARCHAR PRIMARY KEY,
                    data JSONB NOT NULL,
                    extracted_at TIMESTAMP DEFAULT NOW(),
                    processed BOOLEAN DEFAULT FALSE
                )
            """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pipeline_status (
                    pipeline_id VARCHAR PRIMARY KEY,
                    status VARCHAR NOT NULL,
                    records_processed INTEGER DEFAULT 0,
                    started_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP,
                    error_message TEXT
                )
            """
            )

            logger.info("Staging tables created successfully")

        finally:
            await conn.close()

    async def store_calls(self, calls: list[dict]) -> int:
        """Store calls in staging table"""
        if not calls:
            return 0

        conn = await asyncpg.connect(self.connection_string)

        try:
            records = [(call.get("id", ""), json.dumps(call)) for call in calls]

            await conn.executemany(
                "INSERT INTO gong_calls_staging (id, data) VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET data = $2, extracted_at = NOW()",
                records,
            )

            logger.info(f"Stored {len(records)} calls in staging")
            return len(records)

        finally:
            await conn.close()

    async def store_users(self, users: list[dict]) -> int:
        """Store users in staging table"""
        if not users:
            return 0

        conn = await asyncpg.connect(self.connection_string)

        try:
            records = [(user.get("id", ""), json.dumps(user)) for user in users]

            await conn.executemany(
                "INSERT INTO gong_users_staging (id, data) VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET data = $2, extracted_at = NOW()",
                records,
            )

            logger.info(f"Stored {len(records)} users in staging")
            return len(records)

        finally:
            await conn.close()

    async def store_crm_entities(self, entities: list[dict]) -> int:
        """Store CRM entities in staging table"""
        if not entities:
            return 0

        conn = await asyncpg.connect(self.connection_string)

        try:
            records = [
                (entity.get("id", ""), json.dumps(entity)) for entity in entities
            ]

            await conn.executemany(
                "INSERT INTO gong_crm_entities_staging (id, data) VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET data = $2, extracted_at = NOW()",
                records,
            )

            logger.info(f"Stored {len(records)} CRM entities in staging")
            return len(records)

        finally:
            await conn.close()

    async def update_pipeline_status(
        self,
        pipeline_id: str,
        status: str,
        records_processed: int = 0,
        error_message: str | None = None,
    ):
        """Update pipeline execution status"""
        conn = await asyncpg.connect(self.connection_string)

        try:
            if status == "completed":
                await conn.execute(
                    """
                    INSERT INTO pipeline_status (pipeline_id, status, records_processed, completed_at)
                    VALUES ($1, $2, $3, NOW())
                    ON CONFLICT (pipeline_id) DO UPDATE SET
                        status = $2, records_processed = $3, completed_at = NOW()
                """,
                    pipeline_id,
                    status,
                    records_processed,
                )
            else:
                await conn.execute(
                    """
                    INSERT INTO pipeline_status (pipeline_id, status, records_processed, error_message)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (pipeline_id) DO UPDATE SET
                        status = $2, records_processed = $3, error_message = $4
                """,
                    pipeline_id,
                    status,
                    records_processed,
                    error_message,
                )

        finally:
            await conn.close()


async def main():
    """Main extraction pipeline"""
    pipeline_id = f"gong_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        # Initialize components
        staging = PostgreSQLStaging()
        await staging.create_tables()
        await staging.update_pipeline_status(pipeline_id, "started")

        total_records = 0

        async with GongAPIExtractor() as extractor:
            # Extract calls
            calls = await extractor.extract_calls(days_back=30)
            total_records += await staging.store_calls(calls)

            # Extract users
            users = await extractor.extract_users()
            total_records += await staging.store_users(users)

            # Extract CRM entities
            crm_entities = await extractor.extract_crm_entities(days_back=30)
            total_records += await staging.store_crm_entities(crm_entities)

        await staging.update_pipeline_status(pipeline_id, "completed", total_records)
        logger.info(f"Pipeline completed successfully. Total records: {total_records}")

    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        await staging.update_pipeline_status(pipeline_id, "failed", 0, str(e))
        raise


if __name__ == "__main__":
    asyncio.run(main())
