"""
MCP Proxy Routes for Sophia AI
==============================
Intelligent proxy layer for routing requests to distributed MCP services
across 5 Lambda Labs instances using production infrastructure configuration.
"""

import aiohttp
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import json

# Import production infrastructure config
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from infrastructure.config.production import PRODUCTION_INFRASTRUCTURE, get_all_service_endpoints

logger = logging.getLogger(__name__)

router = APIRouter()

# MCP Service Mapping - Based on Production Infrastructure
MCP_SERVICE_ENDPOINTS = get_all_service_endpoints()

class MCPProxyService:
    """Intelligent proxy for MCP service orchestration"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.service_health = {}
        
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def proxy_request(self, service_name: str, endpoint: str, 
                          method: str = "GET", data: Any = None, 
                          headers: Dict = None) -> Dict[str, Any]:
        """Proxy request to specific MCP service"""
        
        if service_name not in MCP_SERVICE_ENDPOINTS:
            raise HTTPException(
                status_code=404, 
                detail=f"MCP service '{service_name}' not found. Available: {list(MCP_SERVICE_ENDPOINTS.keys())}"
            )
        
        base_url = MCP_SERVICE_ENDPOINTS[service_name]
        target_url = f"{base_url}/{endpoint.lstrip('/')}"
        
        session = await self.get_session()
        
        try:
            # Prepare request
            request_kwargs = {
                "url": target_url,
                "headers": headers or {}
            }
            
            if data is not None:
                if isinstance(data, dict):
                    request_kwargs["json"] = data
                    request_kwargs["headers"]["Content-Type"] = "application/json"
                else:
                    request_kwargs["data"] = data
            
            logger.info(f"🔄 Proxying {method} request to {service_name}: {target_url}")
            
            # Make request
            async with session.request(method, **request_kwargs) as response:
                response_data = await response.text()
                
                # Try to parse as JSON
                try:
                    response_json = json.loads(response_data)
                except json.JSONDecodeError:
                    response_json = {"raw_response": response_data}
                
                if response.status >= 400:
                    logger.error(f"❌ MCP service {service_name} error: {response.status} - {response_data}")
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"MCP service error: {response_data}"
                    )
                
                logger.info(f"✅ Successfully proxied to {service_name}")
                return response_json
                
        except aiohttp.ClientError as e:
            logger.error(f"❌ Connection error to {service_name}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Unable to connect to MCP service '{service_name}': {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error proxying to {service_name}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal proxy error: {str(e)}"
            )
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of specific MCP service"""
        try:
            response = await self.proxy_request(service_name, "health", "GET")
            self.service_health[service_name] = {
                "status": "healthy",
                "last_check": "now",
                "response": response
            }
            return response
        except Exception as e:
            self.service_health[service_name] = {
                "status": "unhealthy", 
                "last_check": "now",
                "error": str(e)
            }
            raise

# Global proxy service instance
mcp_proxy = MCPProxyService()

# Routes

@router.get("/api/v4/mcp/services")
async def list_mcp_services():
    """List all available MCP services with their endpoints"""
    services = {}
    for service_name, endpoint in MCP_SERVICE_ENDPOINTS.items():
        instance_name, instance_config = None, None
        
        # Find which instance hosts this service
        for inst_name, inst_config in PRODUCTION_INFRASTRUCTURE.instances.items():
            if any(service_name.startswith(svc) for svc in inst_config.services):
                instance_name = inst_name
                instance_config = inst_config
                break
        
        services[service_name] = {
            "endpoint": endpoint,
            "instance": instance_name,
            "instance_ip": instance_config.ip if instance_config else "unknown",
            "instance_role": instance_config.role if instance_config else "unknown"
        }
    
    return {
        "services": services,
        "total_count": len(services),
        "infrastructure": {
            "total_instances": len(PRODUCTION_INFRASTRUCTURE.instances),
            "nginx_primary": PRODUCTION_INFRASTRUCTURE.nginx_primary
        }
    }

