# Sophia AI Integration Plan - July 2025

## Executive Summary

This plan provides a graceful transition from the current Sophia AI platform to an autonomic, event-driven system powered by MCP control plane, Estuary real-time data fabric, and n8n workflow automation.

**Key Principles:**
- Zero downtime during transition
- Incremental rollout with immediate value
- No breaking changes to existing functionality
- Clear migration paths for legacy components

## Current State Assessment

### ✅ What's Working
- Infrastructure setup complete (Snowflake, Lambda Labs, GitHub Actions)
- MCP server framework established
- Unified Memory Service architecture in place
- CI/CD pipelines configured

### 🔧 Immediate Issues to Fix
1. **Snowflake Connection**: Missing user credentials on startup
2. **Python Path Conflicts**: Snowflake connector issues with project imports
3. **Environment Loading**: Services not reading local.env automatically

### 📊 Technical Debt to Address
- Multiple configuration patterns (settings.py, auto_esc_config.py, service_configs.py)
- Duplicate service implementations
- Inconsistent error handling
- Lack of event-driven architecture

## Phase 0: Foundation Fixes (Week 1)

### 0.1 Environment Loading Fix
```python
# backend/core/startup.py
"""Unified startup module for all services"""

import os
from pathlib import Path
from typing import Optional

def load_environment(env_file: str = "local.env") -> bool:
    """Load environment variables from file"""
    env_path = Path(env_file)
    if not env_path.exists():
        return False
    
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    return True

# Call this at the start of every service
load_environment()
```

### 0.2 Configuration Consolidation
```python
# backend/core/unified_config.py
"""Single source of truth for all configuration"""

from typing import Any, Optional
import os
from backend.core.auto_esc_config import get_config_value

class UnifiedConfig:
    """Centralized configuration with clear precedence"""
    
    @staticmethod
    def get(key: str, default: Optional[Any] = None) -> Any:
        """
        Get configuration value with precedence:
        1. Environment variable
        2. Pulumi ESC
        3. Default value
        """
        # Direct env var
        value = os.getenv(key.upper())
        if value is not None:
            return value
        
        # Pulumi ESC
        value = get_config_value(key.lower())
        if value is not None:
            return value
        
        return default
```

### 0.3 Service Health Dashboard
```python
# backend/services/health_monitor.py
"""Unified health monitoring for all services"""

class HealthMonitor:
    async def check_all_services(self) -> dict:
        return {
            "snowflake": await self.check_snowflake(),
            "redis": await self.check_redis(),
            "mcp_servers": await self.check_mcp_servers(),
            "lambda_labs": await self.check_lambda_labs()
        }
```

## Phase 1: Event-Driven Foundation (Week 2-3)

### 1.1 NATS JetStream Deployment
```yaml
# k8s/base/nats-jetstream.yaml
apiVersion: v1
kind: Service
metadata:
  name: nats
  namespace: sophia-ai-prod
spec:
  selector:
    app: nats
  ports:
    - name: client
      port: 4222
    - name: monitor
      port: 8222
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: nats
  namespace: sophia-ai-prod
spec:
  serviceName: nats
  replicas: 3
  template:
    spec:
      containers:
      - name: nats
        image: nats:2.10-alpine
        command:
          - nats-server
          - --cluster_name=sophia-ai
          - --jetstream
          - --store_dir=/data
```

### 1.2 Event Publisher Service
```python
# backend/services/event_publisher.py
"""Unified event publishing service"""

import asyncio
import json
from typing import Any, Dict
from nats.aio.client import Client as NATS

class EventPublisher:
    def __init__(self):
        self.nc = NATS()
        
    async def connect(self):
        await self.nc.connect("nats://nats:4222")
        
    async def publish(self, subject: str, data: Dict[str, Any]):
        """Publish event to JetStream"""
        await self.nc.publish(
            subject,
            json.dumps(data).encode()
        )
        
    async def publish_data_change(self, table: str, operation: str, data: dict):
        """Publish database change event"""
        subject = f"data.{table}.{operation}"
        await self.publish(subject, {
            "table": table,
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        })
```

### 1.3 Event-Driven Wrapper for Existing Services
```python
# backend/services/event_wrapper.py
"""Wrap existing services with event publishing"""

def event_driven(subject_pattern: str):
    """Decorator to make any method event-driven"""
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            # Execute original function
            result = await func(self, *args, **kwargs)
            
            # Publish event
            subject = subject_pattern.format(
                method=func.__name__,
                service=self.__class__.__name__
            )
            await self.event_publisher.publish(subject, {
                "args": args,
                "kwargs": kwargs,
                "result": result
            })
            
            return result
        return wrapper
    return decorator
```

## Phase 2: Estuary Flow Integration (Week 3-4)

### 2.1 Estuary Flow Deployment
```yaml
# k8s/base/estuary-flow.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: estuary-flow
  namespace: sophia-ai-prod
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: estuary
        image: ghcr.io/estuary/flow:latest
        env:
        - name: ESTUARY_TENANT
          value: sophia-ai
        ports:
        - containerPort: 8080
```

