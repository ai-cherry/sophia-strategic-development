"""
Modified Build Retool Dashboards script
This version works with just the gateway running, without the actual MCP servers
"""
import asyncio
import json
import logging
from typing import Dict, Any
import aiohttp

from backend.mcp.mcp_client import MCPClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RetoolDashboardBuilder:
    """
    An AI Agent orchestrator for building Retool UIs.
    """
    def __init__(self, mcp_gateway_url: str = "http://localhost:8090"):
        self.mcp_client = MCPClient(mcp_gateway_url)
        self.gateway_url = mcp_gateway_url

    async def initialize(self):
        """Connect to the MCP gateway after ensuring it's healthy."""
        await self._wait_for_gateway()
        await self.mcp_client.connect()
        logger.info("MCP Client connected.")
        logger.info(f"Discovered servers: {self.mcp_client.list_servers()}")

    async def _wait_for_gateway(self, timeout: int = 60):
        """Polls the MCP gateway's health endpoint until it's ready."""
        start_time = asyncio.get_event_loop().time()
        health_url = f"{self.gateway_url}/health"
        logger.info(f"Waiting for MCP gateway to be healthy at {health_url}...")

        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"Gateway is healthy! Discovered servers: {data.get('discovered_servers', [])}")
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
        """
        Simulates building the 'MCP Mission Control' dashboard in Retool.
        """
        dashboard_name = "mcp_mission_control"
        logger.info(f"Simulating building dashboard: {dashboard_name}")

        # Since we don't have the actual MCP servers running, we'll simulate the response
        logger.info("This is a simulation - in a real environment, we would call:")
        logger.info("self.mcp_client.call_tool('retool', 'create_admin_dashboard', ...)")
        
        # Simulate a successful response
        app_id = "simulated-app-id-12345"
        logger.info(f"Simulated successful creation of Retool app '{dashboard_name}' with ID: {app_id}")

        # Conceptual next steps (same as original)
        logger.info("--- Conceptual Next Steps ---")
        logger.info(f"1. Add a 'Table' widget to app {app_id}.")
        logger.info("2. Create a new REST query in the Retool app named 'listMCPContainers'.")
        logger.info("3. Configure the query to POST to the MCP Gateway's /call_tool endpoint.")
        logger.info(f"4. The query body should be: {{ 'server': 'docker', 'tool': 'list_containers' }}")
        logger.info("5. Set the table's data source to `{{ listMCPContainers.data }}`.")
        logger.info("6. Set the query to run on page load and on a 30-second interval.")
        logger.info("--- End Conceptual Steps ---")

        return {
            "success": True,
            "app_id": app_id,
            "dashboard_name": dashboard_name,
            "message": "Dashboard creation simulated. In a real environment, manual steps would be required in Retool to add and configure widgets.",
            "note": "This is a simulation since the actual MCP servers are not running."
        }


async def main():
    """
    Main function to run the dashboard builder.
    """
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
