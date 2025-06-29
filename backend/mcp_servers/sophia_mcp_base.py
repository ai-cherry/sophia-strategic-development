"""
Sophia MCP Base Class
Unified base class for all Sophia AI MCP servers
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from mcp import Server, Tool, Resource
    from mcp.types import TextContent, ImageContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Create mock classes for development
    class Server:
        def __init__(self, name: str, version: str = "1.0.0"):
            self.name = name
            self.version = version
    
    class Tool:
        pass
    
    class Resource:
        pass

from backend.core.auto_esc_config import get_config_value


@dataclass
class MCPServerHealth:
    """Health status for MCP servers"""
    status: str  # healthy, degraded, unhealthy
    uptime_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    last_request_time: Optional[datetime]
    error_rate: float


class SophiaMCPServer(ABC):
    """
    Base class for all Sophia AI MCP servers
    Provides unified patterns for authentication, logging, health checks, and error handling
    """
    
    def __init__(self, name: str, version: str = "1.0.0", port: Optional[int] = None):
        self.name = name
        self.version = version
        self.port = port
        self.start_time = time.time()
        
        # Setup logging
        self.logger = logging.getLogger(f"sophia.mcp.{name}")
        self.logger.setLevel(logging.INFO)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "last_request_time": None
        }
        
        # Initialize MCP server if available
        if MCP_AVAILABLE:
            self.mcp_server = Server(name, version)
            self._register_tools()
            self._register_resources()
        else:
            self.mcp_server = None
            self.logger.warning("MCP SDK not available - running in mock mode")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from Pulumi ESC and environment"""
        return {
            "environment": get_config_value("environment", "prod"),
            "log_level": get_config_value("log_level", "INFO"),
            "debug_mode": get_config_value("debug_mode", "false").lower() == "true",
            "max_retries": int(get_config_value("mcp_max_retries", "3")),
            "timeout_seconds": int(get_config_value("mcp_timeout", "30"))
        }
    
    @abstractmethod
    def _register_tools(self):
        """Register MCP tools - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def _register_resources(self):
        """Register MCP resources - must be implemented by subclasses"""
        pass
    
    async def authenticate(self, request: Any) -> bool:
        """
        Standard authentication for all servers
        Override in subclasses for specific auth requirements
        """
        # Basic API key authentication
        api_key = getattr(request, 'api_key', None) or os.getenv(f"{self.name.upper()}_API_KEY")
        
        if not api_key:
            self.logger.warning("No API key provided for authentication")
            return False
        
        # Add custom authentication logic here
        return True
    
    async def health_check(self) -> MCPServerHealth:
        """Standard health check for all servers"""
        uptime = time.time() - self.start_time
        total_requests = self.metrics["total_requests"]
        failed_requests = self.metrics["failed_requests"]
        
        error_rate = (failed_requests / max(total_requests, 1)) * 100
        
        # Determine health status
        if error_rate > 50:
            status = "unhealthy"
        elif error_rate > 10:
            status = "degraded"
        else:
            status = "healthy"
        
        return MCPServerHealth(
            status=status,
            uptime_seconds=uptime,
            total_requests=total_requests,
            successful_requests=self.metrics["successful_requests"],
            failed_requests=failed_requests,
            last_request_time=self.metrics["last_request_time"],
            error_rate=error_rate
        )
    
    async def handle_request(self, request: Any) -> Any:
        """
        Standard request handler with metrics and error handling
        """
        self.metrics["total_requests"] += 1
        self.metrics["last_request_time"] = datetime.now()
        
        try:
            # Authenticate request
            if not await self.authenticate(request):
                self.metrics["failed_requests"] += 1
                raise Exception("Authentication failed")
            
            # Process request
            result = await self.process_request(request)
            
            self.metrics["successful_requests"] += 1
            return result
            
        except Exception as e:
            self.metrics["failed_requests"] += 1
            self.logger.error(f"Request failed: {e}")
            raise
    
    @abstractmethod
    async def process_request(self, request: Any) -> Any:
        """Process the actual request - must be implemented by subclasses"""
        pass
    
    async def start(self):
        """Start the MCP server"""
        self.logger.info(f"🚀 Starting {self.name} MCP Server v{self.version}")
        
        if self.port:
            self.logger.info(f"   Listening on port {self.port}")
        
        # Perform startup health check
        health = await self.health_check()
        self.logger.info(f"   Health status: {health.status}")
        
        # Additional startup logic can be added here
        await self.on_startup()
    
    async def stop(self):
        """Stop the MCP server"""
        self.logger.info(f"🛑 Stopping {self.name} MCP Server")
        await self.on_shutdown()
    
    async def on_startup(self):
        """Override for custom startup logic"""
        pass
    
    async def on_shutdown(self):
        """Override for custom shutdown logic"""
        pass


class SophiaSnowflakeMCPServer(SophiaMCPServer):
    """Example Snowflake MCP Server implementation"""
    
    def __init__(self):
        super().__init__("snowflake", "1.0.0", port=9100)
        self.connection_manager = None
    
    def _register_tools(self):
        """Register Snowflake-specific tools"""
        if not self.mcp_server:
            return
        
        # Register tools would go here when MCP SDK is available
        pass
    
    def _register_resources(self):
        """Register Snowflake-specific resources"""
        if not self.mcp_server:
            return
        
        # Register resources would go here when MCP SDK is available
        pass
    
    async def process_request(self, request: Any) -> Any:
        """Process Snowflake-specific requests"""
        # Implement Snowflake query processing
        return {"status": "success", "message": "Snowflake query processed"}
    
    async def on_startup(self):
        """Initialize Snowflake connection"""
        from backend.core.optimized_connection_manager import OptimizedConnectionManager
        self.connection_manager = OptimizedConnectionManager()
        await self.connection_manager.initialize()
        self.logger.info("✅ Snowflake connection manager initialized")


# Factory function for creating MCP servers
def create_mcp_server(server_type: str, **kwargs) -> SophiaMCPServer:
    """Factory function to create MCP servers"""
    servers = {
        "snowflake": SophiaSnowflakeMCPServer,
        # Add other server types here
    }
    
    if server_type not in servers:
        raise ValueError(f"Unknown server type: {server_type}")
    
    return servers[server_type](**kwargs)
