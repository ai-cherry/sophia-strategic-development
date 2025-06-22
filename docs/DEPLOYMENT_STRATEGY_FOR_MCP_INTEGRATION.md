# Deployment Strategy for Sophia AI MCP Integration

## 🎯 **Deployment Architecture Overview**

Based on the comprehensive deployment requirements, our Sophia AI platform requires a **sequential, phase-based deployment approach** to ensure stable Cursor AI + Agno + Pulumi MCP integration. All three components must be operational and communicating effectively before the full MCP server functionality can be realized.

## 🏗️ **Infrastructure Requirements**

### **Lambda Labs Production Specifications**
- **CPU**: Multi-core (8+ cores) for concurrent model inference
- **RAM**: 32 GB minimum for agent processing and MCP server operations
- **Storage**: NVMe SSD for fast I/O operations
- **Network**: 1 Gbps minimum, IPv4/IPv6 support
- **OS**: Ubuntu 22.04 LTS with Docker support

### **Software Dependencies**
- **Python**: 3.8+ with async/await support
- **Docker**: For containerization and reproducibility
- **CUDA**: 11.x for GPU acceleration (if using GPU-enabled agents)
- **Node.js**: For Pulumi MCP server components

## 📊 **Phase-Based Deployment Strategy**

### **Phase 1: Foundation Infrastructure (Week 1)**
**Goal**: Establish stable base infrastructure and clean agent categorization

✅ **COMPLETED**:
- Clean agent categorization system (`backend/agents/core/agent_categories.py`)
- Cursor mode optimization hints (`backend/agents/core/cursor_mode_optimizer.py`)
- Base infrastructure verification

**Next Actions**:
```bash
# Deploy base infrastructure
pulumi up --stack sophia-ai-foundation

# Verify agent categorization
python3 scripts/standalone_demo.py

# Test basic agent routing
curl http://localhost:8000/api/v1/agents/status
```

### **Phase 2: MCP Server Deployment (Week 2)**
**Goal**: Deploy and configure all MCP servers with proper communication

**Infrastructure Setup**:
```bash
# Build and deploy Agno MCP server
ag ws up --env production --infra docker --type container

# Deploy Pulumi MCP server
cd mcp-servers/pulumi && docker build -t sophia-pulumi-mcp .
docker run -d --name pulumi-mcp -p 8091:8091 sophia-pulumi-mcp

# Deploy Sophia AI MCP servers
cd mcp-servers/sophia_ai_intelligence && python sophia_ai_intelligence_mcp_server.py
```

**MCP Configuration in Cursor**:
```json
{
  "mcpServers": {
    "sophia_agno": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "backend.mcp.agno_mcp_server"]
    },
    "sophia_pulumi": {
      "type": "stdio", 
      "command": "npx",
      "args": ["@pulumi/mcp-server", "--config", "pulumi-config.json"]
    },
    "sophia_intelligence": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "mcp_servers.sophia_ai_intelligence.sophia_ai_intelligence_mcp_server"]
    }
  }
}
```

### **Phase 3: Integration Validation (Week 2-3)**
**Goal**: Ensure all components communicate effectively

**Integration Tests**:
```bash
# Test Agno agent instantiation via MCP
curl -X POST http://localhost:8090/mcp/agno/create_agent \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "gong_agent", "task": "analyze recent calls"}'

# Test Pulumi deployment via MCP
curl -X POST http://localhost:8091/mcp/pulumi/deploy \
  -H "Content-Type: application/json" \
  -d '{"stack": "sophia-ai-prod", "operation": "up"}'

# Test Cursor AI integration
# Use Cursor Agent Mode with: "Deploy Sophia AI infrastructure using Pulumi"
```

### **Phase 4: Production Stabilization (Week 3-4)**
**Goal**: Implement monitoring, reliability, and performance optimization