### 2.2 Estuary MCP Server
```python
# mcp-servers/estuary/server.py
"""MCP server for Estuary Flow control"""

from backend.mcp.base.standardized_mcp_server import StandardizedMCPServer, mcp_tool

class EstuaryMCPServer(StandardizedMCPServer):
    def __init__(self, port: int):
        super().__init__(port=port, service_name="estuary_mcp")
        self.base_url = "http://estuary-flow:8080/api/v1"
    
    @mcp_tool()
    async def create_capture(self, name: str, source: dict) -> dict:
        """Create a new data capture"""
        # Implementation
    
    @mcp_tool()
    async def create_materialization(self, name: str, target: dict) -> dict:
        """Create a new materialization to Snowflake"""
        # Implementation
    
    @mcp_tool()
    async def get_flow_status(self, flow_id: str) -> dict:
        """Get status of a specific flow"""
        # Implementation
```

### 2.3 CDC Configuration for Existing Databases
```json
// estuary/captures/postgres-cdc.json
{
  "name": "sophia-postgres-cdc",
  "endpoint": {
    "connector": {
      "image": "ghcr.io/estuary/source-postgres:latest",
      "config": {
        "address": "postgres:5432",
        "database": "sophia_ai",
        "user": "${POSTGRES_USER}",
        "password": "${POSTGRES_PASSWORD}",
        "replication": {
          "plugin": "pgoutput",
          "slot": "sophia_cdc"
        }
      }
    }
  },
  "bindings": [
    {
      "resource": {
        "schema": "public",
        "table": "conversations"
      },
      "target": "sophia-ai/conversations"
    }
  ]
}
```

## Phase 3: n8n Workflow Engine (Week 4-5)

### 3.1 n8n Deployment
```yaml
# k8s/base/n8n.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: n8n
  namespace: sophia-ai-prod
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: n8n
        image: n8nio/n8n:latest
        env:
        - name: N8N_BASIC_AUTH_ACTIVE
          value: "false"
        - name: EXECUTIONS_MODE
          value: "queue"
        - name: QUEUE_BULL_REDIS_HOST
          value: "redis"
```

### 3.2 n8n MCP Server
```python
# mcp-servers/n8n/server.py
"""MCP server for n8n workflow control"""

class N8nMCPServer(StandardizedMCPServer):
    @mcp_tool()
    async def trigger_workflow(self, workflow_id: str, data: dict) -> dict:
        """Trigger a workflow with data"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.n8n_url}/webhook/{workflow_id}",
                json=data
            )
            return response.json()
    
    @mcp_tool()
    async def create_workflow(self, definition: dict) -> dict:
        """Create a new workflow from definition"""
        # Implementation
```

### 3.3 Core Workflow Templates
```json
// n8n/workflows/gong-call-analysis.json
{
  "name": "Gong Call Analysis",
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "JetStream Trigger",
      "parameters": {
        "path": "gong-call-{{$id}}",
        "responseMode": "immediately"
      }
    },
    {
      "type": "n8n-nodes-sophia.mcp",
      "name": "Analyze Call",
      "parameters": {
        "server": "ai_memory_mcp",
        "tool": "analyze_call_transcript"
      }
    },
    {
      "type": "n8n-nodes-base.if",
      "name": "Check Sentiment",
      "parameters": {
        "conditions": {
          "sentiment": "negative",
          "deal_value": ">50000"
        }
      }
    },
    {
      "type": "n8n-nodes-base.linear",
      "name": "Create Ticket",
      "parameters": {
        "title": "High-Value At-Risk Deal",
        "priority": "urgent"
      }
    }
  ]
}
```

## Phase 4: Unified MCP Control Plane (Week 5-6)

### 4.1 MCP Gateway Enhancement
```python
# backend/mcp/unified_gateway.py
"""Enhanced MCP Gateway with routing intelligence"""

class UnifiedMCPGateway:
    def __init__(self):
        self.routers = {
            "data": ["snowflake_mcp", "estuary_mcp"],
            "workflow": ["n8n_mcp", "cicd_mcp"],
            "intelligence": ["ai_memory_mcp", "gong_mcp"],
            "infrastructure": ["devops_mcp", "lambda_mcp"]
        }
    
    async def route_request(self, domain: str, tool: str, params: dict):
        """Intelligent routing based on domain"""
        servers = self.routers.get(domain, [])
        
        # Try primary server
        for server in servers:
            try:
                return await self.call_mcp_server(server, tool, params)
            except MCPServerUnavailable:
                continue
        
        raise NoAvailableServer(f"No server available for {domain}.{tool}")
```

### 4.2 Internal SDK
```python
# sophia_sdk/__init__.py
"""Sophia AI Internal SDK"""

from typing import Optional
import httpx

class SophiaClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    @property
    def data(self):
        """Data operations"""
        return DataClient(self)
    
    @property
    def workflows(self):
        """Workflow operations"""
        return WorkflowClient(self)
    
    @property
    def ai(self):
        """AI operations"""
        return AIClient(self)

class DataClient:
    def __init__(self, client: SophiaClient):
        self.client = client
    
    async def query(self, sql: str) -> list[dict]:
        """Execute SQL query via MCP"""
        response = await self.client.post("/mcp/data/query", {"sql": sql})
        return response.json()["results"]
```

