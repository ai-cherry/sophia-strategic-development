"""
Estuary Flow Service for Real-Time Data Movement
Part of the Sophia AI Autonomic System

This service manages Estuary Flow for real-time CDC (Change Data Capture)
and data replication across systems.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import aiohttp

from backend.core.unified_config import UnifiedConfig

logger = logging.getLogger(__name__)


@dataclass
class EstuaryBinding:
    """Represents an Estuary capture or materialization binding"""

    name: str
    resource: str
    collection: str
    state: str = "active"


@dataclass
class EstuaryFlow:
    """Represents an Estuary Flow pipeline"""

    name: str
    type: str  # "capture" or "materialization"
    connector: str
    bindings: list[EstuaryBinding]
    state: str = "running"
    config: dict[str, Any] = field(default_factory=dict)


class EstuaryService:
    """
    Service for managing Estuary Flow pipelines.

    Estuary provides real-time data replication with exactly-once semantics,
    enabling true event-driven architecture.
    """

    def __init__(self):
        self.api_url = UnifiedConfig.get("estuary_api_url", "https://api.estuary.dev")
        self.api_token = UnifiedConfig.get("estuary_api_token")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def list_captures(self) -> list[EstuaryFlow]:
        """List all capture pipelines"""
        if not self.session:
            logger.error("Session not initialized - use async context manager")
            return []

        try:
            async with self.session.get(f"{self.api_url}/captures") as response:
                response.raise_for_status()
                data = await response.json()

                captures = []
                for capture_data in data.get("captures", []):
                    flow = EstuaryFlow(
                        name=capture_data["name"],
                        type="capture",
                        connector=capture_data["connector"]["image"],
                        bindings=[
                            EstuaryBinding(
                                name=b["resource"]["stream"],
                                resource=b["resource"]["namespace"],
                                collection=b["collection"],
                                state=b.get("state", "active"),
                            )
                            for b in capture_data.get("bindings", [])
                        ],
                        state=capture_data.get("state", "running"),
                        config=capture_data.get("config", {}),
                    )
                    captures.append(flow)

                logger.info(f"Found {len(captures)} capture pipelines")
                return captures

        except Exception as e:
            logger.error(f"Failed to list captures: {e}")
            return []

    async def list_materializations(self) -> list[EstuaryFlow]:
        """List all materialization pipelines"""
        if not self.session:
            logger.error("Session not initialized - use async context manager")
            return []

        try:
            async with self.session.get(f"{self.api_url}/materializations") as response:
                response.raise_for_status()
                data = await response.json()

                materializations = []
                for mat_data in data.get("materializations", []):
                    flow = EstuaryFlow(
                        name=mat_data["name"],
                        type="materialization",
                        connector=mat_data["connector"]["image"],
                        bindings=[
                            EstuaryBinding(
                                name=b["resource"]["table"],
                                resource=b["resource"]["schema"],
                                collection=b["source"]["collection"],
                                state=b.get("state", "active"),
                            )
                            for b in mat_data.get("bindings", [])
                        ],
                        state=mat_data.get("state", "running"),
                        config=mat_data.get("config", {}),
                    )
                    materializations.append(flow)

                logger.info(f"Found {len(materializations)} materialization pipelines")
                return materializations

        except Exception as e:
            logger.error(f"Failed to list materializations: {e}")
            return []

    async def create_postgres_capture(
        self, name: str, database_config: dict[str, Any], tables: list[str]
    ) -> bool:
        """
        Create a PostgreSQL CDC capture.

        Args:
            name: Name for the capture pipeline
            database_config: PostgreSQL connection config
            tables: List of tables to capture (format: "schema.table")
        """
        if not self.session:
            logger.error("Session not initialized - use async context manager")
            return False

        try:
            capture_spec = {
                "name": name,
                "connector": {
                    "image": "ghcr.io/estuary/source-postgres:latest",
                    "config": {
                        "address": f"{database_config['host']}:{database_config.get('port', 5432)}",
                        "database": database_config["database"],
                        "user": database_config["user"],
                        "password": database_config["password"],
                        "replication": {
                            "method": "CDC",
                            "slot_name": f"estuary_slot_{name.replace('-', '_')}",
                        },
                    },
                },
                "bindings": [
                    {
                        "resource": {
                            "stream": table,
                            "namespace": (
                                table.split(".")[0] if "." in table else "public"
                            ),
                        },
                        "collection": f"sophia/{name}/{table.replace('.', '_')}",
                    }
                    for table in tables
                ],
            }

            async with self.session.post(
                f"{self.api_url}/captures", json=capture_spec
            ) as response:
                response.raise_for_status()
                logger.info(f"Created PostgreSQL capture: {name}")
                return True

        except Exception as e:
            logger.error(f"Failed to create PostgreSQL capture: {e}")
            return False

    async def create_snowflake_materialization(
        self,
        name: str,
        snowflake_config: dict[str, Any],
        collections: list[dict[str, str]],
    ) -> bool:
        """
        Create a Snowflake materialization.

        Args:
            name: Name for the materialization pipeline
            snowflake_config: Snowflake connection config
            collections: List of dicts with 'collection' and 'table' keys
        """
        if not self.session:
            logger.error("Session not initialized - use async context manager")
            return False

        try:
            mat_spec = {
                "name": name,
                "connector": {
                    "image": "ghcr.io/estuary/materialize-snowflake:latest",
                    "config": {
                        "account": snowflake_config["account"],
                        "user": snowflake_config["user"],
                        "password": snowflake_config["password"],
                        "warehouse": snowflake_config["warehouse"],
                        "database": snowflake_config["database"],
                        "schema": snowflake_config.get("schema", "PUBLIC"),
                    },
                },
                "bindings": [
                    {
                        "source": {"collection": col["collection"]},
                        "resource": {
                            "table": col["table"],
                            "schema": snowflake_config.get("schema", "PUBLIC"),
                            "delta_updates": True,
                        },
                    }
                    for col in collections
                ],
            }

            async with self.session.post(
                f"{self.api_url}/materializations", json=mat_spec
            ) as response:
                response.raise_for_status()
                logger.info(f"Created Snowflake materialization: {name}")
                return True

        except Exception as e:
            logger.error(f"Failed to create Snowflake materialization: {e}")
            return False

    async def get_flow_stats(self, flow_name: str, flow_type: str) -> dict[str, Any]:
        """Get statistics for a flow (capture or materialization)"""
        if not self.session:
            logger.error("Session not initialized - use async context manager")
            return {}

        try:
            endpoint = "captures" if flow_type == "capture" else "materializations"
            async with self.session.get(
                f"{self.api_url}/{endpoint}/{flow_name}/stats"
            ) as response:
                response.raise_for_status()
                stats = await response.json()

                return {
                    "documents_processed": stats.get("docsTotal", 0),
                    "bytes_processed": stats.get("bytesTotal", 0),
                    "errors": stats.get("errors", 0),
                    "last_activity": stats.get("lastActivity"),
                    "state": stats.get("state", "unknown"),
                }

        except Exception as e:
            logger.error(f"Failed to get flow stats: {e}")
            return {}

    async def pause_flow(self, flow_name: str, flow_type: str) -> bool:
        """Pause a flow"""
        if not self.session:
            logger.error("Session not initialized - use async context manager")
            return False

        try:
            endpoint = "captures" if flow_type == "capture" else "materializations"
            async with self.session.post(
                f"{self.api_url}/{endpoint}/{flow_name}/pause"
            ) as response:
                response.raise_for_status()
                logger.info(f"Paused {flow_type}: {flow_name}")
                return True

        except Exception as e:
            logger.error(f"Failed to pause flow: {e}")
            return False

    async def resume_flow(self, flow_name: str, flow_type: str) -> bool:
        """Resume a flow"""
        if not self.session:
            logger.error("Session not initialized - use async context manager")
            return False

        try:
            endpoint = "captures" if flow_type == "capture" else "materializations"
            async with self.session.post(
                f"{self.api_url}/{endpoint}/{flow_name}/resume"
            ) as response:
                response.raise_for_status()
                logger.info(f"Resumed {flow_type}: {flow_name}")
                return True

        except Exception as e:
            logger.error(f"Failed to resume flow: {e}")
            return False

    async def delete_flow(self, flow_name: str, flow_type: str) -> bool:
        """Delete a flow"""
        if not self.session:
            logger.error("Session not initialized - use async context manager")
            return False

        try:
            endpoint = "captures" if flow_type == "capture" else "materializations"
            async with self.session.delete(
                f"{self.api_url}/{endpoint}/{flow_name}"
            ) as response:
                response.raise_for_status()
                logger.info(f"Deleted {flow_type}: {flow_name}")
                return True

        except Exception as e:
            logger.error(f"Failed to delete flow: {e}")
            return False

    async def create_hubspot_capture(
        self, name: str, api_key: str, objects: Optional[list[str]] = None
    ) -> bool:
        """
        Create a HubSpot capture for CRM data.

        Args:
            name: Name for the capture pipeline
            api_key: HubSpot API key
            objects: List of HubSpot objects to capture (contacts, deals, etc)
        """
        if not self.session:
            logger.error("Session not initialized - use async context manager")
            return False

        if objects is None:
            objects = ["contacts", "deals", "companies", "engagements"]

        try:
            capture_spec = {
                "name": name,
                "connector": {
                    "image": "ghcr.io/estuary/source-hubspot:latest",
                    "config": {
                        "api_key": api_key,
                        "start_date": "2024-01-01T00:00:00Z",
                    },
                },
                "bindings": [
                    {
                        "resource": {"stream": obj, "namespace": "hubspot"},
                        "collection": f"sophia/{name}/{obj}",
                    }
                    for obj in objects
                ],
            }

            async with self.session.post(
                f"{self.api_url}/captures", json=capture_spec
            ) as response:
                response.raise_for_status()
                logger.info(f"Created HubSpot capture: {name}")
                return True

        except Exception as e:
            logger.error(f"Failed to create HubSpot capture: {e}")
            return False
