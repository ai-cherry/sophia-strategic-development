# Docker Cloud Deployment on Lambda Labs

This guide covers deploying Sophia AI to Lambda Labs infrastructure using Docker Cloud/Swarm with enterprise-grade patterns.

## 🎯 Overview

Sophia AI is designed for **cloud-native deployment** on Lambda Labs infrastructure, not local execution. All services are containerized and deployed using Docker Swarm for production scalability.

### Architecture

```
GitHub Repository → Docker Registry (scoobyjava15) → Lambda Labs Infrastructure → Docker Swarm Cluster
```

## 🏗️ Infrastructure Components

### Lambda Labs Configuration
- **Instance ID**: `7e7b1e5f53c44a26bd574e4266e96194`
- **Instance Name**: `sophia-ai-production`
- **IP Address**: `104.171.202.64`
- **Type**: `gpu_8x_v100` (8x Tesla V100 16GB)
- **Region**: `us-south-1` (Texas, USA)
- **Specs**: 92 vCPUs, 448 GiB RAM, 6041 GiB storage

### Docker Registry
- **Registry**: `scoobyjava15` (Docker Hub)
- **Images**:
  - `scoobyjava15/sophia-ai:latest` (Main backend)
  - `scoobyjava15/sophia-ai-mem0:latest` (Mem0 MCP server)
  - `scoobyjava15/sophia-ai-cortex:latest` (Cortex AISQL MCP server)

## 📋 Deployment Files

### Core Configuration Files

#### 1. `docker-compose.cloud.yml`
**Purpose**: Docker Swarm stack configuration for Lambda Labs
**Features**:
- Multi-replica services with auto-scaling
- GPU resource allocation for AI workloads
- Overlay networking for service communication
- Traefik load balancing with SSL termination
- Prometheus/Grafana monitoring stack
- Docker secrets for secure credential management

#### 2. `Dockerfile` (Multi-stage)
**Purpose**: Production-optimized container builds
**Features**:
- UV-based dependency management (6x faster)
- Multi-stage builds for minimal image size
- Non-root user security
- Health checks for all services

#### 3. `docker/Dockerfile.mcp-server`
**Purpose**: Specialized MCP server containers
**Features**:
- Parameterized builds for different MCP servers
- Optimized for AI/ML workloads
- FastAPI-based REST interfaces

## 🚀 Deployment Process

### Prerequisites

1. **Docker Cloud Setup** ✅
   ```bash
   # Already completed
   docker login
   docker buildx create --name sophia-ai-builder --use
   ```

2. **Lambda Labs Instance** ✅
   ```bash
   # Instance already launched and configured
   # SSH Key: cae55cb8d0f5443cbdf9129f7cec8770
   # IP: 104.171.202.64
   ```

3. **Docker Swarm Initialization**
   ```bash
   # On Lambda Labs instance
   docker swarm init
   ```

### Automated Deployment

Use the comprehensive deployment script:

```bash
# Production deployment
python scripts/deploy_to_lambda_labs_cloud.py --environment prod

# Staging deployment
python scripts/deploy_to_lambda_labs_cloud.py --environment staging

# Dry run (test without changes)
python scripts/deploy_to_lambda_labs_cloud.py --environment prod --dry-run
```

### Manual Deployment Steps

#### 1. Build and Push Images

```bash
# Build main Sophia AI image
docker build --target production -t scoobyjava15/sophia-ai:latest .
docker push scoobyjava15/sophia-ai:latest

# Build Mem0 MCP server
docker build -f docker/Dockerfile.mcp-server \
  --build-arg MCP_SERVER_PATH=backend/mcp_servers/mem0_openmemory \
  --build-arg MCP_SERVER_MODULE=enhanced_mem0_server \
  --build-arg MCP_SERVER_PORT=8080 \
  -t scoobyjava15/sophia-ai-mem0:latest .
docker push scoobyjava15/sophia-ai-mem0:latest

# Build Cortex AISQL MCP server
docker build -f docker/Dockerfile.mcp-server \
  --build-arg MCP_SERVER_PATH=backend/mcp_servers/cortex_aisql \
  --build-arg MCP_SERVER_MODULE=cortex_mcp_server \
  --build-arg MCP_SERVER_PORT=8080 \
  -t scoobyjava15/sophia-ai-cortex:latest .
docker push scoobyjava15/sophia-ai-cortex:latest
```

#### 2. Setup Docker Secrets

```bash
# Create secrets (placeholders - update with real values from Pulumi ESC)
echo "PLACEHOLDER_PULUMI_ACCESS_TOKEN" | docker secret create pulumi_access_token -
echo "PLACEHOLDER_POSTGRES_PASSWORD" | docker secret create postgres_password -
echo "PLACEHOLDER_MEM0_API_KEY" | docker secret create mem0_api_key -
echo "PLACEHOLDER_SNOWFLAKE_ACCOUNT" | docker secret create snowflake_account -
echo "PLACEHOLDER_SNOWFLAKE_USER" | docker secret create snowflake_user -
echo "PLACEHOLDER_SNOWFLAKE_PASSWORD" | docker secret create snowflake_password -
echo "PLACEHOLDER_GRAFANA_PASSWORD" | docker secret create grafana_password -
```

#### 3. Deploy Stack