### 4.3 DevOps MCP Server
```python
# mcp-servers/devops/server.py
"""MCP server for DevOps operations"""

class DevOpsMCPServer(StandardizedMCPServer):
    @mcp_tool()
    async def cleanup_repository(self, dry_run: bool = True) -> dict:
        """Clean up repository artifacts"""
        # Refactored from scripts/comprehensive_legacy_cleanup.py
        
    @mcp_tool()
    async def deploy_service(self, service: str, environment: str) -> dict:
        """Deploy a service to an environment"""
        # Trigger GitHub Actions workflow
        
    @mcp_tool()
    async def scale_infrastructure(self, component: str, replicas: int) -> dict:
        """Scale infrastructure components"""
        # Use kubectl to scale
```

## Phase 5: Migration Strategy

### 5.1 Service Migration Order
1. **Low Risk**: Monitoring, health checks, logging
2. **Medium Risk**: Data pipelines, analytics queries
3. **High Risk**: Core business logic, authentication

### 5.2 Dual-Mode Operation
```python
# backend/services/dual_mode_wrapper.py
"""Run services in both legacy and new mode during transition"""

class DualModeService:
    def __init__(self, legacy_service, new_service):
        self.legacy = legacy_service
        self.new = new_service
        self.mode = os.getenv("SERVICE_MODE", "dual")
    
    async def execute(self, *args, **kwargs):
        if self.mode == "legacy":
            return await self.legacy.execute(*args, **kwargs)
        elif self.mode == "new":
            return await self.new.execute(*args, **kwargs)
        else:  # dual mode
            # Run both, compare results
            legacy_result = await self.legacy.execute(*args, **kwargs)
            new_result = await self.new.execute(*args, **kwargs)
            
            # Log differences for analysis
            if legacy_result != new_result:
                logger.warning("Result mismatch", 
                    legacy=legacy_result, 
                    new=new_result
                )
            
            # Return legacy result during transition
            return legacy_result
```

### 5.3 Rollback Strategy
- Feature flags for all new components
- Blue/green deployments with instant rollback
- Data versioning in Snowflake with time travel

## Phase 6: Documentation & Governance

### 6.1 Architecture Decision Records (ADRs)
```markdown
# ADR-001: Event-Driven Architecture

## Status
Accepted

## Context
Current synchronous architecture limits scalability and resilience

## Decision
Adopt event-driven architecture with NATS JetStream

## Consequences
- Better scalability and fault tolerance
- Increased complexity
- Need for event schema registry
```

### 6.2 Developer Guidelines
```markdown
# Sophia AI Development Guidelines

## Adding a New Service
1. Create MCP server extending StandardizedMCPServer
2. Register in consolidated_mcp_ports.json
3. Add health check endpoint
4. Integrate with UnifiedServiceAuthManager
5. Emit events for all state changes

## Event Naming Convention
- Data events: `data.<table>.<operation>`
- Workflow events: `workflow.<name>.<status>`
- System events: `system.<component>.<event>`
```

### 6.3 AI Coder Instructions
```python
# .cursorrules additions
"""
## Sophia AI Architecture Rules

1. **Event-First Design**
   - All state changes must emit events
   - Subscribe to events, don't poll

2. **MCP Integration**
   - New functionality = new MCP tool
   - Use sophia_sdk for internal calls

3. **Configuration**
   - Use UnifiedConfig.get() for all config
   - Never hardcode values

4. **Error Handling**
   - All errors must include context
   - Use structured logging

5. **Testing**
   - Unit tests for business logic
   - Integration tests for MCP tools
   - Event flow tests for workflows
"""
```

## Success Metrics

### Technical Metrics
- Event processing latency < 100ms p95
- Zero message loss (at-least-once delivery)
- API response time < 200ms p95
- 99.95% uptime SLA

### Business Metrics
- 80% reduction in manual operations
- 5x increase in deployment frequency
- 50% reduction in incident MTTR
- 90% of tasks automated via MCP/n8n

## Risk Mitigation

### Technical Risks
1. **Event Storm**: Rate limiting, back-pressure, circuit breakers
2. **Data Inconsistency**: Event sourcing, saga pattern
3. **Complexity**: Clear documentation, training, tooling

### Operational Risks
1. **Migration Failures**: Incremental rollout, feature flags
2. **Performance Degradation**: Continuous monitoring, load testing
3. **Security**: Zero-trust, encryption, audit logging

## Timeline Summary

- **Week 1**: Foundation fixes, environment setup
- **Week 2-3**: Event infrastructure, NATS deployment
- **Week 3-4**: Estuary Flow, real-time data
- **Week 4-5**: n8n workflows, automation
- **Week 5-6**: MCP control plane, SDK
- **Week 6+**: Migration, monitoring, optimization

## Conclusion

This integration plan provides a clear path from the current architecture to a fully autonomous, event-driven system. By following this incremental approach, we minimize risk while delivering immediate value at each phase.

The key is to maintain backward compatibility while building the new architecture in parallel, allowing for a smooth transition without disrupting existing operations. 