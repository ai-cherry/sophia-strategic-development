# File: scripts/test_all_mcp_servers.py

import asyncio
import aiohttp
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = get_logger(__name__)

async def test_server(session, server_name, port):
    """Tests a single MCP server's health endpoint."""
    url = f"http://localhost:{port}/health"
    try:
        start_time = asyncio.get_event_loop().time()
        async with session.get(url, timeout=5) as response:
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            if response.status == 200:
                return {"server": server_name, "status": "✅ HEALTHY", "response_time_ms": f"{response_time:.2f}"}
            else:
                return {"server": server_name, "status": f"❌ UNHEALTHY (Status: {response.status})"}
    except asyncio.TimeoutError:
        return {"server": server_name, "status": "❌ TIMEOUT"}
    except aiohttp.ClientError as e:
        return {"server": server_name, "status": f"❌ FAILED ({e})"}

async def main():
    """Reads the port config and tests all defined MCP servers."""
    ports_config_path = Path.cwd() / "config" / "mcp_ports.json"
    if not ports_config_path.exists():
        logger.error("Port configuration file not found.")
        return

    with open(ports_config_path, 'r') as f:
        ports_config = json.load(f)

    servers_to_test = ports_config.get("servers", {})
    
    logger.info("--- Testing All MCP Servers ---")
    
    async with aiohttp.ClientSession() as session:
        tasks = [test_server(session, name, port) for name, port in servers_to_test.items()]
        results = await asyncio.gather(*tasks)

    logger.info("--- Test Results ---")
    for result in results:
        logger.info(f"{result['server']:<25} | Status: {result['status']:<30} | Response Time (ms): {result.get('response_time_ms', 'N/A')}")
    logger.info("--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(main()) 