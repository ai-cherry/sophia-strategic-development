#!/usr/bin/env python3
"""
MCP Server Testing Script
Quick testing tool for MCP servers
"""

import asyncio

from backend.mcp_servers.mcp_registry import mcp_registry


async def test_mcp_servers():
    """Test all MCP servers"""
    print("🧪 Testing MCP Servers")
    print("=" * 50)

    # Start all servers
    await mcp_registry.start_all_servers()

    # Wait a moment for servers to initialize
    await asyncio.sleep(2)

    # Perform health checks
    await mcp_registry.health_check_all()

    # Get status
    status = mcp_registry.get_server_status()

    print("\n📊 Server Status:")
    for name, info in status.items():
        enabled = "✅" if info["config"]["enabled"] else "❌"
        registered = "✅" if info["registered"] else "❌"
        health = info["health"]["status"] if info["health"] else "unknown"

        print(f"   {name}: {enabled} enabled, {registered} registered, {health} health")

    print("\n🎉 MCP server testing complete!")


if __name__ == "__main__":
    asyncio.run(test_mcp_servers())
