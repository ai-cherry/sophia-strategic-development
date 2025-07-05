# Comprehensive Infrastructure Remediation Plan

## Executive Summary

This plan addresses two critical infrastructure failures in Sophia AI:
1. **MCP Server Issues**: 75% operational (9/12 servers), with 2 syntax errors remaining
2. **Docker Ecosystem**: Completely broken, preventing Lambda Labs cloud deployment

## 🎯 Strategic Approach

### Phase-Based Implementation
We'll use a systematic approach with clear phases, each building on the previous:

```
Phase 1: Critical Fixes (Day 1-2)
  ↓
Phase 2: Docker Infrastructure (Day 3-5)
  ↓
Phase 3: Integration & Testing (Day 6-7)
  ↓
Phase 4: Production Deployment (Day 8-10)
```

## 📋 Phase 1: Critical Infrastructure Fixes (Day 1-2)

### 1.1 MCP Server Completion (4 hours)

**Current Status**: 9/12 servers operational (75%)

**Remaining Issues**:
- Linear server: Fixed structure, minor linter errors
- Asana server: Fixed structure, minor linter errors

**Actions**:
```python
# 1. Fix linter errors in Linear and Asana
# 2. Test all 12 servers
# 3. Verify 100% operational status
python scripts/test_all_mcp_connections.py
```

### 1.2 Docker File Creation (4 hours)

**Critical Missing Files**:
1. `docker-compose.cloud.yml`
2. `Dockerfile.uv.production`
3. MCP server Dockerfiles

**Action Plan**:
```yaml
# Create docker-compose.cloud.yml with:
- Lambda Labs configuration (146.235.200.1)
- Docker Swarm mode
- Pulumi ESC secrets integration
- Health monitoring
- Auto-scaling configuration
```

### 1.3 Path Corrections (2 hours)

**Fix All Path References**:
```bash
# Change all references from:
./mcp-servers/* → ./backend/mcp_servers/*

# Update deploy_mcp_servers.py module paths
backend.mcp.ai_memory_mcp_server → backend.mcp_servers.ai_memory.ai_memory_mcp_server
```

## 📋 Phase 2: Docker Infrastructure Build (Day 3-5)

### 2.1 Standardized MCP Dockerfile Template

```dockerfile
# Create template for all MCP servers
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV ENVIRONMENT=prod
ENV PULUMI_ORG=scoobyjava-org
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1
CMD ["python", "-m", "uvicorn", "${MODULE}:app", "--host", "0.0.0.0", "--port", "${PORT}"]
```

### 2.2 Lambda Labs Integration

**Docker Swarm Configuration**:
```yaml
version: '3.8'
services:
  mcp-gateway:
    image: scoobyjava15/sophia-mcp-gateway:latest
    deploy:
      mode: replicated
      replicas: 3
      placement:
        constraints:
          - node.labels.type == gpu
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    networks:
      - sophia-overlay
    secrets:
      - source: pulumi_esc
        target: /run/secrets/pulumi_esc

networks:
  sophia-overlay:
    driver: overlay
    attachable: true

secrets:
  pulumi_esc:
    external: true
```

### 2.3 MCP Gateway Implementation

**Unified Request Router**:
```python
class MCPGateway:
    """Routes requests to appropriate MCP servers"""

    def __init__(self):
        self.servers = self.discover_servers()
        self.health_monitor = HealthMonitor()
        self.load_balancer = LoadBalancer()

    async def route_request(self, request):
        # Intelligent routing based on:
        # - Server health
        # - Load distribution
        # - Request type
        # - GPU requirements
```

## 📋 Phase 3: Integration & Testing (Day 6-7)

### 3.1 Comprehensive Testing Suite

```python
class InfrastructureTestSuite:
    """Test all infrastructure components"""

    async def test_all_components(self):
        results = {
            "mcp_servers": await self.test_mcp_servers(),
            "docker_builds": await self.test_docker_builds(),
            "lambda_labs": await self.test_lambda_deployment(),
            "integration": await self.test_end_to_end()
        }
        return results
```

### 3.2 Performance Benchmarks

**Target Metrics**:
- MCP response time: < 200ms
- Docker build time: < 5 minutes
- Deployment time: < 10 minutes
- Health check latency: < 50ms
- GPU utilization: > 70%

### 3.3 Security Validation

**Security Checklist**:
- [ ] All secrets via Pulumi ESC
- [ ] No hardcoded credentials
- [ ] Network isolation configured
- [ ] SSL/TLS for all endpoints
- [ ] Container scanning enabled

## 📋 Phase 4: Production Deployment (Day 8-10)

### 4.1 Deployment Strategy

```bash
# Step 1: Deploy infrastructure
docker stack deploy -c docker-compose.cloud.yml sophia-ai

# Step 2: Verify health
docker service ls
docker service ps sophia-ai_mcp-gateway

# Step 3: Run smoke tests
python scripts/production_smoke_tests.py

# Step 4: Enable monitoring
docker service create \
  --name prometheus \
  --network sophia-overlay \
  prom/prometheus
```

### 4.2 Rollback Plan