```bash
# Set environment variables
export DOCKER_REGISTRY=scoobyjava15
export IMAGE_TAG=latest
export ENVIRONMENT=prod

# Deploy stack
docker stack deploy -c docker-compose.cloud.yml sophia-ai-prod
```

#### 4. Verify Deployment

```bash
# Check stack status
docker stack services sophia-ai-prod

# Check service logs
docker service logs sophia-ai-prod_sophia-backend

# Check service health
docker service ps sophia-ai-prod_sophia-backend
```

## 🔐 Secret Management

### Pulumi ESC Integration

All secrets are managed through Pulumi ESC and automatically synchronized:

```bash
# Secrets are retrieved from Pulumi ESC sophia-ai-production stack
# No manual secret management required
# All secrets available via: values.sophia.* structure
```

### Docker Secrets Update

To update secrets with real values from Pulumi ESC:

```bash
# Remove placeholder secrets
docker secret rm pulumi_access_token

# Create with real value from Pulumi ESC
pulumi env get scoobyjava-org/default/sophia-ai-production values.sophia.platform.pulumi_access_token | \
  docker secret create pulumi_access_token -
```

## 🌐 Service Access

### Service Endpoints

| Service | Internal Port | External Port | URL |
|---------|---------------|---------------|-----|
| Sophia Backend | 8000 | 8000 | `http://104.171.202.64:8000` |
| Mem0 MCP Server | 8080 | 8080 | `http://104.171.202.64:8080` |
| Cortex MCP Server | 8080 | 8081 | `http://104.171.202.64:8081` |
| Traefik Dashboard | 8080 | 8090 | `http://104.171.202.64:8090` |
| Grafana | 3000 | 3000 | `http://104.171.202.64:3000` |
| Prometheus | 9090 | 9090 | `http://104.171.202.64:9090` |

### Health Checks

```bash
# Main API health
curl http://104.171.202.64:8000/api/health

# Mem0 server health
curl http://104.171.202.64:8080/health

# Cortex server health
curl http://104.171.202.64:8081/health
```

## 📊 Monitoring & Scaling

### Auto-scaling Configuration

Services are configured with auto-scaling based on resource utilization:

```yaml
deploy:
  mode: replicated
  replicas: 3  # Default replicas
  placement:
    constraints:
      - node.labels.gpu == true  # GPU-enabled nodes
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 2G
```

### Monitoring Stack

- **Prometheus**: Metrics collection from all services
- **Grafana**: Visualization dashboards
- **Traefik**: Load balancer metrics and SSL termination

### Scaling Commands

```bash
# Scale Sophia backend to 5 replicas
docker service scale sophia-ai-prod_sophia-backend=5

# Scale Mem0 server to 3 replicas
docker service scale sophia-ai-prod_mem0-server=3

# Check current scaling
docker service ls
```

## 🔄 Updates & Rollbacks

### Rolling Updates

```bash
# Update main service
docker service update --image scoobyjava15/sophia-ai:v2.0 sophia-ai-prod_sophia-backend

# Update with environment variable
docker service update --env-add NEW_VAR=value sophia-ai-prod_sophia-backend
```

### Rollbacks

```bash
# Rollback to previous version
docker service rollback sophia-ai-prod_sophia-backend

# Check rollback status
docker service ps sophia-ai-prod_sophia-backend
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Not Starting
```bash
# Check service logs
docker service logs --tail 50 sophia-ai-prod_sophia-backend

# Check service events
docker service ps sophia-ai-prod_sophia-backend
```

#### 2. Image Pull Failures
```bash
# Verify registry access
docker pull scoobyjava15/sophia-ai:latest

# Check registry credentials
docker login
```

#### 3. Secret Access Issues
```bash
# List secrets
docker secret ls

# Recreate secret
docker secret rm postgres_password
echo "new_password" | docker secret create postgres_password -
```

#### 4. Network Connectivity
```bash
# Check overlay networks
docker network ls

# Inspect network
docker network inspect sophia-ai-prod_sophia-overlay
```

### Performance Monitoring

```bash
# Check resource usage
docker stats

# Service-specific stats
docker service ps sophia-ai-prod_sophia-backend --format "table {{.Name}}\t{{.CurrentState}}\t{{.Error}}"

# Node resource usage
docker node ls
```

## 📝 Best Practices

### 1. Resource Management
- Use resource limits and reservations
- Monitor GPU utilization for AI workloads
- Configure appropriate auto-scaling thresholds

### 2. Security
- Use Docker secrets for all credentials
- Implement least-privilege access
- Regular security updates for base images

### 3. Networking
- Use overlay networks for service communication
- Implement proper load balancing with Traefik
- Configure SSL certificates for production

### 4. Monitoring
- Set up comprehensive monitoring with Prometheus/Grafana
- Configure alerting for critical metrics
- Regular health checks for all services

### 5. Backup & Recovery
- Regular database backups
- Configuration backup procedures
- Disaster recovery planning

## 🎯 Next Steps

1. **DNS Configuration**: Set up custom domains pointing to Lambda Labs IP
2. **SSL Certificates**: Configure automatic SSL via Traefik Let's Encrypt
3. **Monitoring Alerts**: Set up Prometheus alerting rules
4. **Backup Strategy**: Implement automated backup procedures
5. **CI/CD Integration**: Connect GitHub Actions for automated deployments

---

**Note**: This configuration is specifically designed for Lambda Labs infrastructure and Docker Cloud deployment. All services run in containers with no local execution required.
