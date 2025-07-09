# Sophia AI Unified Deployment System

This deployment system provides a complete solution for deploying Sophia AI across 5 Lambda Labs GPU instances with a unified, scalable architecture.

## 🏗️ Architecture Overview

The Sophia AI platform is distributed across 5 specialized Lambda Labs instances:

| Instance | GPU | IP Address | Role | Key Services |
|----------|-----|------------|------|--------------|
| **sophia-production-instance** | RTX6000 | `104.171.202.103` | Core Platform Services | Backend API, Dashboard, Chat, Load Balancer |
| **sophia-ai-core** | GH200 | `192.222.58.232` | AI/ML Compute Engine | AI Memory, Snowflake Cortex, LLM Processing |
| **sophia-mcp-orchestrator** | A6000 | `104.171.202.117` | MCP Services Hub | GitHub, Slack, Linear, Notion, Codacy |
| **sophia-data-pipeline** | A100 | `104.171.202.134` | Data Processing Center | Snowflake, Data Analytics, Monitoring |
| **sophia-development** | A10 | `155.248.194.183` | Development & Monitoring | Testing, CI/CD, Performance Monitoring |

## 🚀 Quick Start

### Prerequisites

1. **SSH Key Setup**
   ```bash
   # Ensure SSH key exists with correct permissions
   chmod 600 ~/.ssh/sophia2025.pem
   chmod 644 ~/.ssh/sophia2025.pem.pub
   
   # Test SSH access to all instances
   ssh -i ~/.ssh/sophia2025.pem ubuntu@104.171.202.103 "echo 'Production OK'"
   ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232 "echo 'AI Core OK'"
   ssh -i ~/.ssh/sophia2025.pem ubuntu@104.171.202.117 "echo 'MCP OK'"
   ssh -i ~/.ssh/sophia2025.pem ubuntu@104.171.202.134 "echo 'Data OK'"
   ssh -i ~/.ssh/sophia2025.pem ubuntu@155.248.194.183 "echo 'Dev OK'"
   ```

2. **Docker Hub Authentication**
   ```bash
   docker login -u scoobyjava15
   ```

3. **Environment Variables**
   ```bash
   export DOCKER_REGISTRY=scoobyjava15
   export IMAGE_TAG=latest
   export ENVIRONMENT=prod
   export PULUMI_ORG=scoobyjava-org
   ```

### Option 1: GitHub Actions Deployment (Recommended)

1. **Navigate to GitHub Actions**
   - Go to the GitHub repository
   - Click on "Actions" tab
   - Select "🚀 Sophia AI Unified Deployment"

2. **Run Workflow**
   ```yaml
   Target Instance: all                    # Deploy to all instances
   Build Images: true                      # Build and push Docker images
   Force Rebuild: false                    # Use cached images if available
   Skip Validation: false                  # Validate deployment
   Environment: prod                       # Production environment
   ```

3. **Monitor Deployment**
   - View real-time deployment progress
   - Check deployment summary
   - Access service URLs from summary

### Option 2: Local Script Deployment

1. **Make Script Executable**
   ```bash
   chmod +x scripts/deploy_sophia_unified.sh
   ```

2. **Deploy to All Instances**
   ```bash
   ./scripts/deploy_sophia_unified.sh deploy all
   ```

3. **Deploy to Specific Instance**
   ```bash
   ./scripts/deploy_sophia_unified.sh deploy production
   ./scripts/deploy_sophia_unified.sh deploy ai-core
   ./scripts/deploy_sophia_unified.sh deploy mcp-orchestrator
   ./scripts/deploy_sophia_unified.sh deploy data-pipeline
   ./scripts/deploy_sophia_unified.sh deploy development
   ```

4. **Check Deployment Status**
   ```bash
   ./scripts/deploy_sophia_unified.sh status
   ```

5. **Validate Specific Instance**
   ```bash
   ./scripts/deploy_sophia_unified.sh validate ai-core
   ```

## 📁 Directory Structure

```
deployment/
├── README.md                           # This file
├── docker-compose-production.yml      # Production instance services
├── docker-compose-ai-core.yml         # AI/ML compute services
├── docker-compose-mcp-orchestrator.yml # MCP services
├── docker-compose-data-pipeline.yml   # Data processing services
├── docker-compose-development.yml     # Development services
└── configs/                           # Configuration files
    ├── nginx.conf                     # Nginx configuration
    ├── postgres-init.sql             # Database initialization
    └── ssl/                          # SSL certificates
```

