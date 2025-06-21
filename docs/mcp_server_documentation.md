# SOPHIA AI System - MCP Server Documentation

## Overview

The Model Context Protocol (MCP) server is a critical component of the SOPHIA AI System, providing a standardized way for AI models to access tools and resources. This document outlines the architecture, configuration, and usage of the MCP server in SOPHIA.

## 🔐 **PERMANENT SECRET MANAGEMENT INTEGRATION**

**IMPORTANT**: SOPHIA AI MCP servers now use the **PERMANENT GitHub Organization Secrets → Pulumi ESC** solution for all authentication and configuration. No manual secret management is required.

### **Automatic Secret Loading**
```python
# MCP servers automatically load secrets from Pulumi ESC
from backend.core.auto_esc_config import config

# All API keys are automatically available
openai_key = config.openai_api_key
gong_key = config.gong_access_key
```

### **Configuration Source Priority**
1. **Pulumi ESC** (Primary) - Automatic loading from `scoobyjava-org/default/sophia-ai-production`
2. **Environment Variables** (Fallback) - For local development
3. **Never hardcoded** - All credentials managed centrally

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Configuration](#configuration)
4. [Tools](#tools)
5. [Resources](#resources)
6. [Authentication](#authentication)
7. [Rate Limiting](#rate-limiting)
8. [Monitoring](#monitoring)
9. [Development Guide](#development-guide)
10. [Troubleshooting](#troubleshooting)

## Introduction

The Model Context Protocol (MCP) is a standardized protocol for AI models to access external tools and resources. In SOPHIA, the MCP server acts as a bridge between AI models and various business systems, allowing models to:

- Execute specialized tools for data analysis
- Access structured resources from business systems
- Maintain consistent interfaces across different AI providers
- Ensure security and compliance with business rules

## Architecture

The MCP server in SOPHIA follows a modular architecture:

```
backend/mcp/
├── server.py                # Main server implementation
├── resource_orchestrator.py # Manages resource access
├── tool_orchestrator.py     # Manages tool execution
├── auto_esc_config.py       # Automatic ESC integration (NEW)
├── auth/                    # Authentication modules
├── tools/                   # Tool implementations
│   ├── gong_tools.py        # Gong.io integration tools
│   ├── vector_tools.py      # Vector database tools
│   ├── crm_tools.py         # CRM integration tools
│   └── ...
└── resources/               # Resource implementations
    ├── gong_resources.py    # Gong.io resources
    ├── crm_resources.py     # CRM resources
    └── ...
```

### Key Components

1. **Server**: The main MCP server that handles requests, authentication, and routing.
2. **Tool Orchestrator**: Manages tool registration, validation, and execution.
3. **Resource Orchestrator**: Manages resource registration, access, and caching.
4. **Auto ESC Config**: Automatically loads configuration from Pulumi ESC (NEW)
5. **Tools**: Implementations of specific tools that models can use.
6. **Resources**: Implementations of specific resources that models can access.

## Configuration

### **Automatic Configuration (Recommended)**

MCP servers automatically load configuration from Pulumi ESC:

```python
# backend/mcp/base_mcp_server.py
from backend.core.auto_esc_config import config

class BaseMCPServer:
    def __init__(self):
        # Secrets automatically loaded from ESC
        self.openai_key = config.openai_api_key
        self.gong_key = config.gong_access_key
        # ... all other secrets available automatically
```

### **Manual Configuration (Legacy)**

The MCP server can also be configured using the `mcp_config.json` file at the root of the project. This file defines:

- Server configuration (host, port, etc.)
- Available tools and their configurations
- Available resources and their configurations
- Authentication settings
- Rate limiting rules
- Monitoring settings

Example configuration with ESC integration:

```json
{
  "server_name": "sophia-mcp-server",
  "version": "1.0.0",
  "description": "SOPHIA AI MCP Server for PayReady",
  "host": "0.0.0.0",
  "port": 8002,
  "log_level": "INFO",
  "cors_origins": ["*"],
  "auth": {
    "enabled": true,
    "jwt_secret": "${JWT_SECRET}",
    "jwt_algorithm": "HS256",
    "token_expiration": 86400
  },
  "tools": [
    {
      "name": "gong_tools",
      "module": "backend.mcp.tools.gong_tools",
      "enabled": true,
      "functions": [
        "gong_call_analysis",
        "gong_transcript_extraction"
      ]
    }
  ],
  "resources": [
    {
      "name": "crm_resources",
      "module": "backend.mcp.resources.crm_resources",
      "enabled": true,
      "resources": [
        "hubspot_contacts",
        "hubspot_companies"
      ]
    }
  ]
}
```

### **Environment Variables (Automatic)**

With the permanent solution, environment variables are automatically set from Pulumi ESC:

```bash
# These are automatically available (no manual setup required)
export OPENAI_API_KEY=${sophia.ai.openai.api_key}
export GONG_ACCESS_KEY=${sophia.business.gong.access_key}
export GONG_CLIENT_SECRET=${sophia.business.gong.client_secret}
export HUBSPOT_API_TOKEN=${sophia.business.hubspot.api_token}
export SLACK_BOT_TOKEN=${sophia.business.slack.bot_token}
export SNOWFLAKE_PASSWORD=${sophia.data.snowflake.password}
export PINECONE_API_KEY=${sophia.data.pinecone.api_key}
# ... all other secrets automatically available
```

## Tools

Tools are functions that models can execute to perform specific tasks. Each tool has:

- A unique name
- Input schema (parameters)
- Output schema (return value)
- Implementation logic

### Tool Definition with Automatic Secret Access

Tools now automatically access secrets through the ESC integration:

```python
from typing import Dict, List, Optional
from backend.core.auto_esc_config import config

async def gong_call_analysis(call_id: str) -> Dict[str, any]:
    """
    Analyze a Gong call using the Gong API.

    Args:
        call_id: The ID of the call to analyze

    Returns:
        Analysis results
    """
    # Automatically uses secrets from ESC
    gong_client = GongClient(
        access_key=config.gong_access_key,
        client_secret=config.gong_client_secret
    )

    # Implementation logic here
    return analysis_results
```

### Tool Registration

Tools are automatically registered with the MCP server based on the configuration in `mcp_config.json`. The server scans the specified modules and registers tools that match the names in the configuration.

### Tool Usage

Models can execute tools by sending a request to the MCP server with:

- The tool name
- Input parameters

Example request:

```json
{
  "tool_name": "gong_call_analysis",
  "parameters": {
    "call_id": "12345"
  }
}
```

## Resources

Resources are structured data that models can access. Each resource has:

- A unique URI
- Input schema (query parameters)
- Output schema (return value)
- Implementation logic

### Resource Definition with Automatic Secret Access

```python
from typing import Dict, List, Optional
from backend.core.auto_esc_config import config
from backend.mcp.resource import Resource, ResourceRequest

class HubspotContactsResource(Resource):
    """
    Resource for accessing HubSpot contacts.
    """

    def __init__(self, config_dict: Dict[str, any]):
        super().__init__(config_dict)
        # Automatically uses secrets from ESC
        self.hubspot_client = self._create_hubspot_client()

    def _create_hubspot_client(self):
        """Create HubSpot client with automatic secret access"""
        return HubSpotClient(api_token=config.hubspot_api_token)

    async def get(self, request: ResourceRequest) -> Dict[str, any]:
        """
        Get HubSpot contacts based on the request parameters.

        Args:
            request: The resource request

        Returns:
            Contact data
        """
        # Implementation logic here
        return contacts_data
```

### Resource Registration

Resources are automatically registered with the MCP server based on the configuration in `mcp_config.json`. The server scans the specified modules and registers resources that match the names in the configuration.

### Resource Usage

Models can access resources by sending a request to the MCP server with:

- The resource URI
- Optional query parameters

Example request:

```json
{
  "resource_uri": "hubspot_contacts",
  "query_params": {
    "email": "customer@example.com"
  }
}
```

## Authentication

### **Automatic JWT Configuration**

JWT authentication is automatically configured using secrets from Pulumi ESC:

```python
# Automatic JWT configuration
from backend.core.auto_esc_config import config

jwt_config = {
    "enabled": True,
    "jwt_secret": config.jwt_secret,  # Automatically from ESC
    "jwt_algorithm": "HS256",
    "token_expiration": 86400
}
```

### **Manual JWT Configuration (Legacy)**

JWT authentication can also be configured in the `auth` section of `mcp_config.json`:

```json
"auth": {
  "enabled": true,
  "jwt_secret": "${JWT_SECRET}",
  "jwt_algorithm": "HS256",
  "token_expiration": 86400
}
```

### Token Generation

Tokens can be generated using the `/auth/token` endpoint of the MCP server:

```bash
curl -X POST http://localhost:8002/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "model", "password": "password"}'
```

### Token Usage

Include the token in the `Authorization` header of requests:

```bash
curl http://localhost:8002/tools/gong_call_analysis \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"input": {...}}'
```

## Rate Limiting

The MCP server implements rate limiting to prevent abuse and ensure fair usage of resources.

### Rate Limit Configuration

Rate limits are configured in the `rate_limits` section of `mcp_config.json`:

```json
"rate_limits": {
  "enabled": true,
  "default_rate": 100,
  "default_period": 60,
  "per_tool_limits": {
    "web_search": {
      "rate": 10,
      "period": 60
    }
  }
}
```

### Rate Limit Headers

The server includes rate limit headers in responses:

- `X-RateLimit-Limit`: The maximum number of requests allowed in the period
- `X-RateLimit-Remaining`: The number of requests remaining in the current period
- `X-RateLimit-Reset`: The time when the rate limit will reset (Unix timestamp)

## Monitoring

The MCP server includes monitoring capabilities to track usage, performance, and errors.

### Prometheus Metrics

The server exposes Prometheus metrics at the `/metrics` endpoint, including:

- Request counts by tool/resource
- Request durations
- Error counts
- Rate limit hits

### Logging

The server logs events to both console and file, with structured logging in JSON format. Log levels can be configured in `mcp_config.json`.

## Development Guide

### Adding a New Tool with Automatic Secret Access

1. Create a new Python module in `backend/mcp/tools/` or add to an existing module
2. Define the tool function with automatic secret access
3. Add comprehensive docstrings
4. Add the tool to `mcp_config.json`
5. Write tests for the tool

Example:

```python
# backend/mcp/tools/slack_tools.py

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from backend.core.auto_esc_config import config

class SlackMessageInput(BaseModel):
    channel: str = Field(..., description="The Slack channel to send the message to")
    message: str = Field(..., description="The message content")

class SlackMessageOutput(BaseModel):
    success: bool = Field(..., description="Whether the message was sent successfully")
    message_id: str = Field(..., description="The ID of the sent message")

async def send_slack_message(input_data: SlackMessageInput) -> SlackMessageOutput:
    """
    Send a message to a Slack channel.

    Args:
        input_data: The message input data

    Returns:
        The result of sending the message
    """
    # Automatically uses secrets from ESC
    slack_client = SlackClient(token=config.slack_bot_token)

    try:
        response = await slack_client.send_message(
            channel=input_data.channel,
            message=input_data.message
        )

        return SlackMessageOutput(
            success=True,
            message_id=response["message"]["ts"]
        )
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")
        return SlackMessageOutput(
            success=False,
            message_id=""
        )
```

2. Add the tool to `mcp_config.json`:

```json
"tools": [
  {
    "name": "slack_tools",
    "module": "backend.mcp.tools.slack_tools",
    "enabled": true,
    "functions": [
      "send_slack_message"
    ]
  }
]
```

### Adding a New Resource with Automatic Secret Access

1. Create a new Python module in `backend/mcp/resources/` or add to an existing module
2. Define the resource class with automatic secret access
3. Add comprehensive docstrings
4. Add the resource to `mcp_config.json`
5. Write tests for the resource

Example:

```python
# backend/mcp/resources/slack_resources.py

from typing import Dict, List, Optional
from backend.core.auto_esc_config import config
from backend.mcp.resource import Resource, ResourceRequest

class SlackChannelsResource(Resource):
    """
    Resource for accessing Slack channels.
    """

    def __init__(self, config_dict: Dict[str, any]):
        super().__init__(config_dict)
        # Automatically uses secrets from ESC
        self.slack_client = SlackClient(token=config.slack_bot_token)

    async def get(self, request: ResourceRequest) -> Dict[str, any]:
        """
        Get Slack channels based on the request parameters.

        Args:
            request: The resource request

        Returns:
            Channel data
        """
        try:
            channels = await self.slack_client.list_channels()

            # Filter channels based on query parameters
            if request.query_params.get("name"):
                channels = [
                    channel for channel in channels
                    if request.query_params["name"] in channel["name"]
                ]

            return {
                "channels": channels,
                "count": len(channels)
            }
        except Exception as e:
            logger.error(f"Failed to get Slack channels: {e}")
            return {"channels": [], "count": 0, "error": str(e)}
```

2. Add the resource to `mcp_config.json`:

```json
"resources": [
  {
    "name": "slack_resources",
    "module": "backend.mcp.resources.slack_resources",
    "enabled": true,
    "resources": [
      "slack_channels"
    ]
  }
]
```

## Troubleshooting

### Common Issues

#### Tool Not Found

If a tool is not found, check:

1. The tool name in the request matches the function name
2. The tool is listed in `mcp_config.json`
3. The module containing the tool is correctly specified
4. The tool function is properly defined

#### Resource Not Found

If a resource is not found, check:

1. The resource URI in the request matches the resource name
2. The resource is listed in `mcp_config.json`
3. The module containing the resource is correctly specified
4. The resource class is properly defined

#### Authentication Failures

If authentication fails, check:

1. The JWT token is included in the `Authorization` header
2. The token is valid and not expired
3. The JWT secret in the server matches the one used to generate the token
4. **NEW**: Verify Pulumi ESC access with `export PULUMI_ORG=scoobyjava-org && pulumi env ls`

#### Secret Access Issues (NEW)

If secrets are not loading automatically:

1. **Check Pulumi ESC access**:
   ```bash
   export PULUMI_ORG=scoobyjava-org
   pulumi whoami
   pulumi env ls
   ```

2. **Verify ESC environment**:
   ```bash
   pulumi env open scoobyjava-org/default/sophia-ai-production
   ```

3. **Test automatic config loading**:
   ```python
   from backend.core.auto_esc_config import config
   print(config.openai_api_key)  # Should not be None
   ```

4. **Check GitHub organization secrets**: Verify secrets are set at [GitHub ai-cherry org](https://github.com/ai-cherry/settings/secrets/actions)

#### Rate Limit Exceeded

If rate limits are exceeded, check:

1. The rate limit configuration in `mcp_config.json`
2. The client is respecting rate limit headers
3. Consider implementing backoff and retry logic in the client

### Logs

Check the server logs for detailed error information:

```bash
docker-compose logs mcp-server
```

### Health Check

Use the health check endpoint to verify the server is running correctly:

```bash
curl http://localhost:8002/health
```

### Metrics

Check the metrics endpoint for performance and usage information:

```bash
curl http://localhost:8002/metrics
```

## Conclusion

The MCP server is a powerful component of the SOPHIA AI System, enabling AI models to interact with business systems in a standardized, secure, and efficient way. With the new **permanent GitHub organization secrets solution**, MCP servers automatically load all required credentials from Pulumi ESC, eliminating manual secret management and ensuring enterprise-grade security.

By following the guidelines in this documentation, you can extend and customize the MCP server to meet your specific needs while leveraging the automatic secret management capabilities.
