"""
Standardized MCP Server Base Class
Unified architecture for all Sophia AI MCP servers

Features:
- Consistent health monitoring
- Unified error handling
- Performance metrics
- Automatic service discovery
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from prometheus_client import Counter, Histogram, Gauge

from backend.core.auto_esc_config import get_config_value
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Prometheus metrics
mcp_requests_total = Counter('mcp_requests_total', 'Total MCP requests', ['server_name', 'tool_name'])
mcp_request_duration = Histogram('mcp_request_duration_seconds', 'MCP request duration', ['server_name', 'tool_name'])
mcp_active_connections = Gauge('mcp_active_connections', 'Active MCP connections', ['server_name'])

@dataclass
class MCPServerConfig:
    """Configuration for MCP server"""
    name: str
    port: int
    capabilities: List[str]
    health_endpoint: str = "/health"
    metrics_enabled: bool = True
    max_concurrent_requests: int = 10

class StandardizedMCPServer(ABC):
    """
    Base class for all Sophia AI MCP servers
    
    Provides:
    - Health monitoring
    - Performance metrics
    - Error handling
    - Service discovery
    """
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.server = Server(config.name)
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        
        # Performance tracking
        self.avg_response_time_ms = 0.0
        self.last_health_check = None
        
        # Initialize server
        self._setup_server()
    
    def _setup_server(self):
        """Setup MCP server with tools and handlers"""
        # Add health check tool
        @self.server.call_tool()
        async def health_check(arguments: dict) -> List[TextContent]:
            """Health check endpoint"""
            return [TextContent(
                type="text",
                text=self._get_health_status()
            )]
        
        # Add metrics tool
        @self.server.call_tool()
        async def get_metrics(arguments: dict) -> List[TextContent]:
            """Get server metrics"""
            return [TextContent(
                type="text",
                text=self._get_metrics()
            )]
        
        # Setup custom tools
        self._setup_custom_tools()
    
    @abstractmethod
    def _setup_custom_tools(self):
        """Setup server-specific tools (implemented by subclasses)"""
        pass
    
    def _get_health_status(self) -> str:
        """Get server health status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        health_data = {
            "server_name": self.config.name,
            "status": "healthy",
            "uptime_seconds": uptime,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "avg_response_time_ms": self.avg_response_time_ms,
            "capabilities": self.config.capabilities,
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(health_data, indent=2)
    
    def _get_metrics(self) -> str:
        """Get server metrics"""
        metrics = {
            "requests_per_second": self.request_count / max((datetime.now() - self.start_time).total_seconds(), 1),
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1),
            "avg_response_time_ms": self.avg_response_time_ms,
            "total_requests": self.request_count,
            "total_errors": self.error_count
        }
        
        return json.dumps(metrics, indent=2)
    
    async def handle_request(self, tool_name: str, arguments: dict) -> List[TextContent]:
        """Handle MCP request with metrics and error handling"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Record metrics
            mcp_requests_total.labels(
                server_name=self.config.name,
                tool_name=tool_name
            ).inc()
            
            # Execute tool
            result = await self._execute_tool(tool_name, arguments)
            
            # Update performance metrics
            duration_ms = (time.time() - start_time) * 1000
            self.avg_response_time_ms = (
                (self.avg_response_time_ms * (self.request_count - 1) + duration_ms) / self.request_count
            )
            
            # Record duration
            mcp_request_duration.labels(
                server_name=self.config.name,
                tool_name=tool_name
            ).observe(duration_ms / 1000)
            
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in {self.config.name}.{tool_name}: {e}")
            
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    @abstractmethod
    async def _execute_tool(self, tool_name: str, arguments: dict) -> List[TextContent]:
        """Execute tool (implemented by subclasses)"""
        pass
    
    async def run(self):
        """Run the MCP server"""
        logger.info(f"Starting {self.config.name} MCP server...")
        
        # Update active connections metric
        mcp_active_connections.labels(server_name=self.config.name).inc()
        
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        finally:
            # Cleanup
            mcp_active_connections.labels(server_name=self.config.name).dec()
            logger.info(f"{self.config.name} MCP server stopped")
