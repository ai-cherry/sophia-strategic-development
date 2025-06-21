"""MCP to Agno Bridge.

Converts MCP tools to Agno tools for seamless integration
"""

import logging
import time
from typing import Any, Dict, List, Optional

from backend.integrations.agno_integration import AgnoTool
from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class MCPToAgnoBridge:
    """Bridge between MCP and Agno.

            Converts MCP tools to Agno tools.
    """def __init__(self, mcp_client: MCPClient):."""Initialize the MCP to Agno bridge.

        Args:
            mcp_client: The MCP client to use
        """self.mcp_client = mcp_client.

                        self.tool_cache = {}  # server_name:tool_name -> AgnoTool
                        self.cache_ttl = 3600  # 1 hour
                        self.cache_timestamps = {}  # server_name:tool_name -> timestamp
                        self.conversion_count = 0
                        self.cache_hits = 0
                        self.cache_misses = 0

                    async def convert_mcp_tool(
                        self, server_name: str, tool_name: str
                    ) -> Optional[AgnoTool]:
        """Convert an MCP tool to an Agno tool.

        Args:
            server_name: The name of the MCP server
            tool_name: The name of the MCP tool

        Returns:
            Optional[AgnoTool]: The converted Agno tool, or None if conversion failed
        """# Check cache.

                        cache_key = f"{server_name}:{tool_name}"
                        if cache_key in self.tool_cache:
                            # Check if cache entry is still valid
                            if time.time() - self.cache_timestamps[cache_key] < self.cache_ttl:
                                self.cache_hits += 1
                                return self.tool_cache[cache_key]

                        self.cache_misses += 1

                        try:
                            # Get tool schema from MCP
                            schema = await self.mcp_client.get_tool_schema(server_name, tool_name)
                            if not schema:
                                logger.warning(f"Failed to get schema for {server_name}.{tool_name}")
                                return None

                            # Extract tool information
                            description = schema.get(
                                "description", f"Tool {tool_name} from {server_name}"
                            )
                            parameters = schema.get("parameters", {})

                            # Create function that calls the MCP tool
                            async def tool_function(**kwargs):
                                return await self.mcp_client.call_tool(server_name, tool_name, **kwargs)

                            # Create Agno tool
                            agno_tool = AgnoTool(
                                name=f"{server_name}.{tool_name}",
                                description=description,
                                parameters=parameters,
                                function=tool_function,
                            )

                            # Cache tool
                            self.tool_cache[cache_key] = agno_tool
                            self.cache_timestamps[cache_key] = time.time()
                            self.conversion_count += 1

                            logger.info(f"Converted {server_name}.{tool_name} to Agno tool")
                            return agno_tool
                        except Exception as e:
                            logger.error(
                                f"Failed to convert {server_name}.{tool_name} to Agno tool: {e}"
                            )
                            return None

                    async def convert_server_tools(self, server_name: str) -> List[AgnoTool]:
        """Convert all tools from an MCP server to Agno tools.

        Args:
            server_name: The name of the MCP server

        Returns:
            List[AgnoTool]: The converted Agno tools
        """try:

                            # Get list of tools from MCP
                            tool_names = self.mcp_client.list_tools(server_name)
                            if not tool_names:
                                logger.warning(f"No tools found for server {server_name}")
                                return []

                            # Convert each tool
                            agno_tools = []
                            for tool_name in tool_names:
                                agno_tool = await self.convert_mcp_tool(server_name, tool_name)
                                if agno_tool:
                                    agno_tools.append(agno_tool)

                            logger.info(f"Converted {len(agno_tools)} tools from {server_name}")
                            return agno_tools
                        except Exception as e:
                            logger.error(f"Failed to convert tools from {server_name}: {e}")
                            return []

                    async def convert_all_mcp_tools(self) -> List[AgnoTool]:
        """Convert all MCP tools to Agno tools.

        Returns:
            List[AgnoTool]: The converted Agno tools
        """try:

                            # Get list of servers from MCP
                            server_names = self.mcp_client.list_servers()
                            if not server_names:
                                logger.warning("No MCP servers found")
                                return []

                            # Convert tools from each server
                            all_tools = []
                            for server_name in server_names:
                                server_tools = await self.convert_server_tools(server_name)
                                all_tools.extend(server_tools)

                            logger.info(
                                f"Converted {len(all_tools)} tools from {len(server_names)} servers"
                            )
                            return all_tools
                        except Exception as e:
                            logger.error(f"Failed to convert all MCP tools: {e}")
                            return []

                    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the tool cache.

        Returns:
            Dict[str, Any]: Statistics about the tool cache
        """return {.

                            "cache_size": len(self.tool_cache),
                            "cache_ttl": self.cache_ttl,
                            "conversion_count": self.conversion_count,
                            "cache_hits": self.cache_hits,
                            "cache_misses": self.cache_misses,
                            "hit_ratio": (
                                self.cache_hits / (self.cache_hits + self.cache_misses)
                                if (self.cache_hits + self.cache_misses) > 0
                                else 0
                            ),
                            "cached_tools": list(self.tool_cache.keys()),
                        }

                    def clear_cache(self):
        """Clear the tool cache."""
        self.tool_cache = {}
        self.cache_timestamps = {}
        logger.info("Tool cache cleared")
