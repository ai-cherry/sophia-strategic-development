# Official MCP Servers Documentation

## Overview

Sophia AI leverages official Model Context Protocol (MCP) servers alongside custom implementations to provide a comprehensive, enterprise-grade AI orchestration platform. This document details the official MCP servers, their integration, and the v2 registry system.

## MCP Registry v2

### YAML Configuration

The MCP server configuration is maintained in `config/mcp/mcp_servers.yaml`:

```yaml
servers:
  - name: modern_stack-official
    type: modern_stack
    tier: PRIMARY
    port: 9130
    capabilities: [ANALYTICS, EMBEDDING, SEARCH, COMPLETION]
    pat_secret: modern_stack_MCP_PAT_PROD
    health_endpoint: /health
    config:
      warehouse: SOPHIA_AI_WH
      database: SOPHIA_AI
      schema: PROCESSED_AI
```

### Tier System

MCP servers are organized into three tiers based on criticality:

| Tier | Description | SLA | Examples |
|------|-------------|-----|----------|
| PRIMARY | Mission-critical servers | 99.9% uptime | Modern Stack, Redis, AI Memory |
| SECONDARY | Important but not critical | 99% uptime | GitHub, Linear, Codacy |
| TERTIARY | Optional enhancements | Best effort | n8n, Notion, v0dev |

### Capability Mapping

Servers declare capabilities for intelligent routing:

```yaml
capabilities:
  ANALYTICS: Data analysis and querying
  EMBEDDING: Vector embedding generation
  SEARCH: Semantic or keyword search
  COMPLETION: Text generation
  CACHE: Data caching
  PUBSUB: Pub/sub messaging
  MEMORY: Persistent memory storage
  CRM: Customer relationship management
  WORKFLOW: Workflow automation
```

## Official MCP Servers

### 1. Modern Stack MCP Server

**Repository**: modern_stack-labs/modern_stack-mcp
**Tier**: PRIMARY
**Port**: 9130

**Features**:
- Cortex Search integration
- Cortex Analyst (natural language to SQL)
- Cortex Complete (text generation)
- PAT-based authentication

**Configuration**:
```yaml
config:
  warehouse: SOPHIA_AI_WH
  database: SOPHIA_AI
  schema: PROCESSED_AI
  pat_secret: modern_stack_MCP_PAT_PROD
```

### 2. Redis MCP Server

**Repository**: redis/mcp-redis
**Tier**: PRIMARY
**Port**: 9120

**Features**:
- Key-value caching
- Pub/sub messaging
- Session management
- Distributed locks

**Configuration**:
```yaml
config:
  max_connections: 100
  ttl_default: 3600
  persistence: true
```

### 3. Pulumi MCP Server

**Repository**: pulumi/mcp-server
**Tier**: SECONDARY
**Port**: 9140

**Features**:
- Infrastructure as Code operations
- Stack management
- Secret retrieval
- Preview and deployment

**Configuration**:
```yaml
config:
  organization: scoobyjava-org
  stack: sophia-ai-production
  backend: s3://pulumi-state-sophia
```

### 4. Estuary Flow MCP Server

**Repository**: estuary/flow-mcp
**Tier**: SECONDARY
**Port**: 9160

**Features**:
- Real-time data streaming
- CDC (Change Data Capture)
- ETL pipeline management
- Data quality monitoring

**Configuration**:
```yaml
config:
  tenant: Pay_Ready
  endpoint: https://api.estuary.dev
```

### 5. n8n MCP Server

**Repository**: n8n-io/n8n-mcp
**Tier**: TERTIARY
**Port**: 9180

**Features**:
- Workflow automation
- Multi-system integration
- Event-driven execution
- Visual workflow design

## Integration Patterns

### 1. Direct Integration

```python
from infrastructure.mcp_servers.registry_v2 import get_registry

registry = get_registry()
modern_stack_server = registry.get_server("modern_stack-official")

# Use server directly
client = MCPClient(modern_stack_server.url, modern_stack_server.pat_token)
```

### 2. Capability-Based Discovery

```python
# Find best server for analytics
analytics_server = registry.get_primary_server_for_capability("ANALYTICS")

# Find all servers that can do embeddings
embedding_servers = registry.get_servers_by_capability("EMBEDDING")
```