## 🐳 Docker Compose Files

### Production Instance (RTX6000)
```yaml
# deployment/docker-compose-production.yml
services:
  - sophia-backend           # FastAPI Backend (Port 8000)
  - sophia-unified-chat      # WebSocket Chat (Port 8001)
  - sophia-dashboard         # React Dashboard (Port 3000)
  - mcp-gateway             # MCP Gateway (Port 8080)
  - nginx                   # Load Balancer (Port 80/443)
  - postgres                # Database (Port 5432)
  - redis                   # Cache (Port 6379)
  - traefik                 # Service Discovery (Port 8090)
```

### AI Core Instance (GH200)
```yaml
# deployment/docker-compose-ai-core.yml
services:
  - ai-memory-v2            # AI Memory (Port 9000)
  - snowflake-cortex        # Snowflake AI (Port 8081)
  - mem0-openmemory         # Memory Persistence (Port 8080)
  - huggingface-ai          # ML Models (Port 9012)
  - portkey-admin           # LLM Gateway (Port 9013)
  - prompt-optimizer        # Prompt Enhancement (Port 9014)
  - gong-v2                 # Sales AI (Port 9009)
  - perplexity-v2           # AI Research (Port 9008)
  - apollo                  # Sales Intelligence (Port 9015)
  - bright-data             # Data Intelligence (Port 9105)
  - apify-intelligence      # Automation (Port 9016)
  - redis                   # AI Cache (Port 6379)
  - vector-db               # Weaviate (Port 8088)
```

### MCP Orchestrator Instance (A6000)
```yaml
# deployment/docker-compose-mcp-orchestrator.yml
services:
  - github-v2               # Development (Port 9006)
  - slack-v2                # Communication (Port 9007)
  - linear-v2               # Project Management (Port 9002)
  - notion-v2               # Knowledge (Port 9003)
  - codacy-v2               # Code Quality (Port 9005)
  - asana-v2                # Task Management (Port 9004)
  - hubspot                 # CRM (Port 9017)
  - salesforce              # Enterprise CRM (Port 9018)
  - playwright              # Browser Automation (Port 9020)
  - pulumi                  # Infrastructure as Code (Port 9021)
  - lambda-labs-cli         # GPU Management (Port 9040)
  - ui-ux-agent             # Design Automation (Port 9022)
  - v0dev                   # AI UI Generation (Port 9023)
  - figma-context           # Design-to-Code (Port 9024)
  - code-modifier           # Code Modification (Port 9025)
  - migration-orchestrator  # Data Migration (Port 9026)
  - overlays                # UI Overlays (Port 9027)
```

### Data Pipeline Instance (A100)
```yaml
# deployment/docker-compose-data-pipeline.yml
services:
  - snowflake-v2            # Data Hub (Port 9001)
  - snowflake-unified       # Data Processing (Port 9028)
  - gong-webhook            # Webhooks (Port 8080)
  - snowflake-cortex        # Cortex Processing (Port 9029)
  - postgres                # Database Management (Port 9030)
  - estuary-flow            # Real-time Pipeline (Port 9031)
  - graphiti                # Knowledge Graph (Port 9032)
  - prometheus              # Metrics (Port 9090)
  - grafana                 # Visualization (Port 3000)
  - alertmanager            # Alerts (Port 9093)
  - loki                    # Log Aggregation (Port 3100)
  - mailhog                 # Email Testing (Port 8025)
```

### Development Instance (A10)
```yaml
# deployment/docker-compose-development.yml
services:
  - codacy                  # Code Analysis (Port 3008)
  - performance-monitor     # Performance (Port 9033)
  - health-aggregator       # Health Monitoring (Port 8080)
  - secret-rotator          # Secret Management (Port 9034)
  - secret-health-checker   # Security Validation (Port 9035)
  - dcgm-exporter          # GPU Metrics (Port 9400)
  - grafana                 # Dashboards (Port 3000)
  - promtail               # Log Collection (Port 9080)
  - jenkins                # CI/CD (Port 8080)
  - sonarqube              # Code Quality (Port 9000)
  - docker-registry        # Private Registry (Port 5000)
  - mailhog                # Email Testing (Port 8025)
  - postgres               # Dev Database (Port 5432)
  - redis                  # Dev Cache (Port 6379)
  - nginx                  # Dev Proxy (Port 80)
```

