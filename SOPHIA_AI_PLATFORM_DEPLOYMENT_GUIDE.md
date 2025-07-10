# Sophia AI Platform - K3s Deployment Guide

## 🚀 Overview

This guide covers the complete deployment of the Sophia AI platform including:
- **Unified Chat Interface** with WebSocket support
- **Unified Dashboard** with real-time monitoring
- **10 MCP Servers** (AI Memory, Gong, Snowflake, Slack, Linear, etc.)
- **Backend API** with FastAPI
- **Frontend** with React + TypeScript
- **Infrastructure** (Redis, PostgreSQL, Prometheus, Grafana)

## 📋 Prerequisites

1. **Lambda Labs Access**
   - SSH access to Lambda Labs instance (192.222.58.232)
   - SSH key configured (`~/.ssh/sophia2025.pem`)

2. **Docker Hub Account**
   - Username: `scoobyjava15`
   - Access token configured

3. **Environment Variables**
   ```bash
   export LAMBDA_LABS_IP="192.222.58.232"
   export DOCKER_REGISTRY="scoobyjava15"
   export IMAGE_TAG="latest"
   export PULUMI_ORG="scoobyjava-org"
   ```

4. **Local Tools**
   - Docker installed and running
   - Python 3.11+
   - Node.js 18+
   - SSH client

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Lambda Labs Infrastructure                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Frontend   │    │   Backend   │    │ MCP Gateway │         │
│  │  (React UI)  │◄──►│  (FastAPI)  │◄──►│  (Router)   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                    │                │
│         └───────────────────┴────────────────────┘               │
│                             │                                     │
│  ┌─────────────────────────┴─────────────────────────────┐      │
│  │                    MCP Servers                          │      │
│  ├─────────────┬─────────────┬─────────────┬────────────┤      │
│  │ AI Memory   │    Gong     │  Snowflake  │   Slack    │      │
│  │  (9001)     │   (9002)    │   (9003)    │  (9004)    │      │
│  ├─────────────┼─────────────┼─────────────┼────────────┤      │
│  │   Notion    │   Linear    │   GitHub    │  Codacy    │      │
│  │  (9005)     │   (9006)    │   (9007)    │  (9008)    │      │
│  ├─────────────┴─────────────┴─────────────┴────────────┤      │
│  │              Asana (9009)  │  Perplexity (9010)       │      │
│  └─────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │    Redis    │    │ PostgreSQL  │    │ Prometheus  │         │
│  │   (6379)    │    │   (5432)    │    │   (9090)    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# Run the complete deployment script
./scripts/deploy_sophia_platform.sh

# Select option 1 for full deployment
```

### Option 2: Python Deployment Script

```bash
# Run the Python deployment script
python scripts/deploy_complete_sophia_platform.py
```

### Option 3: Manual Deployment

Follow the step-by-step instructions below.

## 📝 Step-by-Step Deployment

### 1. Build Docker Images

```bash
# Backend
docker build -t scoobyjava15/sophia-backend:latest -f Dockerfile.production .

# Frontend
docker build -t scoobyjava15/sophia-frontend:latest -f frontend/Dockerfile frontend/

# MCP Servers
for server in ai-memory gong snowflake slack notion linear github codacy asana perplexity; do
    server_dir="infrastructure/mcp_servers/${server//-/_}_v2"
    if [ -d "$server_dir" ]; then
        docker build -t scoobyjava15/sophia-${server}:latest \
            -f ${server_dir}/Dockerfile ${server_dir}
    fi
done
```

### 2. Push Images to Docker Hub

```bash
# Login to Docker Hub
docker login -u scoobyjava15

# Push all images
docker push scoobyjava15/sophia-backend:latest
docker push scoobyjava15/sophia-frontend:latest

# Push MCP server images
for server in ai-memory gong snowflake slack notion linear github codacy asana perplexity; do
    docker push scoobyjava15/sophia-${server}:latest
done
```

### 3. Deploy Infrastructure via GitHub Actions (Recommended)

The deployment is fully automated through GitHub Actions:

```bash
# Ensure you're on main branch
git checkout main