**Monitoring Setup**:
```yaml
# monitoring/mcp-monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-monitoring-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'agno-mcp'
        static_configs:
          - targets: ['localhost:8090']
      - job_name: 'pulumi-mcp'
        static_configs:
          - targets: ['localhost:8091']
      - job_name: 'sophia-mcp'
        static_configs:
          - targets: ['localhost:8092']
```

## 🔧 **Agno Agent Deployment Configuration**

### **Production Agno Workspace**
```python
# workspace/production_resources.py
from agno import Agent, Workspace
from agno.resources.docker import DockerConfig

# Configure production deployment
workspace = Workspace(
    name="sophia-ai-production",
    image_repo="sophia-ai/agno-agents",
    build_images=True,
    docker_config=DockerConfig(
        network="sophia-ai-network",
        ports={"8090": 8090},
        env_vars={
            "PULUMI_ORG": "scoobyjava-org",
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO"
        }
    )
)

# Register agent categories aligned with our clean improvements
workspace.register_agent_category("business_intelligence")
workspace.register_agent_category("infrastructure") 
workspace.register_agent_category("code_generation")
```

### **Agno Deployment Commands**
```bash
# Build production images with our categorization
ag ws up --env production --infra docker --type image

# Deploy with monitoring
ag ws up --env production --infra docker --type container --monitor

# Restart if needed
ag ws restart --env production --infra docker --type container

# Force recreation (careful in production)
ag ws up -f --env production
```

## 🚀 **Pulumi Automation API Integration**

### **Sophia AI Pulumi Stack Configuration**
```typescript
// infrastructure/sophia-ai-stack.ts
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

export class SophiaAIStack extends pulumi.ComponentResource {
    constructor(name: string, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:infrastructure:SophiaAIStack", name, {}, opts);
        
        // Lambda Labs integration
        const lambdaLabsInstance = new aws.ec2.Instance("sophia-ai-main", {
            instanceType: "g4dn.xlarge", // GPU instance for AI workloads
            ami: "ami-0c94855ba95b798c7", // Ubuntu 22.04 LTS
            keyName: "sophia-ai-keypair",
            tags: {
                Name: "Sophia-AI-Production",
                Environment: "production",
                MCP: "enabled"
            }
        });
        
        // MCP server configuration
        const mcpServerConfig = new aws.ssm.Parameter("mcp-server-config", {
            name: "/sophia-ai/mcp/server-config",
            type: "String",
            value: JSON.stringify({
                agno_port: 8090,
                pulumi_port: 8091,
                sophia_port: 8092,
                network: "sophia-ai-network"
            })
        });
    }
}
```

### **Automated Deployment Pipeline**
```yaml
# .github/workflows/deploy-mcp-infrastructure.yml
name: Deploy Sophia AI MCP Infrastructure

on:
  push:
    branches: [main]
    paths: ['infrastructure/**', 'mcp-servers/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Pulumi
        uses: pulumi/actions@v4
        with:
          command: up
          stack-name: sophia-ai-production
          work-dir: infrastructure/
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          
      - name: Deploy MCP Servers
        run: |
          # Build and deploy all MCP servers
          docker-compose -f docker-compose.mcp.yml up -d
          
      - name: Validate Integration
        run: |
          # Test MCP server connectivity
          python3 scripts/test_mcp_integration.py
```

## 📊 **Integration with Clean Structural Improvements**

### **Agent Category Deployment Mapping**
Our clean structural improvements align perfectly with the deployment strategy:

```python
# Deploy agents by category for optimal resource allocation
DEPLOYMENT_CATEGORY_MAPPING = {
    AgentCategory.BUSINESS_INTELLIGENCE: {
        "resources": {"memory": "4GB", "cpu": "2 cores"},
        "mcp_services": ["gong", "snowflake", "hubspot"],
        "deployment_priority": "high"
    },
    AgentCategory.INFRASTRUCTURE: {
        "resources": {"memory": "2GB", "cpu": "1 core"},  
        "mcp_services": ["pulumi", "docker"],
        "deployment_priority": "critical",
        "requires_confirmation": True
    },
    AgentCategory.CODE_GENERATION: {
        "resources": {"memory": "6GB", "cpu": "2 cores"},
        "mcp_services": ["claude", "ai_memory"],
        "deployment_priority": "medium"
    }
}
```