## 🔧 Configuration Management

### Environment Variables

The deployment system uses environment variables for configuration:

```bash
# Core Configuration
DOCKER_REGISTRY=scoobyjava15           # Docker Hub registry
IMAGE_TAG=latest                       # Image tag
ENVIRONMENT=prod                       # Environment (prod/staging/dev)
PULUMI_ORG=scoobyjava-org             # Pulumi organization

# Instance-Specific
INSTANCE_NAME=production               # Instance identifier
GPU_TYPE=RTX6000                       # GPU type for optimization

# Service URLs
REDIS_URL=redis://redis:6379           # Redis connection
POSTGRES_URL=postgresql://sophia:password@postgres:5432/sophia_ai
```

### Docker Swarm Configuration

Each instance uses Docker Swarm for orchestration:

```yaml
# Common patterns across all compose files
x-default-deploy: &default-deploy
  restart_policy:
    condition: on-failure
    delay: 5s
    max_attempts: 3
    window: 120s
  update_config:
    parallelism: 1
    delay: 10s
    failure_action: rollback
    monitor: 60s
  rollback_config:
    parallelism: 1
    delay: 10s
    failure_action: pause
    monitor: 60s
```

### Network Configuration

```yaml
# Standardized networks across all instances
networks:
  sophia-network:
    driver: overlay
    attachable: true
    ipam:
      driver: default
      config:
        - subnet: 10.0.1.0/24
  sophia-public:
    driver: overlay
    attachable: true
    ipam:
      driver: default
      config:
        - subnet: 10.0.2.0/24
  sophia-private:
    driver: overlay
    attachable: false
    ipam:
      driver: default
      config:
        - subnet: 10.0.3.0/24
```

## 📊 Monitoring and Validation

### Health Checks

All services include comprehensive health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Deployment Validation

The system includes automated validation:

```bash
# Check service status
docker stack services sophia-production

# Validate all services are running
failed_services=$(docker stack services sophia-production --format 'table {{.Name}}\t{{.Replicas}}' | grep '0/' | wc -l)

if [ $failed_services -gt 0 ]; then
    echo "WARNING: Some services failed to start"
    exit 1
fi
```

### Access URLs

After deployment, services are accessible at:

#### Production Instance (104.171.202.103)
- **Dashboard**: http://104.171.202.103:3000
- **API**: http://104.171.202.103:8000
- **API Documentation**: http://104.171.202.103:8000/docs
- **Chat**: http://104.171.202.103:8001
- **MCP Gateway**: http://104.171.202.103:8080

#### AI Core Instance (192.222.58.232)
- **AI Memory**: http://192.222.58.232:9000
- **Snowflake Cortex**: http://192.222.58.232:8081
- **Mem0 OpenMemory**: http://192.222.58.232:8080
- **HuggingFace AI**: http://192.222.58.232:9012
- **Portkey Admin**: http://192.222.58.232:9013
- **Prompt Optimizer**: http://192.222.58.232:9014

#### MCP Orchestrator Instance (104.171.202.117)
- **GitHub Integration**: http://104.171.202.117:9006
- **Slack Integration**: http://104.171.202.117:9007
- **Linear Integration**: http://104.171.202.117:9002
- **Notion Integration**: http://104.171.202.117:9003
- **Codacy Integration**: http://104.171.202.117:9005

#### Data Pipeline Instance (104.171.202.134)
- **Snowflake Data Hub**: http://104.171.202.134:9001
- **Prometheus**: http://104.171.202.134:9090
- **Grafana**: http://104.171.202.134:3000
- **Alert Manager**: http://104.171.202.134:9093

#### Development Instance (155.248.194.183)
- **Development Dashboard**: http://155.248.194.183:3000
- **Codacy**: http://155.248.194.183:3008
- **Jenkins**: http://155.248.194.183:8080
- **SonarQube**: http://155.248.194.183:9000
- **Docker Registry**: http://155.248.194.183:5000

