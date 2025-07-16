#!/usr/bin/env python3
"""
Sophia AI Unified Project Management MCP Server with Dynamic Routing
Consolidates ALL project management functionality with etcd service discovery
Using official Anthropic MCP SDK with agentic routing

Date: July 12, 2025
"""

import asyncio
import sys
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Dict, List
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import etcd3
import httpx
from base.unified_standardized_base import (
    ServerConfig,
    ToolDefinition,
    ToolParameter,
)
from base.unified_standardized_base import (
    UnifiedStandardizedMCPServer as StandardizedMCPServer,
)

from backend.core.auto_esc_config import get_config_value
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Prometheus metrics
route_counter = Counter('mcp_route_requests_total', 'Total routing requests', ['platform', 'tool'])
route_latency = Histogram('mcp_route_latency_seconds', 'Routing latency', ['platform', 'tool'])
service_health = Gauge('mcp_service_health', 'Service health status', ['service'])

class ProjectPlatform(str, Enum):
    """Supported project management platforms"""
    ASANA = "asana"
    LINEAR = "linear"
    NOTION = "notion"
    JIRA = "jira"
    GITHUB = "github"
    CLICKUP = "clickup"

class ServiceDiscovery:
    """etcd-based service discovery for dynamic MCP routing"""
    
    def __init__(self, etcd_host: str = "localhost", etcd_port: int = 2379):
        self.etcd = etcd3.client(host=etcd_host, port=etcd_port)
        self.service_registry = {}
        self.health_status = {}
        
    async def register_service(self, service_name: str, endpoint: str, capabilities: List[str]):
        """Register a service with etcd"""
        service_info = {
            "endpoint": endpoint,
            "capabilities": capabilities,
            "health_check": f"{endpoint}/health",
            "registered_at": datetime.now(UTC).isoformat(),
            "status": "active"
        }
        
        # Register with etcd
        self.etcd.put(f"/services/{service_name}", json.dumps(service_info))
        self.service_registry[service_name] = service_info
        logger.info(f"Registered service {service_name} at {endpoint}")
        
    async def discover_services(self) -> Dict[str, Dict]:
        """Discover active services from etcd"""
        services = {}
        try:
            for value, metadata in self.etcd.get_prefix("/services/"):
                service_name = metadata.key.decode().split("/")[-1]
                service_info = json.loads(value.decode())
                services[service_name] = service_info
                
            self.service_registry = services
            return services
        except Exception as e:
            logger.error(f"Service discovery failed: {e}")
            return {}
            
    async def health_check_services(self):
        """Continuously monitor service health"""
        while True:
            for service_name, service_info in self.service_registry.items():
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            service_info["health_check"], 
                            timeout=5.0
                        )
                        healthy = response.status_code == 200
                        self.health_status[service_name] = healthy
                        service_health.labels(service=service_name).set(1 if healthy else 0)
                        
                except Exception as e:
                    logger.warning(f"Health check failed for {service_name}: {e}")
                    self.health_status[service_name] = False
                    service_health.labels(service=service_name).set(0)
                    
            await asyncio.sleep(30)  # Check every 30 seconds

