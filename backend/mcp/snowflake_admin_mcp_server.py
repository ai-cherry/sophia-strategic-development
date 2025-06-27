#!/usr/bin/env python3
"""
Sophia AI - Snowflake Administration MCP Server
Provides Model Context Protocol interface for Snowflake management
Integrates with the standardized MCP architecture
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.mcp.base.standardized_mcp_server import StandardizedMCPServer
from scripts.snowflake_config_manager import SnowflakeConfigManager

class SnowflakeAdminMCPServer(StandardizedMCPServer):
    """MCP Server for Snowflake administration and configuration."""
    
    def __init__(self):
        super().__init__("snowflake_admin")
        self.snowflake_manager = SnowflakeConfigManager()
        
    async def initialize(self):
        """Initialize the Snowflake MCP server."""
        await super().initialize()
        print("🏔️ Snowflake Administration MCP Server initialized")
        
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls for Snowflake operations."""
        try:
            if not await self.snowflake_manager.connect():
                return {
                    "success": False,
                    "error": "Failed to connect to Snowflake",
                    "data": None
                }
            
            if tool_name == "sync_schemas":
                result = await self.snowflake_manager.sync_github_schemas()
                return {
                    "success": len(result.get("errors", [])) == 0,
                    "data": result,
                    "message": "Schema synchronization completed"
                }
                
            elif tool_name == "get_status":
                result = await self.snowflake_manager.get_system_status()
                return {
                    "success": True,
                    "data": result,
                    "message": "System status retrieved"
                }
                
            elif tool_name == "optimize_performance":
                result = await self.snowflake_manager.optimize_performance()
                return {
                    "success": len(result.get("errors", [])) == 0,
                    "data": result,
                    "message": "Performance optimization completed"
                }
                
            elif tool_name == "execute_query":
                query = arguments.get("query", "")
                if not query:
                    return {
                        "success": False,
                        "error": "Query parameter is required",
                        "data": None
                    }
                
                result = self.snowflake_manager.execute_query(query)
                return {
                    "success": True,
                    "data": result,
                    "message": f"Query executed successfully, returned {len(result) if result else 0} rows"
                }
                
            elif tool_name == "create_airbyte_integration":
                # Create specific integration for Airbyte data sources
                await self._setup_airbyte_integration()
                return {
                    "success": True,
                    "data": {"integration": "airbyte_ready"},
                    "message": "Airbyte integration configured"
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "data": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
        finally:
            self.snowflake_manager.close_connection()
    
    async def _setup_airbyte_integration(self):
        """Set up specific Airbyte integration configurations."""
        # Create Airbyte-specific roles and permissions
        airbyte_setup_sql = """
        -- Create Airbyte service role
        CREATE ROLE IF NOT EXISTS AIRBYTE_SERVICE_ROLE;
        
        -- Grant necessary permissions
        GRANT USAGE ON DATABASE SOPHIA_AI_CORE TO ROLE AIRBYTE_SERVICE_ROLE;
        GRANT USAGE ON SCHEMA SOPHIA_GONG_RAW TO ROLE AIRBYTE_SERVICE_ROLE;
        GRANT USAGE ON SCHEMA SOPHIA_SLACK_RAW TO ROLE AIRBYTE_SERVICE_ROLE;
        GRANT INSERT, SELECT, UPDATE ON ALL TABLES IN SCHEMA SOPHIA_GONG_RAW TO ROLE AIRBYTE_SERVICE_ROLE;
        GRANT INSERT, SELECT, UPDATE ON ALL TABLES IN SCHEMA SOPHIA_SLACK_RAW TO ROLE AIRBYTE_SERVICE_ROLE;
        
        -- Create Airbyte monitoring table
        CREATE TABLE IF NOT EXISTS SOPHIA_AI_CORE.PUBLIC.airbyte_sync_log (
            sync_id VARCHAR(255),
            source_type VARCHAR(100),
            sync_start_time TIMESTAMP,
            sync_end_time TIMESTAMP,
            records_processed INTEGER,
            status VARCHAR(50),
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        );
        """
        
        self.snowflake_manager.execute_query(airbyte_setup_sql, fetch_results=False)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools for this MCP server."""
        return [
            {
                "name": "sync_schemas",
                "description": "Synchronize Snowflake schemas with GitHub codebase",
                "parameters": {}
            },
            {
                "name": "get_status", 
                "description": "Get comprehensive Snowflake system status",
                "parameters": {}
            },
            {
                "name": "optimize_performance",
                "description": "Apply performance optimizations to Snowflake",
                "parameters": {}
            },
            {
                "name": "execute_query",
                "description": "Execute a SQL query on Snowflake",
                "parameters": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute",
                        "required": True
                    }
                }
            },
            {
                "name": "create_airbyte_integration",
                "description": "Set up Airbyte integration configurations",
                "parameters": {}
            }
        ]

async def main():
    """Main entry point for the Snowflake Admin MCP Server."""
    server = SnowflakeAdminMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())

