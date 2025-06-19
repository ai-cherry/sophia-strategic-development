#!/usr/bin/env python3
"""
Test script for Agno integration
Tests the Agno MCP server, Agno integration, and AG-UI components
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import Agno integration
from backend.integrations.agno_integration import agno_integration
from backend.mcp.agno_bridge import MCPToAgnoBridge
from backend.mcp.mcp_client import MCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"agno_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
    ],
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_AGENT_ID = "test_agent"
TEST_REQUEST = "What is the current status of our Gong integration? Please check the latest calls and provide a summary."


async def test_agno_integration():
    """Test the Agno integration."""
    logger.info("Testing Agno integration...")
    
    try:
        # Initialize Agno integration
        await agno_integration.initialize()
        logger.info("Agno integration initialized successfully.")
        
        # Get pool stats
        pool_stats = agno_integration.get_pool_stats()
        logger.info(f"Agent pool stats: {json.dumps(pool_stats, indent=2)}")
        
        # Create agent
        agent = await agno_integration.get_agent(
            agent_id=TEST_AGENT_ID,
            instructions=[
                "You are Sophia AI, an enterprise AI assistant for Pay Ready",
                "You have access to various tools to help you accomplish tasks",
                "Always provide clear, concise responses",
                "When using tools, explain your reasoning"
            ]
        )
        logger.info(f"Agent {TEST_AGENT_ID} created successfully.")
        
        # Test successful
        logger.info("Agno integration test successful.")
        return True
    except Exception as e:
        logger.error(f"Agno integration test failed: {e}", exc_info=True)
        return False


async def test_agno_bridge():
    """Test the MCP-to-Agno bridge."""
    logger.info("Testing MCP-to-Agno bridge...")
    
    try:
        # Initialize MCP client
        mcp_client = MCPClient()
        await mcp_client.initialize()
        logger.info("MCP client initialized successfully.")
        
        # Initialize bridge
        bridge = MCPToAgnoBridge(mcp_client)
        logger.info("MCP-to-Agno bridge initialized successfully.")
        
        # Convert all MCP tools to Agno tools
        tools = await bridge.convert_all_mcp_tools()
        logger.info(f"Converted {len(tools)} MCP tools to Agno tools.")
        
        # Log tool names
        tool_names = [tool.name for tool in tools]
        logger.info(f"Tool names: {', '.join(tool_names)}")
        
        # Get cache stats
        cache_stats = bridge.get_cache_stats()
        logger.info(f"Bridge cache stats: {json.dumps(cache_stats, indent=2)}")
        
        # Test successful
        logger.info("MCP-to-Agno bridge test successful.")
        return True
    except Exception as e:
        logger.error(f"MCP-to-Agno bridge test failed: {e}", exc_info=True)
        return False


async def test_agent_request():
    """Test an agent request."""
    logger.info("Testing agent request...")
    
    try:
        # Initialize MCP client
        mcp_client = MCPClient()
        await mcp_client.initialize()
        logger.info("MCP client initialized successfully.")
        
        # Initialize bridge
        bridge = MCPToAgnoBridge(mcp_client)
        logger.info("MCP-to-Agno bridge initialized successfully.")
        
        # Convert all MCP tools to Agno tools
        tools = await bridge.convert_all_mcp_tools()
        logger.info(f"Converted {len(tools)} MCP tools to Agno tools.")
        
        # Process request
        logger.info(f"Processing request: {TEST_REQUEST}")
        response_chunks = []
        async for chunk in agno_integration.process_request(
            agent_id=TEST_AGENT_ID,
            request=TEST_REQUEST,
            tools=tools
        ):
            response_chunks.append(chunk)
            logger.info(f"Received chunk: {json.dumps(chunk, indent=2)}")
        
        # Log response
        logger.info(f"Received {len(response_chunks)} response chunks.")
        
        # Test successful
        logger.info("Agent request test successful.")
        return True
    except Exception as e:
        logger.error(f"Agent request test failed: {e}", exc_info=True)
        return False


async def test_mcp_server():
    """Test the Agno MCP server via MCP client."""
    logger.info("Testing Agno MCP server...")
    
    try:
        # Initialize MCP client
        mcp_client = MCPClient()
        await mcp_client.initialize()
        logger.info("MCP client initialized successfully.")
        
        # List servers
        servers = mcp_client.list_servers()
        logger.info(f"Available servers: {', '.join(servers)}")
        
        # Check if Agno server is available
        if "agno" not in servers:
            logger.error("Agno server not found in available servers.")
            return False
        
        # List tools
        tools = mcp_client.list_tools("agno")
        logger.info(f"Available tools: {', '.join(tools)}")
        
        # Call create_agent tool
        result = await mcp_client.call_tool(
            "agno",
            "create_agent",
            agent_id=f"{TEST_AGENT_ID}_mcp",
            instructions=[
                "You are Sophia AI, an enterprise AI assistant for Pay Ready",
                "You have access to various tools to help you accomplish tasks",
                "Always provide clear, concise responses",
                "When using tools, explain your reasoning"
            ]
        )
        logger.info(f"Create agent result: {json.dumps(result, indent=2)}")
        
        # Call process_request tool
        result = await mcp_client.call_tool(
            "agno",
            "process_request",
            agent_id=f"{TEST_AGENT_ID}_mcp",
            request="Hello, I'm testing the Agno MCP server.",
            stream=False
        )
        logger.info(f"Process request result: {json.dumps(result, indent=2)}")
        
        # Test successful
        logger.info("Agno MCP server test successful.")
        return True
    except Exception as e:
        logger.error(f"Agno MCP server test failed: {e}", exc_info=True)
        return False


async def main():
    """Main entry point."""
    logger.info("Starting Agno integration tests...")
    
    # Run tests
    integration_test = await test_agno_integration()
    bridge_test = await test_agno_bridge()
    mcp_server_test = await test_mcp_server()
    agent_test = await test_agent_request()
    
    # Log results
    logger.info("Test results:")
    logger.info(f"  Agno integration: {'PASS' if integration_test else 'FAIL'}")
    logger.info(f"  MCP-to-Agno bridge: {'PASS' if bridge_test else 'FAIL'}")
    logger.info(f"  Agno MCP server: {'PASS' if mcp_server_test else 'FAIL'}")
    logger.info(f"  Agent request: {'PASS' if agent_test else 'FAIL'}")
    
    # Overall result
    overall = all([integration_test, bridge_test, mcp_server_test, agent_test])
    logger.info(f"Overall result: {'PASS' if overall else 'FAIL'}")
    
    # Close resources
    await agno_integration.close()
    
    return 0 if overall else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user.")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)
