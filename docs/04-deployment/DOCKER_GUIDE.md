# Docker Cloud Deployment Guide

## Overview

Sophia AI uses Docker Cloud deployment with Docker Swarm orchestration on Lambda Labs infrastructure. This guide covers building, testing, and production deployment to our cloud infrastructure.

## Quick Start

### Lambda Labs Deployment

```bash
# SSH to Lambda Labs instance
ssh ubuntu@104.171.202.64

# Initialize Docker Swarm (first time only)
docker swarm init

# Deploy the stack
docker stack deploy -c docker-compose.cloud.yml sophia-ai-prod

# Check services
docker stack services sophia-ai-prod
```

### ⚠️ Important: NO Local Docker Deployment

- **All deployments target Lambda Labs infrastructure**
- **Use docker-compose.cloud.yml for production**
- **Secrets managed via Pulumi ESC (no .env files)**
- **Registry: scoobyjava15 on Docker Hub**

## Architecture

### Multi-Stage Dockerfile

Our canonical `Dockerfile` uses multi-stage builds:

1. **base**: Common setup for all stages
2. **dependencies**: UV-based dependency installation
3. **production**: Minimal runtime with only necessary files
4. **development**: Full source (for building only)
5. **testing**: Test execution environment

### Docker Compose Structure

- `docker-compose.cloud.yml`: Production Swarm configuration (PRIMARY)
- `docker-compose.yml`: Base configuration reference
- `docker-compose.override.yml`: Local development overrides (reference only)
- `docker-compose.prod.yml`: Production overrides

## Services

### Core Services

#### sophia-backend
- Main FastAPI application
- Port: 8000 (published)
- Replicas: 3-10 (auto-scaling)
- Health endpoint: `/api/health`

#### mem0-server
- Memory management MCP server
- Port: 8080 (published)
- Replicas: 2-5
- Secrets: Via Docker Secrets

#### cortex-aisql-server
- Snowflake Cortex AI integration
- Port: 8080 (internal), 8080 (published)
- Replicas: 2-5
- Secrets: Via Docker Secrets

### Infrastructure

#### redis
- Session and cache storage
- Port: 6379
- Mode: Replicated with persistence
- Resource limits: 1GB RAM

#### postgres
- Primary database
- Port: 5432 (internal only)
- Version: PostgreSQL 16
- Persistent volume on Lambda Labs

## Building and Pushing Images

### Build for Production

```bash
# Build production image
docker build --target production -t scoobyjava15/sophia-ai:latest .

# Build with specific version
docker build --target production -t scoobyjava15/sophia-ai:v1.2.3 .

# Build MCP server
docker build -f docker/Dockerfile.mcp-server \
  -t scoobyjava15/sophia-mcp:latest .
```

### Push to Registry

```bash
# Login to Docker Hub
docker login -u scoobyjava15

# Push images
docker push scoobyjava15/sophia-ai:latest
docker push scoobyjava15/sophia-ai:v1.2.3
docker push scoobyjava15/sophia-mcp:latest
```

## Secret Management

### Pulumi ESC Integration

All secrets are managed through Pulumi ESC:

```bash
# Secrets are automatically available via:
# - GitHub Organization → Pulumi ESC → Docker Secrets
# - No manual .env files needed
```

### Docker Secrets

```yaml
secrets:
  postgres_password:
    external: true
  snowflake_account:
    external: true
  openai_api_key:
    external: true
```

## Deployment Commands

### Deploy Stack

```bash
# Deploy or update the stack
docker stack deploy -c docker-compose.cloud.yml sophia-ai-prod

# Deploy with specific image version
IMAGE_TAG=v1.2.3 docker stack deploy -c docker-compose.cloud.yml sophia-ai-prod
```

### Scale Services

```bash
# Scale backend service
docker service scale sophia-ai-prod_sophia-backend=5

# Scale MCP servers
docker service scale sophia-ai-prod_mem0-server=3
docker service scale sophia-ai-prod_cortex-aisql-server=4
```

