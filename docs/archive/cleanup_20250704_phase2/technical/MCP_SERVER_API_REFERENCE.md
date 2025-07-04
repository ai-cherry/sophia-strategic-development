---
title: Sophia AI - MCP Server API Reference
description: This document lists the core HTTP endpoints exposed by an MCP server. Endpoints are secured with JWT authentication loaded automatically from Pulumi ESC.
tags: mcp, security, gong, monitoring, docker
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Sophia AI - MCP Server API Reference


## Table of Contents

- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Tool Invocation Example](#tool-invocation-example)
  - [Resource Query Example](#resource-query-example)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

This document lists the core HTTP endpoints exposed by an MCP server. Endpoints are secured with JWT authentication loaded automatically from Pulumi ESC.

## Base URL

```python
# Example usage:
python
```python

## Endpoints

| Method | Endpoint | Description |
|-------|----------|-------------|
| `GET` | `/health` | Server health check |
| `POST` | `/auth/token` | Obtain JWT token |
| `POST` | `/tools/<name>` | Execute a registered tool |
| `POST` | `/resources/<name>` | Access a resource or query data |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/docs` | Interactive API docs |

### Tool Invocation Example

```bash
# Example usage:
bash
```python

### Resource Query Example

```bash
curl -X POST http://localhost:8002/resources/hubspot_contacts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"email": "customer@example.com"}'
```python

## Troubleshooting

- **401 Unauthorized** – verify the JWT token from `/auth/token` and ensure the MCP server can access Pulumi ESC.
- **404 Not Found** – confirm the tool or resource name exists in `mcp_config.json` and the corresponding module is loaded.
- **Server Unreachable** – check container logs with `docker-compose -f docker-compose.mcp.yml logs <service>` and restart if necessary.

## Maintenance

1. Update the `mcp_config.json` file when adding tools or resources.
2. Restart the MCP container to apply configuration changes:
   ```bash
   docker-compose -f docker-compose.mcp.yml restart <service>
   ```python
3. Review `/metrics` regularly to monitor usage and performance.
