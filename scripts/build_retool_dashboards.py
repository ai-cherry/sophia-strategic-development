"""Build Retool Dashboards using AI Agent
This script orchestrates an AI agent to programmatically build
Retool dashboards for system monitoring.
"""
import asyncio
import json
import logging
from typing import Any, Dict

import aiohttp

from backend.mcp.mcp_client import MCPClient

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RetoolDashboardBuilder:
    """An AI Agent orchestrator for building Retool UIs.
    """

    def __init__(self, mcp_gateway_url: str = "http://localhost:8090"):
        self.mcp_client = MCPClient(mcp_gateway_url)

    async def initialize(self):
        """Connect to the MCP gateway after ensuring it's healthy."""
        await self._wait_for_gateway()
        await self.mcp_client.connect()
        logger.info("MCP Client connected.")

    async def _wait_for_gateway(self, timeout: int = 60):
        """Polls the MCP gateway's health endpoint until it's ready."""
        start_time = asyncio.get_event_loop().time()
        health_url = f"{self.mcp_client.gateway_url}/health"
        logger.info(f"Waiting for MCP gateway to be healthy at {health_url}...")

        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url) as response:
                        if response.status == 200:
                            logger.info("MCP gateway is healthy!")
                            return
            except aiohttp.ClientConnectorError:
                pass  # Ignore connection errors while waiting

            if asyncio.get_event_loop().time() - start_time >= timeout:
                raise TimeoutError(f"Gateway not healthy after {timeout} seconds.")

            await asyncio.sleep(5)

    async def close(self):
        """Close the MCP client connection."""
        await self.mcp_client.close()
        logger.info("MCP Client disconnected.")

    async def build_mission_control_dashboard(self) -> Dict[str, Any]:
        """Builds the 'MCP Mission Control' dashboard in Retool.
        """
        dashboard_name = "mcp_mission_control"
        logger.info(f"Attempting to build dashboard: {dashboard_name}")

        try:
            # Step 1: Create the main Retool application
            create_app_result = await self.mcp_client.call_tool(
                "retool",
                "create_admin_dashboard",
                dashboard_name=dashboard_name,
                description="Live dashboard to monitor the health and status of all running MCP servers.",
            )

            if not create_app_result.get("success"):
                logger.error(
                    f"Failed to create Retool app: {create_app_result.get('error')}"
                )
                return {"success": False, "error": "Failed to create Retool app"}

            app_data = create_app_result.get("data", {})
            app_id = app_data.get("id")
            logger.info(
                f"Successfully created Retool app '{dashboard_name}' with ID: {app_id}"
            )

            # Step 2: Conceptually add and configure widgets
            # In a real-world scenario, this would involve more detailed calls to a more mature Retool API client.
            # For now, we log the intent.
            logger.info("--- Conceptual Next Steps ---")
            logger.info(f"1. Add a 'Table' widget to app {app_id}.")
            logger.info(
                "2. Create a new REST query in the Retool app named 'listMCPContainers'."
            )
            logger.info(
                "3. Configure the query to POST to the MCP Gateway's /call_tool endpoint."
            )
            logger.info(
                "4. The query body should be: { 'server': 'docker', 'tool': 'list_containers' }"
            )
            logger.info(
                "5. Set the table's data source to `{{ listMCPContainers.data }}`."
            )
            logger.info(
                "6. Set the query to run on page load and on a 30-second interval."
            )
            logger.info("--- End Conceptual Steps ---")

            return {
                "success": True,
                "app_id": app_id,
                "dashboard_name": dashboard_name,
                "message": "Dashboard creation initiated. Manual steps required in Retool to add and configure widgets.",
            }

        except Exception as e:
            logger.error(
                f"An error occurred while building the dashboard: {e}", exc_info=True
            )
            return {"success": False, "error": str(e)}


async def main():
    """Main function to run the dashboard builder.
    """
    # NOTE: This assumes the MCP Gateway and the Retool/Docker MCP servers are running.
    # You can start them with `docker-compose up mcp-gateway retool-mcp docker-mcp`

    builder = RetoolDashboardBuilder()
    try:
        await builder.initialize()
        result = await builder.build_mission_control_dashboard()

        print("\n--- Retool Dashboard Build Summary ---")
        print(json.dumps(result, indent=2))
        print("--------------------------------------")

    finally:
        await builder.close()


if __name__ == "__main__":
    asyncio.run(main())
