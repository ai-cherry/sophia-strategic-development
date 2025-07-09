# Sophia AI Unified Deployment Guide

**Last Updated:** 1752067238.022169  
**Architecture:** 5 Lambda Labs GPU Instances + Serverless

## 🏗️ Current Infrastructure

- **sophia-production-instance**: `104.171.202.103` (INSTANCE)
- **sophia-ai-core**: `192.222.58.232` (CORE)
- **sophia-mcp-orchestrator**: `104.171.202.117` (ORCHESTRATOR)
- **sophia-data-pipeline**: `104.171.202.134` (PIPELINE)
- **sophia-development**: `155.248.194.183` (DEVELOPMENT)

## 🚀 Deployment Methods

### Method 1: GitHub Actions (Recommended)
```bash
# Navigate to GitHub → Actions → "🚀 Sophia AI Unified Deployment"
# Select target instances and deployment options
```

### Method 2: Unified Script Deployment
```bash
# Deploy to all instances
./scripts/deploy_sophia_unified.sh deploy all

# Deploy to specific instance
./scripts/deploy_sophia_unified.sh deploy production
./scripts/deploy_sophia_unified.sh deploy ai-core
```

### Method 3: Individual Instance Deployment
```bash
# Simple deployment to specific instance
./scripts/deploy_sophia_simple.sh 104.171.202.103

# Platform deployment with all components
./scripts/deploy_sophia_platform.sh
```

## 📁 Essential Files

### Deployment Scripts
- `scripts/deploy_sophia_unified.sh` - Main deployment orchestrator
- `scripts/deploy_sophia_platform.sh` - Complete platform deployment
- `scripts/deploy_sophia_simple.sh` - Simple single-instance deployment
- `scripts/lambda_migration_deploy.sh` - Lambda Labs optimized deployment

### Docker Configurations
- `deployment/docker-compose-production.yml` - Production services (RTX6000)
- `deployment/docker-compose-ai-core.yml` - AI/ML services (GH200)
- `deployment/docker-compose-mcp-orchestrator.yml` - MCP services (A6000)
- `deployment/docker-compose-data-pipeline.yml` - Data services (A100)
- `deployment/docker-compose-development.yml` - Dev/monitoring (A10)

### GitHub Actions
- `.github/workflows/deploy-sophia-platform.yml` - Main deployment workflow
- `.github/workflows/sophia-production-deployment.yml` - Production deployment

## 🔧 Configuration Management

All deployments use:
- **Docker Registry**: `scoobyjava15`
- **Environment**: `prod` (default)
- **Secrets**: Pulumi ESC (`scoobyjava-org/default/sophia-ai-production`)
- **Orchestration**: Docker Swarm mode

## 📊 Post-Deployment Validation

After deployment, verify:
```bash
# Check service status
./scripts/deploy_sophia_unified.sh status

# Validate specific instance
./scripts/deploy_sophia_unified.sh validate ai-core

# Monitor deployment
# - Backend: http://104.171.202.103:8000/health
# - Frontend: http://104.171.202.103:3000
# - Monitoring: http://155.248.194.183:3000 (Grafana)
```

## 🚨 Emergency Procedures

### Rollback Deployment
```bash
# Rollback specific service
docker service rollback sophia_backend

# Full stack rollback
./scripts/deploy_sophia_unified.sh rollback
```

### Instance Recovery
```bash
# Restart failed instance
./scripts/deploy_sophia_unified.sh restart <instance-name>

# Redeploy from scratch
./scripts/deploy_sophia_unified.sh deploy <instance-name> --force
```
