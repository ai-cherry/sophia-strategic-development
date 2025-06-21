"""Builds the main "Sophia AI Command Center" Retool application shell."""

import asyncio
import json
import logging
import time

from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)


async def build_command_center():
    """Uses the Retool MCP to create the main command center app."""
    dashboard_name = "sophia_ai_command_center"
    logger.info(f"Attempting to build Retool App: {dashboard_name}")

    mcp_client = MCPClient("http://localhost:8090")

    try:
        await mcp_client.connect()

        create_app_result = await mcp_client.call_tool(
            "retool",
            "create_admin_dashboard",
            dashboard_name=dashboard_name,
            description="Main command and control center for Sophia AI. Issue natural language commands to manage infrastructure and agents.",
        )

        print("\n--- Retool App Build Summary ---")
        print(json.dumps(create_app_result, indent=2))
        print("----------------------------------")

        if not create_app_result.get("success"):
            logger.error("Failed to create the Retool application shell. Aborting.")
            return

        app_data = create_app_result.get("data", {})
        app_id = app_data.get("id")

        if not app_id:
            logger.error(
                "Could not get App ID from creation response. Aborting widget creation."
            )
            return

        # --- Step 2: Add the MCP Status Table ---
        logger.info(f"Adding the MCP Status Table widget to app {app_id}...")

        # Define the properties for a Retool Table widget
        # This includes the query that will populate it.
        table_properties = {
            "id": "mcpStatusTable",
            "type": "Table",
            "layout": {"x": 0, "y": 1, "width": 12, "height": 10},
            "data": "{{ listMCPContainers.data.result[0].text }}",  # Assumes result is JSON string in text
            "query": {
                "id": "listMCPContainers",
                "type": "rest-query",
                "resource": "SophiaAPI",  # Assumes a pre-configured REST resource in Retool
                "query": "/api/v1/mcp/tool_call",
                "method": "POST",
                "body": {
                    "server": "docker",
                    "tool": "list_containers",
                    "arguments": {"all": True},
                },
                "trigger": "onPageLoad",
            },
        }

        add_widget_result = await mcp_client.call_tool(
            "retool",
            "add_component",
            app_id=app_id,
            component_type="Table",
            name="mcp_status_table",
            properties=table_properties,
        )

        print("\n--- Add Widget Summary ---")
        print(json.dumps(add_widget_result, indent=2))
        print("--------------------------")

        if add_widget_result.get("success"):
            logger.info(
                "🎉 Successfully created and configured the 'MCP Mission Control' dashboard in Retool!"
            )
        else:
            logger.error("Failed to add the status table widget to the Retool app.")

    finally:
        await mcp_client.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Give Docker services time to start up
    print("Waiting 15 seconds for services to initialize...")
    time.sleep(15)
    asyncio.run(build_command_center())
