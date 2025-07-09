# Lambda Labs Infrastructure Guide

> **Last Updated**: 2025-07-08  
> **Cost**: ~$5.83/hour ($4,257/month)  
> **Status**: Active

## Overview

Sophia AI runs on Lambda Labs GPU infrastructure, providing high-performance computing for AI workloads and general services. This guide covers instance management, deployment procedures, and cost optimization.

## Active Instances

### Production Fleet

| Instance | Type | GPU | Memory | IP | Cost/hr | Purpose |
|----------|------|-----|--------|----|---------|---------| 
| sophia-main | GH200 | 96GB | 480GB | 192.222.51.151 | $1.49 | Primary backend, MCP |
| sophia-rtx-1 | RTX 6000 | 24GB | 64GB | 192.222.51.122 | $0.50 | MCP orchestration |
| sophia-a6000 | A6000 | 48GB | 128GB | 192.222.58.232 | $0.80 | AI workloads |
| sophia-a100 | A100 | 40GB | 256GB | 104.171.202.103 | $1.29 | Data processing |
| sophia-a10 | A10 | 24GB | 64GB | 155.248.194.183 | $0.75 | Development/monitoring |

**Total**: $4.83/hour base + $1.00/hour peak = $5.83/hour

### SSH Access

```bash
# Configure SSH
cat >> ~/.ssh/config << EOF
Host sophia-main
    HostName 192.222.51.151
    User ubuntu
    IdentityFile ~/.ssh/lambda_labs_sophia_key
    StrictHostKeyChecking no

Host sophia-rtx-1
    HostName 192.222.51.122
    User ubuntu
    IdentityFile ~/.ssh/lambda_labs_sophia_key
    StrictHostKeyChecking no

# Add other instances...
EOF

# Test connection
ssh sophia-main
```

## Instance Management

### Using Lambda Labs Manager

```bash
# List all instances
python scripts/lambda_labs_manager.py list

# Get instance details
python scripts/lambda_labs_manager.py get sophia-main

# Launch new instance
python scripts/lambda_labs_manager.py launch \
  --name sophia-new \
  --type gpu_1x_a10 \
  --region us-west-1

# Terminate instance
python scripts/lambda_labs_manager.py terminate sophia-old

# Restart instance
python scripts/lambda_labs_manager.py restart sophia-main
```

### Manual API Usage

```bash
# Set API key
export LAMBDA_API_KEY="secret_sophia5apikey_..."

# List instances
curl -H "Authorization: Bearer $LAMBDA_API_KEY" \
  https://cloud.lambdalabs.com/api/v1/instances

# Get specific instance
curl -H "Authorization: Bearer $LAMBDA_API_KEY" \
  https://cloud.lambdalabs.com/api/v1/instances/7e7b1e5f53c44a26bd574e4266e96194
```

## Deployment Procedures

### Backend Deployment

```bash
# 1. Build and push image
docker build -t scoobyjava15/sophia-backend:latest -f Dockerfile.production .
docker push scoobyjava15/sophia-backend:latest

# 2. Deploy to Lambda Labs
ssh sophia-main << 'EOF'
# Pull latest image
docker pull scoobyjava15/sophia-backend:latest

# Stop existing container
docker stop sophia-backend || true
docker rm sophia-backend || true

# Start new container
docker run -d \
  --name sophia-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e PULUMI_ORG=scoobyjava-org \
  --health-cmd="curl -f http://localhost:8000/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  scoobyjava15/sophia-backend:latest

# Verify
docker ps
curl http://localhost:8000/health
EOF
```

### MCP Server Deployment

```bash
# Deploy all MCP servers
python scripts/deployment/deploy_mcp_servers.py \
  --host 192.222.51.151 \
  --servers linear,github,asana,ui-ux,lambda-cli

# Deploy specific server
ssh sophia-main << 'EOF'
docker run -d \
  --name mcp-linear \
  --restart unless-stopped \
  -p 9004:9004 \
  -e ENVIRONMENT=production \
  scoobyjava15/sophia-mcp-linear:latest
EOF
```

### Multi-Instance Deployment

```bash
# Deploy across multiple instances
python scripts/deployment/deploy_sophia_complete.py \
  --backend-host 192.222.51.151 \
  --mcp-host 192.222.51.122 \
  --ai-host 192.222.58.232 \
  --parallel
```

## Service Configuration

### Docker Setup on New Instance

```bash
# Run on new Lambda Labs instance
ssh ubuntu@<instance-ip> << 'EOF'
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configure Docker daemon
sudo tee /etc/docker/daemon.json << END
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
END

sudo systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
EOF
```

### Service Health Monitoring

```bash
# Check all services
python scripts/deployment/health_check.py --all-instances

# Monitor specific instance
python scripts/deployment/monitor.py \
  --host 192.222.51.151 \
  --interval 60 \
  --services backend,mcp-linear,mcp-github

# View logs
ssh sophia-main docker logs -f sophia-backend --tail 100
```

## Cost Optimization

### Instance Selection Guide

| Workload | Recommended | GPU | Cost/hr | Notes |
|----------|-------------|-----|---------|-------|
| API Backend | RTX 6000 | 24GB | $0.50 | Best value |
| MCP Servers | RTX 6000 | 24GB | $0.50 | Sufficient |
| AI Training | A100 | 40GB | $1.29 | Fast training |
| AI Inference | A10 | 24GB | $0.75 | Good balance |
| Development | A10 | 24GB | $0.75 | Cost effective |
| Heavy Compute | GH200 | 96GB | $1.49 | Maximum power |

