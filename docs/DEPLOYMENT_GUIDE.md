# Sophia AI Deployment Guide

## Overview

This is the **authoritative deployment guide** for Sophia AI. All deployments follow the patterns documented here.

## Quick Deployment

### Prerequisites
- Docker Hub account with push permissions
- Pulumi access token configured
- Lambda Labs API key

### Automated Deployment (Recommended)

1. **Push to main branch** - triggers automatic deployment via GitHub Actions
2. **Monitor workflow** - check GitHub Actions tab for progress
3. **Verify deployment** - health checks run automatically

### Manual Deployment (Emergency)

```bash
# 1. Build and push image
docker build -t scoobyjava15/sophia-ai:latest -f Dockerfile.production .
docker push scoobyjava15/sophia-ai:latest

# 2. Deploy infrastructure
cd infrastructure/
pulumi up --stack scoobyjava-org/sophia-prod-on-lambda

# 3. Deploy to Kubernetes
kubectl apply -f kubernetes/
kubectl rollout status deployment/sophia-ai
```

## Infrastructure Architecture

- **CI/CD**: GitHub Actions (`sophia-production-deployment.yml`)
- **Container Registry**: Docker Hub (`scoobyjava15/sophia-ai`)
- **Infrastructure**: Pulumi (Lambda Labs Kubernetes)
- **Deployment**: Kubernetes manifests
- **Monitoring**: Built-in health checks

## Environment Variables

Required secrets (managed in GitHub):
- `DOCKER_USER_NAME` - Docker Hub username
- `DOCKER_PERSONAL_ACCESS_TOKEN` - Docker Hub token
- `PULUMI_ACCESS_TOKEN` - Pulumi access token
- `LAMBDA_LABS_API_KEY` - Lambda Labs API key

## Troubleshooting

### Build Failures
- Check Dockerfile.production exists
- Verify .dockerignore excludes unnecessary files
- Check Docker Hub credentials

### Deployment Failures
- Validate environment variables: `python scripts/validate_deployment_env.py`
- Check Pulumi stack status
- Verify Kubernetes cluster access

### Health Check Failures
- Ensure LAMBDA_LABS_INSTANCE_IP is properly set
- Check service endpoints are accessible
- Verify Pulumi outputs are correct

## Architecture Decisions

### Current Approach (Approved)
- **Hybrid Infrastructure**: Pulumi for AWS resources + manual Kubernetes
- **Single Instance Databases**: Redis/PostgreSQL without HA (sufficient for current scale)
- **Docker Registry**: Docker Hub (scoobyjava15)
- **Primary Dockerfile**: Dockerfile.production

### Rejected Approaches (Over-Engineering)
- Full Pulumi Kubernetes resource management
- High Availability database clustering
- Complex cache invalidation strategies
- Multiple environment complexity

This approach prioritizes **stability and simplicity** over theoretical scalability needs.
