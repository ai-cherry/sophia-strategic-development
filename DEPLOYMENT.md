# Unified Deployment Guide

## Overview

Sophia AI uses a **Unified Deployment** approach with Docker Swarm on Lambda Labs infrastructure.

## 🚀 Quick Start

```bash
# 1. Sync secrets from GitHub to Pulumi ESC
gh workflow run sync_secrets.yml

# 2. Create Docker secrets from ESC
./unified_docker_secrets.sh

# 3. Deploy the stack
./unified_deployment.sh

# 4. Monitor deployment
./unified_monitoring.sh
```

## 📋 Prerequisites

- Lambda Labs account with GH200 instances
- Docker Swarm initialized on master node
- Pulumi ESC access configured
- GitHub CLI authenticated

## 🏗️ Architecture

### Infrastructure
- **Backend**: Docker Swarm on Lambda Labs (192.222.51.151)
- **Frontend**: Vercel (app.sophia-intel.ai)
- **Orchestration**: Docker Swarm (NOT Kubernetes)
- **Secrets**: GitHub → Pulumi ESC → Docker Secrets

### Why Docker Swarm?
- **Simple**: Easy to manage for CEO-led development
- **Sufficient**: Handles our scale perfectly (1-80 users)
- **Proven**: All production deployments use it successfully
- **Fast**: Quick deployment cycles

## 🔐 Secret Management

### Unified Secret Flow
```
GitHub Organization Secrets
         ↓
GitHub Actions (sync_secrets.yml)
         ↓
Pulumi ESC (scoobyjava-org/default/sophia-ai-production)
         ↓
Docker Secrets (via unified_docker_secrets.sh)
         ↓
Application (via /run/secrets/*)
```

### Key Principles
- **NO** hardcoded secrets in any file
- **NO** .env files
- **ALL** secrets through Pulumi ESC
- **ONE** source of truth: GitHub Organization Secrets

## 📦 Services

All services are defined in `docker-compose.cloud.yml`:

### Core Services
- `sophia-backend`: Main API (port 8000)
- `mem0-server`: Memory service (port 8080)
- `cortex-aisql-server`: AI SQL service (port 8080)
- `v0dev-server`: UI generation (port 9030)

### Infrastructure
- `redis`: Caching (port 6379)
- `postgres`: Database (port 5432)
- `traefik`: Load balancer (ports 80/443)
- `prometheus`: Metrics (port 9090)
- `grafana`: Monitoring (port 3000)

## 🛠️ Unified Scripts

### `unified_deployment.sh`
Main deployment script that:
- Checks Swarm health
- Verifies secrets exist
- Deploys the stack
- Shows deployment status

### `unified_docker_secrets.sh`
Creates Docker secrets from Pulumi ESC:
- Extracts secrets using `esc env open`
- Creates Docker secrets safely
- Maps ESC keys to Docker secret names

### `unified_monitoring.sh`
Comprehensive monitoring that checks:
- Swarm cluster health
- Service states
- Container logs
- Resource usage
- Network connectivity

### `unified_troubleshooting.sh`
Network and service troubleshooting:
- Network discovery
- Service connectivity tests
- DNS resolution checks
- Port accessibility
- Container networking

## 📝 Common Tasks

### Deploy a New Version
```bash
# Build and push new image
docker build -t scoobyjava15/sophia-ai:latest .
docker push scoobyjava15/sophia-ai:latest

# Deploy
./unified_deployment.sh
```

### Update Secrets
```bash
# 1. Update in GitHub Organization Secrets
# 2. Run sync workflow
gh workflow run sync_secrets.yml

# 3. Recreate Docker secrets
./unified_docker_secrets.sh

# 4. Restart services
docker service update --force sophia-ai_sophia-backend
```

### Scale Services
```bash
# Scale backend to 3 replicas
docker service scale sophia-ai_sophia-backend=3
```

### View Logs
```bash
# All services
docker service logs sophia-ai_sophia-backend

# Follow logs
docker service logs -f sophia-ai_sophia-backend

# Specific container
docker logs <container_id>
```

## 🚨 Troubleshooting

### Service Won't Start
1. Check secrets: `docker secret ls`
2. Check logs: `docker service logs sophia-ai_<service>`
3. Verify image: `docker service ps sophia-ai_<service>`

### Can't Access Service
1. Check networks: `./unified_troubleshooting.sh`
2. Verify ports: `docker service inspect sophia-ai_<service>`
3. Check Traefik: `docker service logs sophia-ai_traefik`

### Secret Not Found
1. Verify in ESC: `esc env open default/sophia-ai-production`
2. Check Docker secret: `docker secret inspect <secret_name>`
3. Recreate: `./unified_docker_secrets.sh`

## 🎯 Best Practices

1. **Always** use unified scripts - no manual Docker commands
2. **Never** hardcode secrets or configuration
3. **Test** in development before production
4. **Monitor** after deployment
5. **Document** any changes to deployment process

## 🔄 Migration from Legacy

If you have legacy deployments:

1. Run cleanup: `python scripts/unified_deployment_cleanup.py`
2. Remove old compose files
3. Update all scripts to use unified approach
4. Test thoroughly before production

## 📚 Additional Resources

- [Unified Infrastructure](UNIFIED_INFRASTRUCTURE.md)
- [Unified Secret Management](UNIFIED_SECRET_MANAGEMENT_STRATEGY.md)
- [System Handbook](docs/system_handbook/00_SOPHIA_AI_SYSTEM_HANDBOOK.md)

---

**Remember**: If it's not "Unified", it's legacy and should not be used! 