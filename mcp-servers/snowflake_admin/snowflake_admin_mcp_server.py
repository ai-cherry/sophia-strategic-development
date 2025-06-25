#!/usr/bin/env python3

"""
Snowflake Admin MCP Server
Natural language interface for Snowflake administration through LangChain SQL Agent
"""

import asyncio
import json
import logging
from typing import Dict, List, Any

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Snowflake Admin Agent
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.agents.specialized.snowflake_admin_agent import (
    SnowflakeAdminAgent,
    SnowflakeEnvironment,
    execute_snowflake_admin_task,
    confirm_snowflake_admin_task,
)

logger = logging.getLogger(__name__)

# MCP Server instance
server = Server("snowflake-admin")

# Global agent instance
admin_agent = SnowflakeAdminAgent()

# Pending confirmations (in production, use Redis or database)
pending_confirmations = {}


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Snowflake administration tools"""
    return [
        Tool(
            name="execute_admin_task",
            description="Execute a Snowflake administration task using natural language",
            inputSchema={
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "Natural language description of the admin task",
                    },
                    "environment": {
                        "type": "string",
                        "enum": ["dev", "stg", "prod"],
                        "description": "Target Snowflake environment",
                        "default": "dev",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID requesting the task",
                        "default": "system",
                    },
                },
                "required": ["request"],
            },
        ),
        Tool(
            name="confirm_admin_task",
            description="Confirm and execute a previously proposed dangerous SQL operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "confirmation_id": {
                        "type": "string",
                        "description": "ID of the pending confirmation",
                    },
                    "confirmed": {
                        "type": "boolean",
                        "description": "Whether to proceed with the operation",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID confirming the task",
                        "default": "system",
                    },
                },
                "required": ["confirmation_id", "confirmed"],
            },
        ),
        Tool(
            name="get_environment_info",
            description="Get information about a Snowflake environment",
            inputSchema={
                "type": "object",
                "properties": {
                    "environment": {
                        "type": "string",
                        "enum": ["dev", "stg", "prod"],
                        "description": "Target Snowflake environment",
                        "default": "dev",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="health_check",
            description="Perform health check on Snowflake Admin Agent",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="list_common_tasks",
            description="List common Snowflake administration tasks with examples",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": [
                            "schema",
                            "warehouse",
                            "role",
                            "user",
                            "grants",
                            "inspection",
                        ],
                        "description": "Category of tasks to list",
                    }
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for Snowflake administration"""

    try:
        if name == "execute_admin_task":
            request_text = arguments["request"]
            environment = arguments.get("environment", "dev")
            user_id = arguments.get("user_id", "system")

            # Execute the admin task
            response = await execute_snowflake_admin_task(
                natural_language_request=request_text,
                target_environment=environment,
                user_id=user_id,
            )

            # Handle confirmation requirement
            if response.requires_confirmation:
                # Generate confirmation ID
                confirmation_id = f"confirm_{len(pending_confirmations)}_{asyncio.get_event_loop().time()}"

                # Store pending confirmation
                pending_confirmations[confirmation_id] = {
                    "original_request": request_text,
                    "sql": response.confirmation_sql,
                    "environment": environment,
                    "user_id": user_id,
                    "timestamp": asyncio.get_event_loop().time(),
                }

                result = {
                    "status": "confirmation_required",
                    "message": response.message,
                    "confirmation_id": confirmation_id,
                    "proposed_sql": response.confirmation_sql,
                    "environment": environment,
                    "warning": "⚠️ This operation contains potentially destructive SQL. Review carefully before confirming.",
                    "instructions": f"To proceed, use confirm_admin_task with confirmation_id: {confirmation_id}",
                }
            else:
                result = {
                    "status": "success" if response.success else "error",
                    "message": response.message,
                    "sql_executed": response.sql_executed,
                    "environment": environment,
                    "execution_time": f"{response.execution_time:.2f}s",
                }

                if response.results:
                    result["results"] = response.results[
                        :10
                    ]  # Limit results for display
                    if len(response.results) > 10:
                        result["results_truncated"] = (
                            f"Showing 10 of {len(response.results)} results"
                        )

            return [
                TextContent(type="text", text=json.dumps(result, indent=2, default=str))
            ]

        elif name == "confirm_admin_task":
            confirmation_id = arguments["confirmation_id"]
            confirmed = arguments["confirmed"]
            user_id = arguments.get("user_id", "system")

            # Check if confirmation exists
            if confirmation_id not in pending_confirmations:
                result = {
                    "status": "error",
                    "message": f"Confirmation ID {confirmation_id} not found or expired",
                }
            elif not confirmed:
                # User declined
                del pending_confirmations[confirmation_id]
                result = {
                    "status": "cancelled",
                    "message": "Operation cancelled by user",
                }
            else:
                # User confirmed - execute the SQL
                confirmation_data = pending_confirmations[confirmation_id]

                response = await confirm_snowflake_admin_task(
                    natural_language_request=confirmation_data["original_request"],
                    confirmed_sql=confirmation_data["sql"],
                    target_environment=confirmation_data["environment"],
                    user_id=user_id,
                )

                # Remove from pending confirmations
                del pending_confirmations[confirmation_id]

                result = {
                    "status": "executed" if response.success else "error",
                    "message": response.message,
                    "sql_executed": response.sql_executed,
                    "environment": confirmation_data["environment"],
                    "execution_time": f"{response.execution_time:.2f}s",
                }

                if response.results:
                    result["results"] = response.results[:10]
                    if len(response.results) > 10:
                        result["results_truncated"] = (
                            f"Showing 10 of {len(response.results)} results"
                        )

            return [
                TextContent(type="text", text=json.dumps(result, indent=2, default=str))
            ]

        elif name == "get_environment_info":
            environment = arguments.get("environment", "dev")

            try:
                env = SnowflakeEnvironment(environment.lower())
                info = await admin_agent.get_environment_info(env)

                result = {"status": "success", "environment_info": info}
            except ValueError:
                result = {
                    "status": "error",
                    "message": f"Invalid environment: {environment}. Must be one of: dev, stg, prod",
                }

            return [
                TextContent(type="text", text=json.dumps(result, indent=2, default=str))
            ]

        elif name == "health_check":
            health = await admin_agent.health_check()

            result = {
                "status": "success",
                "health_check": health,
                "pending_confirmations": len(pending_confirmations),
            }

            return [
                TextContent(type="text", text=json.dumps(result, indent=2, default=str))
            ]

        elif name == "list_common_tasks":
            category = arguments.get("category")

            common_tasks = {
                "schema": [
                    "Create a new schema called MARKETING_STAGE",
                    "Show all schemas in the current database",
                    "Describe the schema SALES_DATA",
                    "Grant USAGE on schema ANALYTICS to role DATA_ANALYST",
                ],
                "warehouse": [
                    "Create a warehouse called DEV_WH with size XSMALL",
                    "Show all warehouses and their status",
                    "Alter warehouse COMPUTE_WH to auto suspend after 60 seconds",
                    "Grant USAGE on warehouse ANALYTICS_WH to role ANALYST",
                ],
                "role": [
                    "Create a new role called DATA_SCIENTIST",
                    "Show all roles in the account",
                    "Grant role DEVELOPER to user john.doe@company.com",
                    "Show grants for role ANALYST",
                ],
                "user": [
                    "Show all users in the account",
                    "Describe user john.doe@company.com",
                    "Show what roles are granted to user jane.smith@company.com",
                ],
                "grants": [
                    "Show all grants on database ANALYTICS",
                    "Grant SELECT on all tables in schema SALES to role ANALYST",
                    "Show grants for role DATA_ENGINEER",
                    "Revoke USAGE on warehouse DEV_WH from role INTERN",
                ],
                "inspection": [
                    "Show all tables in schema SALES_DATA",
                    "Describe table CUSTOMERS",
                    "Show the DDL for table ORDERS",
                    "List all columns in table PRODUCTS with their data types",
                ],
            }

            if category:
                if category in common_tasks:
                    result = {
                        "status": "success",
                        "category": category,
                        "tasks": common_tasks[category],
                    }
                else:
                    result = {
                        "status": "error",
                        "message": f"Unknown category: {category}",
                        "available_categories": list(common_tasks.keys()),
                    }
            else:
                result = {"status": "success", "all_categories": common_tasks}

            return [
                TextContent(type="text", text=json.dumps(result, indent=2, default=str))
            ]

        else:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2),
                )
            ]

    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "error",
                        "message": f"Tool execution failed: {str(e)}",
                        "tool": name,
                    },
                    indent=2,
                ),
            )
        ]


async def cleanup_expired_confirmations():
    """Cleanup expired confirmation requests"""
    current_time = asyncio.get_event_loop().time()
    expired_confirmations = []

    for confirmation_id, data in pending_confirmations.items():
        # Expire confirmations after 10 minutes
        if current_time - data["timestamp"] > 600:
            expired_confirmations.append(confirmation_id)

    for confirmation_id in expired_confirmations:
        del pending_confirmations[confirmation_id]
        logger.info(f"Expired confirmation: {confirmation_id}")


async def periodic_cleanup():
    """Periodic cleanup task"""
    while True:
        try:
            await cleanup_expired_confirmations()
            await asyncio.sleep(60)  # Run every minute
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
            await asyncio.sleep(60)


async def main():
    """Run the Snowflake Admin MCP server"""

    # Start periodic cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())

    try:
        # Initialize the admin agent
        await admin_agent.initialize()
        logger.info("✅ Snowflake Admin MCP Server initialized")

        # Run the MCP server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream, write_stream, server.create_initialization_options()
            )

    except KeyboardInterrupt:
        logger.info("Shutting down Snowflake Admin MCP Server")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        # Cleanup
        cleanup_task.cancel()
        await admin_agent.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
