#!/usr/bin/env python3
"""
Build Sophia Admin Dashboard using Retool MCP
This script builds the Sophia Admin Dashboard using the Retool MCP server,
replacing the old sophia_admin_frontend UI.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, List

from backend.mcp.mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdminDashboardBuilder:
    """
    Builds the Sophia Admin Dashboard using the Retool MCP server.
    """
    
    def __init__(self, mcp_gateway_url: str = "http://localhost:8090"):
        self.mcp_client = MCPClient(mcp_gateway_url)
    
    async def initialize(self):
        """Connect to the MCP gateway."""
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
                async with self.mcp_client.session.get(health_url) as response:
                    if response.status == 200:
                        logger.info("MCP gateway is healthy!")
                        return
            except Exception:
                pass  # Ignore connection errors while waiting

            if asyncio.get_event_loop().time() - start_time >= timeout:
                raise TimeoutError(f"Gateway not healthy after {timeout} seconds.")
            
            await asyncio.sleep(5)
    
    async def close(self):
        """Close the MCP client connection."""
        await self.mcp_client.close()
        logger.info("MCP Client disconnected.")
    
    async def build_admin_dashboard(self) -> Dict[str, Any]:
        """
        Builds the Sophia Admin Dashboard in Retool.
        """
        dashboard_name = "sophia_admin"
        logger.info(f"Building dashboard: {dashboard_name}")
        
        try:
            # Step 1: Create the main Retool application
            create_app_result = await self.mcp_client.call_tool(
                "retool",
                "create_admin_dashboard",
                {
                    "dashboard_name": dashboard_name,
                    "description": "Sophia AI Admin Dashboard for Pay Ready"
                }
            )
            
            if not create_app_result.get("success", False):
                logger.error(f"Failed to create Retool app: {create_app_result.get('error')}")
                return {"success": False, "error": "Failed to create Retool app"}
            
            app_data = create_app_result.get("data", {})
            app_id = app_data.get("id")
            logger.info(f"Successfully created Retool app '{dashboard_name}' with ID: {app_id}")
            
            # Step 2: Add MCP Server Status Widget
            logger.info("Adding MCP Server Status widget...")
            mcp_status_result = await self.mcp_client.call_tool(
                "retool",
                "add_dashboard_widget",
                {
                    "app_id": app_id,
                    "widget_type": "table",
                    "widget_name": "mcp_server_status",
                    "widget_title": "MCP Server Status",
                    "data_source": "mcp_servers",
                    "refresh_interval": 30
                }
            )
            
            if not mcp_status_result.get("success", False):
                logger.warning(f"Failed to add MCP Server Status widget: {mcp_status_result.get('error')}")
            
            # Step 3: Add User Management Widget
            logger.info("Adding User Management widget...")
            user_mgmt_result = await self.mcp_client.call_tool(
                "retool",
                "add_dashboard_widget",
                {
                    "app_id": app_id,
                    "widget_type": "crud",
                    "widget_name": "user_management",
                    "widget_title": "User Management",
                    "data_source": "users",
                    "actions": ["create", "read", "update", "delete"]
                }
            )
            
            if not user_mgmt_result.get("success", False):
                logger.warning(f"Failed to add User Management widget: {user_mgmt_result.get('error')}")
            
            # Step 4: Add System Health Widget
            logger.info("Adding System Health widget...")
            health_result = await self.mcp_client.call_tool(
                "retool",
                "add_dashboard_widget",
                {
                    "app_id": app_id,
                    "widget_type": "chart",
                    "widget_name": "system_health",
                    "widget_title": "System Health",
                    "chart_type": "line",
                    "data_source": "system_metrics",
                    "refresh_interval": 60
                }
            )
            
            if not health_result.get("success", False):
                logger.warning(f"Failed to add System Health widget: {health_result.get('error')}")
            
            # Step 5: Add Integration Status Widget
            logger.info("Adding Integration Status widget...")
            integration_result = await self.mcp_client.call_tool(
                "retool",
                "add_dashboard_widget",
                {
                    "app_id": app_id,
                    "widget_type": "table",
                    "widget_name": "integration_status",
                    "widget_title": "Integration Status",
                    "data_source": "integrations",
                    "refresh_interval": 60
                }
            )
            
            if not integration_result.get("success", False):
                logger.warning(f"Failed to add Integration Status widget: {integration_result.get('error')}")
            
            # Step 6: Add Knowledge Base Management Widget
            logger.info("Adding Knowledge Base Management widget...")
            kb_result = await self.mcp_client.call_tool(
                "retool",
                "add_dashboard_widget",
                {
                    "app_id": app_id,
                    "widget_type": "crud",
                    "widget_name": "knowledge_base",
                    "widget_title": "Knowledge Base Management",
                    "data_source": "knowledge_base",
                    "actions": ["create", "read", "update", "delete"]
                }
            )
            
            if not kb_result.get("success", False):
                logger.warning(f"Failed to add Knowledge Base Management widget: {kb_result.get('error')}")
            
            # Step 7: Add Gong Call Analytics Widget
            logger.info("Adding Gong Call Analytics widget...")
            gong_result = await self.mcp_client.call_tool(
                "retool",
                "add_dashboard_widget",
                {
                    "app_id": app_id,
                    "widget_type": "chart",
                    "widget_name": "gong_analytics",
                    "widget_title": "Gong Call Analytics",
                    "chart_type": "bar",
                    "data_source": "gong_calls",
                    "refresh_interval": 3600
                }
            )
            
            if not gong_result.get("success", False):
                logger.warning(f"Failed to add Gong Call Analytics widget: {gong_result.get('error')}")
            
            # Step 8: Add AI Memory Inspector Widget
            logger.info("Adding AI Memory Inspector widget...")
            memory_result = await self.mcp_client.call_tool(
                "retool",
                "add_dashboard_widget",
                {
                    "app_id": app_id,
                    "widget_type": "table",
                    "widget_name": "ai_memory",
                    "widget_title": "AI Memory Inspector",
                    "data_source": "ai_memory",
                    "actions": ["read", "delete"]
                }
            )
            
            if not memory_result.get("success", False):
                logger.warning(f"Failed to add AI Memory Inspector widget: {memory_result.get('error')}")
            
            # Step 9: Publish the dashboard
            logger.info("Publishing dashboard...")
            publish_result = await self.mcp_client.call_tool(
                "retool",
                "publish_dashboard",
                {
                    "app_id": app_id
                }
            )
            
            if not publish_result.get("success", False):
                logger.warning(f"Failed to publish dashboard: {publish_result.get('error')}")
            
            return {
                "success": True,
                "app_id": app_id,
                "dashboard_name": dashboard_name,
                "dashboard_url": f"http://localhost:3000/apps/{app_id}",
                "widgets": [
                    "mcp_server_status",
                    "user_management",
                    "system_health",
                    "integration_status",
                    "knowledge_base",
                    "gong_analytics",
                    "ai_memory"
                ]
            }
            
        except Exception as e:
            logger.error(f"An error occurred while building the dashboard: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


async def main():
    """
    Main function to run the dashboard builder.
    """
    # NOTE: This assumes the MCP Gateway and the Retool MCP server are running.
    # You can start them with `docker-compose up mcp-gateway retool-mcp`
    
    builder = AdminDashboardBuilder()
    try:
        await builder.initialize()
        result = await builder.build_admin_dashboard()
        
        print("\n--- Admin Dashboard Build Summary ---")
        print(json.dumps(result, indent=2))
        print("--------------------------------------")
        
        if result.get("success", False):
            print(f"\nDashboard URL: {result.get('dashboard_url')}")
            print("\nYou can now access the Sophia Admin Dashboard at the URL above.")
            print("This dashboard replaces the old sophia_admin_frontend UI.")
        else:
            print("\nFailed to build the Admin Dashboard.")
            sys.exit(1)
        
    finally:
        await builder.close()


if __name__ == "__main__":
    asyncio.run(main())
