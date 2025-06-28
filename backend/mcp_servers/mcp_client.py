# File: backend/mcp/mcp_client.py

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional

import aiohttp
import logging

logger = logging.getLogger(__name__)

class MCPClient:
    """A generic client for interacting with various MCP servers."""

    def __init__(self, config_path: str = "cursor_mcp_config.json"):
        self.config = self._load_config(config_path)
        self.session: Optional[aiohttp.ClientSession] = None

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Loads the MCP configuration file."""
        config_file = Path(config_path)
        if not config_file.exists():
            logger.error(f"MCP config file not found at: {config_path}")
            raise FileNotFoundError(f"MCP config file not found at: {config_path}")
        
        with open(config_file, 'r') as f:
            return json.load(f)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Initializes and returns an aiohttp ClientSession."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
        return self.session

    async def call_mcp_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls a specific tool on a specified MCP server.
        """
        if server_name not in self.config.get("servers", {}):
            raise ValueError(f"MCP Server '{server_name}' not found in configuration.")

        server_config = self.config["servers"][server_name]
        base_url = server_config.get("baseUrl")

        if not base_url:
            raise ValueError(f"No baseUrl configured for MCP server '{server_name}'. Only HTTP servers are supported by this client.")

        endpoint = f"{base_url}/mcp/call_tool" # A conceptual unified endpoint
        payload = {
            "tool_name": tool_name,
            "arguments": arguments,
        }
        
        session = await self._get_session()
        
        try:
            logger.info(f"Calling tool '{tool_name}' on MCP server '{server_name}' with arguments: {arguments}")
            async with session.post(endpoint, json=payload) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Error calling MCP server '{server_name}': {e}")
            raise Exception(f"Failed to communicate with MCP server '{server_name}'.") from e

    async def close(self):
        """Closes the aiohttp session."""
        if self.session:
            await self.session.close()

async def main():
    # Example usage
    mcp_client = MCPClient()
    try:
        # This is an example and assumes a 'codacy' server is configured and running
        # with a tool named 'analyze_file'.
        analysis_result = await mcp_client.call_mcp_tool(
            server_name="codacy",
            tool_name="analyze_file",
            arguments={"file_path": "backend/services/semantic_layer_service.py"}
        )
        print("Analysis Result:", analysis_result)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await mcp_client.close()

if __name__ == "__main__":
    asyncio.run(main()) 
