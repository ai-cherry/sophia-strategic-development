#!/usr/bin/env python3
"""
Simple Test MCP Server for validation
"""
import sys
from datetime import datetime

from aiohttp import web


async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "server": "test_mcp_server",
        "port": request.app.get("port", 9999),
        "timestamp": datetime.now().isoformat(),
        "response_time": 0.001
    })

async def info_endpoint(request):
    """Server info endpoint"""
    return web.json_response({
        "name": "Test MCP Server",
        "version": "1.0.0",
        "description": "Simple test server for MCP deployment validation",
        "endpoints": ["/health", "/info"],
        "port": request.app.get("port", 9999)
    })

async def create_app(port=9999):
    """Create the web application"""
    app = web.Application()
    app["port"] = port
    app.router.add_get("/health", health_check)
    app.router.add_get("/info", info_endpoint)
    return app

def main():
    """Main function"""
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
    print(f"🚀 Starting Test MCP Server on port {port}...")

    app = create_app(port)
    web.run_app(app, host="localhost", port=port)

if __name__ == "__main__":
    main()
