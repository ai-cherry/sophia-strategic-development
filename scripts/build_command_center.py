"""
Builds the main "Sophia AI Command Center" Retool application shell.
"""
import asyncio
import json
import logging
import time

from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)

async def build_command_center():
    """
    Uses the Retool MCP to create the main command center app.
    """
    dashboard_name = "sophia_ai_command_center"
    logger.info(f"Attempting to build Retool App: {dashboard_name}")
    
    mcp_client = MCPClient("http://localhost:8090")
    
    try:
        await mcp_client.connect()
        
        create_app_result = await mcp_client.call_tool(
            "retool",
            "create_admin_dashboard",
            dashboard_name=dashboard_name,
            description="Main command and control center for Sophia AI. Issue natural language commands to manage infrastructure and agents."
        )
        
        print("\n--- Retool App Build Summary ---")
        print(json.dumps(create_app_result, indent=2))
        print("----------------------------------")

        if create_app_result.get("success"):
            logger.info("--- Next Steps in Retool ---")
            logger.info("1. Open the new 'sophia_ai_command_center' app in Retool.")
            logger.info("2. Drag a 'Text Input' component onto the canvas, name it 'command_input'.")
            logger.info("3. Drag a 'Button' component, label it 'Execute'.")
            logger.info("4. Create a new RESTQuery named 'runSophiaCommand'.")
            logger.info("   - Set it to POST to: http://<your_api_host>/api/v1/sophia/command")
            logger.info("   - Set the body to: {'command': {{command_input.value}} }")
            logger.info("5. Set the 'Execute' button's onClick event to trigger the 'runSophiaCommand' query.")
            logger.info("6. Drag a 'JSON Explorer' component onto the canvas and set its data to `{{runSophiaCommand.data}}` to display results.")

    finally:
        await mcp_client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Give Docker services time to start up
    print("Waiting 15 seconds for services to initialize...")
    time.sleep(15)
    asyncio.run(build_command_center()) 