# Push your changes
git push origin main

# Monitor deployment at:
# https://github.com/[your-org]/sophia-ai/actions
```

### 4. Manual Deployment (Emergency Only)

If GitHub Actions is unavailable:

```bash
# 1. SSH to Lambda Labs
ssh root@192.222.58.232

# 2. Pull latest configuration
cd /opt/sophia-ai
git pull origin main

# 3. Apply K3s manifests
kubectl apply -k k8s/overlays/production

# 4. Verify deployment
kubectl get pods -n sophia-ai-prod
kubectl get pods -n mcp-servers
```

## 🔍 Validation

### Check Service Health

```bash
# Backend API
curl http://192.222.58.232:8000/health

# Frontend
curl http://192.222.58.232:3000

# MCP Servers
for port in 9001 9002 9003 9004 9005 9006 9007 9008 9009 9010; do
    echo "Checking port $port..."
    curl http://192.222.58.232:$port/health
done

# Docker Stack Status
ssh root@192.222.58.232 'docker stack services sophia-ai'
```

### Monitor Logs

```bash
# Backend logs
ssh root@192.222.58.232 'docker service logs -f sophia-ai_sophia-backend'

# Frontend logs
ssh root@192.222.58.232 'docker service logs -f sophia-ai_sophia-frontend'

# MCP server logs
ssh root@192.222.58.232 'docker service logs -f sophia-ai_mcp-ai-memory-v2'
```

## 🌐 Access URLs

### Main Applications
- **Dashboard**: http://192.222.58.232:3000
- **API**: http://192.222.58.232:8000
- **API Documentation**: http://192.222.58.232:8000/docs
- **WebSocket Chat**: ws://192.222.58.232:8000/ws

### MCP Servers
- **AI Memory**: http://192.222.58.232:9001
- **Gong Integration**: http://192.222.58.232:9002
- **Snowflake**: http://192.222.58.232:9003
- **Slack**: http://192.222.58.232:9004
- **Notion**: http://192.222.58.232:9005
- **Linear**: http://192.222.58.232:9006
- **GitHub**: http://192.222.58.232:9007
- **Codacy**: http://192.222.58.232:9008
- **Asana**: http://192.222.58.232:9009
- **Perplexity**: http://192.222.58.232:9010

### Monitoring
- **Grafana**: http://192.222.58.232:3001
- **Prometheus**: http://192.222.58.232:9090

## 🛠️ Management Commands

### Scale Services

```bash
# Scale backend to 3 replicas
ssh root@192.222.58.232 'docker service scale sophia-ai_sophia-backend=3'

# Scale MCP gateway to 2 replicas
ssh root@192.222.58.232 'docker service scale sophia-ai_mcp-gateway=2'
```

### Update Services

```bash
# Force update a service
ssh root@192.222.58.232 'docker service update --force sophia-ai_sophia-backend'

# Update with new image
ssh root@192.222.58.232 'docker service update --image scoobyjava15/sophia-backend:v2 sophia-ai_sophia-backend'
```

### Remove Deployment

```bash
# Remove the entire stack
ssh root@192.222.58.232 'docker stack rm sophia-ai'

# Clean up volumes (CAUTION: This removes data)
ssh root@192.222.58.232 'docker volume prune -f'
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for local development:

```env
# Core Configuration
ENVIRONMENT=prod
PULUMI_ORG=scoobyjava-org
DOCKER_REGISTRY=scoobyjava15
IMAGE_TAG=latest

# Lambda Labs
LAMBDA_LABS_IP=192.222.58.232
LAMBDA_SSH_KEY_PATH=~/.ssh/sophia2025.pem

# Database
POSTGRES_PASSWORD=your-secure-password
POSTGRES_USER=sophia
POSTGRES_DB=sophia

# Redis
REDIS_URL=redis://redis:6379

# Monitoring
GRAFANA_PASSWORD=your-grafana-password
```

### Docker Secrets

Create secrets on Lambda Labs:

```bash
# Create secrets
echo "your-pulumi-token" | docker secret create pulumi_access_token -
echo "your-postgres-password" | docker secret create postgres_password -
echo "your-grafana-password" | docker secret create grafana_password -
echo "your-mem0-key" | docker secret create mem0_api_key -
```

