"""
A generic client for interacting with any Model Context Protocol (MCP) server.
"""

import logging
import aiohttp
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# The service discovery gateway, now updated with our new capabilities.
MCP_GATEWAY_ENDPOINTS = {
    # Infrastructure & Ops
    "pulumi": "http://pulumi-mcp-service.mcp-servers.svc.cluster.local:9000",
    "kubernetes": "http://k8s-mcp-service.mcp-servers.svc.cluster.local:9000",
    "github": "http://github-mcp-service.mcp-servers.svc.cluster.local:9000",
    "portkey_admin": "http://portkey-admin-mcp-service.mcp-servers.svc.cluster.local:9000",
    
    # Observability
    "grafana": "http://grafana-mcp-service.mcp-servers.svc.cluster.local:9000",
    
    # Data & Search
    "database": "http://database-mcp-service.mcp-servers.svc.cluster.local:9000",
    "pinecone": "http://pinecone-mcp-service.mcp-servers.svc.cluster.local:9000",
    "tavily": "http://tavily-mcp-service.mcp-servers.svc.cluster.local:9000",

    # Web & Browser
    "playwright": "http://playwright-mcp-service.mcp-servers.svc.cluster.local:9000",
}

class MCPClient:
    """
    A single client to rule them all. An agent uses this client to talk
    to any MCP-compliant server via the gateway.
    """
    async def get_context(
        self, 
        service_name: str, 
        request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sends a request to a specified MCP server to get context.

        :param service_name: The name of the service to contact (e.g., 'kubernetes').
        :param request: The natural language request for the MCP server.
        :param context: Optional dictionary with additional context for the request.
        :return: The structured context response from the MCP server.
        """
        if service_name not in MCP_GATEWAY_ENDPOINTS:
            raise ValueError(f"Service '{service_name}' not found in MCP Gateway.")

        url = MCP_GATEWAY_ENDPOINTS[service_name]
        payload = {
            "request": request,
            "context": context or {},
        }
        
        logger.info(f"Sending MCP request to '{service_name}': '{request}'")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{url}/get_context", json=payload) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                logger.error(f"MCP request to '{service_name}' failed: {e}")
                raise

# Singleton instance for easy use across the application
mcp_client = MCPClient()