### Update Services

```bash
# Update with new image
docker service update --image scoobyjava15/sophia-ai:v2.0 sophia-ai-prod_sophia-backend

# Rolling update with health checks
docker service update --update-parallelism 1 --update-delay 30s sophia-ai-prod_sophia-backend
```

## Monitoring

### Service Status

```bash
# Check all services
docker stack services sophia-ai-prod

# Check service details
docker service ps sophia-ai-prod_sophia-backend

# View logs
docker service logs --tail 100 sophia-ai-prod_sophia-backend
docker service logs -f sophia-ai-prod_sophia-backend
```

### Health Checks

All services include health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Metrics

Production deployment includes:

- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Dashboards (port 3001)
- **Metrics endpoint**: `/metrics` on each service

## Networking

### Overlay Network

Docker Swarm uses overlay network for service communication:

```yaml
networks:
  sophia-overlay:
    driver: overlay
    attachable: true
```

### Service Discovery

Internal service communication via service names:
- Backend → Redis: `redis:6379`
- Backend → Postgres: `postgres:5432`
- Backend → MCP: `mem0-server:8080`

## Volumes

### Persistent Storage

All persistent data stored on Lambda Labs NVMe:

```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      device: /mnt/nvme/postgres
  redis_data:
    driver: local
    driver_opts:
      device: /mnt/nvme/redis
```

## Troubleshooting

### SSH to Lambda Labs

```bash
# Connect to instance
ssh ubuntu@104.171.202.64

# Check Docker status
docker node ls
docker stack ps sophia-ai-prod
```

### Service Issues

```bash
# Check failing service
docker service ps sophia-ai-prod_sophia-backend --no-trunc

# View error logs
docker service logs sophia-ai-prod_sophia-backend 2>&1 | grep ERROR

# Force service update
docker service update --force sophia-ai-prod_sophia-backend
```

### Resource Usage

```bash
# Check node resources
docker node inspect self --pretty

# Monitor resource usage
docker stats $(docker ps -q)
```

## Best Practices

1. **Always use Docker Swarm** for production deployment
2. **Push images to scoobyjava15 registry** before deployment
3. **Use Docker Secrets** for sensitive data (via Pulumi ESC)
4. **Set resource limits** for all services
5. **Implement health checks** for zero-downtime deployments
6. **Use rolling updates** with proper delays
7. **Monitor with Prometheus/Grafana** for production insights

## Security

- **No secrets in images** - Use Pulumi ESC + Docker Secrets
- **Non-root user execution** (appuser)
- **Network isolation** between services
- **TLS encryption** for overlay network
- **Regular security scans** of images
- **Minimal attack surface** in production images

## CI/CD Integration

GitHub Actions workflow for Docker Cloud:

```yaml
- name: Build and push
  run: |
    # Build production image
    docker build --target production -t scoobyjava15/sophia-ai:${{ github.sha }} .

    # Push to registry
    echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
    docker push scoobyjava15/sophia-ai:${{ github.sha }}

    # Deploy to Lambda Labs (via SSH action)
    ssh ubuntu@104.171.202.64 "IMAGE_TAG=${{ github.sha }} docker stack deploy -c docker-compose.cloud.yml sophia-ai-prod"
```

## Disaster Recovery

### Backup

```bash
# Backup PostgreSQL
docker exec $(docker ps -q -f name=sophia-ai-prod_postgres) pg_dump -U sophia sophia > backup.sql

# Backup Redis
docker exec $(docker ps -q -f name=sophia-ai-prod_redis) redis-cli BGSAVE
```

### Rollback

```bash
# Rollback to previous version
docker service rollback sophia-ai-prod_sophia-backend

# Deploy specific version
IMAGE_TAG=v1.2.2 docker stack deploy -c docker-compose.cloud.yml sophia-ai-prod
```