## 🚨 Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   # Check service status
   docker service ps sophia-ai_sophia-backend --no-trunc

   # Check logs for errors
   docker service logs sophia-ai_sophia-backend --tail 100
   ```

2. **Cannot connect to Lambda Labs**
   ```bash
   # Check SSH key permissions
   chmod 600 ~/.ssh/sophia2025.pem

   # Test connection
   ssh -v root@192.222.58.232
   ```

3. **MCP servers not responding**
   ```bash
   # Check if ports are open
   nc -zv 192.222.58.232 9001

   # Check Docker network
   docker network ls
   ```

4. **Database connection issues**
   ```bash
   # Check PostgreSQL logs
   docker service logs sophia-ai_postgres

   # Test connection
   psql -h 192.222.58.232 -U sophia -d sophia
   ```

### Recovery Procedures

1. **Restart a failed service**
   ```bash
   docker service update --force sophia-ai_[service-name]
   ```

2. **Rollback to previous version**
   ```bash
   docker service rollback sophia-ai_[service-name]
   ```

3. **Emergency shutdown**
   ```bash
   docker stack rm sophia-ai
   ```

## 📊 Performance Optimization

### Resource Allocation

Update service resources in `docker-compose.cloud.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 8G
    reservations:
      cpus: '2.0'
      memory: 4G
```

### Scaling Strategy

- **Backend**: 3-5 replicas for high availability
- **Frontend**: 2-3 replicas for load distribution
- **MCP Gateway**: 2-3 replicas for routing
- **MCP Servers**: 1 replica each (stateful services)
- **Databases**: 1 replica (consider replication for production)

## 🔐 Security Considerations

1. **Use Docker Secrets** for all sensitive data
2. **Enable TLS** for all external endpoints
3. **Configure firewall rules** on Lambda Labs
4. **Regular security updates** for all images
5. **Monitor access logs** for suspicious activity

## 📈 Next Steps

1. **Configure DNS** to point to Lambda Labs IP
2. **Set up SSL certificates** with Let's Encrypt
3. **Configure backup strategies** for databases
4. **Set up monitoring alerts** in Grafana
5. **Implement CI/CD pipeline** for automated deployments

## 🆘 Support

For issues or questions:
1. Check the logs first
2. Review this deployment guide
3. Check the [System Handbook](docs/system_handbook/00_SOPHIA_AI_SYSTEM_HANDBOOK.md)
4. Create an issue in the GitHub repository

---

**Last Updated**: January 2025
**Version**: 1.0.0
**Status**: Production Ready

## Deployment Architecture

### Infrastructure Stack
- **Compute**: Lambda Labs H100 GPU Instance (192.222.58.232)
- **Orchestration**: K3s (Lightweight Kubernetes)
- **Container Registry**: Docker Hub (scoobyjava15)
- **Frontend Hosting**: Vercel
- **Secrets Management**: Pulumi ESC
- **CI/CD**: GitHub Actions

### Service Architecture

#### Core Services (Kubernetes Deployments)
1. **Backend API** - FastAPI application
2. **PostgreSQL** - Primary database  
3. **Redis** - Cache and pub/sub
4. **MCP Gateway** - MCP server orchestration
5. **16 MCP Servers** - Specialized microservices

#### K3s Manifest Structure
```
k8s/
├── base/
│   ├── backend/
│   ├── database/
│   ├── mcp-gateway/
│   └── mcp-servers/
├── overlays/
│   ├── production/
│   └── staging/
└── kustomization.yaml
```

## Deployment Commands

### Initial Setup (One Time)

```bash
# On Lambda Labs instance
# Install K3s
curl -sfL https://get.k3s.io | sh -

# Get kubeconfig for remote access
sudo cat /etc/rancher/k3s/k3s.yaml

# Create namespaces
kubectl create namespace sophia-ai-prod
kubectl create namespace mcp-servers
kubectl create namespace monitoring
```

### Deploy Application

```bash
# Via GitHub Actions (push to main branch)
git push origin main