@router.get("/api/v4/mcp/{service_name}/health")
async def check_mcp_service_health(service_name: str):
    """Check health of specific MCP service"""
    try:
        health_data = await mcp_proxy.check_service_health(service_name)
        return {
            "service": service_name,
            "status": "healthy",
            "health_data": health_data,
            "endpoint": MCP_SERVICE_ENDPOINTS.get(service_name)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/api/v4/mcp/health/all")
async def check_all_mcp_services_health():
    """Check health of all MCP services"""
    health_results = {}
    
    # Check all services in parallel
    tasks = []
    for service_name in MCP_SERVICE_ENDPOINTS.keys():
        task = mcp_proxy.check_service_health(service_name)
        tasks.append((service_name, task))
    
    # Gather results
    for service_name, task in tasks:
        try:
            health_data = await task
            health_results[service_name] = {
                "status": "healthy",
                "data": health_data
            }
        except Exception as e:
            health_results[service_name] = {
                "status": "unhealthy",
                "error": str(e)
            }
    
    # Calculate overall health
    total_services = len(health_results)
    healthy_services = sum(1 for result in health_results.values() if result["status"] == "healthy")
    health_rate = (healthy_services / total_services) * 100 if total_services > 0 else 0
    
    return {
        "overall_status": "healthy" if health_rate >= 80 else "degraded",
        "health_rate": round(health_rate, 1),
        "healthy_services": healthy_services,
        "total_services": total_services,
        "services": health_results
    }

@router.api_route("/api/v4/mcp/{service_name}/{endpoint:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_mcp_service(service_name: str, endpoint: str, request: Request):
    """Generic proxy endpoint for all MCP service requests"""
    
    # Get request data
    try:
        if request.method in ["POST", "PUT", "PATCH"]:
            request_data = await request.json()
        else:
            request_data = None
    except:
        request_data = None
    
    # Get headers (exclude host and other proxy-specific headers)
    headers = dict(request.headers)
    excluded_headers = ["host", "content-length", "transfer-encoding"]
    headers = {k: v for k, v in headers.items() if k.lower() not in excluded_headers}
    
    try:
        response_data = await mcp_proxy.proxy_request(
            service_name=service_name,
            endpoint=endpoint,
            method=request.method,
            data=request_data,
            headers=headers
        )
        
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Proxy error for {service_name}/{endpoint}: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

# Business Logic Routes (shortcuts for common operations)

@router.get("/api/v4/mcp/linear/projects")
async def get_linear_projects():
    """Get Linear projects (shortcut route)"""
    return await mcp_proxy.proxy_request("linear_mcp", "projects")

@router.get("/api/v4/mcp/asana/projects")
async def get_asana_projects():
    """Get Asana projects (shortcut route)"""
    return await mcp_proxy.proxy_request("asana_mcp", "projects")

@router.get("/api/v4/mcp/gong/calls/recent")
async def get_recent_gong_calls():
    """Get recent Gong calls (shortcut route)"""
    return await mcp_proxy.proxy_request("gong_mcp", "calls/recent")

@router.get("/api/v4/mcp/hubspot/contacts")
async def get_hubspot_contacts():
    """Get HubSpot contacts (shortcut route)"""
    return await mcp_proxy.proxy_request("hubspot_mcp", "contacts")

@router.get("/api/v4/mcp/github/repositories")
async def get_github_repositories():
    """Get GitHub repositories (shortcut route)"""
    return await mcp_proxy.proxy_request("github_mcp", "repositories")

@router.get("/api/v4/mcp/slack/channels")
async def get_slack_channels():
    """Get Slack channels (shortcut route)"""
    return await mcp_proxy.proxy_request("slack_mcp", "channels")

# Cleanup on shutdown
@router.on_event("shutdown")
async def shutdown_mcp_proxy():
    """Cleanup MCP proxy resources"""
    await mcp_proxy.close_session()
    logger.info("🛑 MCP Proxy service shutdown complete") 