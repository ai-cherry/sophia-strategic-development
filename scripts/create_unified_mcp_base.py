#!/usr/bin/env python3
"""
Create unified MCP base class combining best features from all existing bases.
Consolidates: standalone_mcp_base.py, standalone_mcp_base_v2.py, enhanced_standardized_mcp_server.py
"""

from pathlib import Path


def create_unified_base():
    """Create the definitive unified MCP base class."""

    unified_base_content = '''#!/usr/bin/env python3
"""
Unified MCP Base Class - The Definitive Implementation
Combines best features from all previous base classes:
- FastAPI for HTTP endpoints and health checks
- MCP protocol compliance for AI agent integration
- No backend dependencies (fully standalone)
- Pulumi ESC integration for secrets
- Standardized error handling and logging
- Comprehensive health monitoring
"""

import asyncio
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Unified configuration for all MCP servers"""
    name: str
    port: int
    version: str = "2.0.0"
    host: str = "127.0.0.1"
    log_level: str = "info"
    enable_cors: bool = True
    enable_health_checks: bool = True
    enable_mcp_tools: bool = True

class HealthStatus(BaseModel):
    """Standard health status model"""
    status: str
    version: str
    uptime_seconds: float
    request_count: int
    error_count: int
    error_rate: float
    server_info: Dict[str, Any]
    capabilities: List[str]

class MCPTool(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = []

class UnifiedMCPServer:
    """
    Unified MCP Server Base Class

    Provides both FastAPI endpoints for monitoring and MCP tools for AI integration.
    No backend dependencies - fully standalone with Pulumi ESC integration.
    """

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.name = config.name
        self.port = config.port
        self.version = config.version
        self.app = FastAPI(
            title=f"{self.name} MCP Server",
            version=config.version,
            description=f"Unified MCP server for {self.name}"
        )

        # Server state
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.mcp_tools: Dict[str, MCPTool] = {}
        self.logger = logging.getLogger(f"mcp.{self.name}")

        # Load environment configuration
        self.env_config = self._load_env_config()

        # Setup FastAPI
        self._setup_middleware()
        self._setup_routes()

        # Initialize server-specific components
        self.initialize_server()

    def _load_env_config(self) -> Dict[str, str]:
        """Load configuration from environment variables with Pulumi ESC integration"""
        config = {
            "environment": os.getenv("ENVIRONMENT", "prod"),
            "pulumi_org": os.getenv("PULUMI_ORG", "scoobyjava-org"),
        }

        # Standard API key patterns for this service
        service_patterns = [
            f"{self.name.upper()}_API_KEY",
            f"SOPHIA_{self.name.upper()}_API_KEY",
            f"{self.name.upper()}_ACCESS_TOKEN",
            f"{self.name.upper()}_TOKEN",
        ]

        for pattern in service_patterns:
            if os.getenv(pattern):
                config["api_key"] = os.getenv(pattern)
                break

        return config

    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        if self.config.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    def _setup_routes(self):
        """Setup standard FastAPI routes"""

        @self.app.get("/health")
        async def health() -> HealthStatus:
            """Comprehensive health check endpoint"""
            self.request_count += 1

            uptime = time.time() - self.start_time
            error_rate = self.error_count / max(self.request_count, 1)

            # Server-specific health checks
            server_health = await self.check_server_health()
            capabilities = await self.get_capabilities()

            return HealthStatus(
                status="healthy" if server_health else "degraded",
                version=self.version,
                uptime_seconds=uptime,
                request_count=self.request_count,
                error_count=self.error_count,
                error_rate=error_rate,
                server_info={
                    "name": self.name,
                    "port": self.port,
                    "environment": self.env_config.get("environment"),
                    "api_key_configured": bool(self.env_config.get("api_key"))
                },
                capabilities=capabilities
            )

        @self.app.get("/tools")
        async def list_tools() -> List[MCPTool]:
            """List all available MCP tools"""
            self.request_count += 1
            return list(self.mcp_tools.values())

        @self.app.post("/tools/{tool_name}")
        async def execute_tool(tool_name: str, params: Dict[str, Any] = None):
            """Execute a specific MCP tool"""
            self.request_count += 1

            if tool_name not in self.mcp_tools:
                self.error_count += 1
                raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")

            try:
                result = await self.execute_mcp_tool(tool_name, params or {})
                return {"result": result, "status": "success"}
            except Exception as e:
                self.error_count += 1
                self.logger.exception(f"Tool {tool_name} execution failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def mcp_tool(self, name: str, description: str, parameters: Dict[str, Any] = None, required: List[str] = None):
        """Decorator to register MCP tools"""
        def decorator(func):
            self.mcp_tools[name] = MCPTool(
                name=name,
                description=description,
                parameters=parameters or {},
                required=required or []
            )
            return func
        return decorator

    async def execute_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute MCP tool - to be overridden by subclasses"""
        raise NotImplementedError(f"Tool {tool_name} not implemented")

    async def check_server_health(self) -> bool:
        """Server-specific health check - to be overridden by subclasses"""
        return True

    async def get_capabilities(self) -> List[str]:
        """Get server capabilities - to be overridden by subclasses"""
        capabilities = ["health_check", "tool_listing"]
        if self.mcp_tools:
            capabilities.append("mcp_tools")
        if self.env_config.get("api_key"):
            capabilities.append("authenticated")
        return capabilities

    def initialize_server(self):
        """Initialize server-specific components - to be overridden by subclasses"""
        pass

    def run(self, **kwargs):
        """Run the server"""
        self.logger.info(f"Starting {self.name} MCP Server on port {self.port}")
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level,
            **kwargs
        )

# Convenience base classes for common patterns
class ServiceMCPServer(UnifiedMCPServer):
    """Base for external service integrations (HubSpot, Slack, etc.)"""
    pass

class AIEngineMCPServer(UnifiedMCPServer):
    """Base for AI/ML service integrations (Snowflake Cortex, etc.)"""
    pass

class InfrastructureMCPServer(UnifiedMCPServer):
    """Base for infrastructure service integrations (Pulumi, etc.)"""
    pass
'''

    # Create the unified base directory if it doesn't exist
    output_path = Path("mcp-servers/base/unified_mcp_base.py")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the unified base
    with open(output_path, "w") as f:
        f.write(unified_base_content)

    print(f"✅ Created unified MCP base: {output_path}")

    # Create backup of existing bases
    backup_dir = Path("mcp-servers/base/legacy_backup")
    backup_dir.mkdir(exist_ok=True)

    legacy_files = [
        "mcp-servers/base/standalone_mcp_base.py",
        "mcp-servers/base/standalone_mcp_base_v2.py",
    ]

    for legacy_file in legacy_files:
        legacy_path = Path(legacy_file)
        if legacy_path.exists():
            backup_path = backup_dir / legacy_path.name
            import shutil

            shutil.copy2(legacy_path, backup_path)
            print(f"📋 Backed up {legacy_path} to {backup_path}")


def main():
    """Main function"""
    print("🚀 Creating Unified MCP Base Class...")
    create_unified_base()
    print("✅ Unified MCP base creation complete!")
    print("\nNext steps:")
    print(
        "1. Review the generated unified base at mcp-servers/base/unified_mcp_base.py"
    )
    print(
        "2. Run migration script: python scripts/migrate_all_servers_to_unified_base.py"
    )


if __name__ == "__main__":
    main()
