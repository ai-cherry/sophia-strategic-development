# Lambda Labs MCP Deployment Guide
## Comprehensive Deployment Process for Sophia AI MCP Ecosystem

This guide provides the complete, clean deployment process for all Sophia AI MCP servers to Lambda Labs infrastructure using Docker Cloud and hybrid Kubernetes architecture.

## 🏗️ **DEPLOYMENT ARCHITECTURE OVERVIEW**

### **Three-Tier Lambda Labs Infrastructure**

1. **sophia-platform-prod** (146.235.200.1) - `gpu_1x_a10`
   - Main FastAPI Backend
   - Frontend Services
   - Core Infrastructure (PostgreSQL, Redis, Grafana)

2. **sophia-mcp-prod** (165.1.69.44) - `gpu_1x_a10`
   - All MCP Servers
   - MCP Gateway
   - Service Discovery

3. **sophia-ai-prod** (137.131.6.213) - `gpu_1x_a100_sxm4`
   - Snowflake Cortex AI Processing
   - AI/ML Workloads
   - GPU-intensive operations

### **Hybrid Deployment Strategy**

- **Docker Swarm** for MCP servers (production-ready, simple orchestration)
- **Kubernetes** for advanced workloads (AI processing, scaling)
- **Docker Cloud** for multi-instance coordination
- **GitHub Actions** for CI/CD automation

## 🚀 **CLEAN DEPLOYMENT PROCESS**

### **Phase 1: Pre-deployment Validation**

```bash
# 1. Validate infrastructure connectivity
python scripts/validate_lambda_labs_infrastructure.py

# 2. Check Docker Hub authentication
docker login

# 3. Verify GitHub secrets configuration
python scripts/verify_deployment_secrets.py
```

### **Phase 2: Build and Push Images**

```bash
# Build all MCP server images
python scripts/build_all_mcp_images.py --registry scoobyjava15

# Push to Docker Hub
python scripts/push_mcp_images.py --tag latest
```

### **Phase 3: Deploy to Lambda Labs**

#### **Option A: GitHub Actions Deployment (Recommended)**

```bash
# Trigger production deployment via GitHub Actions
gh workflow run deploy-mcp-production.yml \
  -f servers="codacy,linear,ai_memory,asana,notion" \
  -f environment="prod"
```

#### **Option B: Direct Deployment**

```bash
# Deploy complete MCP ecosystem
python scripts/deploy_sophia_complete_platform.py --environment prod

# Deploy specific servers
python scripts/deploy_mcp_service.py --service codacy --target 165.1.69.44
```

### **Phase 4: Health Verification**

```bash
# Comprehensive health check
python scripts/verify_mcp_deployment_health.py

# Individual server testing
curl http://165.1.69.44:3008/health  # Codacy
curl http://165.1.69.44:9004/health  # Linear
curl http://165.1.69.44:9001/health  # AI Memory
```

## 📋 **MCP SERVER SPECIFICATIONS**

### **Core MCP Servers**

| Server | Port | Image | Purpose | GPU |
|--------|------|-------|---------|-----|
| **Codacy** | 3008 | `scoobyjava15/sophia-codacy-mcp` | Code quality & security | No |
| **Linear** | 9004 | `scoobyjava15/sophia-linear-mcp` | Project management | No |
| **AI Memory** | 9001 | `scoobyjava15/sophia-ai-memory-mcp` | Memory & context | Yes |
| **Asana** | 9100 | `scoobyjava15/sophia-asana-mcp` | Task management | No |
| **Notion** | 9005 | `scoobyjava15/sophia-notion-mcp` | Knowledge base | No |
| **GitHub** | 9103 | `scoobyjava15/sophia-github-mcp` | Repository management | No |
| **Snowflake Admin** | 9020 | `scoobyjava15/sophia-snowflake-admin` | Database operations | Yes |
| **Lambda Labs CLI** | 9040 | `scoobyjava15/sophia-lambda-labs-cli` | Infrastructure control | No |

### **Docker Compose Configuration**

Each MCP server uses standardized Docker configuration:

```yaml
# Example: Codacy MCP Server
codacy-mcp:
  image: scoobyjava15/sophia-codacy-mcp:latest
  environment:
    - ENVIRONMENT=prod
    - PULUMI_ORG=scoobyjava-org
    - PORT=3008
  networks:
    - sophia-overlay
  secrets:
    - pulumi_esc
  deploy:
    replicas: 2
    update_config:
      parallelism: 1
      delay: 10s
      failure_action: rollback
    restart_policy:
      condition: any
      delay: 5s
      max_attempts: 3
    resources:
      limits:
        cpus: '1'
        memory: 2G
      reservations:
        cpus: '0.5'
        memory: 1G
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3008/health"]
    interval: 30s
    timeout: 10s
    retries: 5
```

