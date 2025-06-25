#!/usr/bin/env python3
"""Simple MCP Server Tester"""

import asyncio
import aiohttp
from datetime import datetime


async def test_server(name, port):
    """Test a single MCP server"""
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=3)
        ) as session:
            url = f"http://localhost:{port}/health"
            async with session.get(url) as response:
                if response.status == 200:
                    print(f"🟢 {name} (port {port}): HEALTHY")
                    return True
                else:
                    print(f"🔴 {name} (port {port}): HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"🔴 {name} (port {port}): UNREACHABLE - {str(e)}")
        return False


async def main():
    servers = [
        ("AI Memory", 9000),
        ("Sophia Intelligence", 8092),
        ("Codacy", 3008),
        ("Asana", 3006),
        ("Notion", 3007),
        ("Sophia Backend", 8000),
    ]

    print("🧪 Simple MCP Server Health Check")
    print("=" * 40)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    healthy_count = 0
    for name, port in servers:
        if await test_server(name, port):
            healthy_count += 1

    print(f"\n�� Summary: {healthy_count}/{len(servers)} servers healthy")


if __name__ == "__main__":
    asyncio.run(main())
