# Lambda Labs Deployment Guide for Sophia AI

## Overview

This guide covers the complete deployment process for Sophia AI on Lambda Labs infrastructure, including GitHub Actions CI/CD, Pulumi IaC, and comprehensive monitoring.

## Lambda Labs Infrastructure

### Current Instances

| Instance Name | IP Address | GPU Type | Region | Purpose |
|--------------|------------|----------|---------|----------|
| sophia-production-instance | 104.171.202.103 | RTX 6000 (24GB) | us-south-1 | Production workloads |
| sophia-ai-core | 192.222.58.232 | GH200 (96GB) | us-east-3 | AI/ML processing |
| sophia-mcp-orchestrator | 104.171.202.117 | A6000 (48GB) | us-south-1 | MCP orchestration |
| sophia-data-pipeline | 104.171.202.134 | A100 (80GB) | us-south-1 | Data processing |
| sophia-development | 155.248.194.183 | A10 (24GB) | us-west-1 | Development/testing |

### Credentials

All credentials are stored in GitHub Secrets and Pulumi ESC:

- **LAMBDA_CLOUD_API_KEY**: Cloud API access
- **LAMBDA_API_KEY**: Regular API access
- **LAMBDA_SSH_KEY**: Public SSH key
- **LAMBDA_PRIVATE_SSH_KEY**: Private SSH key for deployments

## Quick Start

### 1. Set Up GitHub Secrets

```bash
# Run the setup script
./scripts/setup_github_secrets.sh

# Verify secrets
gh secret list
```

### 2. Deploy Using GitHub Actions

```bash
# Trigger deployment workflow
gh workflow run lambda-labs-deploy.yml \
  -f target_instance=sophia-production-instance \
  -f deployment_type=full

# Monitor deployment
gh run watch
```

### 3. Manual Deployment

```bash
# Use the Lambda Labs manager
python scripts/lambda_labs_manager.py deploy \
  --instance sophia-production-instance \
  --type full

# Check health
python scripts/lambda_labs_manager.py health \
  --instance sophia-production-instance
```

## Deployment Architecture

### Service Stack

1. **Backend Services**
   - FastAPI application (port 8000)
   - PostgreSQL database
   - Redis cache
   - Background workers

2. **MCP Servers** (ports 9000-9100)
   - AI Memory (9001)
   - Codacy (3008)
   - Linear (9004)
   - GitHub (9103)
   - Asana (9100)
   - UI/UX Agent (9002)
   - Lambda Labs CLI (9040)
   - Lambda Labs Serverless (9025)

3. **Monitoring Stack**
   - Prometheus (9090)
   - Grafana (3000)
   - Custom dashboards

4. **Reverse Proxy**
   - Nginx (80/443)
   - SSL termination
   - Load balancing

### Docker Images

All images are hosted on Docker Hub:
- `scoobyjava15/sophia-backend:latest`
- `scoobyjava15/sophia-mcp-servers:latest`

## CI/CD Pipeline

### GitHub Actions Workflow

The deployment pipeline consists of:

1. **Build Stage**
   - Build Docker images
   - Run tests
   - Push to Docker Hub

2. **Deploy Stage**
   - Deploy to Lambda Labs instances
   - Run health checks
   - Update Pulumi ESC

3. **Monitor Stage**
   - Continuous health monitoring
   - Alert on failures
   - Generate reports

### Triggering Deployments

```bash
# Manual trigger
gh workflow run lambda-labs-deploy.yml

# On push to main
git push origin main

# On pull request
git push origin feature-branch
```

## Pulumi Infrastructure as Code

### Setup

```bash
# Install Pulumi
curl -fsSL https://get.pulumi.com | sh

# Configure
cd infrastructure/pulumi
npm install
pulumi stack init sophia-ai-production
```

### Deploy Infrastructure

```bash
# Preview changes
pulumi preview

# Deploy
pulumi up

# Check status
pulumi stack
```

### Configuration

```typescript
// Pulumi.sophia-ai-production.yaml
config:
  lambdaCloudApiKey:
    secure: <encrypted-key>
  lambdaApiKey:
    secure: <encrypted-key>
  dockerHubUsername: scoobyjava15
  dockerHubPassword:
    secure: <encrypted-password>
```

## Monitoring and Health Checks

### Grafana Dashboards

Access Grafana at `http://<instance-ip>:3000`
- Username: admin
- Password: sophia_admin

