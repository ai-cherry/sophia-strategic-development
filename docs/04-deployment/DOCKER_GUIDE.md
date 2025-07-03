# Docker Deployment Guide

## Overview

Sophia AI uses a streamlined Docker setup with multi-stage builds and UV for fast, efficient containerization. This guide covers development, testing, and production deployment.

## Quick Start

### Development

```bash
# Start all services in development mode
docker-compose up

# Start with specific services
docker-compose up sophia-backend redis postgres

# Start with development tools
docker-compose --profile dev-tools up
```

### Production

```bash
# Build and start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale sophia-backend=3
```

## Architecture

### Multi-Stage Dockerfile

Our canonical `Dockerfile` uses multi-stage builds:

1. **base**: Common setup for all stages
2. **dependencies**: UV-based dependency installation
3. **production**: Minimal runtime with only necessary files
4. **development**: Full source with hot reload
5. **testing**: Test execution environment

### Docker Compose Structure

- `docker-compose.yml`: Base configuration
- `docker-compose.override.yml`: Development overrides (auto-loaded)
- `docker-compose.prod.yml`: Production settings

## Services

### Core Services

#### sophia-backend
- Main FastAPI application
- Port: 8000
- Health endpoint: `/api/health`

#### mem0-server
- Memory management MCP server
- Port: 8080
- Requires: MEM0_API_KEY

#### cortex-server
- Snowflake Cortex AI integration
- Port: 8081
- Requires: Snowflake credentials

### Infrastructure

#### redis
- Session and cache storage
- Port: 6379
- Persistence: AOF enabled

#### postgres
- Primary database
- Port: 5432
- Version: PostgreSQL 16

### Development Tools

#### pgadmin
- Database management UI
- Port: 5050
- Profile: `tools`

#### mailhog
- Email testing
- SMTP: 1025
- Web UI: 8025
- Profile: `dev-tools`

#### jupyter
- Data exploration
- Port: 8888
- Profile: `dev-tools`

## Building Images

### Development Build

```bash
# Build with development target
docker build --target development -t sophia-ai:dev .

# Build specific MCP server
docker build -f docker/Dockerfile.mcp-server \
  --build-arg MCP_SERVER_PATH=backend/mcp_servers/mem0_openmemory \
  --build-arg MCP_SERVER_MODULE=enhanced_mem0_server \
  -t mem0-server:latest .
```

### Production Build

```bash
# Build with production target
docker build --target production -t sophia-ai:prod .

# Build with cache
docker build --cache-from sophia-ai:cache --target production -t sophia-ai:prod .
```

## Environment Variables

### Required

```bash
# Pulumi ESC
PULUMI_ORG=scoobyjava-org
PULUMI_ACCESS_TOKEN=<your-token>

# Database
POSTGRES_PASSWORD=<secure-password>

# MCP Servers
MEM0_API_KEY=<mem0-key>
SNOWFLAKE_ACCOUNT=<account>
SNOWFLAKE_USER=<user>
SNOWFLAKE_PASSWORD=<password>
```

### Optional

```bash
# Ports
BACKEND_PORT=8000
REDIS_PORT=6379
POSTGRES_PORT=5432

# Environment
ENVIRONMENT=dev|staging|prod
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR

# Build
BUILD_TARGET=development|production
PYTHON_VERSION=3.12
```

## Networking

All services use the `sophia-network` bridge network with subnet `172.20.0.0/16`.

Internal service communication:
- Backend → Redis: `redis:6379`
- Backend → Postgres: `postgres:5432`
- Backend → MCP: `mem0-server:8080`

## Volumes

### Persistent Data

- `redis_data`: Redis persistence
- `postgres_data`: PostgreSQL data
- `prometheus_data`: Metrics storage
- `grafana_data`: Dashboard config

### Development Mounts

```yaml
volumes:
  - ./backend:/app/backend:cached
  - ./config:/app/config:cached
```

## Health Checks

All services include health checks:

```bash
# Check all services
docker-compose ps

# Check specific service health
docker inspect sophia-backend | jq '.[0].State.Health'
```

## Monitoring

Production deployment includes:

- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Dashboards (port 3001)

## Troubleshooting

### Build Issues

```bash
# Clean build without cache
docker build --no-cache -t sophia-ai:dev .

# Check build context size
du -sh .
```

### Container Logs

```bash
# View logs
docker-compose logs -f sophia-backend

# View last 100 lines
docker-compose logs --tail=100 sophia-backend
```

### Shell Access

```bash
# Development container
docker-compose exec sophia-backend /bin/bash

# Production container (no shell)
docker-compose exec sophia-backend python -c "print('test')"
```

### Resource Usage

```bash
# Check resource usage
docker stats

# Limit resources in production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Best Practices

1. **Always use .dockerignore** to minimize build context
2. **Use multi-stage builds** to reduce image size
3. **Pin base image versions** for reproducibility
4. **Run as non-root user** (appuser)
5. **Use health checks** for all services
6. **Set resource limits** in production
7. **Use BuildKit** for faster builds:
   ```bash
   DOCKER_BUILDKIT=1 docker build .
   ```

## Migration from Legacy

If upgrading from old Docker setup:

1. Stop all running containers
2. Run archive script: `python scripts/archive_legacy_docker_files.py`
3. Pull latest changes
4. Start with new setup: `docker-compose up`

## Security

- No secrets in images (use Pulumi ESC)
- Non-root user execution
- Minimal attack surface in production
- Network isolation between services
- Read-only root filesystem (where possible)

## CI/CD Integration

GitHub Actions workflow example:

```yaml
- name: Build and test
  run: |
    docker build --target testing -t sophia-ai:test .
    docker run sophia-ai:test

- name: Build production
  run: |
    docker build --target production -t sophia-ai:prod .
    docker tag sophia-ai:prod ${{ secrets.REGISTRY }}/sophia-ai:${{ github.sha }}
    docker push ${{ secrets.REGISTRY }}/sophia-ai:${{ github.sha }}
``` 