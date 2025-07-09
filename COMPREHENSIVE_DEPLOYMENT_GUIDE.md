# 🚀 Comprehensive Sophia AI Deployment Guide

## Overview

This guide covers the complete deployment of Sophia AI platform with all 29 MCP servers and integrated capabilities to Lambda Labs using Docker Swarm orchestration.

## 🏗️ Architecture

### Deployment Stack
- **Orchestration**: Docker Swarm (single-node initially, scalable to multi-node)
- **Registry**: Docker Hub (`scoobyjava15/*`)
- **Infrastructure**: Lambda Labs GPU servers
- **Secret Management**: Pulumi ESC → Docker Swarm Secrets
- **CI/CD**: GitHub Actions automated workflows

### Complete Service Inventory

#### Core AI Orchestration (4 services)
1. **AI Memory MCP Server** (port 9001) - Stores and recalls architectural decisions
2. **Codacy MCP Server** (port 3008) - Real-time code quality analysis
3. **Anthropic MCP Server** (port 9002) - Official MCP implementations
4. **MCP Inspector** (port 9003) - Debugging and development tools

#### Unified AI Agent Authentication System (13 services)
5. **GitHub Agent** (port 9010) - Repository operations via CLI
6. **Pulumi Agent** (port 9011) - Infrastructure as code management
7. **Docker Agent** (port 9012) - Container management
8. **Vercel Agent** (port 9013) - Frontend deployments
9. **Snowflake Agent** (port 9014) - Data operations
10. **Lambda Labs Agent** (port 9015) - Server instance control
11. **Estuary Flow Agent** (port 9016) - Data flow management
12. **OpenAI Agent** (port 9017) - Language processing
13. **Anthropic Agent** (port 9018) - Language processing
14. **Slack Agent** (port 9019) - Communication
15. **Linear Agent** (port 9020) - Project management
16. **HubSpot Agent** (port 9021) - CRM operations
17. **Gong Agent** (port 9022) - Call analysis

#### External Repository Integration (8 services)
18. **Microsoft Playwright** (port 9030) - Browser automation patterns
19. **Figma Context** (port 9031) - Design-to-code workflows
20. **Snowflake Cortex Official** (port 9032) - Official Snowflake AI
21. **Portkey Admin** (port 9033) - AI gateway optimization
22. **OpenRouter Search** (port 9034) - 200+ AI model access
23. **Davidamom Snowflake** (port 9035) - Community Snowflake patterns
24. **Dynamike Snowflake** (port 9036) - Performance-optimized Snowflake
25. **Isaacwasserman Snowflake** (port 9037) - Specialized Snowflake ops

#### Additional Services (4 services)
26. **Mem0 Server** (port 8080) - OpenMemory MCP Server
27. **Cortex AISQL Server** (port 8081) - AI-optimized SQL
28. **WebFetch Server** (port 9040) - Web content retrieval
29. **V0.dev Server** (port 9030) - AI-powered UI generation

#### Infrastructure Services
- **Sophia Backend** (port 8000) - Main FastAPI application
- **PostgreSQL** (port 5432) - Primary database
- **Redis** (port 6379) - Caching and sessions
- **Prometheus** (port 9090) - Metrics collection
- **Grafana** (port 3000) - Monitoring dashboards
- **Traefik** (ports 80, 443, 8090) - Reverse proxy and load balancer

## 🔧 Prerequisites

### Required Secrets in GitHub Organization
All secrets must be configured in the GitHub organization at: https://github.com/organizations/ai-cherry/settings/secrets/actions

```bash
# Core Platform
DOCKER_PERSONAL_ACCESS_TOKEN
PULUMI_ACCESS_TOKEN
LAMBDA_LABS_SSH_KEY

# AI Services
OPENAI_API_KEY
ANTHROPIC_API_KEY

# Business Intelligence
GONG_ACCESS_KEY
HUBSPOT_ACCESS_TOKEN
LINEAR_API_KEY
SLACK_BOT_TOKEN

# Infrastructure
VERCEL_ACCESS_TOKEN
GITHUB_TOKEN
LAMBDA_API_KEY

# Database
POSTGRES_PASSWORD
REDIS_PASSWORD
GRAFANA_PASSWORD

# Snowflake
SNOWFLAKE_ACCOUNT
SNOWFLAKE_USER
SNOWFLAKE_PASSWORD
```

### Lambda Labs Setup
- GPU server with Ubuntu 22.04
- Docker and Docker Compose installed
- SSH access configured
- Minimum 32GB RAM, 8 CPU cores, 1TB storage

## 🚀 Deployment Methods

### Method 1: Automated GitHub Actions (Recommended)

1. **Trigger Deployment**:
   ```bash
   # Push to main branch triggers automatic deployment
   git push origin main

   # Or trigger manually with options
   gh workflow run "🚀 Unified Sophia AI Deployment" \
     --field environment=production \
     --field deploy_mcp_servers=true
   ```

2. **Monitor Progress**:
   ```bash
   # Watch the workflow
   gh run watch

   # View logs
   gh run view --log
   ```

### Method 2: Manual Deployment

1. **Build and Push Images**:
   ```bash
   # Login to Docker Hub
   echo "$DOCKER_PERSONAL_ACCESS_TOKEN" | docker login -u scoobyjava15 --password-stdin

   # Build all MCP server images
   python scripts/build_all_mcp_images.py --registry scoobyjava15 --push
   ```

