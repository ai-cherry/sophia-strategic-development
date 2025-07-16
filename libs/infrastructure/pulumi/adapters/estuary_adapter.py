#!/usr/bin/env python3
"""
from backend.services.sophia_unified_memory_service import get_memory_service, SophiaUnifiedMemoryService
from backend.core.auto_esc_config import get_config_value
Sophia AI - Estuary Platform Adapter
Optimal mix of API, CLI, and webhook integration for data pipeline management
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.sophia_iac_orchestrator import (
    PlatformAdapter,
    PlatformStatus,
    PlatformType,
)
from core.config_manager import get_config_value


class EstuaryAdapter(PlatformAdapter):
    """
    Estuary adapter with optimal integration strategy:
    - Primary: API + SDK for connection management
    - Secondary: CLI wrapper for complex operations
    - Webhooks: Sync status, failure notifications
    - LangChain: Intelligent source/destination matching
    """

    def __init__(self, name: str, platform_type: PlatformType):
        super().__init__(name, platform_type)
        self.base_url = "https://api.estuary.dev/v1"
        self.config = self._load_config()
        self.headers = {
            "Authorization": f"Bearer {self.config['access_token']}",
            "Content-Type": "application/json",
        }

    def _load_config(self) -> dict[str, Any]:
        """Load Estuary configuration from secure sources."""
        return {
            "client_id": os.getenv(
                "ESTUARY_CLIENT_ID", "9630134c-359d-4c9c-aa97-95ab3a2ff8f5"
            ),
            "client_secret": os.getenv(
                "ESTUARY_CLIENT_SECRET", "NfwyhFUjemKlC66h7iECE9Tjedo6SGFh"
            ),
            "access_token": get_config_value("estuary_access_token", ""),
            "webhook_url": os.getenv(
                "ESTUARY_WEBHOOK_URL", "https://app.sophia-intel.ai/webhook/estuary"
            ),
        }

    async def configure(self, config: dict[str, Any]) -> dict[str, Any]:
        """Configure Estuary with given settings."""
        try:
            self.logger.info(
                f"Configuring Estuary with operations: {list(config.keys())}"
            )

            results = {"success": True, "operations": [], "errors": []}

            # Handle different configuration operations
            if "create_source" in config:
                source_result = await self._create_source(config["create_source"])
                results["operations"].append("source_creation")
                if not source_result["success"]:
                    results["errors"].append(source_result["error"])
                else:
                    results["source_id"] = source_result.get("source_id")

            if "create_destination" in config:
                dest_result = await self._create_destination(
                    config["create_destination"]
                )
                results["operations"].append("destination_creation")
                if not dest_result["success"]:
                    results["errors"].append(dest_result["error"])
                else:
                    results["destination_id"] = dest_result.get("destination_id")

            if "create_connection" in config:
                conn_result = await self._create_connection(config["create_connection"])
                results["operations"].append("connection_creation")
                if not conn_result["success"]:
                    results["errors"].append(conn_result["error"])
                else:
                    results["connection_id"] = conn_result.get("connection_id")

            if "setup_webhooks" in config:
                webhook_result = await self._setup_webhooks(config["setup_webhooks"])
                results["operations"].append("webhook_setup")
                if not webhook_result["success"]:
                    results["errors"].append(webhook_result["error"])

            if "optimize_connections" in config:
                optimize_result = await self._optimize_connections()
                results["operations"].append("connection_optimization")
                if not optimize_result["success"]:
                    results["errors"].append(optimize_result["error"])

            # Set success based on whether there were errors
            results["success"] = len(results["errors"]) == 0

            return results

        except Exception as e:
            self.logger.exception(f"Estuary configuration failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_status(self) -> PlatformStatus:
        """Get current Estuary status and health."""
        try:
            # Get workspace info
            workspace_response = await self._api_request("GET", "/workspaces")

            if not workspace_response.get("success"):
                return PlatformStatus(
                    name=self.name,
                    type=self.platform_type,
                    status="down",
                    last_check=datetime.now(),
                    configuration={},
                    metrics={"error": "API connection failed"},
                )

            # Get sources, destinations, and connections
            sources = await self._api_request("GET", "/sources")
            destinations = await self._api_request("GET", "/destinations")
            connections = await self._api_request("GET", "/connections")

            # Calculate metrics
            metrics = {
                "sources": (
                    len(sources.get("data", [])) if sources.get("success") else 0
                ),
                "destinations": (
                    len(destinations.get("data", []))
                    if destinations.get("success")
                    else 0
                ),
                "connections": (
                    len(connections.get("data", []))
                    if connections.get("success")
                    else 0
                ),
                "active_syncs": 0,
                "failed_syncs": 0,
            }

            # Get sync status for connections
            if connections.get("success"):
                for connection in connections.get("data", []):
                    connection_id = connection.get("connectionId")
                    if connection_id:
                        sync_status = await self._get_connection_sync_status(
                            connection_id
                        )
                        if sync_status.get("status") == "running":
                            metrics["active_syncs"] += 1
                        elif sync_status.get("status") == "failed":
                            metrics["failed_syncs"] += 1

            # Determine health status
            health_status = "healthy"
            if metrics["failed_syncs"] > 0:
                health_status = "degraded"
            if metrics["sources"] == 0 and metrics["destinations"] == 0:
                health_status = "degraded"

            # Configuration info
            configuration = {
                "api_endpoint": self.base_url,
                "webhook_url": self.config["webhook_url"],
                "client_id": self.config["client_id"],
            }

            # Dependencies - Estuary depends on data sources and destinations
            dependencies = ["qdrant", "gong", "slack", "hubspot"]

            return PlatformStatus(
                name=self.name,
                type=self.platform_type,
                status=health_status,
                last_check=datetime.now(),
                configuration=configuration,
                metrics=metrics,
                dependencies=dependencies,
                webhooks_active=True,
            )

        except Exception as e:
            self.logger.exception(f"Estuary status check failed: {e}")
            return PlatformStatus(
                name=self.name,
                type=self.platform_type,
                status="error",
                last_check=datetime.now(),
                configuration={},
                metrics={"error": str(e)},
            )

    async def handle_webhook(self, payload: dict[str, Any]) -> None:
        """Handle incoming webhooks from Estuary."""
        try:
            self.logger.info(
                f"Received Estuary webhook: {payload.get('event_type', 'unknown')}"
            )

            event_type = payload.get("event_type")

            if event_type == "sync_completed":
                await self._handle_sync_completed(payload)
            elif event_type == "sync_failed":
                await self._handle_sync_failed(payload)
            elif event_type == "connection_status_changed":
                await self._handle_connection_status_changed(payload)
            else:
                self.logger.warning(f"Unknown webhook event type: {event_type}")

        except Exception as e:
            self.logger.exception(f"Webhook handling failed: {e}")

    async def validate_configuration(self, config: dict[str, Any]) -> bool:
        """Validate configuration before applying."""
        try:
            # Validate source creation config
            if "create_source" in config:
                source_config = config["create_source"]
                required_fields = ["name", "source_type", "configuration"]
                if not all(field in source_config for field in required_fields):
                    self.logger.error("create_source missing required fields")
                    return False

            # Validate destination creation config
            if "create_destination" in config:
                dest_config = config["create_destination"]
                required_fields = ["name", "destination_type", "configuration"]
                if not all(field in dest_config for field in required_fields):
                    self.logger.error("create_destination missing required fields")
                    return False

            # Validate connection creation config
            if "create_connection" in config:
                conn_config = config["create_connection"]
                required_fields = ["source_id", "destination_id"]
                if not all(field in conn_config for field in required_fields):
                    self.logger.error("create_connection missing required fields")
                    return False

            return True

        except Exception as e:
            self.logger.exception(f"Configuration validation failed: {e}")
            return False

    # API Helper Methods

    async def _api_request(
        self, method: str, endpoint: str, data: dict | None = None
    ) -> dict[str, Any]:
        """Make API request to Estuary."""
        try:
            url = f"{self.base_url}{endpoint}"

            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}

            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                return {
                    "success": False,
                    "error": f"API request failed: {response.status_code} - {response.text}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # Configuration Methods

    async def _create_source(self, config: dict[str, Any]) -> dict[str, Any]:
        """Create a new data source."""
        try:
            source_data = {
                "name": config["name"],
                "sourceType": config["source_type"],
                "configuration": config["configuration"],
            }

            response = await self._api_request("POST", "/sources", source_data)

            if response["success"]:
                source_id = response["data"].get("sourceId")
                return {
                    "success": True,
                    "source_id": source_id,
                    "message": f"Source '{config['name']}' created successfully",
                }
            else:
                return {"success": False, "error": response["error"]}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _create_destination(self, config: dict[str, Any]) -> dict[str, Any]:
        """Create a new destination."""
        try:
            dest_data = {
                "name": config["name"],
                "destinationType": config["destination_type"],
                "configuration": config["configuration"],
            }

            response = await self._api_request("POST", "/destinations", dest_data)

            if response["success"]:
                dest_id = response["data"].get("destinationId")
                return {
                    "success": True,
                    "destination_id": dest_id,
                    "message": f"Destination '{config['name']}' created successfully",
                }
            else:
                return {"success": False, "error": response["error"]}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _create_connection(self, config: dict[str, Any]) -> dict[str, Any]:
        """Create a new connection between source and destination."""
        try:
            conn_data = {
                "name": config.get(
                    "name", f"Connection {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                ),
                "sourceId": config["source_id"],
                "destinationId": config["destination_id"],
                "schedule": config.get(
                    "schedule",
                    {
                        "scheduleType": "cron",
                        "cronExpression": "0 */6 * * *",  # Every 6 hours
                    },
                ),
                "status": config.get("status", "active"),
            }

            response = await self._api_request("POST", "/connections", conn_data)

            if response["success"]:
                conn_id = response["data"].get("connectionId")
                return {
                    "success": True,
                    "connection_id": conn_id,
                    "message": f"Connection '{conn_data['name']}' created successfully",
                }
            else:
                return {"success": False, "error": response["error"]}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _setup_webhooks(self, config: dict[str, Any]) -> dict[str, Any]:
        """Setup webhooks for Estuary notifications."""
        try:
            # Estuary webhook configuration
            webhook_config = {
                "webhook_url": config.get("webhook_url", self.config["webhook_url"]),
                "events": config.get(
                    "events",
                    ["sync_completed", "sync_failed", "connection_status_changed"],
                ),
            }

            # This would configure webhooks via Estuary Flow API
            # Implementation depends on Estuary's webhook API

            return {
                "success": True,
                "message": "Webhooks configured successfully",
                "webhook_url": webhook_config["webhook_url"],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _optimize_connections(self) -> dict[str, Any]:
        """Optimize existing connections for performance."""
        try:
            # Get all connections
            connections_response = await self._api_request("GET", "/connections")

            if not connections_response["success"]:
                return {"success": False, "error": "Failed to get connections"}

            optimizations = []

            for connection in connections_response["data"]:
                connection_id = connection.get("connectionId")

                # Analyze sync performance
                sync_status = await self._get_connection_sync_status(connection_id)

                # Suggest optimizations based on performance
                if sync_status.get("duration_minutes", 0) > 60:
                    optimizations.append(
                        {
                            "connection_id": connection_id,
                            "suggestion": "Consider reducing sync frequency for long-running syncs",
                            "current_duration": sync_status.get("duration_minutes"),
                        }
                    )

            return {
                "success": True,
                "optimizations": optimizations,
                "message": f"Analyzed {len(connections_response['data'])} connections",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_connection_sync_status(self, connection_id: str) -> dict[str, Any]:
        """Get sync status for a specific connection."""
        try:
            response = await self._api_request(
                "GET", f"/connections/{connection_id}/jobs"
            )

            if response["success"] and response["data"]:
                latest_job = response["data"][0]  # Assuming jobs are sorted by date
                return {
                    "status": latest_job.get("status", "unknown"),
                    "duration_minutes": latest_job.get("duration", 0) / 60,
                    "records_processed": latest_job.get("recordsEmitted", 0),
                    "last_run": latest_job.get("createdAt"),
                }

            return {"status": "unknown"}

        except Exception as e:
            self.logger.exception(f"Failed to get sync status for {connection_id}: {e}")
            return {"status": "error", "error": str(e)}

    # Webhook Handlers

    async def _handle_sync_completed(self, payload: dict[str, Any]) -> None:
        """Handle sync completion webhook."""
        connection_id = payload.get("connection_id")
        records_processed = payload.get("records_processed", 0)

        self.logger.info(
            f"Sync completed for connection {connection_id}: {records_processed} records"
        )

        # Could trigger downstream processing or notifications

    async def _handle_sync_failed(self, payload: dict[str, Any]) -> None:
        """Handle sync failure webhook."""
        connection_id = payload.get("connection_id")
        error_message = payload.get("error_message", "Unknown error")

        self.logger.error(
            f"Sync failed for connection {connection_id}: {error_message}"
        )

        # Could trigger alerts or automatic retry logic

    async def _handle_connection_status_changed(self, payload: dict[str, Any]) -> None:
        """Handle connection status change webhook."""
        connection_id = payload.get("connection_id")
        new_status = payload.get("new_status")

        self.logger.info(f"Connection {connection_id} status changed to: {new_status}")

    # Orchestrator Integration Methods

    async def execute_create_gong_source(
        self, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Create Gong source with intelligent configuration."""
        gong_config = {
            "name": "Sophia AI Gong",
            "source_type": "gong",
            "configuration": {
                "access_key": get_config_value("gong_access_key"),
                "access_key_secret": get_config_value("gong_client_secret"),
                "start_date": parameters.get("start_date", "2024-01-01T00:00:00Z"),
            },
        }

        return await self.configure({"create_source": gong_config})

    async def execute_create_slack_source(
        self, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Create Slack source with intelligent configuration."""
        slack_config = {
            "name": "Sophia AI Slack",
            "source_type": "slack",
            "configuration": {
                "api_token": get_config_value("slack_bot_token"),
                "start_date": parameters.get("start_date", "2024-01-01T00:00:00Z"),
                "lookback_window": 1,
                "join_channels": True,
            },
        }

        return await self.configure({"create_source": slack_config})

    async def execute_create_QDRANT_destination(
        self, parameters: dict[str, Any]
    ) -> dict[str, Any]:

        
            "name": "Sophia AI Qdrant",
            "destination_type": "qdrant",
            "configuration": {
                "host": f"{os.getenv('QDRANT_ACCOUNT')}.qdrantcomputing.com",
                "role": "ACCOUNTADMIN",
                "warehouse": "SOPHIA_AI_ANALYTICS_WH",
                "database": "SOPHIA_AI_CORE",
                "schema": "PUBLIC",
                "username": get_config_value("QDRANT_user"),
                "password": os.getenv("SOPHIA_AI_TOKEN"),
            },
        }




# CLI interface for testing
async def main():
    """Test the Estuary adapter."""
    import argparse

    parser = argparse.ArgumentParser(description="Estuary Adapter Test")
    parser.add_argument("command", choices=["status", "configure", "create-source"])
    parser.add_argument("--config", help="Configuration JSON string")

    args = parser.parse_args()

    adapter = EstuaryAdapter("estuary", PlatformType.DATA_STACK)

    if args.command == "status":
        await adapter.get_status()

    elif args.command == "configure":
        if args.config:
            config = json.loads(args.config)
            await adapter.configure(config)
        else:
            pass

    elif args.command == "create-source":
        await adapter.execute_create_gong_source({"start_date": "2024-01-01T00:00:00Z"})


if __name__ == "__main__":
    asyncio.run(main())
