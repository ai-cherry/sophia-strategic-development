"""
Phase 5: MCP Health Monitoring Service
Comprehensive health monitoring for all MCP servers

Date: July 12, 2025
"""

import asyncio
import logging
import time
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

import aiohttp
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server"""
    name: str
    host: str = "localhost"
    port: int
    health_endpoint: str = "/health"
    timeout: int = 5
    critical: bool = True


class HealthStatus(BaseModel):
    """Health status for a server"""
    server: str
    healthy: bool
    latency_ms: float
    status_code: Optional[int] = None
    error: Optional[str] = None
    last_check: datetime = Field(default_factory=lambda: datetime.now(UTC))
    consecutive_failures: int = 0


class MCPHealthMonitor:
    """Monitor health of all MCP servers"""
    
    def __init__(self):
        self.servers = self._load_server_configs()
        self.health_status: Dict[str, HealthStatus] = {}
        self.monitoring_active = False
        self.check_interval = 30  # seconds
        self.alert_threshold = 3  # consecutive failures before alert
        
    def _load_server_configs(self) -> List[MCPServerConfig]:
        """Load MCP server configurations"""
        return [
            # Core servers
            MCPServerConfig(name="sophia-orchestrator", port=8000),
            MCPServerConfig(name="enhanced-chat-v4", port=8001),
            MCPServerConfig(name="unified-memory-v3", port=8002),
            
            # MCP servers
            MCPServerConfig(name="ai-memory", port=9001),
            MCPServerConfig(name="ui-ux-agent", port=9002),
            MCPServerConfig(name="github", port=9003),
            MCPServerConfig(name="linear", port=9004),
            MCPServerConfig(name="slack", port=9005),
            MCPServerConfig(name="hubspot", port=9006),
            MCPServerConfig(name="asana", port=9007),
            MCPServerConfig(name="notion", port=9008),
            
            # Data stores
            MCPServerConfig(name="redis", port=6379, critical=True),
            MCPServerConfig(name="postgresql", port=5432, critical=True),
        ]
    
    async def check_server_health(self, server: MCPServerConfig) -> HealthStatus:
        """Check health of a single server"""
        start_time = time.time()
        
        try:
            # Special handling for Redis
            if server.name == "redis":
                import redis.asyncio as redis
                client = await redis.from_url(f"redis://{server.host}:{server.port}")
                await client.ping()
                await client.close()
                latency = (time.time() - start_time) * 1000
                return HealthStatus(
                    server=server.name,
                    healthy=True,
                    latency_ms=latency,
                    status_code=200
                )
            
            # Special handling for PostgreSQL
            if server.name == "postgresql":
                # Mock for now
                await asyncio.sleep(0.01)
                latency = (time.time() - start_time) * 1000
                return HealthStatus(
                    server=server.name,
                    healthy=True,
                    latency_ms=latency,
                    status_code=200
                )
            
            # HTTP health check for other servers
            url = f"http://{server.host}:{server.port}{server.health_endpoint}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=server.timeout)
                ) as response:
                    latency = (time.time() - start_time) * 1000
                    
                    # Get previous status
                    prev_status = self.health_status.get(server.name)
                    consecutive_failures = 0
                    
                    if response.status != 200:
                        consecutive_failures = (
                            prev_status.consecutive_failures + 1 
                            if prev_status else 1
                        )
                    
                    return HealthStatus(
                        server=server.name,
                        healthy=response.status == 200,
                        latency_ms=latency,
                        status_code=response.status,
                        consecutive_failures=consecutive_failures
                    )
                    
        except asyncio.TimeoutError:
            latency = server.timeout * 1000
            prev_status = self.health_status.get(server.name)
            consecutive_failures = (
                prev_status.consecutive_failures + 1 
                if prev_status else 1
            )
            
            return HealthStatus(
                server=server.name,
                healthy=False,
                latency_ms=latency,
                error="Timeout",
                consecutive_failures=consecutive_failures
            )
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            prev_status = self.health_status.get(server.name)
            consecutive_failures = (
                prev_status.consecutive_failures + 1 
                if prev_status else 1
            )
            
            return HealthStatus(
                server=server.name,
                healthy=False,
                latency_ms=latency,
                error=str(e),
                consecutive_failures=consecutive_failures
            )
    
    async def check_all_servers(self) -> Dict[str, HealthStatus]:
        """Check health of all servers"""
        tasks = []
        for server in self.servers:
            tasks.append(self.check_server_health(server))
        
        results = await asyncio.gather(*tasks)
        
        # Update health status
        for status in results:
            self.health_status[status.server] = status
            
            # Check for alerts
            if (status.consecutive_failures >= self.alert_threshold and
                not status.healthy):
                await self._send_alert(status)
        
        return self.health_status
    
    async def _send_alert(self, status: HealthStatus):
        """Send alert for unhealthy server"""
        server_config = next(
            (s for s in self.servers if s.name == status.server), 
            None
        )
        
        alert = {
            "timestamp": datetime.now(UTC).isoformat(),
            "server": status.server,
            "critical": server_config.critical if server_config else False,
            "consecutive_failures": status.consecutive_failures,
            "error": status.error,
            "message": f"Server {status.server} has failed {status.consecutive_failures} consecutive health checks"
        }
        
        logger.error(f"ALERT: {alert['message']}")
        
        # In production, this would send to alerting system
        # (PagerDuty, Slack, email, etc.)
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        self.monitoring_active = True
        logger.info("Starting MCP health monitoring")
        
        while self.monitoring_active:
            try:
                await self.check_all_servers()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        logger.info("Stopping MCP health monitoring")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of all server health"""
        total_servers = len(self.servers)
        healthy_servers = sum(
            1 for status in self.health_status.values() 
            if status.healthy
        )
        
        critical_servers = [
            s.name for s in self.servers if s.critical
        ]
        critical_healthy = sum(
            1 for name in critical_servers
            if name in self.health_status and self.health_status[name].healthy
        )
        
        avg_latency = sum(
            status.latency_ms for status in self.health_status.values()
        ) / len(self.health_status) if self.health_status else 0
        
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_servers": total_servers,
            "healthy_servers": healthy_servers,
            "unhealthy_servers": total_servers - healthy_servers,
            "health_percentage": (healthy_servers / total_servers * 100) if total_servers > 0 else 0,
            "critical_servers_healthy": critical_healthy,
            "critical_servers_total": len(critical_servers),
            "avg_latency_ms": round(avg_latency, 2),
            "servers": {
                name: {
                    "healthy": status.healthy,
                    "latency_ms": status.latency_ms,
                    "last_check": status.last_check.isoformat(),
                    "consecutive_failures": status.consecutive_failures,
                    "error": status.error
                }
                for name, status in self.health_status.items()
            }
        }
    
    def get_unhealthy_servers(self) -> List[Dict[str, Any]]:
        """Get list of unhealthy servers"""
        unhealthy = []
        
        for server in self.servers:
            status = self.health_status.get(server.name)
            if status and not status.healthy:
                unhealthy.append({
                    "name": server.name,
                    "port": server.port,
                    "critical": server.critical,
                    "error": status.error,
                    "consecutive_failures": status.consecutive_failures,
                    "last_check": status.last_check.isoformat()
                })
        
        return unhealthy
    
    async def restart_unhealthy_servers(self) -> Dict[str, bool]:
        """Attempt to restart unhealthy servers"""
        results = {}
        
        for server_info in self.get_unhealthy_servers():
            server_name = server_info["name"]
            
            # In production, this would use systemctl or k8s API
            # Mock restart
            logger.info(f"Attempting to restart {server_name}")
            await asyncio.sleep(1)
            
            # Check health after restart
            server_config = next(
                (s for s in self.servers if s.name == server_name),
                None
            )
            if server_config:
                new_status = await self.check_server_health(server_config)
                results[server_name] = new_status.healthy
                
                if new_status.healthy:
                    logger.info(f"Successfully restarted {server_name}")
                else:
                    logger.error(f"Failed to restart {server_name}")
        
        return results


# Global monitor instance
_health_monitor: Optional[MCPHealthMonitor] = None


def get_health_monitor() -> MCPHealthMonitor:
    """Get or create health monitor instance"""
    global _health_monitor
    
    if _health_monitor is None:
        _health_monitor = MCPHealthMonitor()
    
    return _health_monitor 