2. **Create Docker Swarm Secrets**:
   ```bash
   # Setup SSH key
   export LAMBDA_LABS_SSH_KEY="path/to/ssh/key"

   # Create secrets from Pulumi ESC
   python scripts/create_docker_swarm_secrets.py \
     --host 192.222.58.232 \
     --ssh-key ~/.ssh/sophia2025.pem \
     --environment sophia-ai-production
   ```

3. **Deploy Complete Platform**:
   ```bash
   # Deploy everything
   python scripts/unified_lambda_labs_deployment.py \
     --host 192.222.58.232 \
     --ssh-key ~/.ssh/sophia2025.pem \
     --registry scoobyjava15 \
     --environment production \
     --deploy-mcp-servers true
   ```

## 📊 Monitoring and Validation

### Service Health Checks
```bash
# Check all services
ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232 "sudo docker service ls"

# Check specific service
ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232 "sudo docker service ps sophia-ai_ai-memory-server"

# View service logs
ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232 "sudo docker service logs sophia-ai_sophia-backend"
```

### Access URLs
After successful deployment, services are available at:

- **Main Backend**: http://192.222.58.232:8000
- **API Documentation**: http://192.222.58.232:8000/docs
- **Grafana Dashboard**: http://192.222.58.232:3000
- **Prometheus Metrics**: http://192.222.58.232:9090
- **Traefik Dashboard**: http://192.222.58.232:8090

### MCP Server Endpoints
All MCP servers expose standard endpoints:
- `/health` - Health check
- `/` - Service information
- `/mcp/tools` - Available MCP tools
- `/docs` - API documentation (if available)

## 🔍 Troubleshooting

### Common Issues

#### Services Stuck in "New" State
```bash
# Check if images are being pulled
ssh ubuntu@192.222.58.232 "sudo docker service ps sophia-ai_service-name --no-trunc"

# Manual image pull test
ssh ubuntu@192.222.58.232 "sudo docker pull scoobyjava15/sophia-ai:latest"
```

#### Secret Access Issues
```bash
# List Docker secrets
ssh ubuntu@192.222.58.232 "sudo docker secret ls"

# Recreate specific secret
ssh ubuntu@192.222.58.232 "sudo docker secret rm secret_name"
python scripts/create_docker_swarm_secrets.py --host 192.222.58.232 --ssh-key ~/.ssh/sophia2025.pem
```

#### Network Issues
```bash
# Check networks
ssh ubuntu@192.222.58.232 "sudo docker network ls"

# Recreate overlay networks
ssh ubuntu@192.222.58.232 "sudo docker network rm sophia-overlay traefik-public"
ssh ubuntu@192.222.58.232 "sudo docker network create --driver overlay --attachable sophia-overlay"
ssh ubuntu@192.222.58.232 "sudo docker network create --driver overlay --attachable traefik-public"
```

### Debug Commands
```bash
# Complete system status
ssh ubuntu@192.222.58.232 "sudo docker system df && sudo docker system info"

# Service resource usage
ssh ubuntu@192.222.58.232 "sudo docker stats --no-stream"

# Swarm node status
ssh ubuntu@192.222.58.232 "sudo docker node ls"

# Stack status
ssh ubuntu@192.222.58.232 "sudo docker stack ls && sudo docker stack services sophia-ai"
```

## 🔄 Updates and Maintenance

### Rolling Updates
```bash
# Update specific service
ssh ubuntu@192.222.58.232 "sudo docker service update --image scoobyjava15/sophia-ai:new-tag sophia-ai_sophia-backend"

# Update entire stack
git push origin main  # Triggers GitHub Actions deployment
```

### Scaling Services
```bash
# Scale specific service
ssh ubuntu@192.222.58.232 "sudo docker service scale sophia-ai_ai-memory-server=3"

# Scale multiple services
ssh ubuntu@192.222.58.232 "sudo docker service scale sophia-ai_sophia-backend=2 sophia-ai_ai-memory-server=3"
```

### Backup and Recovery
```bash
# Backup volumes
ssh ubuntu@192.222.58.232 "sudo docker run --rm -v sophia-ai_postgres_data:/data -v /backup:/backup ubuntu tar czf /backup/postgres_backup.tar.gz -C /data ."

# Restore volumes
ssh ubuntu@192.222.58.232 "sudo docker run --rm -v sophia-ai_postgres_data:/data -v /backup:/backup ubuntu tar xzf /backup/postgres_backup.tar.gz -C /data"
```

## 🎯 Performance Optimization

### Resource Limits
Services are configured with appropriate resource constraints in the docker-compose file:
- Memory limits based on service requirements
- CPU reservations for critical services
- Health checks with appropriate intervals

### Monitoring
- Prometheus scrapes metrics from all services
- Grafana provides visualization dashboards
- Traefik provides request metrics and load balancing

## 🔐 Security

### Secret Management
- All secrets stored in Docker Swarm secrets (encrypted at rest)
- Secrets mounted as files, not environment variables
- Automatic secret rotation via Pulumi ESC integration

### Network Security
- All services communicate via encrypted overlay networks
- Traefik handles TLS termination
- No direct external access to internal services

### Access Control
- SSH key-based authentication to Lambda Labs
- Docker Hub registry authentication
- Service-specific API key management

## 📈 Scaling Strategy

### Current: Single-Node Swarm
- All services on one Lambda Labs server
- Suitable for development and initial production

### Future: Multi-Node Swarm
- Add worker nodes for horizontal scaling
- Database clustering for high availability
- Geographic distribution for performance

### Migration to Kubernetes
- Planned migration path to K3s then full Kubernetes
- Helm charts for easier management
- Advanced scheduling and resource management

This comprehensive deployment system provides a robust, scalable foundation for the complete Sophia AI platform with all 29 MCP servers and integrated capabilities.