class UnifiedProjectMCPServer(StandardizedMCPServer):
    """Unified Project Management MCP Server with Dynamic Routing"""

    def __init__(self):
        config = ServerConfig(
            name="unified_project",
            version="3.0.0",
            port=9005,
            capabilities=["PROJECT_MANAGEMENT", "TASK_TRACKING", "KNOWLEDGE_BASE", "ANALYTICS", "DYNAMIC_ROUTING"],
            tier="PRIMARY",
        )
        super().__init__(config)

        # Service discovery
        self.service_discovery = ServiceDiscovery()
        
        # Platform configurations - fallback for direct API calls
        self.platform_configs = {
            ProjectPlatform.ASANA: {
                "token": get_config_value("asana_access_token"),
                "url": "https://app.asana.com/api/1.0",
                "service_name": "asana_service"
            },
            ProjectPlatform.LINEAR: {
                "token": get_config_value("linear_api_key"),
                "url": "https://api.linear.app/graphql",
                "service_name": "linear_service"
            },
            ProjectPlatform.NOTION: {
                "token": get_config_value("notion_api_token"),
                "url": "https://api.notion.com/v1",
                "service_name": "notion_service"
            },
            ProjectPlatform.JIRA: {
                "token": get_config_value("jira_api_token"),
                "url": get_config_value("jira_url", "https://sophia-ai.atlassian.net"),
                "service_name": "jira_service"
            },
            ProjectPlatform.GITHUB: {
                "token": get_config_value("github_token"),
                "url": "https://api.github.com",
                "service_name": "github_service"
            },
            ProjectPlatform.CLICKUP: {
                "token": get_config_value("clickup_token"),
                "url": "https://api.clickup.com/api/v2",
                "service_name": "clickup_service"
            }
        }
        
        # Dynamic tool registry - populated from service discovery
        self.dynamic_tools = {}
        
        # Start health monitoring
        asyncio.create_task(self.service_discovery.health_check_services())
        
    async def initialize_services(self):
        """Initialize and register all project management services"""
        # Register known services
        for platform, config in self.platform_configs.items():
            await self.service_discovery.register_service(
                config["service_name"],
                f"http://localhost:{self.config.port + hash(platform.value) % 100}",
                [platform.value, "project_management"]
            )
            
        # Discover additional services
        await self.service_discovery.discover_services()
        
        # Update dynamic tools based on discovered services
        await self.update_dynamic_tools()

    async def update_dynamic_tools(self):
        """Update available tools based on discovered services"""
        self.dynamic_tools = {}
        
        for service_name, service_info in self.service_discovery.service_registry.items():
            capabilities = service_info.get("capabilities", [])
            
            # Generate tools based on capabilities
            if "project_management" in capabilities:
                self.dynamic_tools[f"{service_name}_list_projects"] = {
                    "service": service_name,
                    "endpoint": service_info["endpoint"],
                    "description": f"List projects from {service_name}",
                    "parameters": [
                        ToolParameter(name="limit", type="integer", description="Max projects to return", required=False)
                    ]
                }
                
                self.dynamic_tools[f"{service_name}_create_task"] = {
                    "service": service_name,
                    "endpoint": service_info["endpoint"],
                    "description": f"Create task in {service_name}",
                    "parameters": [
                        ToolParameter(name="title", type="string", description="Task title", required=True),
                        ToolParameter(name="project_id", type="string", description="Project ID", required=True),
                        ToolParameter(name="description", type="string", description="Task description", required=False),
                        ToolParameter(name="assignee", type="string", description="Assignee", required=False),
                        ToolParameter(name="due_date", type="string", description="Due date", required=False)
                    ]
                }

    def get_tool_definitions(self) -> list[ToolDefinition]:
        """Define unified project management tools with dynamic discovery"""
        static_tools = [
            ToolDefinition(
                name="list_projects",
                description="List projects across all platforms with intelligent routing",
                parameters=[
                    ToolParameter(
                        name="platform",
                        type="string",
                        description="Platform to query (asana/linear/notion/jira/github/clickup/all)",
                        required=False,
                    ),
                    ToolParameter(
                        name="limit",
                        type="integer",
                        description="Maximum number of projects to return",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="create_task",
                description="Create a task with intelligent platform routing",
                parameters=[
                    ToolParameter(
                        name="platform",
                        type="string",
                        description="Platform to create task on",
                        required=True,
                    ),
                    ToolParameter(
                        name="title",
                        type="string",
                        description="Task title",
                        required=True,
                    ),
                    ToolParameter(
                        name="project_id",
                        type="string",
                        description="Project ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="description",
                        type="string",
                        description="Task description",
                        required=False,
                    ),
                    ToolParameter(
                        name="assignee",
                        type="string",
                        description="Task assignee",
                        required=False,
                    ),
                    ToolParameter(
                        name="due_date",
                        type="string",
                        description="Due date (YYYY-MM-DD)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="intelligent_route",
                description="Intelligently route requests to best available service",
                parameters=[
                    ToolParameter(
                        name="query",
                        type="string",
                        description="Natural language query to route",
                        required=True,
                    ),
                    ToolParameter(
                        name="context",
                        type="string",
                        description="Additional context for routing decision",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="service_health",
                description="Get health status of all registered services",
                parameters=[],
            ),
        ]
        
        # Add dynamic tools
        dynamic_tools = [
            ToolDefinition(
                name=tool_name,
                description=tool_info["description"],
                parameters=tool_info["parameters"],
            )
            for tool_name, tool_info in self.dynamic_tools.items()
        ]
        
        return static_tools + dynamic_tools

    async def handle_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Handle tool calls with dynamic routing"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Route to appropriate handler
            if tool_name == "list_projects":
                result = await self._intelligent_list_projects(**arguments)
            elif tool_name == "create_task":
                result = await self._intelligent_create_task(**arguments)
            elif tool_name == "intelligent_route":
                result = await self._intelligent_route(**arguments)
            elif tool_name == "service_health":
                result = await self._get_service_health()
            elif tool_name in self.dynamic_tools:
                result = await self._route_to_service(tool_name, arguments)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
                
            # Record metrics
            platform = arguments.get("platform", "unknown")
            route_counter.labels(platform=platform, tool=tool_name).inc()
            
            return result
            
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {"error": str(e)}
        finally:
            # Record latency
            latency = asyncio.get_event_loop().time() - start_time
            platform = arguments.get("platform", "unknown")
            route_latency.labels(platform=platform, tool=tool_name).observe(latency)

    async def _intelligent_list_projects(self, platform: Optional[str] = "all", limit: Optional[int] = 10) -> dict[str, Any]:
        """Intelligently list projects with service routing"""
        if platform == "all":
            # Get from all healthy services
            all_projects = []
            for service_name, healthy in self.service_discovery.health_status.items():
                if healthy and service_name in self.service_discovery.service_registry:
                    try:
                        service_projects = await self._get_projects_from_service(service_name, limit)
                        all_projects.extend(service_projects)
                    except Exception as e:
                        logger.warning(f"Failed to get projects from {service_name}: {e}")
            
            return {
                "projects": all_projects[:limit] if limit else all_projects,
                "total": len(all_projects),
                "sources": list(self.service_discovery.health_status.keys())
            }
        else:
            # Get from specific platform
            service_name = self.platform_configs.get(ProjectPlatform(platform), {}).get("service_name")
            if service_name and self.service_discovery.health_status.get(service_name, False):
                projects = await self._get_projects_from_service(service_name, limit)
                return {
                    "projects": projects,
                    "total": len(projects),
                    "platform": platform
                }
            else:
                return {
                    "error": f"Service {service_name} not available",
                    "platform": platform
                }

    async def _intelligent_create_task(self, platform: str, title: str, project_id: str, **kwargs) -> dict[str, Any]:
        """Intelligently create task with service routing"""
        service_name = self.platform_configs.get(ProjectPlatform(platform), {}).get("service_name")
        
        if service_name and self.service_discovery.health_status.get(service_name, False):
            return await self._create_task_in_service(service_name, title, project_id, **kwargs)
        else:
            return {
                "error": f"Service {service_name} not available",
                "platform": platform
            }

    async def _intelligent_route(self, query: str, context: Optional[str] = None) -> dict[str, Any]:
        """Intelligently route natural language queries to best service"""
        # Simple routing logic - can be enhanced with ML
        query_lower = query.lower()
        
        # Platform detection
        if "asana" in query_lower:
            platform = ProjectPlatform.ASANA
        elif "linear" in query_lower:
            platform = ProjectPlatform.LINEAR
        elif "notion" in query_lower:
            platform = ProjectPlatform.NOTION
        elif "jira" in query_lower:
            platform = ProjectPlatform.JIRA
        elif "github" in query_lower:
            platform = ProjectPlatform.GITHUB
        elif "clickup" in query_lower:
            platform = ProjectPlatform.CLICKUP
        else:
            # Default to healthiest service
            healthy_services = [
                name for name, healthy in self.service_discovery.health_status.items()
                if healthy
            ]
            if healthy_services:
                platform = None
                service_name = healthy_services[0]
            else:
                return {"error": "No healthy services available"}
        
        # Action detection
        if "create" in query_lower or "add" in query_lower:
            action = "create_task"
        elif "list" in query_lower or "show" in query_lower:
            action = "list_projects"
        else:
            action = "list_projects"  # Default
        
        # Route to appropriate service
        if platform:
            service_name = self.platform_configs[platform]["service_name"]
        
        return {
            "routing_decision": {
                "query": query,
                "detected_platform": platform.value if platform else "auto",
                "service": service_name,
                "action": action,
                "confidence": 0.8  # Placeholder - enhance with ML
            },
            "service_health": self.service_discovery.health_status.get(service_name, False)
        }

    async def _get_service_health(self) -> dict[str, Any]:
        """Get health status of all services"""
        return {
            "services": dict(self.service_discovery.health_status),
            "healthy_count": sum(1 for healthy in self.service_discovery.health_status.values() if healthy),
            "total_count": len(self.service_discovery.health_status),
            "registry": self.service_discovery.service_registry
        }

    async def _route_to_service(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Route dynamic tool calls to appropriate service"""
        tool_info = self.dynamic_tools[tool_name]
        tool_info["service"]
        endpoint = tool_info["endpoint"]
        
        # Make HTTP request to service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{endpoint}/tool/{tool_name}",
                json=arguments,
                timeout=30.0
            )
            return response.json()

    async def _get_projects_from_service(self, service_name: str, limit: int) -> List[dict]:
        """Get projects from a specific service"""
        # Placeholder - implement actual service calls
        service_info = self.service_discovery.service_registry.get(service_name, {})
        endpoint = service_info.get("endpoint", "")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{endpoint}/projects?limit={limit}",
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json().get("projects", [])
        except Exception as e:
            logger.error(f"Failed to get projects from {service_name}: {e}")
        
        return []

    async def _create_task_in_service(self, service_name: str, title: str, project_id: str, **kwargs) -> dict[str, Any]:
        """Create task in a specific service"""
        service_info = self.service_discovery.service_registry.get(service_name, {})
        endpoint = service_info.get("endpoint", "")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{endpoint}/tasks",
                    json={
                        "title": title,
                        "project_id": project_id,
                        **kwargs
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Failed to create task in {service_name}: {e}")
        
        return {"error": f"Failed to create task in {service_name}"}

if __name__ == "__main__":
    server = UnifiedProjectMCPServer()
    asyncio.run(server.initialize_services())
    server.run() 