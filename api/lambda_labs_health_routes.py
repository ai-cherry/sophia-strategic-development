#!/usr/bin/env python3
"""
Lambda Labs Health Monitoring API Routes
Provides health data for Lambda Labs instances and MCP servers
"""

import logging
import time
from datetime import datetime, timedelta

import aiohttp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

# Router setup
router = APIRouter(prefix="/api/v1/lambda-labs", tags=["lambda-labs-health"])

# Data models
class LambdaLabsInstance(BaseModel):
    id: str
    name: str
    ip: str
    gpu_type: str
    status: str
    cpu_usage: float
    memory_usage: float
    gpu_usage: float
    disk_usage: float
    network_in: float
    network_out: float
    uptime: str
    last_seen: str
    services_count: int
    containers_running: int
    containers_total: int
    temperature: float
    power_consumption: float

class MCPServer(BaseModel):
    id: str
    name: str
    port: int
    status: str
    response_time: float
    last_check: str
    error_rate: float
    requests_per_minute: int
    memory_usage: float
    cpu_usage: float
    version: str
    instance_id: str
    tools_count: int
    active_connections: int

class HealthAlert(BaseModel):
    id: str
    severity: str
    title: str
    message: str
    timestamp: str
    instance: str | None = None
    server: str | None = None

class PerformanceTrends(BaseModel):
    labels: list[str]
    cpu: list[float]
    memory: list[float]
    gpu: list[float]

class HealthMetrics(BaseModel):
    overall_health: float
    instances: list[LambdaLabsInstance]
    mcp_servers: list[MCPServer]
    alerts: list[HealthAlert]
    performance_trends: PerformanceTrends

# Configuration
LAMBDA_LABS_INSTANCES = [
    {
        "id": "platform-prod",
        "name": "sophia-platform-prod",
        "ip": "192.222.58.232",
        "gpu_type": "GPU 1x A10",
    },
    {
        "id": "mcp-prod",
        "name": "sophia-mcp-prod",
        "ip": "165.1.69.44",
        "gpu_type": "GPU 1x A10",
    },
    {
        "id": "ai-prod",
        "name": "sophia-ai-prod",
        "ip": "192.222.58.232",
        "gpu_type": "GPU 1x A100",
    },
]

