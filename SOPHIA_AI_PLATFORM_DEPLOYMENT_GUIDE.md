# Sophia AI Complete Platform Deployment Guide

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
        docker build -t scoobyjava15/sophia-${server}-v2:latest \
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
    docker push scoobyjava15/sophia-${server}-v2:latest
done
```

### 3. Deploy to Lambda Labs

```bash
# Copy compose file to Lambda Labs
scp docker-compose.cloud.yml root@192.222.58.232:/opt/sophia-ai/

# SSH to Lambda Labs
ssh root@192.222.58.232

# Initialize Docker Swarm (if needed)
docker swarm init

# Create required directories
mkdir -p /opt/sophia-ai/data/{redis,postgres,prometheus,grafana,traefik}

# Deploy the stack
cd /opt/sophia-ai
docker stack deploy -c docker-compose.cloud.yml sophia-ai --with-registry-auth
```

### 4. Start Local MCP Servers (Development)

```bash
# Start MCP servers locally
cd mcp-servers

# AI Memory Server
cd ai_memory && MCP_SERVER_PORT=9001 python ai_memory_mcp_server.py &

# Codacy Server
cd ../codacy && MCP_SERVER_PORT=9008 python codacy_mcp_server.py &

# Linear Server
cd ../linear && MCP_SERVER_PORT=9006 python linear_mcp_server.py &

# Continue for other servers...
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
