"""Enhanced MCP Registry v2 with YAML configuration and tiering support."""

import asyncio
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import yaml
from prometheus_client import Counter, Gauge
from pydantic import BaseModel, Field, validator

from backend.core.auto_esc_config import get_config_value

# Metrics
MCP_REGISTRY_SERVERS = Gauge(
    "mcp_registry_servers_total", "Total registered MCP servers", ["tier", "type"]
)
MCP_REGISTRY_HEALTH = Gauge(
    "mcp_registry_server_health", "MCP server health status", ["name", "tier"]
)
MCP_REGISTRY_LOOKUPS = Counter(
    "mcp_registry_lookups_total", "MCP registry lookups", ["capability", "tier"]
)
MCP_REGISTRY_ERRORS = Counter(
    "mcp_registry_errors_total", "MCP registry errors", ["operation", "error_type"]
)


class Tier(str, Enum):
    """Server tier levels."""

    PRIMARY = "PRIMARY"  # Critical servers
    SECONDARY = "SECONDARY"  # Important servers
    TERTIARY = "TERTIARY"  # Optional servers


class ServerStatus(str, Enum):
    """Server status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"


class MCPServerConfig(BaseModel):
    """MCP server configuration from YAML."""

    name: str
    type: str
    tier: Tier
    port: int
    capabilities: list[str]
    health_endpoint: str = "/health"
    pat_secret: Optional[str] = None
    config: dict[str, Any] = Field(default_factory=dict)

    @validator("tier", pre=True)
    def validate_tier(cls, v):
        """Validate tier value."""
        if isinstance(v, str):
            return Tier(v.upper())
        return v


class GlobalConfig(BaseModel):
    """Global MCP configuration."""

    health_check_interval: int = 30
    timeout: int = 10
    retry_attempts: int = 3
    circuit_breaker: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)


class YAMLConfig(BaseModel):
    """Complete YAML configuration."""

    servers: list[MCPServerConfig]
    global_config: GlobalConfig = Field(alias="global", default_factory=GlobalConfig)

    class Config:
        allow_population_by_field_name = True


@dataclass
class MCPServer:
    """Enhanced MCP server representation."""

    name: str
    type: str
    tier: Tier
    port: int
    capabilities: set[str]
    health_endpoint: str
    config: dict[str, Any]
    status: ServerStatus = ServerStatus.UNKNOWN
    last_health_check: Optional[float] = None
    error_count: int = 0
    pat_token: Optional[str] = None

    @property
    def url(self) -> str:
        """Get server URL."""
        host = self.config.get("host", "localhost")
        return f"http://{host}:{self.port}"

    @property
    def health_url(self) -> str:
        """Get health check URL."""
        return f"{self.url}{self.health_endpoint}"

    def has_capability(self, capability: str) -> bool:
        """Check if server has capability."""
        return capability.upper() in {cap.upper() for cap in self.capabilities}


class RegistryV2:
    """Enhanced MCP registry with YAML configuration and tiering."""

    def __init__(self, config_path: Optional[Path] = None, auto_load: bool = True):
        """Initialize registry.

        Args:
            config_path: Path to YAML configuration
            auto_load: Whether to auto-load configuration
        """
        self._config_path = config_path or Path("config/mcp/mcp_servers.yaml")
        self._servers: dict[str, MCPServer] = {}
        self._capabilities: dict[str, list[str]] = {}
        self._tiers: dict[Tier, list[str]] = {
            Tier.PRIMARY: [],
            Tier.SECONDARY: [],
            Tier.TERTIARY: [],
        }
        self._global_config: GlobalConfig = GlobalConfig()

        if auto_load and self._config_path.exists():
            self.load_configuration()

    def load_configuration(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self._config_path) as f:
                data = yaml.safe_load(f)

            config = YAMLConfig(**data)
            self._global_config = config.global_config

            # Clear existing data
            self._servers.clear()
            self._capabilities.clear()
            for tier_list in self._tiers.values():
                tier_list.clear()

            # Load servers
            for server_cfg in config.servers:
                # Load PAT token if specified
                pat_token = None
                if server_cfg.pat_secret:
                    pat_token = get_config_value(server_cfg.pat_secret.lower())

                server = MCPServer(
                    name=server_cfg.name,
                    type=server_cfg.type,
                    tier=server_cfg.tier,
                    port=server_cfg.port,
                    capabilities=set(server_cfg.capabilities),
                    health_endpoint=server_cfg.health_endpoint,
                    config=server_cfg.config,
                    pat_token=pat_token,
                )

                self.register_server(server)

            # Update metrics
            for tier in Tier:
                count = len(self._tiers[tier])
                MCP_REGISTRY_SERVERS.labels(tier=tier.value, type="all").set(count)

        except Exception as e:
            MCP_REGISTRY_ERRORS.labels(
                operation="load_configuration", error_type=type(e).__name__
            ).inc()
            raise

    def register_server(self, server: MCPServer) -> None:
        """Register a server."""
        self._servers[server.name] = server

        # Update tier mapping
        self._tiers[server.tier].append(server.name)

        # Update capability mapping
        for capability in server.capabilities:
            if capability not in self._capabilities:
                self._capabilities[capability] = []
            self._capabilities[capability].append(server.name)

        # Update metrics
        MCP_REGISTRY_SERVERS.labels(tier=server.tier.value, type=server.type).inc()

    def get_server(self, name: str) -> Optional[MCPServer]:
        """Get server by name."""
        return self._servers.get(name)

    def get_servers_by_tier(self, tier: Tier) -> list[MCPServer]:
        """Get all servers in a tier."""
        server_names = self._tiers.get(tier, [])
        return [self._servers[name] for name in server_names if name in self._servers]

    def get_servers_by_capability(
        self, capability: str, tier: Optional[Tier] = None
    ) -> list[MCPServer]:
        """Get servers with a specific capability.

        Args:
            capability: Required capability
            tier: Optional tier filter

        Returns:
            List of matching servers
        """
        MCP_REGISTRY_LOOKUPS.labels(
            capability=capability, tier=tier.value if tier else "all"
        ).inc()

        server_names = self._capabilities.get(capability.upper(), [])
        servers = [
            self._servers[name] for name in server_names if name in self._servers
        ]

        if tier:
            servers = [s for s in servers if s.tier == tier]

        # Sort by tier priority
        return sorted(servers, key=lambda s: list(Tier).index(s.tier))

    def get_primary_server_for_capability(self, capability: str) -> Optional[MCPServer]:
        """Get the primary server for a capability."""
        servers = self.get_servers_by_capability(capability, Tier.PRIMARY)
        if servers:
            return servers[0]

        # Fallback to secondary
        servers = self.get_servers_by_capability(capability, Tier.SECONDARY)
        return servers[0] if servers else None

    async def check_server_health(self, server: MCPServer) -> bool:
        """Check server health."""
        import time

        import httpx

        try:
            async with httpx.AsyncClient(timeout=self._global_config.timeout) as client:
                response = await client.get(server.health_url)

                if response.status_code == 200:
                    server.status = ServerStatus.HEALTHY
                    server.error_count = 0
                else:
                    server.status = ServerStatus.UNHEALTHY
                    server.error_count += 1

                server.last_health_check = time.time()

                # Update metrics
                MCP_REGISTRY_HEALTH.labels(
                    name=server.name, tier=server.tier.value
                ).set(1 if server.status == ServerStatus.HEALTHY else 0)

                return server.status == ServerStatus.HEALTHY

        except Exception as e:
            server.status = ServerStatus.UNHEALTHY
            server.error_count += 1
            server.last_health_check = time.time()

            MCP_REGISTRY_ERRORS.labels(
                operation="health_check", error_type=type(e).__name__
            ).inc()

            return False

    async def check_all_health(self) -> dict[str, bool]:
        """Check health of all servers."""
        tasks = []
        for server in self._servers.values():
            tasks.append(self.check_server_health(server))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            name: result if isinstance(result, bool) else False
            for name, result in zip(self._servers.keys(), results, strict=False)
        }

    def get_healthy_servers(self) -> list[MCPServer]:
        """Get all healthy servers."""
        return [
            server
            for server in self._servers.values()
            if server.status == ServerStatus.HEALTHY
        ]

    def get_statistics(self) -> dict[str, Any]:
        """Get registry statistics."""
        total_servers = len(self._servers)
        healthy_servers = len(self.get_healthy_servers())

        tier_stats = {}
        for tier in Tier:
            servers = self.get_servers_by_tier(tier)
            healthy = [s for s in servers if s.status == ServerStatus.HEALTHY]
            tier_stats[tier.value] = {
                "total": len(servers),
                "healthy": len(healthy),
                "health_percentage": (len(healthy) / len(servers) * 100)
                if servers
                else 0,
            }

        capability_stats = {}
        for capability, server_names in self._capabilities.items():
            servers = [
                self._servers[name] for name in server_names if name in self._servers
            ]
            healthy = [s for s in servers if s.status == ServerStatus.HEALTHY]
            capability_stats[capability] = {
                "total": len(servers),
                "healthy": len(healthy),
            }

        return {
            "total_servers": total_servers,
            "healthy_servers": healthy_servers,
            "health_percentage": (healthy_servers / total_servers * 100)
            if total_servers
            else 0,
            "tier_statistics": tier_stats,
            "capability_statistics": capability_stats,
            "global_config": self._global_config.dict(),
        }

    def export_to_dict(self) -> dict[str, Any]:
        """Export registry to dictionary."""
        return {
            "servers": {
                name: {
                    "type": server.type,
                    "tier": server.tier.value,
                    "port": server.port,
                    "capabilities": list(server.capabilities),
                    "status": server.status.value,
                    "url": server.url,
                    "config": server.config,
                }
                for name, server in self._servers.items()
            },
            "statistics": self.get_statistics(),
        }


# Singleton instance
_registry: Optional[RegistryV2] = None


def get_registry() -> RegistryV2:
    """Get singleton registry instance."""
    global _registry
    if _registry is None:
        _registry = RegistryV2()
    return _registry
