"""A generic client for interacting with any Model Context Protocol (MCP) server."""

import logging
from typing import Any, Dict, Optional

import aiohttp

logger = logging.getLogger(__name__)

# The definitive service discovery gateway for the Sophia AI Platform.
MCP_GATEWAY_ENDPOINTS = {
    # Core Business Operations
    "gong": "http://gong-mcp-service.mcp-servers.svc.cluster.local:9000",
    "hubspot": "http://hubspot-mcp-service.mcp-servers.svc.cluster.local:9000",
    "snowflake": "http://snowflake-mcp-service.mcp-servers.svc.cluster.local:9000",
    "apollo": "http://apollo-io-mcp-service.mcp-servers.svc.cluster.local:9000",
    "looker": "https://zapier.com/mcp/looker",  # Accessed via Zapier webhook
    # Content & Knowledge Management
    "notion": "http://notion-mcp-service.mcp-servers.svc.cluster.local:9000",
    "slidespeak": "http://slidespeak-mcp-service.mcp-servers.svc.cluster.local:9000",
    "cognee": "http://cognee-local-service:7777",  # For local dev via Cline
    # Project & Team Management
    "slack": "http://slack-mcp-service.mcp-servers.svc.cluster.local:9000",
    "asana": "http://asana-mcp-service.mcp-servers.svc.cluster.local:9000",
    "linear": "http://linear-mcp-service.mcp-servers.svc.cluster.local:9000",
    "github": "http://github-mcp-service.mcp-servers.svc.cluster.local:9000",
    # Infrastructure & Code Intelligence
    "pulumi": "http://pulumi-mcp-service.mcp-servers.svc.cluster.local:9000",
    "kubernetes": "http://k8s-mcp-service.mcp-servers.svc.cluster.local:9000",
    "consult7": "http://consult7-mcp-service.mcp-servers.svc.cluster.local:9000",
    "llama": "http://llama-mcp-service.mcp-servers.svc.cluster.local:9000",
    # Web Search & Automation
    "apify": "http://apify-mcp-service.mcp-servers.svc.cluster.local:9000",
    "exa": "http://exa-mcp-service.mcp-servers.svc.cluster.local:9000",
    "serpapi": "http://serpapi-mcp-service.mcp-servers.svc.cluster.local:9000",
    "playwright": "http://playwright-mcp-service.mcp-servers.svc.cluster.local:9000",
    "zenrows": "https://mcp.pipedream.com/app/zenrows",  # Accessed via Pipedream webhook
    "pipedream": "https://mcp.pipedream.com/app/pipedream",  # Generic
    "zapier": "https://zapier.com/mcp/zapier",  # Generic
    "n8n": "https://n8n.io/mcp",  # Generic
}


class MCPClient:
    """A single client to rule them all. An agent uses this client to talk.

    to any MCP-compliant server via the gateway.
    """
    async def get_context(
        self, service_name: str, request: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Sends a request to a specified MCP server to get context.

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