## 🔧 **KUBERNETES INTEGRATION**

### **When to Use Kubernetes vs Docker Swarm**

**Docker Swarm (Primary):**
- ✅ MCP servers
- ✅ Simple web services
- ✅ Database services
- ✅ Monitoring stack

**Kubernetes (Advanced):**
- ✅ AI/ML workloads requiring GPU scheduling
- ✅ Complex auto-scaling scenarios
- ✅ Advanced networking requirements
- ✅ Multi-tenant environments

### **Kubernetes Deployment for GPU Workloads**

```yaml
# Snowflake Cortex AI Processing
apiVersion: apps/v1
kind: Deployment
metadata:
  name: snowflake-cortex-ai
  namespace: sophia-ai
spec:
  replicas: 2
  selector:
    matchLabels:
      app: snowflake-cortex-ai
  template:
    metadata:
      labels:
        app: snowflake-cortex-ai
    spec:
      nodeSelector:
        lambdalabs.com/gpu-type: "a100"
        lambdalabs.com/instance-type: "gpu_1x_a100_sxm4"
      tolerations:
        - key: "lambdalabs.com/gpu"
          operator: "Equal"
          value: "true"
          effect: "NoSchedule"
      containers:
        - name: snowflake-cortex
          image: scoobyjava15/sophia-snowflake-cortex:latest
          resources:
            limits:
              nvidia.com/gpu: 1
              memory: "32Gi"
              cpu: "8"
            requests:
              nvidia.com/gpu: 1
              memory: "16Gi"
              cpu: "4"
          env:
            - name: CUDA_VISIBLE_DEVICES
              value: "all"
            - name: NVIDIA_VISIBLE_DEVICES
              value: "all"
```

## 🔐 **SECRET MANAGEMENT**

### **Pulumi ESC Integration**

All secrets are managed through Pulumi ESC with automatic synchronization:

```bash
# Secrets are automatically loaded from:
# scoobyjava-org/default/sophia-ai-production

# Key secrets include:
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- SNOWFLAKE_ACCOUNT/USER/PASSWORD
- GONG_ACCESS_KEY
- HUBSPOT_ACCESS_TOKEN
- LINEAR_API_KEY
- ASANA_ACCESS_TOKEN
- NOTION_API_KEY
- LAMBDA_LABS_API_KEY
```

### **Docker Secrets Configuration**

```yaml
secrets:
  pulumi_esc:
    external: true
    name: sophia-ai-pulumi-esc
  snowflake_credentials:
    external: true
    name: sophia-ai-snowflake-credentials
```

## 📊 **MONITORING AND HEALTH CHECKS**

### **Comprehensive Health Monitoring**

```bash
# Real-time monitoring dashboard
python scripts/mcp_monitoring_dashboard.py

# Health check automation
python scripts/automated_health_checks.py --interval 60

# Performance monitoring
python scripts/mcp_performance_monitor.py
```

### **Grafana Dashboard Integration**

Access comprehensive metrics at:
- **Main Dashboard**: http://146.235.200.1:3000
- **MCP Metrics**: http://165.1.69.44:9090 (Prometheus)
- **AI Metrics**: http://137.131.6.213:8080 (Custom dashboard)

## 🚨 **TROUBLESHOOTING GUIDE**

### **Common Issues and Solutions**

#### **1. MCP Server Not Starting**
```bash
# Check container logs
docker service logs sophia-codacy-mcp --tail 50

# Check resource constraints
docker service ps sophia-codacy-mcp

# Restart service
docker service update --force sophia-codacy-mcp
```

#### **2. Health Check Failures**
```bash
# Direct health check
curl -v http://165.1.69.44:3008/health

# Check container status
docker service ps sophia-codacy-mcp --no-trunc

# Review deployment logs
docker service logs sophia-codacy-mcp
```

#### **3. Port Conflicts**
```bash
# Check port usage
python scripts/check_port_conflicts.py

# Update port configuration
python scripts/update_mcp_ports.py --server codacy --new-port 3009
```

#### **4. Secret Loading Issues**
```bash
# Validate Pulumi ESC access
pulumi env get scoobyjava-org/default/sophia-ai-production

# Test secret loading in container
docker exec -it $(docker ps -q -f name=sophia-codacy-mcp) printenv | grep -E "(OPENAI|ANTHROPIC|SNOWFLAKE)"
```

## 🔄 **ROLLBACK PROCEDURES**

### **Automated Rollback**

```bash
# Rollback specific service
docker service rollback sophia-codacy-mcp

# Rollback complete stack
python scripts/rollback_mcp_deployment.py --version previous
```

### **Manual Recovery**

