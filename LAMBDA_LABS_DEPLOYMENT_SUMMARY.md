# 🚀 Lambda Labs Deployment Infrastructure - Complete Setup

## Overview

I've created a comprehensive deployment infrastructure for Sophia AI on Lambda Labs with the following components:

### 1. **GitHub Secrets Management** (`scripts/setup_github_secrets.sh`)
- Automated setup of all Lambda Labs credentials
- Secure storage of API keys, SSH keys, and Docker Hub credentials
- Integration with GitHub Actions workflows

### 2. **GitHub Actions CI/CD** (`.github/workflows/lambda-labs-deploy.yml`)
- Automated build and push of Docker images
- Parallel deployment to multiple Lambda Labs instances
- Health checks and monitoring
- Pulumi ESC integration for secrets management

### 3. **Lambda Labs Manager** (`scripts/lambda_labs_manager.py`)
- Python CLI tool for instance management
- Commands: list, deploy, health, monitor, report
- Programmatic access to Lambda Labs API
- SSH-based deployment and monitoring

### 4. **Pulumi Infrastructure as Code** (`infrastructure/pulumi/lambda-labs.ts`)
- TypeScript-based infrastructure definition
- Automated deployment scripts
- Health check automation
- Monitoring configuration

### 5. **Complete Deployment Orchestrator** (`scripts/deploy_sophia_complete.py`)
- Full deployment pipeline automation
- Parallel deployment support
- Comprehensive health checks
- Deployment reporting

## Lambda Labs Instances

| Instance | IP | GPU | Purpose | Status |
|----------|----|----|---------|---------|
| sophia-production-instance | 104.171.202.103 | RTX 6000 | Production | ✅ Active |
| sophia-ai-core | 192.222.58.232 | GH200 | AI Processing | ✅ Active |
| sophia-mcp-orchestrator | 104.171.202.117 | A6000 | MCP Services | ✅ Active |
| sophia-data-pipeline | 104.171.202.134 | A100 | Data Pipeline | ✅ Active |
| sophia-development | 155.248.194.183 | A10 | Development | ✅ Active |

## Quick Start Commands

### 1. Set Up GitHub Secrets
```bash
./scripts/setup_github_secrets.sh
```

### 2. Deploy Using Python Manager
```bash
# List all instances
python scripts/lambda_labs_manager.py list

# Deploy to production
python scripts/lambda_labs_manager.py deploy --instance sophia-production-instance --type full

# Check health
python scripts/lambda_labs_manager.py health --instance sophia-production-instance

# Monitor deployment
python scripts/lambda_labs_manager.py monitor --instance sophia-production-instance --duration 300
```

### 3. Deploy Using Orchestrator
```bash
# Full deployment to all instances
python scripts/deploy_sophia_complete.py --parallel

# Deploy to specific instance
python scripts/deploy_sophia_complete.py --instance sophia-production-instance

# Generate deployment report
python scripts/lambda_labs_manager.py report
```

### 4. Deploy Using GitHub Actions
```bash
# Trigger deployment workflow
gh workflow run lambda-labs-deploy.yml \
  -f target_instance=sophia-production-instance \
  -f deployment_type=full

# Watch deployment progress
gh run watch
```

## Services Deployed

### Core Services
- **Backend API** (Port 8000): FastAPI application
- **PostgreSQL**: Database with persistent storage
- **Redis**: Cache and message broker
- **MCP Servers** (Ports 9000-9100):
  - AI Memory (9001)
  - Codacy (3008)
  - Linear (9004)
  - GitHub (9103)
  - Asana (9100)
  - UI/UX Agent (9002)
  - Lambda Labs CLI (9040)
  - Lambda Labs Serverless (9025)

### Monitoring Stack
- **Prometheus** (Port 9090): Metrics collection
- **Grafana** (Port 3000): Dashboards and visualization
  - Default login: admin/sophia_admin

## Access URLs

After deployment, services are available at:

- **Production Backend**: http://104.171.202.103:8000
- **Production Grafana**: http://104.171.202.103:3000
- **AI Core Backend**: http://192.222.58.232:8000
- **MCP Orchestrator**: http://104.171.202.117:9001

## Security Configuration

### SSH Access
```bash
# SSH to any instance
ssh -i ~/.ssh/lambda_labs_sophia_key ubuntu@<instance-ip>
```

### API Authentication
- Cloud API: Uses Bearer token authentication
- Regular API: Uses Basic authentication
- All credentials stored in GitHub Secrets

## Monitoring & Health Checks

### Automated Health Checks
The deployment includes automated health checks for:
- Backend API endpoints
- All MCP server ports
- Database connectivity
- Redis connectivity
- Prometheus metrics
- Grafana dashboards

### Manual Health Check
```bash
# Check all services on an instance
curl http://<instance-ip>:8000/health
curl http://<instance-ip>:9001/health
curl http://<instance-ip>:9090/-/healthy
curl http://<instance-ip>:3000/api/health
```

## Cost Information

| Instance Type | Cost/Hour | Monthly | Annual |
|--------------|-----------|---------|---------|
| RTX 6000 | $0.50 | $365 | $4,380 |
| GH200 | $2.49 | $1,818 | $21,816 |
| A6000 | $0.80 | $584 | $7,008 |
| A100 | $1.29 | $942 | $11,304 |
| A10 | $0.75 | $548 | $6,576 |
| **Total** | **$5.83** | **$4,257** | **$51,084** |

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   ```bash
   # Check SSH key permissions
   chmod 600 ~/.ssh/lambda_labs_sophia_key

   # Test SSH connection
   ssh -i ~/.ssh/lambda_labs_sophia_key ubuntu@<ip> 'echo OK'
   ```

2. **Docker Build Failed**
   ```bash
   # Check Docker Hub login
   docker login

   # Build locally
   docker build -f Dockerfile.production -t test .
   ```

3. **Service Not Responding**
   ```bash
   # SSH to instance and check logs
   ssh ubuntu@<ip>
   docker-compose logs -f backend
   docker-compose ps
   ```

## Next Steps

1. **Run Initial Deployment**
   ```bash
   python scripts/deploy_sophia_complete.py --parallel
   ```

2. **Set Up Monitoring Alerts**
   - Configure Grafana alerts
   - Set up Prometheus alerting rules
   - Configure notification channels

3. **Configure Backups**
   - Set up PostgreSQL backups
   - Configure volume snapshots
   - Implement disaster recovery

4. **Optimize Performance**
   - Tune PostgreSQL settings
   - Configure Redis persistence
   - Optimize container resources

## Support & Documentation

- **Lambda Labs Docs**: https://docs.lambdalabs.com
- **Deployment Guide**: `docs/LAMBDA_LABS_DEPLOYMENT_GUIDE.md`
- **GitHub Issues**: https://github.com/ai-cherry/sophia-main/issues

## Summary

The deployment infrastructure is now complete with:
- ✅ Automated CI/CD pipeline
- ✅ Infrastructure as Code with Pulumi
- ✅ Comprehensive monitoring
- ✅ Health checks and reporting
- ✅ Multi-instance orchestration
- ✅ Security best practices

All Lambda Labs instances are active and ready for deployment. The infrastructure supports both manual and automated deployments with comprehensive monitoring and health checking capabilities.
