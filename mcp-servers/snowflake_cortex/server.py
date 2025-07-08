#!/usr/bin/env python3
"""
Enhanced Snowflake MCP Server with CortexGateway integration.
Provides unified access to Snowflake Cortex AI functions and SQL operations.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

from core.infra.cortex_gateway import get_gateway
from infrastructure.adapters.enhanced_snowflake_adapter import get_adapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("snowflake-cortex")

# Get gateway and adapter instances
gateway = get_gateway()
adapter = get_adapter()


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available Snowflake tools"""
    return [
        Tool(
            name="snowflake_complete",
            description="Generate text using Snowflake Cortex COMPLETE function",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt for text generation",
                    },
                    "model": {
                        "type": "string",
                        "enum": ["llama2-70b-chat", "mixtral-8x7b", "mistral-7b"],
                        "description": "The model to use",
                        "default": "mixtral-8x7b",
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="snowflake_embed",
            description="Generate embeddings using Snowflake Cortex",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to embed"},
                    "model": {
                        "type": "string",
                        "enum": ["e5-base-v2", "all-MiniLM-L6-v2"],
                        "description": "Embedding model",
                        "default": "e5-base-v2",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="snowflake_batch_embed",
            description="Generate embeddings for multiple texts",
            inputSchema={
                "type": "object",
                "properties": {
                    "texts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of texts to embed",
                    },
                    "model": {
                        "type": "string",
                        "enum": ["e5-base-v2", "all-MiniLM-L6-v2"],
                        "description": "Embedding model",
                        "default": "e5-base-v2",
                    },
                },
                "required": ["texts"],
            },
        ),
        Tool(
            name="snowflake_sentiment",
            description="Analyze sentiment of text using Snowflake Cortex",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to analyze"}
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="snowflake_search",
            description="Search using Snowflake Cortex search service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Name of the search service",
                    },
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 10,
                    },
                },
                "required": ["service", "query"],
            },
        ),
        Tool(
            name="snowflake_sql",
            description="Execute SQL query on Snowflake",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query to execute"},
                    "workload_type": {
                        "type": "string",
                        "enum": ["ai_workloads", "analytics", "general", "loading"],
                        "description": "Type of workload for warehouse selection",
                        "default": "general",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="snowflake_optimize_warehouse",
            description="Get warehouse optimization recommendations",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="snowflake_credit_usage",
            description="Get current credit usage summary",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="snowflake_health_check",
            description="Check Snowflake connection and system health",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

    try:
        # Initialize gateway if needed
        await gateway.initialize()
        await adapter.initialize()

        if name == "snowflake_complete":
            prompt = arguments["prompt"]
            model = arguments.get("model", "mixtral-8x7b")

            result = await gateway.complete(prompt, model)

            return [TextContent(type="text", text=result)]

        elif name == "snowflake_embed":
            text = arguments["text"]
            model = arguments.get("model", "e5-base-v2")

            embedding = await gateway.embed(text, model)

            return [
                TextContent(
                    type="text",
                    text=f"Generated embedding with {len(embedding)} dimensions",
                )
            ]

        elif name == "snowflake_batch_embed":
            texts = arguments["texts"]
            model = arguments.get("model", "e5-base-v2")

            embeddings = await gateway.batch_embed(texts, model)

            return [
                TextContent(
                    type="text",
                    text=f"Generated {len(embeddings)} embeddings, each with {len(embeddings[0]) if embeddings else 0} dimensions",
                )
            ]

        elif name == "snowflake_sentiment":
            text = arguments["text"]

            sentiment = await gateway.sentiment(text)

            return [TextContent(type="text", text=f"Sentiment: {sentiment}")]

        elif name == "snowflake_search":
            service = arguments["service"]
            query = arguments["query"]
            limit = arguments.get("limit", 10)

            results = await gateway.search(service, query, limit)

            return [
                TextContent(
                    type="text",
                    text=f"Search results:\n{json.dumps(results, indent=2, default=str)}",
                )
            ]

        elif name == "snowflake_sql":
            query = arguments["query"]
            workload_type = arguments.get("workload_type", "general")

            results = await adapter.execute_query(query, workload_type)

            # Format results
            if results:
                formatted = json.dumps(results[:10], indent=2, default=str)
                if len(results) > 10:
                    formatted += f"\n... and {len(results) - 10} more rows"
            else:
                formatted = "No results returned"

            return [TextContent(type="text", text=f"Query results:\n{formatted}")]

        elif name == "snowflake_optimize_warehouse":
            optimization = await adapter.optimize_warehouse_usage()

            # Format recommendations
            recommendations = optimization.get("recommendations", [])
            if recommendations:
                text = "Warehouse Optimization Recommendations:\n\n"
                for rec in recommendations:
                    text += f"• {rec['warehouse']}: {rec['action']}\n"
                    text += f"  Reason: {rec['reason']}\n"
                    if "potential_savings" in rec:
                        text += (
                            f"  Potential savings: {rec['potential_savings']} credits\n"
                        )
                    text += "\n"

                text += f"Total potential monthly savings: ${optimization.get('estimated_monthly_savings', 0):.2f}"
            else:
                text = "No optimization recommendations at this time. Warehouses are properly sized."

            return [TextContent(type="text", text=text)]

        elif name == "snowflake_credit_usage":
            usage = await adapter.get_credit_usage_summary()

            text = f"""Credit Usage Summary:
Date: {usage['date']}
Daily Limit: {usage['daily_limit']} credits
Credits Used: {usage['credits_used']:.2f}
Credits Remaining: {usage['credits_remaining']:.2f}
Usage: {usage['usage_percentage']:.1f}%
Queries Executed: {usage['queries_executed']}

Top Warehouses by Credit Usage:"""

            for wh in usage.get("top_warehouses", [])[:5]:
                text += f"\n• {wh['warehouse']}: {wh['credits']:.2f} credits ({wh['queries']} queries)"

            return [TextContent(type="text", text=text)]

        elif name == "snowflake_health_check":
            health = await gateway.health_check()
            adapter_health = await adapter.health_check()

            text = f"""Snowflake Health Check:
Gateway Status: {health['status']}
Adapter Status: {adapter_health['status']}

Connection Info:
{json.dumps(adapter_health.get('connection_info', {}), indent=2)}

Credit Usage:
{json.dumps(adapter_health.get('credit_usage', {}), indent=2)}

Components:
- Redis Cache: {adapter_health.get('redis_status', 'unknown')}
- Warehouse Optimizer: {adapter_health.get('warehouse_optimizer', 'unknown')}
- Initialized: {adapter_health.get('initialized', False)}"""

            return [TextContent(type="text", text=text)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error executing {name}: {e!s}")]


async def main():
    """Main server function"""
    logger.info("🚀 Starting Snowflake Cortex MCP Server")

    # Initialize components
    try:
        await gateway.initialize()
        await adapter.initialize()
        logger.info("✅ Gateway and adapter initialized")
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="snowflake-cortex",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
