#!/usr/bin/env python3
"""
Simple MCP Test Servers
Simplified versions of MCP servers for testing platform functionality
"""

import asyncio
import json
import logging
import multiprocessing
import signal
import sys
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleMCPServer:
    """Base class for simple MCP servers"""

    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        self.running = True

    async def start(self):
        """Start the MCP server"""
        logger.info(f"🚀 Starting {self.name} MCP Server on port {self.port}")

        # Simulate server initialization
        await asyncio.sleep(1)

        logger.info(f"✅ {self.name} MCP Server ready on port {self.port}")

        # Keep server running
        while self.running:
            await asyncio.sleep(1)

    def stop(self):
        """Stop the MCP server"""
        logger.info(f"🛑 Stopping {self.name} MCP Server")
        self.running = False


def start_ai_memory_server():
    """Start AI Memory MCP Server"""
    try:
        import sys

        sys.path.append("/Users/lynnmusil/sophia-main")

        # Try to start the enhanced AI Memory server first
        try:
            from backend.mcp_servers.enhanced_ai_memory_mcp_server import (
                EnhancedAIMemoryMCPServer,
            )

            async def run_server():
                server = EnhancedAIMemoryMCPServer()
                await server.start()

            asyncio.run(run_server())

        except Exception as e:
            logger.warning(f"Enhanced AI Memory server failed: {e}")
            # Fallback to simple server
            server = SimpleMCPServer("AI Memory", 9000)
            asyncio.run(server.start())

    except Exception as e:
        logger.error(f"AI Memory server error: {e}")
        # Create basic HTTP server
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "status": "healthy",
                                "service": "AI Memory MCP",
                                "port": 9000,
                            }
                        ).encode()
                    )
                else:
                    self.send_response(404)
                    self.end_headers()

        httpd = HTTPServer(("localhost", 9000), HealthHandler)
        logger.info("✅ AI Memory MCP fallback server running on port 9000")
        httpd.serve_forever()


def start_codacy_server():
    """Start Codacy MCP Server"""
    try:
        # Create basic HTTP server for Codacy
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class CodeAnalysisHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "status": "healthy",
                                "service": "Codacy MCP",
                                "port": 3008,
                                "features": [
                                    "code_analysis",
                                    "security_scan",
                                    "quality_check",
                                ],
                            }
                        ).encode()
                    )
                elif self.path == "/analyze":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "analysis": "mock_analysis",
                                "quality_score": 85,
                                "issues": [],
                            }
                        ).encode()
                    )
                else:
                    self.send_response(404)
                    self.end_headers()

        httpd = HTTPServer(("localhost", 3008), CodeAnalysisHandler)
        logger.info("✅ Codacy MCP server running on port 3008")
        httpd.serve_forever()

    except Exception as e:
        logger.error(f"Codacy server error: {e}")


def start_asana_server():
    """Start Asana MCP Server"""
    try:
        # Create basic HTTP server for Asana
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class AsanaHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "status": "healthy",
                                "service": "Asana MCP",
                                "port": 3006,
                                "features": [
                                    "project_management",
                                    "task_tracking",
                                    "team_analytics",
                                ],
                            }
                        ).encode()
                    )
                elif self.path == "/projects":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "projects": [
                                    {
                                        "id": "1",
                                        "name": "Sophia AI Development",
                                        "status": "active",
                                    },
                                    {
                                        "id": "2",
                                        "name": "Platform Integration",
                                        "status": "in_progress",
                                    },
                                ]
                            }
                        ).encode()
                    )
                else:
                    self.send_response(404)
                    self.end_headers()

        httpd = HTTPServer(("localhost", 3006), AsanaHandler)
        logger.info("✅ Asana MCP server running on port 3006")
        httpd.serve_forever()

    except Exception as e:
        logger.error(f"Asana server error: {e}")


def start_notion_server():
    """Start Notion MCP Server"""
    try:
        # Create basic HTTP server for Notion
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class NotionHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "status": "healthy",
                                "service": "Notion MCP",
                                "port": 3007,
                                "features": [
                                    "knowledge_management",
                                    "documentation",
                                    "content_sync",
                                ],
                            }
                        ).encode()
                    )
                elif self.path == "/pages":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "pages": [
                                    {
                                        "id": "1",
                                        "title": "Sophia AI Documentation",
                                        "type": "page",
                                    },
                                    {
                                        "id": "2",
                                        "title": "Development Notes",
                                        "type": "database",
                                    },
                                ]
                            }
                        ).encode()
                    )
                else:
                    self.send_response(404)
                    self.end_headers()

        httpd = HTTPServer(("localhost", 3007), NotionHandler)
        logger.info("✅ Notion MCP server running on port 3007")
        httpd.serve_forever()

    except Exception as e:
        logger.error(f"Notion server error: {e}")


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Shutting down MCP servers...")
    sys.exit(0)


def start_all_mcp_servers():
    """Start all MCP servers in separate processes"""
    signal.signal(signal.SIGINT, signal_handler)

    logger.info("🚀 Starting all simplified MCP servers...")

    # Start servers in separate processes
    servers = [
        multiprocessing.Process(target=start_ai_memory_server, name="AI Memory MCP"),
        multiprocessing.Process(target=start_codacy_server, name="Codacy MCP"),
        multiprocessing.Process(target=start_asana_server, name="Asana MCP"),
        multiprocessing.Process(target=start_notion_server, name="Notion MCP"),
    ]

    # Start all servers
    for server in servers:
        server.start()
        time.sleep(1)  # Stagger starts

    logger.info("✅ All MCP servers started successfully")
    logger.info("📊 Server Summary:")
    logger.info("   - AI Memory MCP: localhost:9000")
    logger.info("   - Codacy MCP: localhost:3008")
    logger.info("   - Asana MCP: localhost:3006")
    logger.info("   - Notion MCP: localhost:3007")
    logger.info("")
    logger.info("🔍 Test endpoints:")
    logger.info("   curl http://localhost:9000/health")
    logger.info("   curl http://localhost:3008/health")
    logger.info("   curl http://localhost:3006/health")
    logger.info("   curl http://localhost:3007/health")
    logger.info("")
    logger.info("Press Ctrl+C to stop all servers")

    try:
        # Wait for all servers
        for server in servers:
            server.join()
    except KeyboardInterrupt:
        logger.info("🛑 Stopping all servers...")
        for server in servers:
            server.terminate()
            server.join()


if __name__ == "__main__":
    start_all_mcp_servers()
