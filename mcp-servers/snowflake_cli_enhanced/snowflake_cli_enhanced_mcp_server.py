#!/usr/bin/env python3
"""
Enhanced Snowflake CLI MCP Server for Sophia AI
Advanced CLI operations to complement existing Snowflake Cortex integration
Provides enhanced data operations, pipeline management, and Cortex AI features
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SnowflakeCLIEnhancedMCPServer:
    """Enhanced Snowflake CLI MCP Server with advanced operations"""
    
    def __init__(self, port: int = 9021):
        self.port = port
        self.server = Server("snowflake-cli-enhanced")
        
        # Snowflake configuration from environment/ESC
        self.account = os.getenv("SNOWFLAKE_ACCOUNT", "ZNB04675")
        self.user = os.getenv("SNOWFLAKE_USER", "SCOOBYJAVA15")
        self.database = os.getenv("SNOWFLAKE_DATABASE", "SOPHIA_AI_PROD")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
        self.role = os.getenv("SNOWFLAKE_ROLE", "SYSADMIN")
        
        # Enhanced CLI operation templates
        self.operation_templates = {
            "cortex_analysis": {
                "description": "Run Snowflake Cortex AI analysis",
                "supports": ["sentiment", "summarization", "classification", "translation"]
            },
            "data_pipeline": {
                "description": "Manage data pipelines and streams",
                "supports": ["create_stream", "create_task", "monitor_pipes"]
            },
            "optimization": {
                "description": "Database and warehouse optimization",
                "supports": ["query_optimization", "warehouse_scaling", "cost_analysis"]
            },
            "security": {
                "description": "Security and governance operations",
                "supports": ["role_management", "data_masking", "audit_logs"]
            }
        }
        
        self._register_tools()

    def _register_tools(self):
        """Register MCP tools for enhanced Snowflake CLI operations"""
        
        @self.server.call_tool()
        async def execute_cortex_ai(arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute Snowflake Cortex AI operations via CLI"""
            operation = arguments.get("operation", "")
            text_data = arguments.get("text", "")
            
            if not operation or not text_data:
                return [TextContent(
                    type="text",
                    text="❌ Error: Both 'operation' and 'text' are required"
                )]
            
            logger.info(f"🧠 Executing Cortex AI operation: {operation}")
            
            try:
                cortex_sql = self._generate_cortex_sql(operation, text_data)
                result = await self._execute_snowflake_sql(cortex_sql)
                
                if result["success"]:
                    response = f"🧠 **Snowflake Cortex AI - {operation.title()}:**\n\n"
                    response += f"**Input:** {text_data[:200]}...\n"
                    response += f"**Result:** {result['output']}"
                    return [TextContent(type="text", text=response)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Cortex AI operation failed: {result['error']}"
                    )]
                    
            except Exception as e:
                logger.error(f"❌ Error executing Cortex AI: {e}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error executing Cortex AI: {str(e)}"
                )]

        @self.server.call_tool()
        async def manage_data_pipeline(arguments: Dict[str, Any]) -> List[TextContent]:
            """Manage Snowflake data pipelines, streams, and tasks"""
            action = arguments.get("action", "")  # create_stream, create_task, list_pipes, monitor
            pipeline_name = arguments.get("name", "")
            config = arguments.get("config", {})
            
            if not action:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'action' is required (create_stream, create_task, list_pipes, monitor)"
                )]
            
            logger.info(f"🔄 Managing data pipeline: {action}")
            
            try:
                if action == "create_stream":
                    result = await self._create_stream(pipeline_name, config)
                elif action == "create_task":
                    result = await self._create_task(pipeline_name, config)
                elif action == "list_pipes":
                    result = await self._list_pipes()
                elif action == "monitor":
                    result = await self._monitor_pipelines()
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Unknown action: {action}"
                    )]
                
                if result["success"]:
                    response = f"🔄 **Data Pipeline Management - {action.title()}:**\n\n"
                    if pipeline_name:
                        response += f"**Pipeline:** {pipeline_name}\n"
                    response += f"**Action:** {action}\n"
                    response += f"**Status:** Success\n\n"
                    response += f"**Details:**\n{result['output']}"
                    
                    return [TextContent(type="text", text=response)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Pipeline operation failed: {result['error']}"
                    )]
                    
            except Exception as e:
                logger.error(f"❌ Error managing pipeline: {e}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error managing pipeline: {str(e)}"
                )]

        @self.server.call_tool()
        async def optimize_warehouse(arguments: Dict[str, Any]) -> List[TextContent]:
            """Optimize Snowflake warehouse performance and costs"""
            operation = arguments.get("operation", "analyze")  # analyze, scale, suspend, resume
            warehouse_name = arguments.get("warehouse", self.warehouse)
            target_size = arguments.get("size", "")
            
            logger.info(f"⚡ Optimizing warehouse: {operation}")
            
            try:
                if operation == "analyze":
                    result = await self._analyze_warehouse_usage(warehouse_name)
                elif operation == "scale":
                    if not target_size:
                        return [TextContent(
                            type="text",
                            text="❌ Error: 'size' is required for scale operation"
                        )]
                    result = await self._scale_warehouse(warehouse_name, target_size)
                elif operation == "suspend":
                    result = await self._suspend_warehouse(warehouse_name)
                elif operation == "resume":
                    result = await self._resume_warehouse(warehouse_name)
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Unknown operation: {operation}"
                    )]
                
                if result["success"]:
                    response = f"⚡ **Warehouse Optimization - {operation.title()}:**\n\n"
                    response += f"**Warehouse:** {warehouse_name}\n"
                    response += f"**Operation:** {operation}\n"
                    response += f"**Status:** Success\n\n"
                    response += f"**Results:**\n{result['output']}"
                    
                    return [TextContent(type="text", text=response)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Warehouse optimization failed: {result['error']}"
                    )]
                    
            except Exception as e:
                logger.error(f"❌ Error optimizing warehouse: {e}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error optimizing warehouse: {str(e)}"
                )]

        @self.server.call_tool()
        async def query_performance_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
            """Analyze query performance and provide optimization suggestions"""
            query_id = arguments.get("query_id", "")
            time_range = arguments.get("time_range", "last_24h")  # last_1h, last_24h, last_week
            limit = arguments.get("limit", 10)
            
            logger.info(f"📊 Analyzing query performance (range: {time_range})")
            
            try:
                if query_id:
                    result = await self._analyze_specific_query(query_id)
                else:
                    result = await self._analyze_query_performance(time_range, limit)
                
                if result["success"]:
                    response = f"📊 **Query Performance Analysis:**\n\n"
                    if query_id:
                        response += f"**Query ID:** {query_id}\n"
                    else:
                        response += f"**Time Range:** {time_range}\n"
                        response += f"**Top Queries:** {limit}\n"
                    response += f"\n**Analysis Results:**\n{result['output']}\n\n"
                    response += f"**Optimization Suggestions:**\n{result.get('suggestions', 'No specific suggestions available')}"
                    
                    return [TextContent(type="text", text=response)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Query analysis failed: {result['error']}"
                    )]
                    
            except Exception as e:
                logger.error(f"❌ Error analyzing queries: {e}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error analyzing queries: {str(e)}"
                )]

        @self.server.call_tool()
        async def execute_advanced_sql(arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute advanced SQL with enhanced features"""
            sql_query = arguments.get("query", "")
            explain = arguments.get("explain", False)
            profile = arguments.get("profile", False)
            format_output = arguments.get("format", "table")  # table, json, csv
            
            if not sql_query:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'query' is required"
                )]
            
            logger.info(f"🔍 Executing advanced SQL query")
            
            try:
                # Add EXPLAIN or PROFILE if requested
                if explain:
                    sql_query = f"EXPLAIN {sql_query}"
                elif profile:
                    sql_query = f"EXPLAIN USING TABLESCAN {sql_query}"
                
                result = await self._execute_snowflake_sql(sql_query, format_output)
                
                if result["success"]:
                    response = f"🔍 **Advanced SQL Execution:**\n\n"
                    response += f"**Query:** {sql_query[:200]}{'...' if len(sql_query) > 200 else ''}\n"
                    response += f"**Format:** {format_output}\n"
                    if explain:
                        response += f"**Type:** Query Explanation\n"
                    elif profile:
                        response += f"**Type:** Query Profiling\n"
                    response += f"**Execution Time:** {result.get('execution_time', 'unknown')}\n\n"
                    response += f"**Results:**\n{result['output']}"
                    
                    return [TextContent(type="text", text=response)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ SQL execution failed: {result['error']}"
                    )]
                    
            except Exception as e:
                logger.error(f"❌ Error executing SQL: {e}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error executing SQL: {str(e)}"
                )]

        @self.server.call_tool()
        async def cost_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
            """Analyze Snowflake costs and usage patterns"""
            analysis_type = arguments.get("type", "overview")
            time_range = arguments.get("time_range", "last_30d")
            
            logger.info(f"💰 Analyzing costs: {analysis_type}")
            
            try:
                if analysis_type == "overview":
                    result = await self._cost_overview(time_range)
                elif analysis_type == "warehouse":
                    result = await self._warehouse_cost_analysis(time_range)
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Unknown analysis type: {analysis_type}"
                    )]
                
                if result["success"]:
                    response = f"💰 **Cost Analysis - {analysis_type.title()}:**\n\n"
                    response += f"**Time Range:** {time_range}\n"
                    response += f"**Results:** {result['output']}"
                    return [TextContent(type="text", text=response)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Cost analysis failed: {result['error']}"
                    )]
                    
            except Exception as e:
                logger.error(f"❌ Error analyzing costs: {e}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error analyzing costs: {str(e)}"
                )]

    def _generate_cortex_sql(self, operation: str, text: str) -> str:
        """Generate Cortex AI SQL based on operation"""
        text_escaped = text.replace("'", "''")
        
        if operation == "sentiment":
            return f"SELECT SNOWFLAKE.CORTEX.SENTIMENT('{text_escaped}') as sentiment_score;"
        elif operation == "summarize":
            return f"SELECT SNOWFLAKE.CORTEX.SUMMARIZE('{text_escaped}') as summary;"
        else:
            raise ValueError(f"Unknown Cortex operation: {operation}")

    async def _execute_snowflake_sql(self, sql: str, format_output: str = "table") -> Dict[str, Any]:
        """Execute SQL using Snowflake CLI"""
        try:
            # Create temporary config file
            config_data = {
                "connections": {
                    "sophia_ai": {
                        "account": self.account,
                        "user": self.user,
                        "database": self.database,
                        "warehouse": self.warehouse,
                        "role": self.role
                    }
                }
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
                # Write TOML config
                f.write("[connections.sophia_ai]\n")
                f.write(f'account = "{self.account}"\n')
                f.write(f'user = "{self.user}"\n')
                f.write(f'database = "{self.database}"\n')
                f.write(f'warehouse = "{self.warehouse}"\n')
                f.write(f'role = "{self.role}"\n')
                config_file = f.name
            
            try:
                start_time = datetime.now()
                
                # Execute using snow CLI
                cmd = [
                    "snow", "sql",
                    "--config-file", config_file,
                    "--connection", "sophia_ai",
                    "--query", sql
                ]
                
                if format_output == "json":
                    cmd.extend(["--format", "json"])
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "output": result.stdout,
                        "execution_time": f"{execution_time:.2f}s"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.stderr or result.stdout
                    }
                    
            finally:
                # Clean up temp config file
                os.unlink(config_file)
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Query timed out after 60 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_stream(self, name: str, config: Dict) -> Dict[str, Any]:
        """Create a Snowflake stream"""
        table_name = config.get("table", "")
        if not table_name:
            return {"success": False, "error": "Table name required for stream"}
        
        sql = f"CREATE OR REPLACE STREAM {name} ON TABLE {table_name};"
        return await self._execute_snowflake_sql(sql)

    async def _create_task(self, name: str, config: Dict) -> Dict[str, Any]:
        """Create a Snowflake task"""
        schedule = config.get("schedule", "60 MINUTE")
        query = config.get("query", "")
        
        if not query:
            return {"success": False, "error": "Query required for task"}
        
        sql = f"""
        CREATE OR REPLACE TASK {name}
        WAREHOUSE = {self.warehouse}
        SCHEDULE = '{schedule}'
        AS
        {query};
        """
        return await self._execute_snowflake_sql(sql)

    async def _list_pipes(self) -> Dict[str, Any]:
        """List Snowflake pipes"""
        sql = "SHOW PIPES;"
        return await self._execute_snowflake_sql(sql)

    async def _monitor_pipelines(self) -> Dict[str, Any]:
        """Monitor pipeline status"""
        sql = """
        SELECT 
            pipe_name,
            is_stalled,
            last_received_message_timestamp,
            last_loaded_file_timestamp
        FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY())
        ORDER BY last_received_message_timestamp DESC
        LIMIT 10;
        """
        return await self._execute_snowflake_sql(sql)

    async def _analyze_warehouse_usage(self, warehouse: str) -> Dict[str, Any]:
        """Analyze warehouse usage patterns"""
        sql = f"""
        SELECT 
            warehouse_name,
            avg(credits_used) as avg_credits,
            sum(credits_used) as total_credits,
            count(*) as total_queries
        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
        WHERE warehouse_name = '{warehouse}'
        AND start_time >= CURRENT_DATE - 7
        GROUP BY warehouse_name;
        """
        return await self._execute_snowflake_sql(sql)

    async def _scale_warehouse(self, warehouse: str, size: str) -> Dict[str, Any]:
        """Scale warehouse size"""
        sql = f"ALTER WAREHOUSE {warehouse} SET WAREHOUSE_SIZE = {size};"
        return await self._execute_snowflake_sql(sql)

    async def _suspend_warehouse(self, warehouse: str) -> Dict[str, Any]:
        """Suspend warehouse"""
        sql = f"ALTER WAREHOUSE {warehouse} SUSPEND;"
        return await self._execute_snowflake_sql(sql)

    async def _resume_warehouse(self, warehouse: str) -> Dict[str, Any]:
        """Resume warehouse"""
        sql = f"ALTER WAREHOUSE {warehouse} RESUME;"
        return await self._execute_snowflake_sql(sql)

    async def _analyze_specific_query(self, query_id: str) -> Dict[str, Any]:
        """Analyze specific query performance"""
        sql = f"""
        SELECT 
            query_id,
            query_text,
            total_elapsed_time,
            compilation_time,
            execution_time,
            credits_used,
            warehouse_name
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE query_id = '{query_id}';
        """
        return await self._execute_snowflake_sql(sql)

    async def _analyze_query_performance(self, time_range: str, limit: int) -> Dict[str, Any]:
        """Analyze query performance for time range"""
        days = {"last_1h": 0, "last_24h": 1, "last_week": 7}.get(time_range, 1)
        
        sql = f"""
        SELECT 
            query_id,
            user_name,
            warehouse_name,
            total_elapsed_time,
            credits_used,
            query_text
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE start_time >= CURRENT_DATE - {days}
        ORDER BY total_elapsed_time DESC
        LIMIT {limit};
        """
        return await self._execute_snowflake_sql(sql)

    async def _cost_overview(self, time_range: str) -> Dict[str, Any]:
        """Get cost overview"""
        days = {"last_7d": 7, "last_30d": 30}.get(time_range, 30)
        
        sql = f"""
        SELECT 
            service_type,
            sum(credits_used) as total_credits
        FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
        WHERE start_time >= CURRENT_DATE - {days}
        GROUP BY service_type;
        """
        return await self._execute_snowflake_sql(sql)

    async def _warehouse_cost_analysis(self, time_range: str) -> Dict[str, Any]:
        """Analyze warehouse costs"""
        days = {"last_7d": 7, "last_30d": 30}.get(time_range, 30)
        
        sql = f"""
        SELECT 
            warehouse_name,
            sum(credits_used) as total_credits
        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
        WHERE start_time >= CURRENT_DATE - {days}
        GROUP BY warehouse_name;
        """
        return await self._execute_snowflake_sql(sql)

    async def start_server(self):
        """Start the Enhanced Snowflake CLI MCP server"""
        logger.info(f"🚀 Starting Enhanced Snowflake CLI MCP Server on port {self.port}")
        
        # Add health check endpoint
        @self.server.call_tool()
        async def health_check(arguments: Dict[str, Any]) -> List[TextContent]:
            """Health check for Enhanced Snowflake CLI MCP server"""
            
            # Check if snow CLI is available
            cli_available = subprocess.run(["which", "snow"], capture_output=True).returncode == 0
            config_complete = all([self.account, self.user, self.database])
            
            status = "healthy" if cli_available and config_complete else "degraded"
            
            response = f"✅ **Enhanced Snowflake CLI MCP Server Status:**\n\n"
            response += f"**Overall Status:** {status}\n"
            response += f"**Port:** {self.port}\n"
            response += f"**Snow CLI Available:** {'✅' if cli_available else '❌'}\n"
            response += f"**Configuration Complete:** {'✅' if config_complete else '❌'}\n\n"
            response += f"**Connection Details:**\n"
            response += f"  Account: {self.account}\n"
            response += f"  User: {self.user}\n"
            response += f"  Database: {self.database}\n"
            response += f"  Warehouse: {self.warehouse}\n\n"
            
            if not cli_available:
                response += f"⚠️ Install Snowflake CLI: Follow https://docs.snowflake.com/en/developer-guide/snowflake-cli\n"
            if not config_complete:
                response += f"⚠️ Set environment variables: SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_DATABASE\n"
            
            return [TextContent(type="text", text=response)]
        
        # Register tools as MCP tools
        tools = [
            Tool(
                name="execute_cortex_ai",
                description="Execute Snowflake Cortex AI operations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["sentiment", "summarize"]},
                        "text": {"type": "string"}
                    },
                    "required": ["operation", "text"]
                }
            ),
            Tool(
                name="manage_data_pipeline",
                description="Manage Snowflake data pipelines, streams, and tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["create_stream", "create_task", "list_pipes", "monitor"]},
                        "name": {"type": "string"},
                        "config": {"type": "object"}
                    },
                    "required": ["action"]
                }
            ),
            Tool(
                name="optimize_warehouse",
                description="Optimize Snowflake warehouse performance and costs",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["analyze", "scale", "suspend", "resume"]},
                        "warehouse": {"type": "string"},
                        "size": {"type": "string", "enum": ["X-SMALL", "SMALL", "MEDIUM", "LARGE", "X-LARGE", "2X-LARGE", "3X-LARGE", "4X-LARGE"]}
                    },
                    "required": ["operation"]
                }
            ),
            Tool(
                name="query_performance_analysis",
                description="Analyze query performance and provide optimization suggestions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query_id": {"type": "string"},
                        "time_range": {"type": "string", "enum": ["last_1h", "last_24h", "last_week"], "default": "last_24h"},
                        "limit": {"type": "number", "default": 10}
                    }
                }
            ),
            Tool(
                name="execute_advanced_sql",
                description="Execute advanced SQL with enhanced features (explain, profile)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "explain": {"type": "boolean", "default": False},
                        "profile": {"type": "boolean", "default": False},
                        "format": {"type": "string", "enum": ["table", "json", "csv"], "default": "table"}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="cost_analysis",
                description="Analyze Snowflake costs and usage patterns",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["overview", "warehouse"], "default": "overview"},
                        "time_range": {"type": "string", "enum": ["last_7d", "last_30d"], "default": "last_30d"}
                    }
                }
            ),
            Tool(
                name="health_check",
                description="Check Enhanced Snowflake CLI MCP server health and configuration",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
        
        # Set tools on server
        self.server.tools = tools
        
        # Start the server
        await self.server.run(port=self.port)

# Main execution
async def main():
    server = SnowflakeCLIEnhancedMCPServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down Enhanced Snowflake CLI MCP Server")

if __name__ == "__main__":
    asyncio.run(main()) 