### Cost Saving Strategies

1. **Auto-shutdown Development**
   ```bash
   # Schedule shutdown for dev instances
   python scripts/lambda_labs_manager.py schedule-shutdown \
     --instance sophia-dev \
     --after-hours 8
   ```

2. **Use Spot Instances** (when available)
   ```bash
   python scripts/lambda_labs_manager.py launch \
     --name sophia-spot \
     --type gpu_1x_a10 \
     --spot
   ```

3. **Resource Monitoring**
   ```bash
   # Monitor GPU usage
   ssh sophia-main nvidia-smi -l 5
   
   # Check if underutilized
   python scripts/deployment/resource_monitor.py \
     --threshold 20 \
     --alert-underutilized
   ```

## Backup and Recovery

### Automated Backups

```bash
# Backup critical data
python scripts/deployment/backup_lambda_labs.py \
  --instance sophia-main \
  --backup-path /mnt/shared/backups \
  --include postgres,redis,logs
```

### Disaster Recovery

```bash
# 1. Launch replacement instance
python scripts/lambda_labs_manager.py launch \
  --name sophia-recovery \
  --type gpu_1x_gh200 \
  --region us-west-1

# 2. Restore from backup
python scripts/deployment/restore_instance.py \
  --source-backup /mnt/shared/backups/latest \
  --target-instance <new-ip>

# 3. Update DNS/load balancer
python scripts/deployment/update_endpoints.py \
  --old-ip 192.222.51.151 \
  --new-ip <new-ip>
```

## Monitoring and Alerts

### Prometheus Setup

```bash
ssh sophia-main << 'EOF'
# Deploy Prometheus
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /opt/prometheus:/etc/prometheus \
  prom/prometheus

# Deploy Grafana
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana
EOF
```

### Alert Configuration

```yaml
# alerts.yml
groups:
  - name: lambda_labs
    rules:
      - alert: InstanceDown
        expr: up{job="lambda_labs"} == 0
        for: 5m
        annotations:
          summary: "Lambda Labs instance {{ $labels.instance }} is down"
          
      - alert: HighGPUUsage
        expr: gpu_utilization > 90
        for: 15m
        annotations:
          summary: "High GPU usage on {{ $labels.instance }}"
          
      - alert: DiskSpaceLow
        expr: disk_free_percent < 10
        for: 5m
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
```

## Troubleshooting

### Common Issues

#### Connection Timeout
```bash
# Check instance status
python scripts/lambda_labs_manager.py status sophia-main

# Verify security groups
curl -H "Authorization: Bearer $LAMBDA_API_KEY" \
  https://cloud.lambdalabs.com/api/v1/instances/<id>

# Test network
ping 192.222.51.151
traceroute 192.222.51.151
```

#### GPU Not Available
```bash
# Check NVIDIA drivers
ssh sophia-main nvidia-smi

# Reinstall if needed
ssh sophia-main << 'EOF'
sudo apt update
sudo apt install -y nvidia-driver-525
sudo reboot
EOF
```

#### Container Won't Start
```bash
# Check logs
ssh sophia-main docker logs sophia-backend

# Inspect container
ssh sophia-main docker inspect sophia-backend

# Check resources
ssh sophia-main df -h
ssh sophia-main free -h
```

## Best Practices

### Security
- ✅ Use SSH keys, never passwords
- ✅ Restrict SSH access by IP
- ✅ Regular security updates
- ✅ Monitor access logs
- ✅ Use private networks when possible

### Performance
- ✅ Use GPU instances only when needed
- ✅ Monitor resource utilization
- ✅ Optimize container images
- ✅ Use local SSD for databases
- ✅ Enable Docker BuildKit

### Reliability
- ✅ Health checks on all services
- ✅ Automated restarts
- ✅ Regular backups
- ✅ Multi-instance redundancy
- ✅ Monitoring and alerts

## Appendix

### Useful Commands

```bash
# System info
ssh sophia-main << 'EOF'
# GPU info
nvidia-smi

# System resources
htop

# Disk usage
df -h

# Network connections
ss -tulpn

# Docker status
docker ps -a
docker stats

# Service logs
journalctl -u docker -f
EOF
```

### Instance Types Reference

| Type | GPU | VRAM | RAM | vCPUs | Storage | Cost/hr |
|------|-----|------|-----|-------|---------|---------|
| gpu_1x_a10 | 1x A10 | 24 GB | 64 GB | 30 | 512 GB | $0.75 |
| gpu_1x_rtx6000 | 1x RTX 6000 | 24 GB | 64 GB | 14 | 512 GB | $0.50 |
| gpu_1x_a6000 | 1x A6000 | 48 GB | 128 GB | 30 | 512 GB | $0.80 |
| gpu_1x_a100_sxm4 | 1x A100 | 40 GB | 256 GB | 30 | 512 GB | $1.29 |
| gpu_1x_gh200 | 1x GH200 | 96 GB | 480 GB | 72 | 1 TB | $1.49 |

### Support

- **Lambda Labs Support**: support@lambdalabs.com
- **Documentation**: https://docs.lambdalabs.com
- **Status Page**: https://status.lambdalabs.com
- **Community**: https://community.lambdalabs.com 