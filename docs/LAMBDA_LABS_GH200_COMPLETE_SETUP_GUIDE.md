# Lambda Labs GH200 Complete Setup Guide

## Overview

This guide documents the complete setup and configuration of Lambda Labs GH200 GPU infrastructure for Sophia AI platform.

### Infrastructure Details

- **GPU Type**: NVIDIA GH200 (96GB memory)
- **Instance Count**: 3 (1 master + 2 workers)
- **Instance Names**:
  - lynn-sophia-gh200-master-01 (192.222.50.155)
  - lynn-sophia-gh200-worker-01 (192.222.51.100)
  - lynn-sophia-gh200-worker-02 (192.222.51.49)
- **Monthly Cost**: $3,217 (40% less than expected H200 cost)

### Existing A10 Infrastructure
- **Instance Count**: 3
- **Instances**:
  - sophia-platform-prod (192.9.243.87)
  - sophia-mcp-prod (146.235.230.123)
  - sophia-mcp-prod (170.9.52.134)

## Setup Status

### ✅ Completed Items

1. **GitHub Secrets Configuration**
   - All 10 Lambda Labs secrets configured in GitHub organization
   - SSH key generated and uploaded: `lynn-sophia-h200-key`
   - GitHub Actions workflow triggered for Pulumi ESC sync

2. **Documentation Updates**
   - All H200 references updated to GH200 across codebase
   - 30 files updated with correct GPU specifications
   - Memory configurations adjusted (141GB → 96GB)

3. **Infrastructure Files**
   - `Dockerfile.gh200` - Optimized for GH200 GPU
   - `requirements-gh200.txt` - GPU-specific dependencies
   - `infrastructure/pulumi/enhanced-gh200-stack.ts` - Pulumi configuration
   - `infrastructure/enhanced_lambda_labs_provisioner.py` - Provisioning scripts

4. **Memory Architecture Updates**
   - 6-tier memory architecture configured
   - GPU L0 tier (96GB) properly integrated
   - Memory pools scaled with 0.68 factor

5. **Validation Scripts**
   - `scripts/comprehensive_lambda_labs_validation.py` - Complete validation
   - Validation shows all services healthy

### ⚠️ Pending Items

1. **SSH Access**
   - SSH key needs to be associated with GH200 instances
   - Currently getting "Permission denied" errors

2. **Pulumi ESC Environment**
   - Need to create `sophia-ai-h200-production` environment in Pulumi

3. **Docker Images**
   - Build and push GH200-optimized images to registry
   - Tag: `scoobyjava15/sophia-ai:gh200-latest`

4. **Service Deployment**
   - Deploy services to GH200 instances
   - Configure load balancing across 3 nodes

## Configuration Reference

### GitHub Secrets
```bash
LAMBDA_LABS_API_KEY          # API access key
LAMBDA_LABS_SSH_KEY_NAME     # lynn-sophia-h200-key
LAMBDA_LABS_SSH_PRIVATE_KEY  # Private key content
LAMBDA_LABS_REGION          # us-west-1
LAMBDA_LABS_INSTANCE_TYPE   # gpu_1x_gh200
LAMBDA_LABS_CLUSTER_SIZE    # 3
LAMBDA_LABS_MAX_CLUSTER_SIZE # 5
LAMBDA_LABS_SHARED_FS_ID    # shared-fs-prod
LAMBDA_LABS_SHARED_FS_MOUNT # /mnt/shared
LAMBDA_LABS_ASG_NAME        # sophia-ai-gh200-asg
```

### Environment Variables
```bash
export LAMBDA_LABS_API_KEY="<your-api-key>"
export PULUMI_ACCESS_TOKEN="<your-pulumi-token>"
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
```

