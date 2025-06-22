#!/usr/bin/env python3
"""
Sophia AI MCP Gateway Server
Modern implementation based on Docker MCP Catalog patterns
"""

import asyncio
import json
import logging
from typing import Dict, Any
import aiohttp
from aiohttp import web
import signal
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SophiaMCPGateway:
    def __init__(self):
        self.servers = {}
        self.config = self._load_config()
        self.app = web.Application()
        self._setup_routes()
    
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open('mcp-config/gateway-config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        return {
            "name": "Sophia AI MCP Gateway",
            "transport": {"port": 3000},
            "servers": {}
        }
    
    def _setup_routes(self):
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/servers', self.list_servers)
        self.app.router.add_post('/mcp/{server}', self.proxy_request)
        self.app.router.add_get('/capabilities', self.get_capabilities)
    
    async def health_check(self, request):
        return web.json_response({
            "status": "healthy",
            "name": self.config.get("name", "Sophia AI MCP Gateway"),
            "servers": len(self.config.get("servers", {})),
            "timestamp": "2025-01-21T12:00:00Z"
        })
    
    async def list_servers(self, request):
        servers = []
        for name, config in self.config.get("servers", {}).items():
            servers.append({
                "name": name,
                "description": config.get("description", ""),
                "capabilities": config.get("capabilities", []),
                "endpoint": config.get("endpoint", ""),
                "status": "available"
            })
        return web.json_response({"servers": servers})
    
    async def get_capabilities(self, request):
        all_capabilities = set()
        for server_config in self.config.get("servers", {}).values():
            all_capabilities.update(server_config.get("capabilities", []))
        
        return web.json_response({
            "capabilities": list(all_capabilities),
            "gateway": "Sophia AI MCP Gateway",
            "version": "2.0.0"
        })
    
    async def proxy_request(self, request):
        server_name = request.match_info['server']
        server_config = self.config.get("servers", {}).get(server_name)
        
        if not server_config:
            return web.json_response(
                {"error": f"Server '{server_name}' not found"},
                status=404
            )
        
        # For now, return a mock response - in production this would proxy to actual MCP servers
        return web.json_response({
            "server": server_name,
            "status": "processed",
            "message": f"Request processed by {server_name} MCP server",
            "capabilities": server_config.get("capabilities", [])
        })
    
    async def start_server(self):
        port = self.config.get("transport", {}).get("port", 3000)
        logger.info(f"🚀 Starting Sophia AI MCP Gateway on port {port}")
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        logger.info(f"✅ MCP Gateway running on http://0.0.0.0:{port}")
        return runner

async def main():
    gateway = SophiaMCPGateway()
    runner = await gateway.start_server()
    
    # Handle shutdown gracefully
    def signal_handler():
        logger.info("🔄 Shutting down MCP Gateway...")
        loop = asyncio.get_event_loop()
        loop.create_task(runner.cleanup())
    
    if sys.platform != 'win32':
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        signal_handler()

if __name__ == "__main__":
    asyncio.run(main())
