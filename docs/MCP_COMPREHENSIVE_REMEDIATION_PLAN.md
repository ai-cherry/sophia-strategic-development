# MCP Server Comprehensive Remediation Plan

## Executive Summary

The MCP server infrastructure has critical issues preventing proper operation:
- **Fatal Import Error**: Snowflake Admin server has broken syntax
- **Configuration Chaos**: cursor_mcp_config.json has misaligned ports and missing servers
- **Zero Lambda Labs Integration**: No servers configured for 104.171.202.64
- **Architecture Fragmentation**: 4+ competing base classes

## Phase 1: Critical Infrastructure Fixes (Immediate)

### 1.1 Fix Fatal Import Error

**File**: `backend/mcp_servers/snowflake_admin_mcp_server.py`
```python
# BROKEN (Line 16):
from backend.mcp_servers.base.standardized_mcp_server from backend.mcp_servers.base.standardized_mcp_server import StandardizedMCPServer

# FIXED:
from backend.mcp_servers.base.standardized_mcp_server import StandardizedMCPServer
```

### 1.2 Standardize MCP Configuration

**Issues in cursor_enhanced_mcp_config.json**:
- Missing critical servers (snowflake_admin, linear, github)
- Port misalignments (ai_memory shows 9000 but runs on 9001)
- Inconsistent command formats
- No Lambda Labs endpoints

### 1.3 Create Lambda Labs Configuration

All servers need Lambda Labs integration:
```json
{
  "lambda_labs_endpoint": "http://104.171.202.64:PORT",
  "docker_swarm_mode": true,
  "health_check_endpoint": "/health"
}
```

## Phase 2: Architecture Consolidation

### 2.1 Unified Base Class

Migrate all servers to single base class:
```python
from backend.mcp_servers.base.unified_mcp_base import UnifiedMCPServer
```

### 2.2 Standardized Health Checks

Every server must implement:
```python
@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": self.name,
        "version": self.version,
        "lambda_labs": self.lambda_labs_connected
    }
```

### 2.3 Environment Configuration

Standardize environment handling:
```python
ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")
LAMBDA_LABS_HOST = os.getenv("LAMBDA_LABS_HOST", "104.171.202.64")
```

## Phase 3: System Integration

### 3.1 Unified Dashboard Integration

Add MCP status display:
```typescript
interface MCPServerStatus {
  name: string;
  port: number;
  status: 'healthy' | 'unhealthy' | 'unknown';
  lastCheck: Date;
  lambdaLabsConnected: boolean;
}
```

### 3.2 Chat Service Enhancement

Enable MCP discovery:
```python
async def discover_mcp_capabilities():
    """Discover all available MCP server capabilities"""
    servers = await registry.get_all_mcp_servers()
    return {
        server.name: await server.list_tools()
        for server in servers
    }
```

### 3.3 FastAPI Route Standardization

All servers must expose:
- `/health` - Health check
- `/tools` - List available tools
- `/execute` - Execute tool
- `/status` - Server status

## Phase 4: Testing & Validation

### 4.1 Server Startup Tests

```python
async def test_all_servers_startup():
    """Test that all MCP servers start successfully"""
    for server in MCP_SERVERS:
        assert await server.start()
        assert await server.health_check()
```

### 4.2 Lambda Labs Connectivity

```python
async def test_lambda_labs_connection():
    """Test Lambda Labs connectivity for all servers"""
    for server in MCP_SERVERS:
        response = await server.connect_lambda_labs()
        assert response.status == "connected"
```

### 4.3 Integration Tests

- Dashboard displays all server statuses
- Chat can discover and use all MCP tools
- FastAPI endpoints are accessible
- Portkey integration works

## Implementation Timeline

**Week 1**: Critical fixes (import errors, configuration)
**Week 2**: Architecture consolidation
**Week 3**: System integration
**Week 4**: Testing and deployment

## Success Metrics

- 100% server startup success
- All servers connected to Lambda Labs
- <200ms health check response
- Zero configuration conflicts
- Complete dashboard integration
