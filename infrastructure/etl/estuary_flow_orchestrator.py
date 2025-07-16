"""
Estuary Flow Orchestrator for Sophia AI
Replaces estuary with Estuary Flow for real-time data pipeline management
Implements ELT pattern: Estuary Flow → PostgreSQL → Redis → Qdrant
"""

import backend.utils.path_utils  # noqa: F401, must be before other imports

import asyncio
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

# Add project root to path for consistent imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

logger = logging.getLogger(__name__)

@dataclass
class EstuaryFlowConfig:
    """Configuration for Estuary Flow integration"""

    api_url: str
    access_token: str
    tenant: str

@dataclass
class DataFlowSpec:
    """Specification for a data flow in Estuary Flow"""

    name: str
    source_type: str
    source_config: dict[str, Any]
    destination_type: str
    destination_config: dict[str, Any]
    transforms: list[dict[str, Any]] | None = None

class EstuaryFlowOrchestrator:
    """
    Orchestrates data pipelines using Estuary Flow
    Manages real-time data ingestion from HubSpot, Gong, Slack to PostgreSQL staging
    """

    def __init__(self):
        self.config = EstuaryFlowConfig(
            api_url=get_config_value("estuary_flow_api_url", "https://api.estuary.dev")
            or "https://api.estuary.dev",
            access_token=get_config_value("estuary_flow_access_token") or "",
            tenant=get_config_value("estuary_flow_tenant", "sophia-ai") or "sophia-ai",
        )
        self.session: aiohttp.ClientSession | None = None
        self._validate_config()

    def _validate_config(self):
        """Validate Estuary Flow configuration"""
        if not self.config.access_token:
            raise ValueError("Estuary Flow access token not configured")

        logger.info(
            f"Estuary Flow orchestrator initialized for tenant: {self.config.tenant}"
        )

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        reraise=True
    )
    async def _make_request(
        self, method: str, endpoint: str, data: dict | None = None
    ) -> dict[str, Any]:
        """Make authenticated request to Estuary Flow API with rate limiting retry"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")

        url = f"{self.config.api_url}/{endpoint}"

        try:
            async with self.session.request(method, url, json=data) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.exception(f"Estuary Flow API request failed: {e}")
            raise

    async def create_hubspot_flow(self) -> dict[str, Any]:
        """
        Create HubSpot → PostgreSQL data flow
        Real-time ingestion of contacts, companies, deals, and activities
        """
        flow_spec = DataFlowSpec(
            name="hubspot-to-postgresql",
            source_type="source-hubspot",
            source_config={
                "api_key": get_config_value("hubspot_api_key"),
                "start_date": "2024-01-01T00:00:00Z",
                "streams": [
                    "contacts",
                    "companies",
                    "deals",
                    "engagements",
                    "owners",
                    "pipelines",
                ],
            },
            destination_type="destination-postgres",
            destination_config={
                "host": get_config_value("postgresql_host"),
                "port": get_config_value("postgresql_port", "5432"),
                "database": get_config_value("postgresql_database", "sophia_staging"),
                "schema": "hubspot_raw",
                "username": get_config_value("postgresql_user"),
                "password": get_config_value("postgresql_password"),
                "ssl_mode": "require",
            },
            transforms=[
                {
                    "name": "add_ingestion_metadata",
                    "type": "sql",
                    "sql": """
                        SELECT *,
                               CURRENT_TIMESTAMP as _estuary_ingested_at,
                               'hubspot' as _estuary_source_system
                        FROM source_data
                    """,
                }
            ],
        )

        return await self._create_flow(flow_spec)

    async def create_gong_flow(self) -> dict[str, Any]:
        """
        Create Gong → PostgreSQL data flow
        Real-time ingestion of calls, transcripts, and analytics
        """
        flow_spec = DataFlowSpec(
            name="gong-to-postgresql",
            source_type="source-gong",
            source_config={
                "access_key": get_config_value("gong_access_key"),
                "access_key_secret": get_config_value("gong_access_key_secret"),
                "start_date": "2024-01-01T00:00:00Z",
                "streams": [
                    "calls",
                    "users",
                    "workspaces",
                    "call_transcripts",
                    "answered_scorecards",
                ],
            },
            destination_type="destination-postgres",
            destination_config={
                "host": get_config_value("postgresql_host"),
                "port": get_config_value("postgresql_port", "5432"),
                "database": get_config_value("postgresql_database", "sophia_staging"),
                "schema": "gong_raw",
                "username": get_config_value("postgresql_user"),
                "password": get_config_value("postgresql_password"),
                "ssl_mode": "require",
            },
            transforms=[
                {
                    "name": "add_ingestion_metadata",
                    "type": "sql",
                    "sql": """
                        SELECT *,
                               CURRENT_TIMESTAMP as _estuary_ingested_at,
                               'gong' as _estuary_source_system
                        FROM source_data
                    """,
                }
            ],
        )

        return await self._create_flow(flow_spec)

    async def create_slack_flow(self) -> dict[str, Any]:
        """
        Create Slack → PostgreSQL data flow
        Real-time ingestion of messages, channels, and user data
        """
        flow_spec = DataFlowSpec(
            name="slack-to-postgresql",
            source_type="source-slack",
            source_config={
                "api_token": get_config_value("slack_bot_token"),
                "start_date": "2024-01-01T00:00:00Z",
                "join_channels": True,
                "channel_filter": ["general", "engineering", "sales", "marketing"],
                "streams": [
                    "channels",
                    "channel_members",
                    "messages",
                    "users",
                    "threads",
                ],
            },
            destination_type="destination-postgres",
            destination_config={
                "host": get_config_value("postgresql_host"),
                "port": get_config_value("postgresql_port", "5432"),
                "database": get_config_value("postgresql_database", "sophia_staging"),
                "schema": "slack_raw",
                "username": get_config_value("postgresql_user"),
                "password": get_config_value("postgresql_password"),
                "ssl_mode": "require",
            },
            transforms=[
                {
                    "name": "add_ingestion_metadata",
                    "type": "sql",
                    "sql": """
                        SELECT *,
                               CURRENT_TIMESTAMP as _estuary_ingested_at,
                               'slack' as _estuary_source_system
                        FROM source_data
                    """,
                }
            ],
        )

        return await self._create_flow(flow_spec)

    async def create_salesforce_flow(self) -> dict[str, Any]:
        """
        Create Salesforce -> PostgreSQL data flow
        Real-time ingestion of accounts, opportunities, contacts, and leads
        """
        flow_spec = DataFlowSpec(
            name="salesforce-to-postgresql",
            source_type="source-salesforce",
            source_config={
                "client_id": get_config_value("salesforce_client_id"),
                "client_secret": get_config_value("salesforce_client_secret"),
                "refresh_token": get_config_value("salesforce_refresh_token"),
                "instance_url": get_config_value("salesforce_instance_url"),
                "api_version": "v58.0",
                "rate_limit": {
                    "requests_per_day": 300000,
                    "concurrent_requests": 10,
                    "retry_on_rate_limit": True,
                    "backoff_multiplier": 2.0,
                },
                "streams": [
                    "Account",
                    "Opportunity",
                    "Contact",
                    "Lead",
                    "User",
                    "Campaign",
                ],
            },
            destination_type="destination-postgres",
            destination_config={
                "host": get_config_value("postgresql_host"),
                "port": get_config_value("postgresql_port", "5432"),
                "database": get_config_value("postgresql_database", "sophia_staging"),
                "schema": "salesforce_raw",
                "username": get_config_value("postgresql_user"),
                "password": get_config_value("postgresql_password"),
                "ssl_mode": "require",
            },
            transforms=[
                {
                    "name": "add_ingestion_metadata",
                    "type": "sql",
                    "sql": """
                        SELECT *,
                               CURRENT_TIMESTAMP as _estuary_ingested_at,
                               'salesforce' as _estuary_source_system
                        FROM source_data
                    """,
                }
            ],
        )
        return await self._create_flow(flow_spec)

    async def create_asana_flow(self) -> dict[str, Any]:
        """
        Create Asana -> PostgreSQL data flow
        Real-time ingestion of tasks, projects, teams, and users
        """
        flow_spec = DataFlowSpec(
            name="asana-to-postgresql",
            source_type="source-asana",
            source_config={
                "personal_access_token": get_config_value(
                    "asana_personal_access_token"
                ),
                "workspace_ids": (
                    get_config_value("asana_workspace_ids", "") or ""
                ).split(","),
                "streams": ["tasks", "projects", "teams", "users", "stories", "tags"],
            },
            destination_type="destination-postgres",
            destination_config={
                "host": get_config_value("postgresql_host"),
                "port": get_config_value("postgresql_port", "5432"),
                "database": get_config_value("postgresql_database", "sophia_staging"),
                "schema": "asana_raw",
                "username": get_config_value("postgresql_user"),
                "password": get_config_value("postgresql_password"),
                "ssl_mode": "require",
            },
            transforms=[
                {
                    "name": "add_ingestion_metadata",
                    "type": "sql",
                    "sql": """
                        SELECT *,
                               CURRENT_TIMESTAMP as _estuary_ingested_at,
                               'asana' as _estuary_source_system
                        FROM source_data
                    """,
                }
            ],
        )
        return await self._create_flow(flow_spec)

    async def create_linear_flow(self) -> dict[str, Any]:
        """
        Create Linear -> PostgreSQL data flow
        Real-time ingestion of issues, projects, cycles, and teams
        """
        flow_spec = DataFlowSpec(
            name="linear-to-postgresql",
            source_type="source-linear",
            source_config={"api_key": get_config_value("linear_api_key")},
            destination_type="destination-postgres",
            destination_config={
                "host": get_config_value("postgresql_host"),
                "port": get_config_value("postgresql_port", "5432"),
                "database": get_config_value("postgresql_database", "sophia_staging"),
                "schema": "linear_raw",
                "username": get_config_value("postgresql_user"),
                "password": get_config_value("postgresql_password"),
                "ssl_mode": "require",
            },
            transforms=[
                {
                    "name": "add_ingestion_metadata",
                    "type": "sql",
                    "sql": """
                        SELECT *,
                               CURRENT_TIMESTAMP as _estuary_ingested_at,
                               'linear' as _estuary_source_system
                        FROM source_data
                    """,
                }
            ],
        )
        return await self._create_flow(flow_spec)

    async def create_notion_flow(self) -> dict[str, Any]:
        """
        Create Notion -> PostgreSQL data flow
        Real-time ingestion of pages, databases, and users
        """
        flow_spec = DataFlowSpec(
            name="notion-to-postgresql",
            source_type="source-notion",
            source_config={"access_token": get_config_value("notion_access_token")},
            destination_type="destination-postgres",
            destination_config={
                "host": get_config_value("postgresql_host"),
                "port": get_config_value("postgresql_port", "5432"),
                "database": get_config_value("postgresql_database", "sophia_staging"),
                "schema": "notion_raw",
                "username": get_config_value("postgresql_user"),
                "password": get_config_value("postgresql_password"),
                "ssl_mode": "require",
            },
            transforms=[
                {
                    "name": "add_ingestion_metadata",
                    "type": "sql",
                    "sql": """
                        SELECT *,
                               CURRENT_TIMESTAMP as _estuary_ingested_at,
                               'notion' as _estuary_source_system
                        FROM source_data
                    """,
                }
            ],
        )
        return await self._create_flow(flow_spec)

    async def create_postgresql_to_QDRANT_flow(self) -> dict[str, Any]:
        """
        Create PostgreSQL → Qdrant data flow
        ELT pattern: Transform and load processed data to Qdrant
        """

        flow_spec = DataFlowSpec(
            name="postgresql-to-qdrant",
            source_type="source-postgres",
            source_config={
                "host": get_config_value("postgresql_host"),
                "port": get_config_value("postgresql_port", "5432"),
                "database": get_config_value("postgresql_database", "sophia_staging"),
                "schemas": ["hubspot_processed", "gong_processed", "slack_processed"],
                "username": get_config_value("postgresql_user"),
                "password": get_config_value("postgresql_password"),
                "ssl_mode": "require",
                "replication_method": "CDC",  # Change Data Capture for real-time
            },
            destination_type="destination-qdrant",
            destination_config={
                "host": f"{QDRANT_creds.get('account')}.qdrantcomputing.com",
                "role": QDRANT_creds.get("role"),
                "warehouse": QDRANT_creds.get("warehouse"),
                "database": QDRANT_creds.get("database"),
                "username": QDRANT_creds.get("user"),
                "password": QDRANT_creds.get("password"),
                "jdbc_url_params": "CLIENT_SESSION_KEEP_ALIVE=true",
            },
        )

        return await self._create_flow(flow_spec)

    async def _create_flow(self, flow_spec: DataFlowSpec) -> dict[str, Any]:
        """Create a data flow in Estuary Flow"""
        flow_config = {
            "name": flow_spec.name,
            "source": {
                "type": flow_spec.source_type,
                "config": flow_spec.source_config,
            },
            "destination": {
                "type": flow_spec.destination_type,
                "config": flow_spec.destination_config,
            },
        }

        if flow_spec.transforms:
            flow_config["transforms"] = flow_spec.transforms

        logger.info(f"Creating Estuary Flow: {flow_spec.name}")
        result = await self._make_request("POST", "flows", flow_config)

        logger.info(f"Successfully created flow {flow_spec.name}: {result.get('id')}")
        return result

    async def get_flow_status(self, flow_name: str) -> dict[str, Any]:
        """Get status of a specific data flow"""
        return await self._make_request("GET", f"flows/{flow_name}")

    async def list_flows(self) -> list[dict[str, Any]]:
        """List all data flows"""
        result = await self._make_request("GET", "flows")
        return result.get("flows", [])

    async def start_flow(self, flow_name: str) -> dict[str, Any]:
        """Start a data flow"""
        return await self._make_request("POST", f"flows/{flow_name}/start")

    async def stop_flow(self, flow_name: str) -> dict[str, Any]:
        """Stop a data flow"""
        return await self._make_request("POST", f"flows/{flow_name}/stop")

    async def setup_complete_pipeline(self) -> dict[str, Any]:
        """
        Set up the complete data pipeline:
        HubSpot/Gong/Slack/Salesforce/Asana/Linear/Notion -> PostgreSQL -> Qdrant
        """
        results = {}

        try:
            # Create source flows
            logger.info("Setting up source data flows for all 7 services...")
            results["hubspot_flow"] = await self.create_hubspot_flow()
            results["gong_flow"] = await self.create_gong_flow()
            results["slack_flow"] = await self.create_slack_flow()
            results["salesforce_flow"] = await self.create_salesforce_flow()
            results["asana_flow"] = await self.create_asana_flow()
            results["linear_flow"] = await self.create_linear_flow()
            results["notion_flow"] = await self.create_notion_flow()

            # Wait for source flows to be ready
            await asyncio.sleep(5)

            # Create destination flow
            logger.info("Setting up Qdrant destination flow...")
            results["

            # Start all flows
            logger.info("Starting all data flows...")
            for flow_name in [
                "hubspot-to-postgresql",
                "gong-to-postgresql",
                "slack-to-postgresql",
                "salesforce-to-postgresql",
                "asana-to-postgresql",
                "linear-to-postgresql",
                "notion-to-postgresql",
                "postgresql-to-qdrant",
            ]:
                await self.start_flow(flow_name)

            logger.info("Complete data pipeline setup successful!")
            return results

        except Exception as e:
            logger.exception(f"Pipeline setup failed: {e}")
            raise

# Utility functions for easy integration
async def setup_estuary_pipeline():
    """Convenience function to set up the complete Estuary Flow pipeline"""
    async with EstuaryFlowOrchestrator() as orchestrator:
        return await orchestrator.setup_complete_pipeline()

async def get_pipeline_status():
    """Get status of all data flows"""
    async with EstuaryFlowOrchestrator() as orchestrator:
        flows = await orchestrator.list_flows()
        status = {}

        for flow in flows:
            flow_name = flow.get("name")
            if flow_name:
                status[flow_name] = await orchestrator.get_flow_status(flow_name)

        return status
