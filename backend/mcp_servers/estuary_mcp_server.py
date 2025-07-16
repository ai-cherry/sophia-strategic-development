#!/usr/bin/env python3
"""
Estuary Flow MCP Server
Provides AI control over real-time data pipelines

This MCP server enables the AI to manage Estuary Flow pipelines for:
- Real-time CDC from source systems
- Materialization to analytical databases
- Data pipeline monitoring and management
"""

from backend.services.sophia_unified_memory_service import get_memory_service, SophiaUnifiedMemoryService
import logging

# CRITICAL: Load environment before any other imports
import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.core.startup import startup_sequence

# Run startup sequence
startup_config = startup_sequence(
    "Estuary MCP Server", required_vars=["ESTUARY_API_TOKEN"]
)

from backend.core.unified_config import UnifiedConfig
from backend.mcp.base.standardized_mcp_server import StandardizedMCPServer, mcp_tool
from backend.services.estuary_service import EstuaryService

logger = logging.getLogger(__name__)


class EstuaryMCPServer(StandardizedMCPServer):
    """MCP Server for Estuary Flow data pipeline management"""

    def __init__(self):
        super().__init__(
            name="estuary-mcp-server",
            description="AI control for real-time data pipelines via Estuary Flow",
        )
        self.estuary_service = None

    async def initialize(self):
        """Initialize server"""
        logger.info("Initializing Estuary MCP Server...")
        # EstuaryService uses async context manager

    @mcp_tool(
        description="List all active data capture pipelines", include_context=True
    )
    async def list_captures(self, context: dict) -> dict[str, Any]:
        """
        List all data capture pipelines.

        Captures are source connectors that stream changes from systems like:
        - PostgreSQL (CDC)
        - HubSpot
        - Salesforce
        - MySQL
        """
        try:
            async with EstuaryService() as service:
                captures = await service.list_captures()

                return {
                    "status": "success",
                    "capture_count": len(captures),
                    "captures": [
                        {
                            "name": flow.name,
                            "connector": flow.connector,
                            "state": flow.state,
                            "bindings": [
                                {
                                    "source": f"{b.resource}.{b.name}",
                                    "collection": b.collection,
                                }
                                for b in flow.bindings
                            ],
                        }
                        for flow in captures
                    ],
                }
        except Exception as e:
            logger.error(f"Failed to list captures: {e}")
            return {"status": "error", "error": str(e)}

    @mcp_tool(
        description="List all data materialization pipelines to analytical databases",
        include_context=True,
    )
    async def list_materializations(self, context: dict) -> dict[str, Any]:
        """
        List all materialization pipelines.

        Materializations write data from Estuary collections to:
        - Qdrant
        - BigQuery
        - Redshift
        - ClickHouse
        """
        try:
            async with EstuaryService() as service:
                materializations = await service.list_materializations()

                return {
                    "status": "success",
                    "materialization_count": len(materializations),
                    "materializations": [
                        {
                            "name": flow.name,
                            "connector": flow.connector,
                            "state": flow.state,
                            "bindings": [
                                {
                                    "collection": b.collection,
                                    "target": f"{b.resource}.{b.name}",
                                }
                                for b in flow.bindings
                            ],
                        }
                        for flow in materializations
                    ],
                }
        except Exception as e:
            logger.error(f"Failed to list materializations: {e}")
            return {"status": "error", "error": str(e)}

    @mcp_tool(
        description="Create a PostgreSQL CDC capture pipeline", include_context=True
    )
    async def create_postgres_capture(
        self, name: str, tables: list[str], context: dict
    ) -> dict[str, Any]:
        """
        Create a PostgreSQL CDC (Change Data Capture) pipeline.

        Args:
            name: Name for the capture (e.g., "sophia-production-cdc")
            tables: List of tables to capture (e.g., ["public.users", "public.transactions"])
        """
        try:
            # Get PostgreSQL config
            pg_config = UnifiedConfig.get_postgres_config()

            async with EstuaryService() as service:
                success = await service.create_postgres_capture(
                    name=name, database_config=pg_config, tables=tables
                )

                if success:
                    return {
                        "status": "success",
                        "message": f"Created PostgreSQL capture: {name}",
                        "capture_name": name,
                        "tables": tables,
                    }
                else:
                    return {"status": "error", "error": "Failed to create capture"}

        except Exception as e:
            logger.error(f"Failed to create PostgreSQL capture: {e}")
            return {"status": "error", "error": str(e)}

    @mcp_tool(
        description="Create a Qdrant materialization pipeline", include_context=True
    )
    async def create_QDRANT_materialization(
        self, name: str, collection_mappings: list[dict[str, str]], context: dict
    ) -> dict[str, Any]:
        """
        Create a Qdrant materialization pipeline.

        Args:
            name: Name for the materialization (e.g., "sophia-to-qdrant")
            collection_mappings: List of dicts mapping collections to tables
                Example: [{"collection": "sophia/cdc/users", "table": "STG_USERS"}]
        """
        try:



            async with EstuaryService() as service:
                success = await service.create_QDRANT_materialization(
                    name=name,

                    collections=collection_mappings,
                )

                if success:
                    return {
                        "status": "success",
                        "message": f"Created Qdrant materialization: {name}",
                        "materialization_name": name,
                        "mappings": collection_mappings,
                    }
                else:
                    return {
                        "status": "error",
                        "error": "Failed to create materialization",
                    }

        except Exception as e:
            logger.error(f"Failed to create Qdrant materialization: {e}")
            return {"status": "error", "error": str(e)}

    @mcp_tool(
        description="Create a HubSpot CRM data capture pipeline", include_context=True
    )
    async def create_hubspot_capture(
        self, name: str, context: dict, objects: list[str] = None
    ) -> dict[str, Any]:
        """
        Create a HubSpot capture pipeline.

        Args:
            name: Name for the capture (e.g., "hubspot-crm-sync")
            objects: HubSpot objects to capture (default: contacts, deals, companies)
        """
        try:
            # Get HubSpot API key
            hubspot_key = UnifiedConfig.get("hubspot_api_key")
            if not hubspot_key:
                return {"status": "error", "error": "HubSpot API key not configured"}

            async with EstuaryService() as service:
                success = await service.create_hubspot_capture(
                    name=name, api_key=hubspot_key, objects=objects
                )

                if success:
                    return {
                        "status": "success",
                        "message": f"Created HubSpot capture: {name}",
                        "capture_name": name,
                        "objects": objects
                        or ["contacts", "deals", "companies", "engagements"],
                    }
                else:
                    return {
                        "status": "error",
                        "error": "Failed to create HubSpot capture",
                    }

        except Exception as e:
            logger.error(f"Failed to create HubSpot capture: {e}")
            return {"status": "error", "error": str(e)}

    @mcp_tool(description="Get statistics for a data pipeline", include_context=True)
    async def get_flow_stats(
        self, flow_name: str, flow_type: str, context: dict
    ) -> dict[str, Any]:
        """
        Get statistics for a capture or materialization.

        Args:
            flow_name: Name of the flow
            flow_type: Either "capture" or "materialization"
        """
        try:
            async with EstuaryService() as service:
                stats = await service.get_flow_stats(flow_name, flow_type)

                return {
                    "status": "success",
                    "flow_name": flow_name,
                    "flow_type": flow_type,
                    "statistics": stats,
                }

        except Exception as e:
            logger.error(f"Failed to get flow stats: {e}")
            return {"status": "error", "error": str(e)}

    @mcp_tool(description="Pause a data pipeline", include_context=True)
    async def pause_flow(
        self, flow_name: str, flow_type: str, context: dict
    ) -> dict[str, Any]:
        """
        Pause a capture or materialization.

        Args:
            flow_name: Name of the flow to pause
            flow_type: Either "capture" or "materialization"
        """
        try:
            async with EstuaryService() as service:
                success = await service.pause_flow(flow_name, flow_type)

                if success:
                    return {
                        "status": "success",
                        "message": f"Paused {flow_type}: {flow_name}",
                    }
                else:
                    return {"status": "error", "error": f"Failed to pause {flow_type}"}

        except Exception as e:
            logger.error(f"Failed to pause flow: {e}")
            return {"status": "error", "error": str(e)}

    @mcp_tool(description="Resume a paused data pipeline", include_context=True)
    async def resume_flow(
        self, flow_name: str, flow_type: str, context: dict
    ) -> dict[str, Any]:
        """
        Resume a paused capture or materialization.

        Args:
            flow_name: Name of the flow to resume
            flow_type: Either "capture" or "materialization"
        """
        try:
            async with EstuaryService() as service:
                success = await service.resume_flow(flow_name, flow_type)

                if success:
                    return {
                        "status": "success",
                        "message": f"Resumed {flow_type}: {flow_name}",
                    }
                else:
                    return {"status": "error", "error": f"Failed to resume {flow_type}"}

        except Exception as e:
            logger.error(f"Failed to resume flow: {e}")
            return {"status": "error", "error": str(e)}

    @mcp_tool(
        description="Get real-time data pipeline health summary", include_context=True
    )
    async def get_pipeline_health(self, context: dict) -> dict[str, Any]:
        """
        Get overall health of all data pipelines.

        Returns summary of all captures and materializations with their status.
        """
        try:
            async with EstuaryService() as service:
                # Get all flows
                captures = await service.list_captures()
                materializations = await service.list_materializations()

                # Count by state
                capture_states = {}
                for cap in captures:
                    state = cap.state
                    capture_states[state] = capture_states.get(state, 0) + 1

                mat_states = {}
                for mat in materializations:
                    state = mat.state
                    mat_states[state] = mat_states.get(state, 0) + 1

                return {
                    "status": "success",
                    "summary": {
                        "total_captures": len(captures),
                        "total_materializations": len(materializations),
                        "capture_states": capture_states,
                        "materialization_states": mat_states,
                    },
                    "healthy": (
                        capture_states.get("running", 0) == len(captures)
                        and mat_states.get("running", 0) == len(materializations)
                    ),
                }

        except Exception as e:
            logger.error(f"Failed to get pipeline health: {e}")
            return {"status": "error", "error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Health check for the MCP server"""
        try:
            # Check if we can reach Estuary API
            async with EstuaryService() as service:
                # Try to list captures as a health check
                captures = await service.list_captures()

                return {
                    "status": "healthy",
                    "service": "estuary-mcp-server",
                    "api_reachable": True,
                    "active_pipelines": len(captures),
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "estuary-mcp-server",
                "error": str(e),
            }


def main():
    """Run the Estuary MCP server"""
    server = EstuaryMCPServer()
    server.run()


if __name__ == "__main__":
    main()