```bash
# Stop problematic service
docker service rm sophia-codacy-mcp

# Deploy known good version
docker service create \
  --name sophia-codacy-mcp \
  --replicas 2 \
  --publish 3008:3008 \
  --env ENVIRONMENT=prod \
  scoobyjava15/sophia-codacy-mcp:stable
```

## 📚 **DEPLOYMENT SCRIPTS REFERENCE**

### **Essential Scripts**

| Script | Purpose | Usage |
|--------|---------|-------|
| `deploy_sophia_complete_platform.py` | Full platform deployment | `python scripts/deploy_sophia_complete_platform.py` |
| `deploy_mcp_service.py` | Single service deployment | `python scripts/deploy_mcp_service.py --service codacy` |
| `validate_lambda_labs_infrastructure.py` | Infrastructure validation | `python scripts/validate_lambda_labs_infrastructure.py` |
| `monitor_mcp_deployment.py` | Deployment monitoring | `python scripts/monitor_mcp_deployment.py` |
| `debug_all_mcp_servers.py` | Comprehensive debugging | `python scripts/debug_all_mcp_servers.py` |

### **GitHub Actions Workflows**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `deploy-mcp-production.yml` | Manual/Push to main | Production deployment |
| `mcp-health-monitoring.yml` | Schedule (hourly) | Automated health checks |
| `security-scanning.yml` | Push to main | Security vulnerability scanning |

## 🎯 **PERFORMANCE OPTIMIZATION**

### **Resource Allocation Guidelines**

```yaml
# Resource allocation by server type
resources:
  # Code analysis servers
  codacy:
    cpu: "500m-1000m"
    memory: "1Gi-2Gi"

  # Project management servers
  linear:
    cpu: "200m-500m"
    memory: "512Mi-1Gi"

  # AI-enhanced servers
  ai_memory:
    cpu: "1000m-2000m"
    memory: "2Gi-4Gi"
    gpu: "0.25-0.5"
```

### **Auto-scaling Configuration**

```yaml
# Horizontal Pod Autoscaler for Kubernetes workloads
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 8
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## 🔗 **INTEGRATION TESTING**

### **End-to-End Testing**

```bash
# Full integration test suite
python scripts/run_integration_tests.py

# Specific server testing
python scripts/test_mcp_server.py --server codacy --comprehensive

# Performance testing
python scripts/mcp_load_testing.py --servers all --duration 300
```

### **Automated Testing in CI/CD**

```yaml
# GitHub Actions integration testing
- name: Run MCP Integration Tests
  run: |
    python scripts/run_integration_tests.py --environment staging
    python scripts/validate_mcp_health.py --timeout 300
```

## 🚀 **PRODUCTION READINESS CHECKLIST**

### **Pre-Production Validation**

- [ ] All Docker images built and pushed to registry
- [ ] Pulumi ESC secrets synchronized
- [ ] Lambda Labs instances healthy and accessible
- [ ] Network connectivity validated between instances
- [ ] Resource quotas and limits configured
- [ ] Health checks configured for all services
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery procedures tested
- [ ] Security scanning completed
- [ ] Load testing performed

### **Production Deployment**

- [ ] Blue-green deployment strategy executed
- [ ] Zero-downtime deployment verified
- [ ] All health checks passing
- [ ] Monitoring dashboards operational
- [ ] Log aggregation working
- [ ] Performance metrics within SLA
- [ ] Security policies enforced
- [ ] Disaster recovery procedures documented

## 📞 **SUPPORT AND ESCALATION**

### **Support Tiers**

1. **Self-Service**: Use automated scripts and monitoring
2. **Documentation**: Reference this guide and troubleshooting sections
3. **Escalation**: Contact platform team with deployment logs

### **Critical Issue Response**

```bash
# Emergency rollback
python scripts/emergency_rollback.py --reason "critical issue description"

# Incident response
python scripts/incident_response.py --severity critical --affected-services "codacy,linear"
```

---

## 🎉 **SUCCESS METRICS**

### **Deployment KPIs**

- **Deployment Success Rate**: >99%
- **Health Check Success Rate**: >99.9%
- **Average Response Time**: <200ms
- **Zero-Downtime Deployments**: 100%
- **Mean Time to Recovery**: <5 minutes

### **Business Value Delivered**

- **Real-time Code Quality Analysis**: Codacy MCP
- **Intelligent Project Management**: Linear MCP
- **AI-Powered Context Awareness**: AI Memory MCP
- **Enterprise-Grade Security**: Comprehensive security scanning
- **Scalable Infrastructure**: Auto-scaling and load balancing

This deployment guide ensures reliable, scalable, and secure deployment of the Sophia AI MCP ecosystem to Lambda Labs infrastructure with comprehensive monitoring, troubleshooting, and optimization capabilities.
