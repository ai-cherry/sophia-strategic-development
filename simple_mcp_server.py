#!/usr/bin/env python3
"""Simple MCP Server for Sophia AI Deployment Demonstration.

A minimal MCP server that demonstrates the deployment concepts without complex dependencies.
"""

import asyncio
import json
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleMCPHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for MCP server functionality"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/health":
            self.send_health_response()
        elif self.path == "/status":
            self.send_status_response()
        elif self.path == "/":
            self.send_root_response()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests for MCP operations"""
        if self.path == "/mcp/agent/create":
            self.handle_agent_creation()
        elif self.path == "/mcp/agent/execute":
            self.handle_agent_execution()
        else:
            self.send_error(404, "Not Found")
    
    def send_health_response(self):
        """Send health check response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "server": "simple_mcp",
            "version": "1.0.0"
        }
        
        self.wfile.write(json.dumps(health_data).encode())
    
    def send_status_response(self):
        """Send status response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        status_data = {
            "operational": True,
            "agents_available": ["demo_agent", "test_agent"],
            "capabilities": ["agent_creation", "task_execution", "health_monitoring"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.wfile.write(json.dumps(status_data).encode())
    
    def send_root_response(self):
        """Send root response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        root_data = {
            "message": "Simple MCP Server for Sophia AI",
            "status": "operational",
            "endpoints": ["/health", "/status", "/mcp/agent/create", "/mcp/agent/execute"]
        }
        
        self.wfile.write(json.dumps(root_data).encode())
    
    def handle_agent_creation(self):
        """Handle agent creation requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            agent_type = request_data.get('agent_type', 'default')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_data = {
                "success": True,
                "agent_id": f"{agent_type}_{datetime.utcnow().timestamp()}",
                "agent_type": agent_type,
                "status": "created",
                "instantiation_time": "< 3μs",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_error(500, f"Agent creation failed: {str(e)}")
    
    def handle_agent_execution(self):
        """Handle agent execution requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            task = request_data.get('task', 'default_task')
            agent_id = request_data.get('agent_id', 'unknown')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_data = {
                "success": True,
                "agent_id": agent_id,
                "task": task,
                "result": f"Task '{task}' executed successfully",
                "execution_time": "< 100ms",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_error(500, f"Agent execution failed: {str(e)}")
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")


class SimpleMCPServer:
    """Simple MCP Server for demonstration"""
    
    def __init__(self, port: int = 8092):
        self.port = port
        self.server = None
        self.server_thread = None
    
    def start(self):
        """Start the MCP server"""
        try:
            self.server = HTTPServer(('localhost', self.port), SimpleMCPHandler)
            logger.info(f"🚀 Simple MCP Server starting on port {self.port}")
            
            # Run server in a separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            logger.info(f"✅ Simple MCP Server running on http://localhost:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start MCP server: {e}")
            return False
    
    def stop(self):
        """Stop the MCP server"""
        if self.server:
            logger.info("🛑 Stopping Simple MCP Server...")
            self.server.shutdown()
            self.server.server_close()
            if self.server_thread:
                self.server_thread.join()
            logger.info("✅ Simple MCP Server stopped")


async def main():
    """Main function to run multiple MCP servers"""
    servers = []
    ports = [8092, 8093, 8094, 8095]  # Sophia AI MCP server ports
    
    logger.info("🚀 Starting Sophia AI MCP Server Deployment")
    logger.info("=" * 60)
    
    # Start servers on different ports
    for port in ports:
        server = SimpleMCPServer(port)
        if server.start():
            servers.append(server)
            logger.info(f"✅ MCP Server started on port {port}")
        else:
            logger.error(f"❌ Failed to start MCP Server on port {port}")
    
    if servers:
        logger.info(f"🎉 {len(servers)} MCP servers deployed successfully!")
        logger.info("Press Ctrl+C to stop all servers")
        
        try:
            # Keep the servers running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down all MCP servers...")
            for server in servers:
                server.stop()
            logger.info("✅ All MCP servers stopped")
    else:
        logger.error("❌ No MCP servers could be started")


if __name__ == "__main__":
    asyncio.run(main()) 