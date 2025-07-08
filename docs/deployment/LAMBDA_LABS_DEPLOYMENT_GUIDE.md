# Lambda Labs Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying and managing Sophia AI infrastructure on Lambda Labs, addressing all issues identified in the troubleshooting analysis and implementing best practices for production deployments.

## Table of Contents

1. [Infrastructure Overview](#infrastructure-overview)
2. [Credential Management](#credential-management)
3. [Deployment Pipeline](#deployment-pipeline)
4. [Monitoring & Health Checks](#monitoring--health-checks)
5. [Cost Optimization](#cost-optimization)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

## Infrastructure Overview

### Active Instances

| Instance | IP Address | GPU | Memory | Cost/Day | Purpose |
|----------|------------|-----|---------|----------|---------|
| sophia-ai-core | 192.222.58.232 | GH200 | 96GB | $35.76 | Primary AI Core |
| sophia-mcp-orchestrator | 104.171.202.117 | A6000 | 48GB | $19.20 | MCP Orchestration |
| sophia-data-pipeline | 104.171.202.134 | A100 | 40GB | $30.96 | Data Processing |
| sophia-development | 155.248.194.183 | A10 | 24GB | $18.00 | Development |

**Total Infrastructure Cost**: $103.92/day ($3,117.60/month)

### Service Endpoints

- **Primary Backend API**: http://192.222.58.232:8000
- **MCP Orchestrator**: http://104.171.202.117:8001
- **Health Check**: `/health` endpoint on each service

## Credential Management

### GitHub Organization Secrets

All credentials are stored in GitHub Organization Secrets (org: `ai-cherry`) and accessed via:

1. **GitHub CLI**:
```bash
gh auth login
gh secret list --org ai-cherry
gh secret get LAMBDA_API_KEY --org ai-cherry
```

2. **Pulumi ESC**:
```bash
pulumi env get ai-cherry/lambda-labs-production
```

### Required Secrets

- `LAMBDA_API_KEY`: Lambda Labs API access key
- `LAMBDA_SSH_KEY`: Public SSH key for instances
- `LAMBDA_PRIVATE_SSH_KEY`: Private SSH key for SSH access
- `PULUMI_ACCESS_TOKEN`: Pulumi service token
- `SNOWFLAKE_PAT_PROD`: Snowflake PAT for MCP authentication

### Local Setup

```bash
# Run credential setup script
./scripts/lambda_labs/setup_credentials.sh

# This will:
# - Validate GitHub CLI authentication
# - Retrieve secrets from GitHub Organization
# - Configure SSH key (~/.ssh/sophia2025)
# - Create .env.lambda-labs file
# - Test connectivity to all instances
```

## Deployment Pipeline

### Automated Deployment

The deployment is fully automated via GitHub Actions:

```bash
# Trigger deployment from main branch
git push origin main

# Or manually trigger with options
gh workflow run lambda-labs-deployment.yml \
  -f deploy_backend=true \
  -f deploy_mcp=true \
  -f run_health_check=true
```

### Deployment Phases

1. **Validate Infrastructure**: Check API and SSH connectivity
2. **Fix Code Issues**: Auto-fix known import errors
3. **Build Images**: Build and push Docker images
4. **Deploy Services**: Deploy to Lambda Labs instances
5. **Health Check**: Validate deployment success
6. **Setup Monitoring**: Install exporters and monitoring

### Manual Deployment

If needed, deploy manually:

```bash
# Deploy backend
ssh -i ~/.ssh/sophia2025 ubuntu@192.222.58.232
docker pull scoobyjava15/sophia-backend:latest
docker stop backend || true
docker run -d --name backend --restart unless-stopped \
  -p 8000:8000 -e ENVIRONMENT=production \
  scoobyjava15/sophia-backend:latest

# Deploy MCP orchestrator
ssh -i ~/.ssh/sophia2025 ubuntu@104.171.202.117
docker pull scoobyjava15/sophia-mcp-orchestrator:latest
docker stop mcp-orchestrator || true
docker run -d --name mcp-orchestrator --restart unless-stopped \
  -p 8001:8001 -e ENVIRONMENT=production \
  scoobyjava15/sophia-mcp-orchestrator:latest
```

## Monitoring & Health Checks

### Daily Health Monitoring

```bash
# Run comprehensive health check
python scripts/lambda_labs/health_monitor.py

# Output includes:
# - Instance accessibility
# - Service health status
# - Resource utilization (CPU, Memory, GPU)
# - Cost tracking
# - Alert generation
```

### Continuous Monitoring

1. **Prometheus Metrics**:
   - Node Exporter: System metrics (port 9100)
   - GPU Exporter: NVIDIA GPU metrics (port 9400)
   - Custom app metrics: Application-specific metrics

2. **Grafana Dashboards**:
   - Import dashboards from `infrastructure/monitoring/dashboards/`
   - Access at: http://<instance-ip>:3000

3. **Automated Alerts**:
   - High GPU utilization (>90%)
   - Low memory (<10% free)
   - Service downtime
   - Cost burn rate exceeded

### Setting Up Monitoring

```bash
# Install on each instance
for ip in 192.222.58.232 104.171.202.117; do
  ssh -i ~/.ssh/sophia2025 ubuntu@$ip << 'EOF'
    # Node exporter
    docker run -d --name node-exporter --restart unless-stopped \
      --net host --pid host -v /:/host:ro,rslave \
      quay.io/prometheus/node-exporter:latest --path.rootfs=/host

    # GPU exporter (if GPU available)
    docker run -d --name gpu-exporter --restart unless-stopped \
      --gpus all -p 9400:9400 nvidia/dcgm-exporter:latest
EOF
done
```

## Cost Optimization

### Cost Analysis

```bash
# Run cost optimization analysis
python scripts/lambda_labs/cost_optimizer.py

# Generates:
# - Current utilization report
# - Cost breakdown by instance
# - Optimization recommendations
# - Auto-scaling script
```

### Optimization Strategies

1. **Auto-Scaling**:
   - Shut down idle instances (GPU < 15% for 4 hours)
   - Scale up when utilization > 70%
   - Business hours scheduling for dev instance

2. **Resource Right-Sizing**:
   - Monitor actual usage vs. allocated resources
   - Downsize overprovisioned instances
   - Consolidate underutilized workloads

3. **Scheduled Shutdowns**:
```bash
# Add to crontab on sophia-development
# Shutdown at 2 AM, start at 9 AM on weekdays
0 2 * * 1-5 sudo shutdown -h now
0 9 * * 1-5 wakeonlan <MAC-ADDRESS>
```

### Cost Tracking

Monitor daily costs and set up alerts:

```bash
# Check current burn rate
curl -s http://192.222.58.232:8000/metrics | grep cost_daily

# Alert if exceeds threshold
if [ $(calculate_daily_cost) -gt 120 ]; then
  send_slack_alert "High burn rate: $$(calculate_daily_cost)/day"
fi
```

## Troubleshooting

### Common Issues and Solutions

1. **SSH Connection Failed**:
```bash
# Check SSH key permissions
ls -la ~/.ssh/sophia2025  # Should be 600

# Test connectivity
ssh -v -i ~/.ssh/sophia2025 ubuntu@192.222.58.232

# If still failing, retrieve key again
gh secret get LAMBDA_PRIVATE_SSH_KEY --org ai-cherry > ~/.ssh/sophia2025
chmod 600 ~/.ssh/sophia2025
```

2. **Import Errors (OptimizedCache)**:
```bash
# Run import fixer
python scripts/lambda_labs/fix_import_errors.py

# Or manually fix
sed -i 's/from core.optimized_cache import OptimizedCache/from core.optimized_cache import OptimizedHierarchicalCache as OptimizedCache/g' \
  infrastructure/services/data_source_manager.py
```

3. **Service Not Accessible**:
```bash
# Check container status
ssh -i ~/.ssh/sophia2025 ubuntu@192.222.58.232 docker ps

# Check logs
ssh -i ~/.ssh/sophia2025 ubuntu@192.222.58.232 docker logs backend

# Restart if needed
ssh -i ~/.ssh/sophia2025 ubuntu@192.222.58.232 docker restart backend
```

4. **High Memory Usage**:
```bash
# Check memory consumers
ssh -i ~/.ssh/sophia2025 ubuntu@192.222.58.232 \
  "ps aux --sort=-%mem | head -10"

# Clear Docker cache if needed
ssh -i ~/.ssh/sophia2025 ubuntu@192.222.58.232 \
  "docker system prune -af"
```

### Diagnostic Commands

```bash
# Full system diagnostic
for ip in 192.222.58.232 104.171.202.117 104.171.202.134 155.248.194.183; do
  echo "=== Checking $ip ==="
  ssh -i ~/.ssh/sophia2025 ubuntu@$ip << 'EOF'
    echo "System Info:"
    uname -a
    echo "Memory:"
    free -h
    echo "Disk:"
    df -h /
    echo "Docker:"
    docker ps
    echo "GPU:"
    nvidia-smi || echo "No GPU"
EOF
done
```

## Best Practices

### 1. Security

- **Never commit credentials**: Use GitHub Secrets + Pulumi ESC
- **Rotate SSH keys quarterly**: Update in GitHub Secrets
- **Use PAT for Snowflake**: Not username/password
- **Enable firewall rules**: Restrict access to known IPs

### 2. Deployment

- **Blue-Green Deployments**: Minimize downtime
- **Health checks before cutover**: Validate new deployment
- **Automated rollback**: On health check failure
- **Version tagging**: Use git SHA for traceability

### 3. Monitoring

- **Set up alerts early**: Don't wait for issues
- **Track cost daily**: Avoid surprise bills
- **Monitor GPU utilization**: Optimize workload distribution
- **Log aggregation**: Centralize logs for debugging

### 4. Cost Management

- **Tag resources**: Track costs by project/team
- **Set budget alerts**: At 80% of monthly budget
- **Review weekly**: Identify optimization opportunities
- **Automate shutdowns**: For non-critical instances

### 5. Development Workflow

```bash
# Development cycle
1. Make changes locally
2. Test with minimal Docker image
3. Push to feature branch
4. Deploy to sophia-development instance
5. Validate functionality
6. Merge to main for production deployment
```

## Maintenance Schedule

### Daily
- Health monitoring script
- Cost tracking
- Alert review

### Weekly
- Security updates
- Performance analysis
- Cost optimization review

### Monthly
- Full system audit
- Credential rotation check
- Capacity planning
- Cost report to stakeholders

## Emergency Procedures

### Service Outage
```bash
# 1. Check instance status
python scripts/lambda_labs/health_monitor.py

# 2. Restart affected services
ssh -i ~/.ssh/sophia2025 ubuntu@<IP> docker restart <service>

# 3. Check logs
ssh -i ~/.ssh/sophia2025 ubuntu@<IP> docker logs --tail 100 <service>

# 4. Rollback if needed
ssh -i ~/.ssh/sophia2025 ubuntu@<IP> \
  docker run -d --name <service>-rollback <previous-image>
```

### Complete Infrastructure Recovery
```bash
# If all instances are down
1. Check Lambda Labs API status
2. Verify billing/account status
3. Re-provision instances if needed
4. Restore from backups
5. Redeploy all services
```

## Conclusion

This deployment guide provides a comprehensive framework for managing Sophia AI infrastructure on Lambda Labs. By following these procedures and best practices, you can maintain a reliable, cost-effective, and high-performance deployment.

For additional support or questions, contact the platform team or refer to the troubleshooting section above.