Pre-configured dashboards:
- System Overview
- Service Health
- MCP Server Status
- GPU Utilization
- API Performance

### Prometheus Metrics

Access Prometheus at `http://<instance-ip>:9090`

Key metrics:
- `sophia_backend_requests_total`
- `sophia_mcp_server_health`
- `sophia_gpu_utilization`
- `sophia_memory_usage`

### Health Check Endpoints

```bash
# Backend health
curl http://<instance-ip>:8000/health

# MCP server health
curl http://<instance-ip>:9001/health

# Prometheus health
curl http://<instance-ip>:9090/-/healthy

# Grafana health
curl http://<instance-ip>:3000/api/health
```

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   ```bash
   # Check instance status
   python scripts/lambda_labs_manager.py list

   # Test SSH connection
   ssh -i ~/.ssh/sophia2025.pem ubuntu@<ip>
   ```

2. **Docker Issues**
   ```bash
   # SSH into instance
   ssh ubuntu@<ip>

   # Check Docker status
   sudo systemctl status docker
   docker-compose ps
   docker-compose logs -f backend
   ```

3. **Service Failures**
   ```bash
   # Restart services
   docker-compose restart backend
   docker-compose restart mcp-servers

   # Check logs
   docker-compose logs -f --tail=100
   ```

### Debug Commands

```bash
# Full system check
python scripts/lambda_labs_manager.py report

# Monitor deployment
python scripts/lambda_labs_manager.py monitor \
  --instance sophia-production-instance \
  --duration 600

# Check resource usage
ssh ubuntu@<ip> 'htop'
ssh ubuntu@<ip> 'nvidia-smi'
ssh ubuntu@<ip> 'df -h'
```

## Security Considerations

1. **SSH Access**
   - Use provided SSH keys only
   - Keys are rotated monthly
   - Access logged and monitored

2. **API Security**
   - All API keys in GitHub Secrets
   - Pulumi ESC for runtime secrets
   - No hardcoded credentials

3. **Network Security**
   - Firewall rules configured
   - Only required ports exposed
   - SSL/TLS for all services

## Maintenance

### Regular Tasks

1. **Weekly**
   - Check service health
   - Review logs for errors
   - Update Docker images

2. **Monthly**
   - Rotate credentials
   - Update dependencies
   - Performance review

3. **Quarterly**
   - Security audit
   - Capacity planning
   - Cost optimization

### Backup and Recovery

```bash
# Backup database
docker exec postgres pg_dump -U sophia_user sophia_db > backup.sql

# Backup volumes
docker run --rm -v sophia-ai_postgres_data:/data \
  -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data

# Restore database
docker exec -i postgres psql -U sophia_user sophia_db < backup.sql
```

## Cost Management

### Instance Costs

| Instance Type | Cost/Hour | Monthly (730h) | Purpose |
|--------------|-----------|----------------|----------|
| RTX 6000 | $0.50 | $365 | Production |
| GH200 | $2.49 | $1,818 | AI Core |
| A6000 | $0.80 | $584 | MCP Orchestrator |
| A100 | $1.29 | $942 | Data Pipeline |
| A10 | $0.75 | $548 | Development |

**Total Monthly**: ~$4,257

### Optimization Strategies

1. **Auto-scaling**
   - Scale down during off-hours
   - Use spot instances for dev
   - Batch processing jobs

2. **Resource Sharing**
   - Consolidate services
   - Use multi-tenancy
   - Optimize GPU usage

## Support

### Lambda Labs Support
- Email: support@lambdalabs.com
- Documentation: https://docs.lambdalabs.com

### Sophia AI Team
- GitHub Issues: https://github.com/ai-cherry/sophia-main
- Internal Slack: #sophia-deployment

## Appendix

### Environment Variables

```bash
# Backend
ENVIRONMENT=production
DATABASE_URL=postgresql://sophia_user:password@postgres:5432/sophia_db
REDIS_URL=redis://redis:6379
PULUMI_ORG=scoobyjava-org
PULUMI_STACK=sophia-ai-production

# MCP Servers
MCP_SERVER_PORT_BASE=9000
MCP_SERVER_COUNT=12
ENABLE_METRICS=true
```

### Useful Scripts

```bash
# Full deployment
./scripts/deploy_sophia_platform.sh

# Update specific service
./scripts/update_service.sh backend

# Generate deployment report
./scripts/generate_deployment_report.sh
```