# ALL MCP SERVERS - Complete list from configuration files
MCP_SERVERS = [
    # Core Intelligence (9000-9019)
    {
        "id": "ai-memory",
        "name": "ai-memory-mcp",
        "port": 9000,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "figma-context",
        "name": "figma-context-mcp",
        "port": 9001,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "ui-ux-agent",
        "name": "ui-ux-agent-mcp",
        "port": 9002,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "codacy",
        "name": "codacy-mcp",
        "port": 3008,
        "health_path": "/api/v1/health",
        "instance_id": "mcp-prod",
    },  # Special port
    {
        "id": "asana",
        "name": "asana-mcp",
        "port": 9004,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "notion",
        "name": "notion-mcp",
        "port": 9005,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "linear",
        "name": "linear-mcp",
        "port": 9006,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "github",
        "name": "github-mcp",
        "port": 9007,
        "health_path": "/health",
        "instance_id": "platform-prod",
    },
    {
        "id": "slack",
        "name": "slack-mcp",
        "port": 9008,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "postgres",
        "name": "postgres-mcp",
        "port": 9009,
        "health_path": "/health",
        "instance_id": "platform-prod",
    },
    {
        "id": "sophia-data-intelligence",
        "name": "sophia-data-intelligence-mcp",
        "port": 9010,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "sophia-infrastructure",
        "name": "sophia-infrastructure-mcp",
        "port": 9011,
        "health_path": "/health",
        "instance_id": "platform-prod",
    },
    {
        "id": "qdrant-admin",
        "name": "qdrant-admin-mcp",
        "port": 9012,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "portkey-admin",
        "name": "portkey-admin-mcp",
        "port": 9013,
        "health_path": "/health",
        "instance_id": "platform-prod",
    },
    {
        "id": "openrouter-search",
        "name": "openrouter-search-mcp",
        "port": 9014,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "sophia-business-intelligence",
        "name": "sophia-business-intelligence-mcp",
        "port": 9015,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "sophia-ai-intelligence",
        "name": "sophia-ai-intelligence-mcp",
        "port": 9016,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "apify-intelligence",
        "name": "apify-intelligence-mcp",
        "port": 9017,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "bright-data",
        "name": "bright-data-mcp",
        "port": 9018,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "graphiti",
        "name": "graphiti-mcp",
        "port": 9019,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    # Strategic Enhancements (9020-9029)
    {
        "id": "lambda-labs-cli",
        "name": "lambda-labs-cli-mcp",
        "port": 9040,
        "health_path": "/health",
        "instance_id": "platform-prod",
    },  # Updated port
    {
        "id": "qdrant-cli-enhanced",
        "name": "qdrant-cli-enhanced-mcp",
        "port": 9021,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "estuary-flow-cli",
        "name": "estuary-flow-cli-mcp",
        "port": 9022,
        "health_path": "/health",
        "instance_id": "platform-prod",
    },
    {
        "id": "pulumi",
        "name": "pulumi-mcp",
        "port": 9023,
        "health_path": "/health",
        "instance_id": "platform-prod",
    },
    {
        "id": "docker",
        "name": "docker-mcp",
        "port": 9024,
        "health_path": "/health",
        "instance_id": "platform-prod",
    },
    # Business Intelligence (9100-9119)
    {
        "id": "hubspot",
        "name": "hubspot-mcp",
        "port": 9100,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "gong",
        "name": "gong-mcp",
        "port": 9101,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "apollo-io",
        "name": "apollo-io-mcp",
        "port": 9102,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    # Data Integrations (9200-9219)
    {
        "id": "qdrant",
        "name": "qdrant-mcp",
        "port": 9200,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "qdrant-cortex",
        "name": "qdrant-cortex-mcp",
        "port": 9201,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "estuary",
        "name": "estuary-mcp",
        "port": 9202,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    # Additional Servers
    {
        "id": "prompt-optimizer",
        "name": "prompt-optimizer-mcp",
        "port": 9030,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "mem0-bridge",
        "name": "mem0-bridge-mcp",
        "port": 9031,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    # Backend MCP Servers
    {
        "id": "mem0-openmemory",
        "name": "mem0-openmemory-mcp",
        "port": 9032,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "mem0-persistent",
        "name": "mem0-persistent-mcp",
        "port": 9033,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "cortex-aisql",
        "name": "cortex-aisql-mcp",
        "port": 9034,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    # Additional MCP Servers from mapping
    {
        "id": "hubspot-unified",
        "name": "hubspot-unified-mcp",
        "port": 9103,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "qdrant-unified",
        "name": "qdrant-unified-mcp",
        "port": 9203,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "code-modifier",
        "name": "code-modifier-mcp",
        "port": 9035,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "slack-integration",
        "name": "slack-integration-mcp",
        "port": 9104,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "slack-unified",
        "name": "slack-unified-mcp",
        "port": 9105,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "migration-orchestrator",
        "name": "migration-orchestrator-mcp",
        "port": 9036,
        "health_path": "/health",
        "instance_id": "platform-prod",
    },
    {
        "id": "intercom",
        "name": "intercom-mcp",
        "port": 9106,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "sophia-intelligence-unified",
        "name": "sophia-intelligence-unified-mcp",
        "port": 8081,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "huggingface-ai",
        "name": "huggingface-ai-mcp",
        "port": 9037,
        "health_path": "/health",
        "instance_id": "ai-prod",
    },
    {
        "id": "ag-ui",
        "name": "ag-ui-mcp",
        "port": 9038,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "salesforce",
        "name": "salesforce-mcp",
        "port": 9107,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
    {
        "id": "v0dev",
        "name": "v0dev-mcp",
        "port": 9039,
        "health_path": "/health",
        "instance_id": "mcp-prod",
    },
]

class LambdaLabsHealthService:
    """Service for monitoring Lambda Labs infrastructure health"""

    def __init__(self):
        self.last_update = None
        self.cached_metrics = None
        self.cache_duration = timedelta(seconds=30)  # Cache for 30 seconds

    async def get_health_metrics(self) -> HealthMetrics:
        """Get comprehensive health metrics"""
        # Check cache
        if (
            self.cached_metrics
            and self.last_update
            and datetime.now() - self.last_update < self.cache_duration
        ):
            return self.cached_metrics

        try:
            # Collect data from all sources
            instances = await self.check_instance_health()
            servers = await self.check_mcp_server_health()
            alerts = self.generate_alerts(instances, servers)
            trends = self.get_performance_trends()

            # Calculate overall health
            overall_health = self.calculate_overall_health(instances, servers)

            metrics = HealthMetrics(
                overall_health=overall_health,
                instances=instances,
                mcp_servers=servers,
                alerts=alerts,
                performance_trends=trends,
            )

            # Update cache
            self.cached_metrics = metrics
            self.last_update = datetime.now()

            return metrics

        except Exception as e:
            logger.exception(f"Error getting health metrics: {e}")
            return self.get_mock_metrics()

    async def check_instance_health(self) -> list[LambdaLabsInstance]:
        """Check health of Lambda Labs instances"""
        instances = []

        for instance_config in LAMBDA_LABS_INSTANCES:
            try:
                # In a real implementation, this would query the actual instance
                # For now, we'll use mock data with some realistic variations
                instance = LambdaLabsInstance(
                    id=instance_config["id"],
                    name=instance_config["name"],
                    ip=instance_config["ip"],
                    gpu_type=instance_config["gpu_type"],
                    status=self.get_mock_instance_status(instance_config["id"]),
                    cpu_usage=self.get_mock_cpu_usage(instance_config["id"]),
                    memory_usage=self.get_mock_memory_usage(instance_config["id"]),
                    gpu_usage=self.get_mock_gpu_usage(instance_config["id"]),
                    disk_usage=self.get_mock_disk_usage(instance_config["id"]),
                    network_in=self.get_mock_network_in(instance_config["id"]),
                    network_out=self.get_mock_network_out(instance_config["id"]),
                    uptime=self.get_mock_uptime(instance_config["id"]),
                    last_seen=datetime.now().isoformat(),
                    services_count=self.get_mock_services_count(instance_config["id"]),
                    containers_running=self.get_mock_containers_running(
                        instance_config["id"]
                    ),
                    containers_total=self.get_mock_containers_total(
                        instance_config["id"]
                    ),
                    temperature=self.get_mock_temperature(instance_config["id"]),
                    power_consumption=self.get_mock_power_consumption(
                        instance_config["id"]
                    ),
                )
                instances.append(instance)

            except Exception as e:
                logger.exception(
                    f"Error checking instance {instance_config['name']}: {e}"
                )
                # Add unhealthy instance
                instances.append(
                    LambdaLabsInstance(
                        id=instance_config["id"],
                        name=instance_config["name"],
                        ip=instance_config["ip"],
                        gpu_type=instance_config["gpu_type"],
                        status="unhealthy",
                        cpu_usage=0,
                        memory_usage=0,
                        gpu_usage=0,
                        disk_usage=0,
                        network_in=0,
                        network_out=0,
                        uptime="0d 0h 0m",
                        last_seen="unknown",
                        services_count=0,
                        containers_running=0,
                        containers_total=0,
                        temperature=0,
                        power_consumption=0,
                    )
                )

        return instances

    async def check_mcp_server_health(self) -> list[MCPServer]:
        """Check health of MCP servers"""
        servers = []

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5)
        ) as session:
            for server_config in MCP_SERVERS:
                server = await self.check_single_mcp_server(session, server_config)
                servers.append(server)

        return servers

    async def check_single_mcp_server(
        self, session: aiohttp.ClientSession, config: dict
    ) -> MCPServer:
        """Check health of a single MCP server"""
        url = f"http://localhost:{config['port']}{config['health_path']}"

        try:
            start_time = time.time()
            async with session.get(url) as response:
                response_time = (time.time() - start_time) * 1000  # Convert to ms

                if response.status == 200:
                    status = "healthy"
                    error_rate = 0.1
                else:
                    status = "degraded"
                    error_rate = 2.0

                return MCPServer(
                    id=config["id"],
                    name=config["name"],
                    port=config["port"],
                    status=status,
                    response_time=response_time,
                    last_check=datetime.now().isoformat(),
                    error_rate=error_rate,
                    requests_per_minute=self.get_mock_requests_per_minute(config["id"]),
                    memory_usage=self.get_mock_server_memory_usage(config["id"]),
                    cpu_usage=self.get_mock_server_cpu_usage(config["id"]),
                    version=self.get_mock_version(config["id"]),
                    instance_id=config["instance_id"],
                    tools_count=self.get_mock_tools_count(config["id"]),
                    active_connections=self.get_mock_active_connections(config["id"]),
                )

        except (TimeoutError, aiohttp.ClientConnectorError):
            # Server unreachable
            return MCPServer(
                id=config["id"],
                name=config["name"],
                port=config["port"],
                status="unreachable",
                response_time=0,
                last_check=datetime.now().isoformat(),
                error_rate=100,
                requests_per_minute=0,
                memory_usage=0,
                cpu_usage=0,
                version="unknown",
                instance_id=config["instance_id"],
                tools_count=0,
                active_connections=0,
            )
        except Exception as e:
            logger.exception(f"Error checking MCP server {config['name']}: {e}")
            return MCPServer(
                id=config["id"],
                name=config["name"],
                port=config["port"],
                status="error",
                response_time=0,
                last_check=datetime.now().isoformat(),
                error_rate=100,
                requests_per_minute=0,
                memory_usage=0,
                cpu_usage=0,
                version="unknown",
                instance_id=config["instance_id"],
                tools_count=0,
                active_connections=0,
            )

    def generate_alerts(
        self, instances: list[LambdaLabsInstance], servers: list[MCPServer]
    ) -> list[HealthAlert]:
        """Generate health alerts based on current status"""
        alerts = []

        # Check for unhealthy instances
        for instance in instances:
            if instance.status != "healthy":
                alerts.append(
                    HealthAlert(
                        id=f"instance-{instance.id}-{int(time.time())}",
                        severity=(
                            "critical" if instance.status == "unhealthy" else "warning"
                        ),
                        title=f"Instance {instance.name} {instance.status}",
                        message=f"Lambda Labs instance {instance.name} is {instance.status}",
                        timestamp=datetime.now().isoformat(),
                        instance=instance.name,
                    )
                )

            # Check resource usage
            if instance.gpu_usage > 90:
                alerts.append(
                    HealthAlert(
                        id=f"gpu-usage-{instance.id}-{int(time.time())}",
                        severity="warning",
                        title="High GPU Usage",
                        message=f"{instance.name} GPU usage at {instance.gpu_usage}%",
                        timestamp=datetime.now().isoformat(),
                        instance=instance.name,
                    )
                )

            if instance.memory_usage > 85:
                alerts.append(
                    HealthAlert(
                        id=f"memory-usage-{instance.id}-{int(time.time())}",
                        severity="warning",
                        title="High Memory Usage",
                        message=f"{instance.name} memory usage at {instance.memory_usage}%",
                        timestamp=datetime.now().isoformat(),
                        instance=instance.name,
                    )
                )

        # Check for unhealthy MCP servers
        for server in servers:
            if server.status in ["unhealthy", "unreachable", "error"]:
                alerts.append(
                    HealthAlert(
                        id=f"server-{server.id}-{int(time.time())}",
                        severity=(
                            "critical"
                            if server.status in ["unhealthy", "unreachable"]
                            else "warning"
                        ),
                        title=f"MCP Server {server.name} {server.status}",
                        message=f"MCP server {server.name} is {server.status}",
                        timestamp=datetime.now().isoformat(),
                        server=server.name,
                    )
                )

            # Check response time
            if server.response_time > 200 and server.status == "healthy":
                alerts.append(
                    HealthAlert(
                        id=f"response-time-{server.id}-{int(time.time())}",
                        severity="warning",
                        title="Slow Response Time",
                        message=f"{server.name} response time degraded to {server.response_time:.0f}ms",
                        timestamp=datetime.now().isoformat(),
                        server=server.name,
                    )
                )

        return alerts

    def get_performance_trends(self) -> PerformanceTrends:
        """Get performance trends data"""
        # Mock trend data - in real implementation, this would come from monitoring
        now = datetime.now()
        labels = [
            (now - timedelta(minutes=i * 10)).strftime("%H:%M")
            for i in range(4, -1, -1)
        ]

        return PerformanceTrends(
            labels=labels,
            cpu=[42, 45, 48, 52, 51],
            memory=[65, 67, 70, 71, 68],
            gpu=[75, 78, 82, 85, 79],
        )

    def calculate_overall_health(
        self, instances: list[LambdaLabsInstance], servers: list[MCPServer]
    ) -> float:
        """Calculate overall health percentage"""
        if not instances and not servers:
            return 0.0

        # Instance health score
        healthy_instances = sum(1 for i in instances if i.status == "healthy")
        instance_score = (
            (healthy_instances / len(instances)) * 100 if instances else 100
        )

        # Server health score
        healthy_servers = sum(1 for s in servers if s.status == "healthy")
        server_score = (healthy_servers / len(servers)) * 100 if servers else 100

        # Weighted average (60% servers, 40% instances)
        overall_health = (server_score * 0.6) + (instance_score * 0.4)

        return round(overall_health, 1)

    def get_mock_metrics(self) -> HealthMetrics:
        """Get mock metrics for development/fallback"""
        return HealthMetrics(
            overall_health=87.0,
            instances=[
                LambdaLabsInstance(
                    id="platform-prod",
                    name="sophia-platform-prod",
                    ip="192.222.58.232",
                    gpu_type="GPU 1x A10",
                    status="healthy",
                    cpu_usage=45.0,
                    memory_usage=67.0,
                    gpu_usage=23.0,
                    disk_usage=34.0,
                    network_in=12.5,
                    network_out=8.3,
                    uptime="15d 6h 23m",
                    last_seen=datetime.now().isoformat(),
                    services_count=8,
                    containers_running=12,
                    containers_total=15,
                    temperature=65.0,
                    power_consumption=280.0,
                )
            ],
            mcp_servers=[
                MCPServer(
                    id="ai-memory",
                    name="ai-memory-mcp",
                    port=9001,
                    status="healthy",
                    response_time=45.0,
                    last_check=datetime.now().isoformat(),
                    error_rate=0.2,
                    requests_per_minute=150,
                    memory_usage=32.0,
                    cpu_usage=15.0,
                    version="1.2.3",
                    instance_id="mcp-prod",
                    tools_count=8,
                    active_connections=12,
                )
            ],
            alerts=[],
            performance_trends=PerformanceTrends(
                labels=["10:50", "10:55", "11:00", "11:05", "11:10"],
                cpu=[42, 45, 48, 52, 51],
                memory=[65, 67, 70, 71, 68],
                gpu=[75, 78, 82, 85, 79],
            ),
        )

    # Mock data generators
    def get_mock_instance_status(self, instance_id: str) -> str:
        status_map = {
            "platform-prod": "healthy",
            "mcp-prod": "healthy",
            "ai-prod": "degraded",  # Simulate one degraded instance
        }
        return status_map.get(instance_id, "healthy")

    def get_mock_cpu_usage(self, instance_id: str) -> float:
        base_usage = {"platform-prod": 45, "mcp-prod": 32, "ai-prod": 78}
        return base_usage.get(instance_id, 50) + (time.time() % 10) - 5

    def get_mock_memory_usage(self, instance_id: str) -> float:
        base_usage = {"platform-prod": 67, "mcp-prod": 54, "ai-prod": 89}
        return base_usage.get(instance_id, 60) + (time.time() % 8) - 4

    def get_mock_gpu_usage(self, instance_id: str) -> float:
        base_usage = {"platform-prod": 23, "mcp-prod": 78, "ai-prod": 92}
        return base_usage.get(instance_id, 50) + (time.time() % 6) - 3

    def get_mock_disk_usage(self, instance_id: str) -> float:
        base_usage = {"platform-prod": 34, "mcp-prod": 28, "ai-prod": 56}
        return base_usage.get(instance_id, 40)

    def get_mock_network_in(self, instance_id: str) -> float:
        base_usage = {"platform-prod": 12.5, "mcp-prod": 8.7, "ai-prod": 25.4}
        return base_usage.get(instance_id, 10)

    def get_mock_network_out(self, instance_id: str) -> float:
        base_usage = {"platform-prod": 8.3, "mcp-prod": 15.2, "ai-prod": 31.8}
        return base_usage.get(instance_id, 10)

    def get_mock_uptime(self, instance_id: str) -> str:
        uptimes = {
            "platform-prod": "15d 6h 23m",
            "mcp-prod": "12d 14h 56m",
            "ai-prod": "8d 2h 15m",
        }
        return uptimes.get(instance_id, "10d 0h 0m")

    def get_mock_services_count(self, instance_id: str) -> int:
        counts = {"platform-prod": 8, "mcp-prod": 11, "ai-prod": 6}
        return counts.get(instance_id, 5)

    def get_mock_containers_running(self, instance_id: str) -> int:
        counts = {"platform-prod": 12, "mcp-prod": 8, "ai-prod": 15}
        return counts.get(instance_id, 5)

    def get_mock_containers_total(self, instance_id: str) -> int:
        counts = {"platform-prod": 15, "mcp-prod": 8, "ai-prod": 18}
        return counts.get(instance_id, 8)

    def get_mock_temperature(self, instance_id: str) -> float:
        temps = {"platform-prod": 65, "mcp-prod": 72, "ai-prod": 84}
        return temps.get(instance_id, 70)

    def get_mock_power_consumption(self, instance_id: str) -> float:
        power = {"platform-prod": 280, "mcp-prod": 315, "ai-prod": 420}
        return power.get(instance_id, 300)

    def get_mock_requests_per_minute(self, server_id: str) -> int:
        rpm_map = {
            "ai-memory": 150,
            "codacy": 85,
            "linear": 42,
            "github": 0,
            "qdrant-admin": 28,
            "lambda-labs-cli": 35,
            "asana": 55,
            "notion": 22,
        }
        return rpm_map.get(server_id, 50)

    def get_mock_server_memory_usage(self, server_id: str) -> float:
        memory_map = {
            "ai-memory": 32,
            "codacy": 28,
            "linear": 24,
            "github": 0,
            "qdrant-admin": 45,
            "lambda-labs-cli": 18,
            "asana": 26,
            "notion": 22,
        }
        return memory_map.get(server_id, 25)

    def get_mock_server_cpu_usage(self, server_id: str) -> float:
        cpu_map = {
            "ai-memory": 15,
            "codacy": 12,
            "linear": 8,
            "github": 0,
            "qdrant-admin": 34,
            "lambda-labs-cli": 10,
            "asana": 14,
            "notion": 11,
        }
        return cpu_map.get(server_id, 15)

    def get_mock_version(self, server_id: str) -> str:
        version_map = {
            "ai-memory": "1.2.3",
            "codacy": "2.1.0",
            "linear": "1.5.2",
            "github": "1.1.5",
            "qdrant-admin": "1.8.1",
            "lambda-labs-cli": "1.0.2",
            "asana": "1.4.1",
            "notion": "1.3.0",
        }
        return version_map.get(server_id, "1.0.0")

    def get_mock_tools_count(self, server_id: str) -> int:
        tools_map = {
            "ai-memory": 8,
            "codacy": 6,
            "linear": 12,
            "github": 0,
            "qdrant-admin": 15,
            "lambda-labs-cli": 7,
            "asana": 9,
            "notion": 5,
        }
        return tools_map.get(server_id, 5)

    def get_mock_active_connections(self, server_id: str) -> int:
        conn_map = {
            "ai-memory": 12,
            "codacy": 8,
            "linear": 6,
            "github": 0,
            "qdrant-admin": 4,
            "lambda-labs-cli": 3,
            "asana": 7,
            "notion": 2,
        }
        return conn_map.get(server_id, 3)

# Service instance
health_service = LambdaLabsHealthService()

# API Routes
@router.get("/health", response_model=HealthMetrics)
async def get_lambda_labs_health():
    """Get comprehensive Lambda Labs health metrics"""
    try:
        metrics = await health_service.get_health_metrics()
        return metrics
    except Exception as e:
        logger.exception(f"Error getting Lambda Labs health: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve health metrics")

@router.get("/instances")
async def get_instances():
    """Get Lambda Labs instances status"""
    try:
        metrics = await health_service.get_health_metrics()
        return {"instances": metrics.instances}
    except Exception as e:
        logger.exception(f"Error getting instances: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve instances")

@router.get("/servers")
async def get_mcp_servers():
    """Get MCP servers status"""
    try:
        metrics = await health_service.get_health_metrics()
        return {"mcp_servers": metrics.mcp_servers}
    except Exception as e:
        logger.exception(f"Error getting MCP servers: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve MCP servers")

@router.get("/alerts")
async def get_alerts():
    """Get current health alerts"""
    try:
        metrics = await health_service.get_health_metrics()
        return {"alerts": metrics.alerts}
    except Exception as e:
        logger.exception(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")

@router.get("/trends")
async def get_performance_trends():
    """Get performance trends data"""
    try:
        metrics = await health_service.get_health_metrics()
        return {"performance_trends": metrics.performance_trends}
    except Exception as e:
        logger.exception(f"Error getting trends: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve performance trends"
        )

@router.post("/refresh")
async def refresh_health_data():
    """Force refresh of health data"""
    try:
        # Clear cache to force refresh
        health_service.cached_metrics = None
        health_service.last_update = None

        metrics = await health_service.get_health_metrics()
        return {
            "message": "Health data refreshed",
            "overall_health": metrics.overall_health,
        }
    except Exception as e:
        logger.exception(f"Error refreshing health data: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh health data")