## 🔧 Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   ```bash
   # Check SSH key permissions
   chmod 600 ~/.ssh/sophia2025.pem
   
   # Test SSH connection
   ssh -i ~/.ssh/sophia2025.pem -o ConnectTimeout=10 ubuntu@104.171.202.103 "echo 'Test'"
   ```

2. **Docker Swarm Not Initialized**
   ```bash
   # Initialize Docker Swarm
   docker swarm init
   
   # Check swarm status
   docker info | grep -i swarm
   ```

3. **Service Health Check Failing**
   ```bash
   # Check service logs
   docker service logs sophia-production_sophia-backend
   
   # Check service status
   docker stack services sophia-production
   ```

4. **Network Issues**
   ```bash
   # List Docker networks
   docker network ls
   
   # Inspect network
   docker network inspect sophia-network
   ```

### Debug Commands

```bash
# Check deployment status
./scripts/deploy_sophia_unified.sh status

# Validate specific instance
./scripts/deploy_sophia_unified.sh validate ai-core

# Check service logs
ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232 "docker service logs sophia-ai-core_ai-memory-v2"

# Check running containers
ssh -i ~/.ssh/sophia2025.pem ubuntu@104.171.202.103 "docker ps"

# Check Docker Swarm services
ssh -i ~/.ssh/sophia2025.pem ubuntu@104.171.202.103 "docker stack services sophia-production"
```

## 🔒 Security Considerations

### SSH Key Management
- Use the standardized SSH key: `~/.ssh/sophia2025.pem`
- Ensure proper permissions (600 for private key, 644 for public key)
- Never commit SSH keys to version control

### Docker Hub Authentication
- Use GitHub secrets for Docker Hub credentials
- Rotate credentials regularly
- Use least privilege access

### Network Security
- Private networks for database and cache services
- Public networks only for web-facing services
- Proper firewall rules on Lambda Labs instances

### Secret Management
- All secrets managed through Pulumi ESC
- GitHub organization secrets for CI/CD
- No hardcoded secrets in configurations

## 🚀 Scaling and Optimization

### Resource Allocation
Each instance is optimized for its specific role:
- **RTX6000**: Optimized for web services and load balancing
- **GH200**: Optimized for AI/ML workloads with GPU acceleration
- **A6000**: Optimized for MCP service orchestration
- **A100**: Optimized for data processing and analytics
- **A10**: Optimized for development and testing

### Auto-scaling
- Use Docker Swarm replicas for horizontal scaling
- Monitor resource usage and adjust replica counts
- Implement load balancing for high-availability services

### Performance Monitoring
- Prometheus metrics collection on all instances
- Grafana dashboards for visualization
- Custom alerts for critical service failures
- GPU utilization monitoring on GPU instances

## 📋 Maintenance

### Regular Tasks
1. **Update Docker images**: Run deployment with `force_rebuild: true`
2. **Monitor resource usage**: Check Grafana dashboards
3. **Rotate secrets**: Use Pulumi ESC secret rotation
4. **Update configurations**: Modify compose files and redeploy
5. **Backup data**: Ensure database and volume backups

### Upgrade Process
1. **Test in development**: Deploy to development instance first
2. **Validate changes**: Run comprehensive tests
3. **Rolling deployment**: Deploy to instances one by one
4. **Monitor health**: Check all service health after deployment
5. **Rollback if needed**: Use Docker Swarm rollback capabilities

## 🎯 Best Practices

### Development Workflow
1. **Local development**: Use development instance for testing
2. **Feature branches**: Create feature branches for new deployments
3. **Pull requests**: Use PR workflow for deployment changes
4. **CI/CD integration**: Leverage GitHub Actions for automated deployments
5. **Monitoring**: Always monitor deployments and set up alerts

### Deployment Strategy
1. **Blue-green deployments**: Use Docker Swarm update strategies
2. **Health checks**: Implement comprehensive health checks
3. **Rollback planning**: Always have rollback procedures ready
4. **Documentation**: Keep deployment documentation up to date
5. **Testing**: Test deployments in non-production environments first

This deployment system provides a robust, scalable, and maintainable architecture for the Sophia AI platform across multiple Lambda Labs GPU instances.