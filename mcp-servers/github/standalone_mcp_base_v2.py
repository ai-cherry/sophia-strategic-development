#!/usr/bin/env python3
"""
Standalone MCP Base Classes V2
Fixed version without inheritance issues
"""

import asyncio
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for MCP servers"""
    name: str
    port: int
    version: str = "1.0.0"
    host: str = "127.0.0.1"
    log_level: str = "info"


class SimpleMCPServer:
    """
    Simple MCP server with tool support
    No complex inheritance or abstract methods
    """
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.name = config.name
        self.port = config.port
        self.version = config.version
        self.app = FastAPI(title=f"{self.name} MCP Server")
        self.logger = logging.getLogger(f"mcp.{self.name}")
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.tools = {}
        
        # Load configuration from environment
        self.env_config = self._load_env_config()
        
        # Setup routes
        self._setup_basic_routes()
        self._setup_tool_routes()

    def _load_env_config(self) -> Dict[str, str]:
        """Load configuration from environment variables"""
        config = {
            "environment": os.getenv("ENVIRONMENT", "prod"),
            "pulumi_org": os.getenv("PULUMI_ORG", "scoobyjava-org"),
        }
        
        # Load service-specific API keys
        service_key = f"{self.name.upper()}_API_KEY"
        if os.getenv(service_key):
            config["api_key"] = os.getenv(service_key)
            
        # Load alternative key patterns
        alt_patterns = [
            f"SOPHIA_{self.name.upper()}_API_KEY",
            f"{self.name.upper()}_ACCESS_TOKEN",
            f"{self.name.upper()}_TOKEN"
        ]
        
        for pattern in alt_patterns:
            if os.getenv(pattern):
                config["api_key"] = os.getenv(pattern)
                break
                
        return config

    def _setup_basic_routes(self):
        """Setup basic MCP server routes"""
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            try:
                server_health = await self.check_server_health()
                uptime = time.time() - self.start_time
                
                return {
                    "status": "healthy" if server_health else "degraded",
                    "service": f"{self.name}-mcp-server",
                    "version": self.version,
                    "uptime_seconds": uptime,
                    "request_count": self.request_count,
                    "error_count": self.error_count,
                    "error_rate": self.error_count / max(self.request_count, 1),
                    "capabilities": await self.get_capabilities()
                }
            except Exception as e:
                self.logger.exception(f"Health check failed: {e}")
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "service": f"{self.name}-mcp-server",
                        "error": str(e)
                    }
                )

        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "service": f"{self.name} MCP Server",
                "version": self.version,
                "status": "operational",
                "endpoints": ["/health", "/capabilities", "/tools"]
            }

        @self.app.get("/capabilities")
        async def capabilities():
            """Get server capabilities"""
            try:
                caps = await self.get_capabilities()
                return {"capabilities": caps}
            except Exception as e:
                self.logger.exception(f"Failed to get capabilities: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/tools")
        async def tools():
            """Get available tools"""
            try:
                tools = await self.get_tools()
                return {"tools": tools}
            except Exception as e:
                self.logger.exception(f"Failed to get tools: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def _setup_tool_routes(self):
        """Setup tool execution routes"""
        
        @self.app.post("/tools/{tool_name}")
        async def execute_tool(tool_name: str, params: Dict[str, Any] = None):
            """Execute a specific tool"""
            self.request_count += 1
            
            if tool_name not in self.tools:
                self.error_count += 1
                raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
            
            try:
                tool = self.tools[tool_name]
                result = await tool["function"](**(params or {}))
                return {"result": result}
            except Exception as e:
                self.error_count += 1
                self.logger.exception(f"Tool {tool_name} execution failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def mcp_tool(self, name: str, description: str, parameters: Dict[str, Any] = None):
        """Decorator for registering MCP tools"""
        def decorator(func):
            self.tools[name] = {
                "name": name,
                "description": description,
                "parameters": parameters or {},
                "function": func
            }
            return func
        return decorator

    async def check_server_health(self) -> bool:
        """Check server health - can be overridden by subclasses"""
        return True

    async def get_capabilities(self) -> List[Dict[str, Any]]:
        """Get server capabilities - can be overridden by subclasses"""
        return [
            {
                "name": "health_monitoring",
                "description": "Server health monitoring and status reporting",
                "category": "monitoring",
                "available": True,
                "version": "1.0.0"
            }
        ]

    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools"""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
            for tool in self.tools.values()
        ]

    async def server_specific_init(self):
        """Server-specific initialization - can be overridden by subclasses"""
        pass

    async def server_specific_cleanup(self):
        """Server-specific cleanup - can be overridden by subclasses"""
        pass

    def run(self):
        """Run the MCP server"""
        self.logger.info(f"🚀 Starting {self.name} MCP Server on port {self.port}")
        
        try:
            # Run server-specific initialization
            asyncio.run(self.server_specific_init())
            
            # Start the server
            uvicorn.run(
                self.app,
                host=self.config.host,
                port=self.config.port,
                log_level=self.config.log_level
            )
        except KeyboardInterrupt:
            self.logger.info(f"🛑 {self.name} MCP Server stopped by user")
        except Exception as e:
            self.logger.exception(f"❌ {self.name} MCP Server failed: {e}")
            raise
        finally:
            # Run cleanup
            asyncio.run(self.server_specific_cleanup()) 