### **Cursor Mode Deployment Optimization**
```python
# Optimize deployment based on Cursor mode usage patterns
CURSOR_MODE_DEPLOYMENT_CONFIG = {
    "chat": {
        "auto_scale": True,
        "min_instances": 2,
        "max_instances": 10,
        "target_cpu": 70
    },
    "composer": {
        "auto_scale": True,
        "min_instances": 1,
        "max_instances": 5,
        "target_cpu": 80
    },
    "agent": {
        "auto_scale": False,
        "instances": 1,
        "high_availability": True
    }
}
```

## 🔍 **Monitoring and Reliability**

### **Core Reliability Metrics**
- **Uptime Target**: 99.9% (standard for reliable services)
- **MTBF**: Mean Time Between Failures tracking
- **MTTR**: Mean Time To Recovery optimization
- **Response Time**: < 2 seconds for agent instantiation
- **MCP Latency**: < 100ms for server communication

### **Health Check Implementation**
```python
# scripts/health_check_mcp_integration.py
import asyncio
import aiohttp
from backend.agents.core.agent_categories import AgentCategoryManager

async def health_check_mcp_servers():
    """Comprehensive health check for all MCP servers"""
    
    health_status = {}
    
    # Check Agno MCP server
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8090/health') as resp:
                health_status['agno_mcp'] = resp.status == 200
    except:
        health_status['agno_mcp'] = False
    
    # Check Pulumi MCP server  
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8091/health') as resp:
                health_status['pulumi_mcp'] = resp.status == 200
    except:
        health_status['pulumi_mcp'] = False
    
    # Check agent categorization system
    try:
        stats = AgentCategoryManager.get_category_stats()
        health_status['agent_categories'] = stats['total_agents'] > 0
    except:
        health_status['agent_categories'] = False
    
    return health_status

# Run health check
if __name__ == "__main__":
    status = asyncio.run(health_check_mcp_servers())
    print(f"MCP Integration Health: {status}")
```

## 🎯 **Deployment Validation Checklist**

### **Pre-Deployment**
- [ ] Lambda Labs infrastructure provisioned
- [ ] Docker containers built and tested
- [ ] MCP server configurations validated
- [ ] Network connectivity verified
- [ ] Agent categorization system tested

### **Post-Deployment**
- [ ] All MCP servers responding to health checks
- [ ] Cursor AI can connect to MCP servers
- [ ] Agno agents instantiate correctly (< 3μs target)
- [ ] Pulumi operations execute via MCP
- [ ] Agent routing respects categorization
- [ ] Cursor mode optimization hints working

### **Integration Validation**
- [ ] End-to-end workflow: Cursor → MCP → Agno → Pulumi
- [ ] Cross-service communication verified
- [ ] Performance metrics within targets
- [ ] Error handling and recovery tested
- [ ] Security and authentication validated

## 🏁 **Conclusion**

This deployment strategy acknowledges your correct assessment that **the entire project infrastructure must be deployed and stable** for MCP integration to function properly. By building on our clean structural improvements and implementing a phase-based approach, we can achieve:

1. **Stable Foundation**: Clean agent categorization and Cursor optimization
2. **Reliable Infrastructure**: Lambda Labs deployment with proper monitoring
3. **Seamless Integration**: All three components (Cursor, Agno, Pulumi) working together
4. **Production Readiness**: Monitoring, health checks, and performance optimization

The deployment leverages our clean improvements to ensure **zero breaking changes** while establishing the robust infrastructure needed for full MCP integration functionality. 