# Or manually
kubectl apply -k k8s/overlays/production
```

### Verify Deployment

```bash
# Check all pods
kubectl get pods -A

# Check specific namespace
kubectl get pods -n sophia-ai-prod
kubectl get pods -n mcp-servers

# Get service endpoints
kubectl get svc -A

# View ingress routes
kubectl get ingress -A
```

## Monitoring and Management

### View Logs

```bash
# Backend API logs
kubectl logs -n sophia-ai-prod deployment/backend-api -f

# MCP Gateway logs  
kubectl logs -n mcp-servers deployment/mcp-gateway -f

# Specific MCP server logs
kubectl logs -n mcp-servers deployment/mcp-slack -f
```

### Scale Services

```bash
# Scale backend API
kubectl scale deployment backend-api -n sophia-ai-prod --replicas=3

# Scale MCP servers
kubectl scale deployment -n mcp-servers -l tier=mcp --replicas=2
```

### Update Services

```bash
# Update via rolling deployment
kubectl set image deployment/backend-api -n sophia-ai-prod \
  backend-api=scoobyjava15/sophia-backend:v2.0.0

# Or apply updated manifests
kubectl apply -k k8s/overlays/production
```

### Health Checks

```bash
# Cluster health
kubectl get nodes
kubectl top nodes

# Pod health
kubectl get pods -A
kubectl top pods -A

# Service endpoints
curl https://api.sophia-ai.com/health
curl https://mcp.sophia-ai.com/health
```

## Secret Management

All secrets are managed through Pulumi ESC and automatically synced to K3s:

```bash
# List secrets (names only)
kubectl get secrets -n sophia-ai-prod

# Secrets are automatically created from Pulumi ESC
# Never create secrets manually
```

## Troubleshooting

### Common Issues

1. **Pod CrashLoopBackOff**
```bash
kubectl describe pod [pod-name] -n [namespace]
kubectl logs [pod-name] -n [namespace] --previous
```

2. **Service Not Accessible**
```bash
# Check service endpoints
kubectl get endpoints -n [namespace]

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  nslookup [service-name].[namespace].svc.cluster.local
```

3. **Resource Constraints**
```bash
# Check resource usage
kubectl top nodes
kubectl top pods -A

# Check resource limits
kubectl describe pod [pod-name] -n [namespace]
```

### Emergency Procedures

```bash
# Rollback deployment
kubectl rollout undo deployment/[deployment-name] -n [namespace]

# Emergency pod deletion
kubectl delete pod [pod-name] -n [namespace] --force --grace-period=0

# Restart all pods in namespace
kubectl delete pods --all -n [namespace]
```

## Backup and Recovery

### Backup Database
```bash
# Create database backup
kubectl exec -n sophia-ai-prod deployment/postgres -- \
  pg_dump -U postgres sophia_ai > backup.sql
```

### Restore Database
```bash
# Restore from backup
kubectl exec -i -n sophia-ai-prod deployment/postgres -- \
  psql -U postgres sophia_ai < backup.sql
```

## Security Considerations

1. **Network Policies**: Implemented via K3s default policies
2. **RBAC**: Role-based access control configured
3. **Secrets**: All secrets encrypted at rest
4. **TLS**: Automatic via cert-manager and Let's Encrypt
5. **Pod Security**: Security contexts enforced

## Maintenance

### Update K3s
```bash
# On Lambda Labs instance
curl -sfL https://get.k3s.io | sh -
```

### Cleanup Old Resources
```bash
# Remove completed jobs
kubectl delete jobs --field-selector status.successful=1 -A

# Remove evicted pods
kubectl delete pods --field-selector status.phase=Failed -A
```

## Monitoring Stack

Prometheus and Grafana are deployed for monitoring:

```bash
# Access Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Visit http://localhost:3000

# Access Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Visit http://localhost:9090
```

## References

- K3s Documentation: https://docs.k3s.io/
- Kubernetes Documentation: https://kubernetes.io/docs/
- GitHub Actions Workflows: `.github/workflows/`
- Architecture Documentation: `docs/system_handbook/`
