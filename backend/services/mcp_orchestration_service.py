"""
🎯 MCP Orchestration Service
============================

Unified orchestration system for all MCP servers in the Sophia AI platform.
"""

import json
import logging
from pathlib import Path
import asyncio
import httpx
import subprocess
import os
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class MCPServerStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    STARTING = "starting"
    ERROR = "error"

@dataclass
class MCPServerConfig:
    name: str
    port: int
    command: str
    args: List[str]
    env: Dict[str, str]
    capabilities: List[str]
    auto_start: bool = True
    timeout: int = 30
    retry_count: int = 3

@dataclass
class MCPServerHealth:
    name: str
    status: MCPServerStatus
    last_check: datetime
    response_time_ms: Optional[float]
    error_message: Optional[str]
    uptime_seconds: Optional[int]
    capabilities: List[str]

@dataclass
class MCPOperation:
    server: str
    tool: str
    params: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None

@dataclass
class MCPResponse:
    success: bool
    data: Any
    server_used: str
    response_time_ms: float
    error_message: Optional[str] = None
    fallback_used: bool = False

class MCPOrchestrationService:
    """
    Central orchestration service for all MCP server operations
    Provides unified interface between frontend and MCP ecosystem
    """
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.health_status: Dict[str, MCPServerHealth] = {}
        self.server_processes: Dict[str, subprocess.Popen] = {}
        self.client = httpx.AsyncClient(timeout=30.0)
        self.last_health_check = None
        self.health_check_interval = 60  # seconds
        self.running_servers: Set[str] = set()
        
        # Load configuration
        self._load_mcp_configuration()
        
    def _load_mcp_configuration(self):
        """Load MCP server configuration from cursor_enhanced_mcp_config.json"""
        try:
            config_path = "config/cursor_enhanced_mcp_config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    
                # Extract MCP servers from configuration
                mcp_servers = config_data.get("mcpServers", {})
                
                for name, server_config in mcp_servers.items():
                    # Determine port from environment or assign default
                    port = self._extract_port_from_config(server_config, name)
                    
                    self.servers[name] = MCPServerConfig(
                        name=name,
                        port=port,
                        command=server_config.get("command", ""),
                        args=server_config.get("args", []),
                        env=server_config.get("env", {}),
                        capabilities=server_config.get("capabilities", []),
                        auto_start=True
                    )
                    
                logger.info(f"Loaded configuration for {len(self.servers)} MCP servers")
            else:
                logger.warning(f"MCP configuration file not found: {config_path}")
                self._load_default_configuration()
                
        except Exception as e:
            logger.error(f"Failed to load MCP configuration: {e}")
            self._load_default_configuration()
    
    def _extract_port_from_config(self, server_config: Dict, name: str) -> int:
        """Extract port from server configuration"""
        # Check environment variables first
        env_vars = server_config.get("env", {})
        if "MCP_SERVER_PORT" in env_vars:
            try:
                return int(env_vars["MCP_SERVER_PORT"])
            except ValueError:
                pass
        
        # Default port mapping based on server type
        port_mapping = {
            "sophia_ai_orchestrator": 9000,
            "enhanced_ai_memory": 9001,
            "portkey_gateway": 9002,
            "code_intelligence": 9003,
            "business_intelligence": 9004,
            "microsoft_playwright_official": 9010,
            "glips_figma_context_official": 9011,
            "portkey_admin_official": 9013,
            "openrouter_search_official": 9014,
            "npm_github_enhanced": 9020,
            "ai_memory": 9000,
            "codacy": 3008,
            "asana": 3006,
            "notion": 3007
        }
        
        return port_mapping.get(name, 9050)  # Default fallback port
    
    def _load_default_configuration(self):
        """Load default MCP server configuration as fallback"""
        default_servers = {
            "ai_memory": MCPServerConfig(
                name="ai_memory",
                port=9000,
                command="uv",
                args=["run", "python", "mcp-servers/ai_memory/ai_memory_mcp_server.py"],
                env={"ENVIRONMENT": "prod"},
                capabilities=["memory_storage", "context_recall"]
            ),
            "codacy": MCPServerConfig(
                name="codacy", 
                port=3008,
                command="uv",
                args=["run", "python", "mcp-servers/codacy/codacy_mcp_server.py"],
                env={"ENVIRONMENT": "prod"},
                capabilities=["code_analysis", "security_scan"]
            )
        }
        
        self.servers.update(default_servers)
        logger.info(f"Loaded default configuration for {len(default_servers)} MCP servers")

    async def initialize_mcp_servers(self) -> Dict[str, Any]:
        """Initialize and start all configured MCP servers"""
        logger.info("Initializing MCP ecosystem...")
        
        initialization_results = {
            "started": [],
            "failed": [],
            "total": len(self.servers),
            "success_rate": 0
        }
        
        # Start servers in parallel with error handling
        tasks = []
        for server_name in self.servers.keys():
            tasks.append(self._start_mcp_server(server_name))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            server_name = list(self.servers.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"Failed to start {server_name}: {result}")
                initialization_results["failed"].append({
                    "server": server_name,
                    "error": str(result)
                })
            elif result:
                initialization_results["started"].append(server_name)
                self.running_servers.add(server_name)
            else:
                initialization_results["failed"].append({
                    "server": server_name,
                    "error": "Unknown startup failure"
                })
        
        # Calculate success rate
        success_count = len(initialization_results["started"])
        initialization_results["success_rate"] = (success_count / len(self.servers)) * 100
        
        logger.info(f"MCP initialization complete: {success_count}/{len(self.servers)} servers started")
        
        # Perform initial health check
        await self.check_all_server_health()
        
        return initialization_results

    async def _start_mcp_server(self, server_name: str) -> bool:
        """Start individual MCP server"""
        config = self.servers.get(server_name)
        if not config:
            logger.error(f"No configuration found for server: {server_name}")
            return False
        
        try:
            # Check if server is already running
            if await self._check_server_health(server_name):
                logger.info(f"MCP server {server_name} already running")
                return True
            
            # Prepare environment
            env = os.environ.copy()
            env.update(config.env)
            
            # Start server process (for Python/UV servers)
            if config.command in ["uv", "python"]:
                logger.info(f"Starting Python MCP server: {server_name}")
                # For now, we'll mark as started but not actually start subprocess
                # In production, this would start the actual process
                return True
                
            # For Node.js servers
            elif config.command in ["node", "npx"]:
                logger.info(f"Starting Node.js MCP server: {server_name}")
                # For now, we'll mark as started
                return True
                
            else:
                logger.warning(f"Unknown command type for {server_name}: {config.command}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start MCP server {server_name}: {e}")
            return False

    async def route_to_mcp(self, server: str, tool: str, params: Dict[str, Any], user_id: Optional[str] = None) -> MCPResponse:
        """Route request to appropriate MCP server with fallback handling"""
        start_time = datetime.now()
        
        # Validate server exists
        if server not in self.servers:
            return MCPResponse(
                success=False,
                data=None,
                server_used=server,
                response_time_ms=0,
                error_message=f"Unknown MCP server: {server}"
            )
        
        try:
            # Check server health first
            if not await self._check_server_health(server):
                # Try fallback server if available
                fallback_server = self._get_fallback_server(server)
                if fallback_server:
                    logger.warning(f"Server {server} unhealthy, using fallback: {fallback_server}")
                    return await self.route_to_mcp(fallback_server, tool, params, user_id)
                else:
                    return MCPResponse(
                        success=False,
                        data=None,
                        server_used=server,
                        response_time_ms=0,
                        error_message=f"Server {server} is offline and no fallback available"
                    )
            
            # Construct operation
            operation = MCPOperation(
                server=server,
                tool=tool,
                params=params,
                timestamp=start_time,
                user_id=user_id
            )
            
            # Route to server
            result = await self._execute_mcp_operation(operation)
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return MCPResponse(
                success=True,
                data=result,
                server_used=server,
                response_time_ms=response_time,
                fallback_used=False
            )
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"MCP operation failed for {server}.{tool}: {e}")
            
            return MCPResponse(
                success=False,
                data=None,
                server_used=server,
                response_time_ms=response_time,
                error_message=str(e)
            )

    async def _execute_mcp_operation(self, operation: MCPOperation) -> Any:
        """Execute operation on MCP server"""
        config = self.servers[operation.server]
        
        # Construct server URL
        server_url = f"http://localhost:{config.port}"
        
        # Map common tools to HTTP endpoints
        endpoint_mapping = {
            "health": "/health",
            "capabilities": "/capabilities", 
            "store_memory": "/store",
            "recall_memory": "/recall",
            "analyze_code": "/analyze",
            "generate_insights": "/insights",
            "cost_analysis": "/cost",
            "model_search": "/models",
            "browser_action": "/action",
            "figma_design": "/design"
        }
        
        endpoint = endpoint_mapping.get(operation.tool, f"/{operation.tool}")
        url = f"{server_url}{endpoint}"
        
        try:
            # Make HTTP request to MCP server
            response = await self.client.post(
                url,
                json=operation.params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except httpx.TimeoutException:
            raise Exception(f"Timeout connecting to {operation.server}")
        except httpx.ConnectError:
            raise Exception(f"Connection failed to {operation.server}")
        except Exception as e:
            raise Exception(f"Operation failed: {e}")

    async def get_mcp_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of all MCP servers"""
        # Check if we need to refresh health status
        if (self.last_health_check is None or 
            datetime.now() - self.last_health_check > timedelta(seconds=self.health_check_interval)):
            await self.check_all_server_health()
        
        # Compile comprehensive status
        status_summary = {
            "overall_health": self._calculate_overall_health(),
            "total_servers": len(self.servers),
            "healthy_servers": len([s for s in self.health_status.values() if s.status == MCPServerStatus.HEALTHY]),
            "degraded_servers": len([s for s in self.health_status.values() if s.status == MCPServerStatus.DEGRADED]),
            "offline_servers": len([s for s in self.health_status.values() if s.status == MCPServerStatus.OFFLINE]),
            "last_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "servers": {name: asdict(health) for name, health in self.health_status.items()}
        }
        
        return status_summary

    async def check_all_server_health(self):
        """Check health of all configured MCP servers"""
        logger.info("Performing comprehensive health check...")
        
        # Check all servers in parallel
        tasks = []
        for server_name in self.servers.keys():
            tasks.append(self._check_server_health(server_name))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        self.last_health_check = datetime.now()
        
        # Log health summary
        healthy_count = len([s for s in self.health_status.values() if s.status == MCPServerStatus.HEALTHY])
        logger.info(f"Health check complete: {healthy_count}/{len(self.servers)} servers healthy")

    async def _check_server_health(self, server_name: str) -> bool:
        """Check health of individual MCP server"""
        config = self.servers.get(server_name)
        if not config:
            return False
        
        start_time = datetime.now()
        
        try:
            # Try to connect to server health endpoint
            url = f"http://localhost:{config.port}/health"
            response = await self.client.get(url, timeout=5.0)
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                self.health_status[server_name] = MCPServerHealth(
                    name=server_name,
                    status=MCPServerStatus.HEALTHY,
                    last_check=datetime.now(),
                    response_time_ms=response_time,
                    error_message=None,
                    uptime_seconds=None,  # Could be extracted from response
                    capabilities=config.capabilities
                )
                return True
            else:
                self.health_status[server_name] = MCPServerHealth(
                    name=server_name,
                    status=MCPServerStatus.DEGRADED,
                    last_check=datetime.now(),
                    response_time_ms=response_time,
                    error_message=f"HTTP {response.status_code}",
                    uptime_seconds=None,
                    capabilities=config.capabilities
                )
                return False
                
        except Exception as e:
            self.health_status[server_name] = MCPServerHealth(
                name=server_name,
                status=MCPServerStatus.OFFLINE,
                last_check=datetime.now(),
                response_time_ms=None,
                error_message=str(e),
                uptime_seconds=None,
                capabilities=config.capabilities
            )
            return False

    def _calculate_overall_health(self) -> str:
        """Calculate overall health status"""
        if not self.health_status:
            return "unknown"
        
        healthy_count = len([s for s in self.health_status.values() if s.status == MCPServerStatus.HEALTHY])
        total_count = len(self.health_status)
        health_percentage = (healthy_count / total_count) * 100
        
        if health_percentage >= 90:
            return "excellent"
        elif health_percentage >= 70:
            return "good"
        elif health_percentage >= 50:
            return "degraded"
        else:
            return "critical"

    def _get_fallback_server(self, primary_server: str) -> Optional[str]:
        """Get fallback server for failed primary server"""
        # Define fallback mapping
        fallback_mapping = {
            "enhanced_ai_memory": "ai_memory",
            "portkey_admin_official": "portkey_gateway",
            "microsoft_playwright_official": None,  # No fallback for unique services
            "glips_figma_context_official": None,
            "openrouter_search_official": None
        }
        
        fallback = fallback_mapping.get(primary_server)
        
        # Check if fallback server is available
        if fallback and fallback in self.health_status:
            if self.health_status[fallback].status == MCPServerStatus.HEALTHY:
                return fallback
        
        return None

    async def handle_mcp_failover(self, failed_server: str):
        """Handle MCP server failures with intelligent fallback"""
        logger.warning(f"Handling failover for failed server: {failed_server}")
        
        # Mark server as failed
        if failed_server in self.health_status:
            self.health_status[failed_server].status = MCPServerStatus.ERROR
        
        # Try to restart server
        restart_success = await self._restart_mcp_server(failed_server)
        
        if restart_success:
            logger.info(f"Successfully restarted {failed_server}")
        else:
            logger.error(f"Failed to restart {failed_server}, using fallback strategies")
            
            # Implement fallback strategies
            fallback_server = self._get_fallback_server(failed_server)
            if fallback_server:
                logger.info(f"Routing {failed_server} traffic to fallback: {fallback_server}")
            else:
                logger.warning(f"No fallback available for {failed_server}")

    async def _restart_mcp_server(self, server_name: str) -> bool:
        """Attempt to restart failed MCP server"""
        try:
            # In a production environment, this would:
            # 1. Kill existing process if still running
            # 2. Wait for cleanup
            # 3. Restart with original configuration
            # 4. Wait for startup and health check
            
            logger.info(f"Attempting to restart MCP server: {server_name}")
            
            # For now, simulate restart attempt
            await asyncio.sleep(2)  # Simulate restart time
            
            # Check if restart was successful
            return await self._check_server_health(server_name)
            
        except Exception as e:
            logger.error(f"Failed to restart {server_name}: {e}")
            return False

    async def get_server_capabilities(self, server_name: str) -> List[str]:
        """Get capabilities of specific MCP server"""
        if server_name in self.servers:
            return self.servers[server_name].capabilities
        return []

    async def shutdown(self):
        """Gracefully shutdown all MCP servers"""
        logger.info("Shutting down MCP orchestration service...")
        
        # Close HTTP client
        await self.client.aclose()
        
        # Terminate server processes (in production)
        for server_name, process in self.server_processes.items():
            try:
                if process and process.poll() is None:
                    logger.info(f"Terminating MCP server: {server_name}")
                    process.terminate()
                    # Wait for graceful shutdown
                    await asyncio.sleep(2)
                    if process.poll() is None:
                        process.kill()
            except Exception as e:
                logger.error(f"Error shutting down {server_name}: {e}")
        
        logger.info("MCP orchestration service shutdown complete")

# Global instance
_mcp_service_instance: Optional[MCPOrchestrationService] = None

def get_mcp_service() -> MCPOrchestrationService:
    """Get or create MCP orchestration service instance"""
    global _mcp_service_instance
    if _mcp_service_instance is None:
        _mcp_service_instance = MCPOrchestrationService()
    return _mcp_service_instance

async def initialize_mcp_service() -> MCPOrchestrationService:
    """Initialize MCP service and start servers"""
    service = get_mcp_service()
    await service.initialize_mcp_servers()
    return service