```bash
# Automated rollback on failure
if [ $HEALTH_CHECK_FAILED ]; then
  docker stack rm sophia-ai
  docker stack deploy -c docker-compose.cloud.previous.yml sophia-ai
fi
```

### 4.3 Monitoring & Observability

**Grafana Dashboard**:
- MCP server health matrix
- Request latency percentiles
- Error rate by service
- GPU utilization metrics
- Container resource usage

## 🔧 Implementation Scripts

### Script 1: Complete Infrastructure Fix
```python
#!/usr/bin/env python3
"""
Complete infrastructure fix implementation
"""

async def main():
    # Phase 1: Fix MCP servers
    await fix_remaining_mcp_servers()

    # Phase 2: Create Docker files
    await create_missing_docker_files()

    # Phase 3: Fix path references
    await fix_all_path_references()

    # Phase 4: Test everything
    results = await test_complete_infrastructure()

    print(f"Infrastructure ready: {results['success_rate']}%")
```

### Script 2: Docker Ecosystem Builder
```python
#!/usr/bin/env python3
"""
Build complete Docker ecosystem
"""

class DockerEcosystemBuilder:
    def create_cloud_compose(self):
        """Create docker-compose.cloud.yml"""

    def create_production_dockerfile(self):
        """Create Dockerfile.uv.production"""

    def containerize_mcp_servers(self):
        """Create Dockerfiles for all MCP servers"""

    def configure_swarm_mode(self):
        """Configure Docker Swarm for Lambda Labs"""
```

### Script 3: Lambda Labs Deployer
```python
#!/usr/bin/env python3
"""
Deploy to Lambda Labs infrastructure
"""

class LambdaLabsDeployer:
    def __init__(self):
        self.host = "146.235.200.1"
        self.registry = "scoobyjava15"

    async def deploy(self):
        # Build and push images
        await self.build_and_push_images()

        # Deploy stack
        await self.deploy_docker_stack()

        # Verify deployment
        await self.verify_deployment()
```

## 📊 Success Metrics

### Technical Metrics
- **MCP Servers**: 100% operational (12/12)
- **Docker Builds**: 100% success rate
- **Lambda Labs**: Fully deployed and accessible
- **Response Times**: < 200ms p95
- **Uptime**: 99.9% availability

### Business Metrics
- **Deployment Time**: 10 days → 10 minutes
- **Maintenance Effort**: 70% reduction
- **Cost Efficiency**: 40% reduction via GPU optimization
- **Scalability**: Unlimited with auto-scaling

## 🚨 Risk Mitigation

### Identified Risks
1. **Dependency Conflicts**: Use UV for deterministic builds
2. **Network Latency**: Implement edge caching
3. **GPU Availability**: Configure CPU fallback
4. **Secret Exposure**: Enforce Pulumi ESC usage
5. **Deployment Failures**: Automated rollback

### Mitigation Strategies
- Comprehensive testing at each phase
- Incremental deployment approach
- Real-time monitoring and alerting
- Automated recovery mechanisms
- Documentation and runbooks

## 📅 Timeline

### Week 1
- **Day 1-2**: Critical fixes (MCP + Docker files)
- **Day 3-5**: Docker infrastructure build
- **Day 6-7**: Integration and testing

### Week 2
- **Day 8-10**: Production deployment
- **Day 11-12**: Monitoring setup
- **Day 13-14**: Documentation and training

## 🎯 Immediate Actions (Next 4 Hours)

1. **Fix Linear/Asana Linter Errors**
   ```bash
   # Minor import adjustments needed
   python scripts/fix_mcp_linter_errors.py
   ```

2. **Create docker-compose.cloud.yml**
   ```bash
   python scripts/create_cloud_docker_compose.py
   ```

3. **Fix Path References**
   ```bash
   python scripts/fix_docker_path_references.py
   ```

4. **Test Current State**
   ```bash
   python scripts/test_infrastructure_status.py
   ```

## 📝 Deliverables

### Phase 1 Deliverables
- [ ] 12/12 MCP servers operational
- [ ] docker-compose.cloud.yml created
- [ ] Dockerfile.uv.production created
- [ ] All path references fixed

### Phase 2 Deliverables
- [ ] All MCP servers containerized
- [ ] Lambda Labs integration complete
- [ ] MCP gateway implemented
- [ ] Health monitoring active

### Phase 3 Deliverables
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Security validation complete
- [ ] Documentation updated

### Phase 4 Deliverables
- [ ] Production deployment successful
- [ ] Monitoring dashboards live
- [ ] Rollback procedures tested
- [ ] Team training complete

## 🏁 Conclusion

This comprehensive plan addresses both the MCP server issues (nearly complete) and the critical Docker infrastructure failures. By following this systematic approach, we will achieve:

1. **100% MCP server operational status**
2. **Complete Docker ecosystem for Lambda Labs**
3. **Production-ready deployment pipeline**
4. **Enterprise-grade monitoring and reliability**

The plan prioritizes immediate fixes while building toward a robust, scalable infrastructure that supports the Sophia AI platform's growth and reliability requirements.
