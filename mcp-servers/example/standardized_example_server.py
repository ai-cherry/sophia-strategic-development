"""
Example Standardized MCP Server
Demonstrates usage of StandardizedMCPServer base class
"""

import json
from typing import List
from mcp.types import TextContent, Tool

from backend.services.standardized_mcp_server import StandardizedMCPServer, MCPServerConfig

class ExampleMCPServer(StandardizedMCPServer):
    """Example MCP server using standardized base"""
    
    def __init__(self):
        config = MCPServerConfig(
            name="example_server",
            port=9999,
            capabilities=["example_capability", "health_check", "metrics"]
        )
        super().__init__(config)
    
    def _setup_custom_tools(self):
        """Setup example-specific tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="example_tool",
                    description="Example tool for demonstration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "Message to process"}
                        },
                        "required": ["message"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def example_tool(arguments: dict) -> List[TextContent]:
            """Example tool implementation"""
            message = arguments.get("message", "Hello, World!")
            
            response = {
                "processed_message": message.upper(),
                "timestamp": datetime.now().isoformat(),
                "server": self.config.name
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(response, indent=2)
            )]
    
    async def _execute_tool(self, tool_name: str, arguments: dict) -> List[TextContent]:
        """Execute tool with server-specific logic"""
        if tool_name == "example_tool":
            return await self.example_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

# Main entry point
if __name__ == "__main__":
    import asyncio
    
    async def main():
        server = ExampleMCPServer()
        await server.run()
    
    asyncio.run(main())
