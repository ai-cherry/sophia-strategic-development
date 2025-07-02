"""
PostgreSQL Staging Manager for Sophia AI
Manages the staging layer in the data pipeline: Estuary Flow → PostgreSQL → Redis → Snowflake
Handles schema creation, data transformation, and pipeline orchestration
"""

import logging
from dataclasses import dataclass
from typing import Any

import asyncpg

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


@dataclass
class PostgreSQLConfig:
    """Configuration for PostgreSQL staging database"""

    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "require"


@dataclass
class StagingSchema:
    """Definition of a staging schema"""

    name: str
    tables: list[str]
    indexes: list[str]
    transforms: list[str]


class PostgreSQLStagingManager:
    """
    Manages PostgreSQL staging layer for Sophia AI data pipeline
    Handles raw data ingestion, transformation, and preparation for Snowflake
    """

    def __init__(self):
        self.config = PostgreSQLConfig(
            host=get_config_value("postgresql_host"),
            port=get_config_value("postgresql_port", 5432),
            database=get_config_value("postgresql_database", "sophia_staging"),
            username=get_config_value("postgresql_user"),
            password=get_config_value("postgresql_password"),
            ssl_mode=get_config_value("postgresql_ssl_mode", "require"),
        )
        self.pool: asyncpg.Pool | None = None
        self._validate_config()

    def _validate_config(self):
        """Validate PostgreSQL configuration"""
        required_fields = ["host", "username", "password"]
        missing = [
            field for field in required_fields if not getattr(self.config, field)
        ]

        if missing:
            raise ValueError(f"Missing PostgreSQL configuration: {missing}")

        logger.info(
            f"PostgreSQL staging manager initialized for {self.config.host}:{self.config.port}"
        )

    async def initialize_pool(self, min_size: int = 5, max_size: int = 20):
        """Initialize connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                ssl=self.config.ssl_mode,
                min_size=min_size,
                max_size=max_size,
            )
            logger.info(
                f"PostgreSQL connection pool initialized ({min_size}-{max_size} connections)"
            )
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise

    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize_pool()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_pool()

    async def execute_query(self, query: str, *args) -> Any:
        """Execute a query with connection from pool"""
        if not self.pool:
            raise RuntimeError("Connection pool not initialized")

        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch_query(self, query: str, *args) -> list[dict[str, Any]]:
        """Fetch query results with connection from pool"""
        if not self.pool:
            raise RuntimeError("Connection pool not initialized")

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def create_staging_schemas(self):
        """Create all staging schemas for data sources"""
        schemas = [
            self._get_hubspot_schema(),
            self._get_gong_schema(),
            self._get_slack_schema(),
            self._get_processed_schema(),
        ]

        for schema in schemas:
            await self._create_schema(schema)

    def _get_hubspot_schema(self) -> StagingSchema:
        """Define HubSpot staging schema"""
        return StagingSchema(
            name="hubspot_raw",
            tables=[
                """
                CREATE TABLE IF NOT EXISTS hubspot_raw.contacts (
                    id BIGINT PRIMARY KEY,
                    email VARCHAR(255),
                    firstname VARCHAR(255),
                    lastname VARCHAR(255),
                    company VARCHAR(255),
                    jobtitle VARCHAR(255),
                    phone VARCHAR(50),
                    website VARCHAR(255),
                    lifecyclestage VARCHAR(100),
                    lead_status VARCHAR(100),
                    createdate TIMESTAMP WITH TIME ZONE,
                    lastmodifieddate TIMESTAMP WITH TIME ZONE,
                    properties JSONB,
                    _estuary_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    _estuary_source_system VARCHAR(50) DEFAULT 'hubspot'
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS hubspot_raw.companies (
                    id BIGINT PRIMARY KEY,
                    name VARCHAR(255),
                    domain VARCHAR(255),
                    industry VARCHAR(255),
                    city VARCHAR(255),
                    state VARCHAR(255),
                    country VARCHAR(255),
                    numberofemployees INTEGER,
                    annualrevenue DECIMAL(15,2),
                    createdate TIMESTAMP WITH TIME ZONE,
                    properties JSONB,
                    _estuary_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    _estuary_source_system VARCHAR(50) DEFAULT 'hubspot'
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS hubspot_raw.deals (
                    id BIGINT PRIMARY KEY,
                    dealname VARCHAR(255),
                    amount DECIMAL(15,2),
                    dealstage VARCHAR(255),
                    pipeline VARCHAR(255),
                    closedate TIMESTAMP WITH TIME ZONE,
                    createdate TIMESTAMP WITH TIME ZONE,
                    hubspot_owner_id BIGINT,
                    properties JSONB,
                    _estuary_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    _estuary_source_system VARCHAR(50) DEFAULT 'hubspot'
                )
                """,
            ],
            indexes=[
                "CREATE INDEX IF NOT EXISTS idx_hubspot_contacts_email ON hubspot_raw.contacts(email)",
                "CREATE INDEX IF NOT EXISTS idx_hubspot_contacts_company ON hubspot_raw.contacts(company)",
                "CREATE INDEX IF NOT EXISTS idx_hubspot_companies_domain ON hubspot_raw.companies(domain)",
                "CREATE INDEX IF NOT EXISTS idx_hubspot_deals_stage ON hubspot_raw.deals(dealstage)",
                "CREATE INDEX IF NOT EXISTS idx_hubspot_deals_closedate ON hubspot_raw.deals(closedate)",
            ],
            transforms=[
                """
                CREATE OR REPLACE VIEW hubspot_processed.contacts_enriched AS
                SELECT
                    c.*,
                    co.name as company_name,
                    co.industry as company_industry,
                    co.numberofemployees as company_size
                FROM hubspot_raw.contacts c
                LEFT JOIN hubspot_raw.companies co ON c.company = co.name
                """
            ],
        )

    def _get_gong_schema(self) -> StagingSchema:
        """Define Gong staging schema"""
        return StagingSchema(
            name="gong_raw",
            tables=[
                """
                CREATE TABLE IF NOT EXISTS gong_raw.calls (
                    id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(500),
                    url VARCHAR(500),
                    purpose VARCHAR(255),
                    meeting_url VARCHAR(500),
                    scheduled TIMESTAMP WITH TIME ZONE,
                    started TIMESTAMP WITH TIME ZONE,
                    duration INTEGER,
                    primary_user_id VARCHAR(255),
                    direction VARCHAR(50),
                    system VARCHAR(100),
                    scope VARCHAR(100),
                    media VARCHAR(100),
                    language VARCHAR(10),
                    workspace_id VARCHAR(255),
                    properties JSONB,
                    _estuary_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    _estuary_source_system VARCHAR(50) DEFAULT 'gong'
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS gong_raw.call_transcripts (
                    call_id VARCHAR(255),
                    speaker_id VARCHAR(255),
                    speaker_name VARCHAR(255),
                    speaker_email VARCHAR(255),
                    start_time INTEGER,
                    end_time INTEGER,
                    text TEXT,
                    sentiment DECIMAL(3,2),
                    properties JSONB,
                    _estuary_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    _estuary_source_system VARCHAR(50) DEFAULT 'gong',
                    PRIMARY KEY (call_id, start_time)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS gong_raw.users (
                    id VARCHAR(255) PRIMARY KEY,
                    email_address VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    title VARCHAR(255),
                    phone_number VARCHAR(50),
                    extension VARCHAR(20),
                    personal_meeting_room VARCHAR(500),
                    created TIMESTAMP WITH TIME ZONE,
                    active BOOLEAN,
                    properties JSONB,
                    _estuary_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    _estuary_source_system VARCHAR(50) DEFAULT 'gong'
                )
                """,
            ],
            indexes=[
                "CREATE INDEX IF NOT EXISTS idx_gong_calls_started ON gong_raw.calls(started)",
                "CREATE INDEX IF NOT EXISTS idx_gong_calls_user ON gong_raw.calls(primary_user_id)",
                "CREATE INDEX IF NOT EXISTS idx_gong_transcripts_call ON gong_raw.call_transcripts(call_id)",
                "CREATE INDEX IF NOT EXISTS idx_gong_transcripts_sentiment ON gong_raw.call_transcripts(sentiment)",
                "CREATE INDEX IF NOT EXISTS idx_gong_users_email ON gong_raw.users(email_address)",
            ],
            transforms=[
                """
                CREATE OR REPLACE VIEW gong_processed.call_analytics AS
                SELECT
                    c.id,
                    c.title,
                    c.started,
                    c.duration,
                    u.first_name || ' ' || u.last_name as primary_user_name,
                    u.email_address as primary_user_email,
                    AVG(t.sentiment) as avg_sentiment,
                    COUNT(t.speaker_id) as speaker_count,
                    STRING_AGG(DISTINCT t.speaker_name, ', ') as participants
                FROM gong_raw.calls c
                LEFT JOIN gong_raw.users u ON c.primary_user_id = u.id
                LEFT JOIN gong_raw.call_transcripts t ON c.id = t.call_id
                GROUP BY c.id, c.title, c.started, c.duration, u.first_name, u.last_name, u.email_address
                """
            ],
        )

    def _get_slack_schema(self) -> StagingSchema:
        """Define Slack staging schema"""
        return StagingSchema(
            name="slack_raw",
            tables=[
                """
                CREATE TABLE IF NOT EXISTS slack_raw.messages (
                    ts VARCHAR(50) PRIMARY KEY,
                    channel VARCHAR(50),
                    user_id VARCHAR(50),
                    text TEXT,
                    thread_ts VARCHAR(50),
                    reply_count INTEGER DEFAULT 0,
                    reply_users_count INTEGER DEFAULT 0,
                    latest_reply VARCHAR(50),
                    message_type VARCHAR(50),
                    subtype VARCHAR(50),
                    created_at TIMESTAMP WITH TIME ZONE,
                    properties JSONB,
                    _estuary_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    _estuary_source_system VARCHAR(50) DEFAULT 'slack'
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS slack_raw.channels (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255),
                    is_channel BOOLEAN,
                    is_group BOOLEAN,
                    is_im BOOLEAN,
                    is_mpim BOOLEAN,
                    is_private BOOLEAN,
                    is_archived BOOLEAN,
                    is_general BOOLEAN,
                    is_shared BOOLEAN,
                    is_org_shared BOOLEAN,
                    creator VARCHAR(50),
                    created TIMESTAMP WITH TIME ZONE,
                    topic_value TEXT,
                    purpose_value TEXT,
                    num_members INTEGER,
                    properties JSONB,
                    _estuary_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    _estuary_source_system VARCHAR(50) DEFAULT 'slack'
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS slack_raw.users (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255),
                    real_name VARCHAR(255),
                    display_name VARCHAR(255),
                    email VARCHAR(255),
                    title VARCHAR(255),
                    phone VARCHAR(50),
                    is_admin BOOLEAN,
                    is_owner BOOLEAN,
                    is_primary_owner BOOLEAN,
                    is_restricted BOOLEAN,
                    is_ultra_restricted BOOLEAN,
                    is_bot BOOLEAN,
                    is_app_user BOOLEAN,
                    updated TIMESTAMP WITH TIME ZONE,
                    properties JSONB,
                    _estuary_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    _estuary_source_system VARCHAR(50) DEFAULT 'slack'
                )
                """,
            ],
            indexes=[
                "CREATE INDEX IF NOT EXISTS idx_slack_messages_channel ON slack_raw.messages(channel)",
                "CREATE INDEX IF NOT EXISTS idx_slack_messages_user ON slack_raw.messages(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_slack_messages_created ON slack_raw.messages(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_slack_channels_name ON slack_raw.channels(name)",
                "CREATE INDEX IF NOT EXISTS idx_slack_users_email ON slack_raw.users(email)",
            ],
            transforms=[
                """
                CREATE OR REPLACE VIEW slack_processed.channel_activity AS
                SELECT
                    c.name as channel_name,
                    c.purpose_value as channel_purpose,
                    COUNT(m.ts) as message_count,
                    COUNT(DISTINCT m.user_id) as active_users,
                    MIN(m.created_at) as first_message,
                    MAX(m.created_at) as last_message
                FROM slack_raw.channels c
                LEFT JOIN slack_raw.messages m ON c.id = m.channel
                WHERE c.is_archived = false
                GROUP BY c.id, c.name, c.purpose_value
                """
            ],
        )

    def _get_processed_schema(self) -> StagingSchema:
        """Define processed data schema for Snowflake ingestion"""
        return StagingSchema(
            name="processed_data",
            tables=[
                """
                CREATE TABLE IF NOT EXISTS processed_data.unified_contacts (
                    id VARCHAR(255) PRIMARY KEY,
                    source_system VARCHAR(50),
                    source_id VARCHAR(255),
                    email VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    full_name VARCHAR(500),
                    company_name VARCHAR(255),
                    job_title VARCHAR(255),
                    phone VARCHAR(50),
                    created_at TIMESTAMP WITH TIME ZONE,
                    updated_at TIMESTAMP WITH TIME ZONE,
                    last_activity TIMESTAMP WITH TIME ZONE,
                    properties JSONB,
                    _processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS processed_data.interaction_timeline (
                    id VARCHAR(255) PRIMARY KEY,
                    contact_id VARCHAR(255),
                    interaction_type VARCHAR(100),
                    interaction_date TIMESTAMP WITH TIME ZONE,
                    source_system VARCHAR(50),
                    source_id VARCHAR(255),
                    title VARCHAR(500),
                    description TEXT,
                    sentiment DECIMAL(3,2),
                    metadata JSONB,
                    _processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
                """,
            ],
            indexes=[
                "CREATE INDEX IF NOT EXISTS idx_unified_contacts_email ON processed_data.unified_contacts(email)",
                "CREATE INDEX IF NOT EXISTS idx_unified_contacts_company ON processed_data.unified_contacts(company_name)",
                "CREATE INDEX IF NOT EXISTS idx_interaction_timeline_contact ON processed_data.interaction_timeline(contact_id)",
                "CREATE INDEX IF NOT EXISTS idx_interaction_timeline_date ON processed_data.interaction_timeline(interaction_date)",
            ],
            transforms=[],
        )

    async def _create_schema(self, schema: StagingSchema):
        """Create a staging schema with tables and indexes"""
        try:
            # Create schema
            await self.execute_query(f"CREATE SCHEMA IF NOT EXISTS {schema.name}")
            logger.info(f"Created schema: {schema.name}")

            # Create tables
            for table_sql in schema.tables:
                await self.execute_query(table_sql)

            # Create indexes
            for index_sql in schema.indexes:
                await self.execute_query(index_sql)

            # Create transforms (views, functions)
            for transform_sql in schema.transforms:
                await self.execute_query(transform_sql)

            logger.info(
                f"Successfully created schema {schema.name} with {len(schema.tables)} tables"
            )

        except Exception as e:
            logger.error(f"Failed to create schema {schema.name}: {e}")
            raise

    async def run_data_transformations(self):
        """Run data transformations to prepare data for Snowflake"""
        transformations = [
            self._transform_hubspot_data,
            self._transform_gong_data,
            self._transform_slack_data,
            self._create_unified_contacts,
            self._create_interaction_timeline,
        ]

        for transform in transformations:
            try:
                await transform()
                logger.info(f"Completed transformation: {transform.__name__}")
            except Exception as e:
                logger.error(f"Transformation failed {transform.__name__}: {e}")
                raise

    async def _transform_hubspot_data(self):
        """Transform HubSpot raw data"""
        await self.execute_query(
            """
            INSERT INTO processed_data.unified_contacts (
                id, source_system, source_id, email, first_name, last_name,
                full_name, company_name, job_title, phone, created_at, updated_at, properties
            )
            SELECT
                'hubspot_' || id::text,
                'hubspot',
                id::text,
                email,
                firstname,
                lastname,
                COALESCE(firstname, '') || ' ' || COALESCE(lastname, ''),
                company,
                jobtitle,
                phone,
                createdate,
                lastmodifieddate,
                properties
            FROM hubspot_raw.contacts
            ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                full_name = EXCLUDED.full_name,
                company_name = EXCLUDED.company_name,
                job_title = EXCLUDED.job_title,
                phone = EXCLUDED.phone,
                updated_at = EXCLUDED.updated_at,
                properties = EXCLUDED.properties,
                _processed_at = CURRENT_TIMESTAMP
        """
        )

    async def _transform_gong_data(self):
        """Transform Gong raw data"""
        await self.execute_query(
            """
            INSERT INTO processed_data.interaction_timeline (
                id, contact_id, interaction_type, interaction_date,
                source_system, source_id, title, description, sentiment, metadata
            )
            SELECT
                'gong_call_' || c.id,
                'gong_user_' || c.primary_user_id,
                'call',
                c.started,
                'gong',
                c.id,
                c.title,
                'Gong call: ' || COALESCE(c.purpose, 'No purpose specified'),
                (SELECT AVG(sentiment) FROM gong_raw.call_transcripts WHERE call_id = c.id),
                jsonb_build_object(
                    'duration', c.duration,
                    'direction', c.direction,
                    'system', c.system,
                    'meeting_url', c.meeting_url
                )
            FROM gong_raw.calls c
            ON CONFLICT (id) DO UPDATE SET
                interaction_date = EXCLUDED.interaction_date,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                sentiment = EXCLUDED.sentiment,
                metadata = EXCLUDED.metadata,
                _processed_at = CURRENT_TIMESTAMP
        """
        )

    async def _transform_slack_data(self):
        """Transform Slack raw data"""
        await self.execute_query(
            """
            INSERT INTO processed_data.interaction_timeline (
                id, contact_id, interaction_type, interaction_date,
                source_system, source_id, title, description, metadata
            )
            SELECT
                'slack_msg_' || m.ts,
                'slack_user_' || m.user_id,
                'message',
                m.created_at,
                'slack',
                m.ts,
                'Slack message in #' || c.name,
                LEFT(m.text, 500),
                jsonb_build_object(
                    'channel', c.name,
                    'channel_id', m.channel,
                    'thread_ts', m.thread_ts,
                    'reply_count', m.reply_count
                )
            FROM slack_raw.messages m
            LEFT JOIN slack_raw.channels c ON m.channel = c.id
            WHERE m.text IS NOT NULL AND LENGTH(m.text) > 0
            ON CONFLICT (id) DO UPDATE SET
                interaction_date = EXCLUDED.interaction_date,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                metadata = EXCLUDED.metadata,
                _processed_at = CURRENT_TIMESTAMP
        """
        )

    async def _create_unified_contacts(self):
        """Create unified contact records from all sources"""
        # This is handled in individual transform methods
        pass

    async def _create_interaction_timeline(self):
        """Create unified interaction timeline"""
        # This is handled in individual transform methods
        pass

    async def get_pipeline_metrics(self) -> dict[str, Any]:
        """Get metrics about the data pipeline"""
        metrics = {}

        # Raw data counts
        for schema in ["hubspot_raw", "gong_raw", "slack_raw"]:
            schema_metrics = await self.fetch_query(
                """
                SELECT
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_rows
                FROM pg_stat_user_tables
                WHERE schemaname = $1
            """,
                schema,
            )
            metrics[schema] = schema_metrics

        # Processed data counts
        processed_metrics = await self.fetch_query(
            """
            SELECT
                'unified_contacts' as table_name,
                COUNT(*) as total_records,
                COUNT(DISTINCT source_system) as source_systems,
                MAX(_processed_at) as last_processed
            FROM processed_data.unified_contacts
            UNION ALL
            SELECT
                'interaction_timeline' as table_name,
                COUNT(*) as total_records,
                COUNT(DISTINCT source_system) as source_systems,
                MAX(_processed_at) as last_processed
            FROM processed_data.interaction_timeline
        """
        )
        metrics["processed_data"] = processed_metrics

        return metrics


# Utility functions
async def setup_postgresql_staging():
    """Set up PostgreSQL staging environment"""
    async with PostgreSQLStagingManager() as manager:
        await manager.create_staging_schemas()
        logger.info("PostgreSQL staging environment setup complete")


async def run_data_pipeline():
    """Run the complete data transformation pipeline"""
    async with PostgreSQLStagingManager() as manager:
        await manager.run_data_transformations()
        metrics = await manager.get_pipeline_metrics()
        logger.info(f"Data pipeline completed. Metrics: {metrics}")
        return metrics