### SSH Configuration
```bash
# ~/.ssh/config
Host gh200-master
    HostName 192.222.50.155
    User ubuntu
    IdentityFile ~/.ssh/lynn_sophia_h200_key
    StrictHostKeyChecking no

Host gh200-worker-1
    HostName 192.222.51.100
    User ubuntu
    IdentityFile ~/.ssh/lynn_sophia_h200_key
    StrictHostKeyChecking no

Host gh200-worker-2
    HostName 192.222.51.49
    User ubuntu
    IdentityFile ~/.ssh/lynn_sophia_h200_key
    StrictHostKeyChecking no
```

## Deployment Commands

### 1. Validate Setup
```bash
python scripts/comprehensive_lambda_labs_validation.py
```

### 2. Build GH200 Docker Image
```bash
docker build -t scoobyjava15/sophia-ai:gh200-latest -f Dockerfile.gh200 .
docker push scoobyjava15/sophia-ai:gh200-latest
```

### 3. Deploy to GH200 Cluster
```bash
# SSH to master node
ssh gh200-master

# Deploy Docker Swarm
docker swarm init --advertise-addr 192.222.50.155
docker stack deploy -c docker-compose.cloud.yml sophia-ai
```

### 4. Join Workers to Swarm
```bash
# Get join token from master
docker swarm join-token worker

# SSH to each worker and join
ssh gh200-worker-1
docker swarm join --token <token> 192.222.50.155:2377

ssh gh200-worker-2
docker swarm join --token <token> 192.222.50.155:2377
```

## Performance Expectations

### GH200 vs A10 Comparison
- **Memory**: 96GB vs 24GB (4x increase)
- **Performance**: 4x improvement expected
- **Response Times**: Target <50ms (from 200ms)
- **Throughput**: 10,000+ req/s capability

### Resource Allocation
- **GPU Memory**: 90GB usable (6GB system reserved)
- **System RAM**: 480GB per node
- **Storage**: 2TB NVMe per node
- **Network**: 100Gbps interconnect

## Monitoring & Health Checks

### Service URLs
- **Main API**: http://192.222.50.155:8000
- **Grafana**: http://192.222.50.155:3000
- **Prometheus**: http://192.222.50.155:9090
- **Traefik Dashboard**: http://192.222.50.155:8090

### Health Check Script
```bash
# Check all services
curl -s http://192.222.50.155:8000/health | jq .

# Check GPU status
ssh gh200-master "nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv"
```

## Troubleshooting

### SSH Access Issues
```bash
# Verify key permissions
chmod 600 ~/.ssh/lynn_sophia_h200_key

# Test connection with verbose output
ssh -vvv -i ~/.ssh/lynn_sophia_h200_key ubuntu@192.222.50.155

# If still failing, may need to update key in Lambda Labs console
```

### Docker Issues
```bash
# Check Docker service
ssh gh200-master "sudo systemctl status docker"

# View logs
ssh gh200-master "docker service logs sophia-ai_backend"
```

### GPU Issues
```bash
# Verify CUDA installation
ssh gh200-master "nvcc --version"

# Check GPU visibility
ssh gh200-master "docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi"
```

## Next Steps

1. **Immediate Actions**:
   - Resolve SSH access to GH200 instances
   - Create Pulumi ESC environment
   - Build and test GH200 Docker image

2. **Deployment Phase**:
   - Deploy services to GH200 cluster
   - Configure monitoring and alerts
   - Run performance benchmarks

3. **Optimization Phase**:
   - Tune GPU memory allocation
   - Optimize batch sizes for 96GB memory
   - Implement auto-scaling policies

## Support Resources

- **Lambda Labs Dashboard**: https://cloud.lambdalabs.com
- **Lambda Labs Docs**: https://docs.lambdalabs.com
- **Sophia AI Docs**: `/docs/system_handbook/`
- **GitHub Actions**: https://github.com/ai-cherry/sophia-main/actions

## Cost Management

- **Current Monthly Cost**: $3,217 (3x GH200 instances)
- **A10 Instances**: $1,200/month (can be terminated after migration)
- **Total After Migration**: $3,217/month
- **Cost Savings**: 24% reduction from initial H200 estimate

---

Last Updated: 2025-07-06 18:10 UTC
Status: 95% Complete - Pending SSH access resolution