### 3. Tier-Based Failover

```python
# Get servers by tier for failover
primary_servers = registry.get_servers_by_tier(Tier.PRIMARY)
secondary_servers = registry.get_servers_by_tier(Tier.SECONDARY)

# Implement failover logic
for server in primary_servers + secondary_servers:
    if server.status == ServerStatus.HEALTHY:
        return server
```

## Health Monitoring

### Automatic Health Checks

The registry performs health checks every 30 seconds:

```python
# Health check configuration
global:
  health_check_interval: 30
  timeout: 10
  retry_attempts: 3
  circuit_breaker:
    failure_threshold: 5
    recovery_timeout: 60
```

### Manual Health Check

```python
# Check individual server
healthy = await registry.check_server_health(server)

# Check all servers
health_status = await registry.check_all_health()
```

## Authentication

### PAT-Based Authentication

Official MCP servers use Programmatic Access Tokens (PAT):

1. **Modern Stack PAT**: For Cortex operations
2. **Pulumi PAT**: For infrastructure operations
3. **Estuary PAT**: For data pipeline management

### Secret Management

PATs are stored in GitHub Organization Secrets and synced to Pulumi ESC:

```yaml
# GitHub Secret → Pulumi ESC Mapping
modern_stack_MCP_PAT_PROD → modern_stack_mcp_pat
PULUMI_MCP_PAT_PROD → pulumi_mcp_pat
ESTUARY_MCP_PAT_PROD → estuary_mcp_pat
```

## Performance Optimization

### 1. Connection Pooling

Each MCP server maintains connection pools:
- Minimum connections: 2
- Maximum connections: 10
- Idle timeout: 300s

### 2. Request Caching

Results are cached in Redis:
- Default TTL: 3600s
- Cache key: SHA256(request_params)
- Hit rate target: >80%

### 3. Load Balancing

Multiple instances of critical servers:
- Round-robin distribution
- Health-based routing
- Automatic failover

## Monitoring and Metrics

### Prometheus Metrics

```python
# Server availability
mcp_registry_server_health{name="...", tier="..."}

# Request metrics
mcp_registry_lookups_total{capability="...", tier="..."}

# Error tracking
mcp_registry_errors_total{operation="...", error_type="..."}
```

### Grafana Dashboards

- MCP Server Health Overview
- Capability Usage Statistics
- Tier Performance Metrics
- Error Rate Tracking

## Migration from v1

### Code Changes

```python
# Old (v1)
from infrastructure.mcp_servers.mcp_registry import MCPRegistry
registry = MCPRegistry()
server = registry.get_server_config("modern_stack")

# New (v2)
from infrastructure.mcp_servers.registry_v2 import get_registry
registry = get_registry()
server = registry.get_server("modern_stack-official")
```

### Configuration Migration

1. Run migration script: `python scripts/migration/migrate_mcp_registry.py`
2. Review YAML configuration
3. Update code imports
4. Test health checks

## Best Practices

1. **Use PRIMARY servers** for critical operations
2. **Implement failover** for high availability
3. **Monitor health metrics** continuously
4. **Cache responses** when appropriate
5. **Rotate PATs** every 90 days

## Troubleshooting

### Common Issues

1. **Server Unhealthy**
   - Check network connectivity
   - Verify PAT token validity
   - Review server logs

2. **Capability Not Found**
   - Ensure server is registered
   - Check capability spelling
   - Verify server health

3. **Performance Issues**
   - Monitor connection pool usage
   - Check cache hit rates
   - Review request patterns

### Debug Commands

```bash
# Check registry status
curl http://localhost:9090/api/mcp/registry/status

# Force health check
curl -X POST http://localhost:9090/api/mcp/registry/health-check

# View server details
curl http://localhost:9090/api/mcp/servers/modern_stack-official
```

## Future Enhancements

1. **Dynamic Server Discovery**: Automatic registration of new servers
2. **Advanced Load Balancing**: ML-based request routing
3. **Multi-Region Support**: Geographic server distribution
4. **Enhanced Security**: mTLS for all communications
5. **GraphQL Interface**: Unified query interface for all servers
