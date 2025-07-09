# Sophia AI Master Deployment Guide

> **Last Updated**: 2025-07-08  
> **Version**: 2.0  
> **Status**: Production Ready

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Deployment Methods](#deployment-methods)
5. [Security](#security)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Emergency Procedures](#emergency-procedures)

## Overview

Sophia AI is deployed on Lambda Labs GPU infrastructure using Docker containerization and GitHub Actions automation. This guide provides the authoritative deployment procedures for all environments.

### Key Principles

- **Infrastructure as Code**: All infrastructure managed via Pulumi
- **GitOps**: Deployments triggered via Git operations
- **Zero Trust Security**: No hardcoded secrets, all credentials in GitHub/Pulumi ESC
- **Automated Everything**: From builds to deployments to monitoring

## Architecture

### Infrastructure Overview

```
┌─────────────────────────────────────────────────┐
│            GitHub Repository                     │
│         (ai-cherry/sophia-main)                 │
└────────────────┬────────────────────────────────┘
                 │ Push to main
                 ▼
┌─────────────────────────────────────────────────┐
│          GitHub Actions CI/CD                    │
│    • Build Docker images                         │
│    • Push to Docker Hub (scoobyjava15)         │
│    • Deploy via SSH to Lambda Labs             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           Lambda Labs Infrastructure             │
├─────────────────────────────────────────────────┤
│  Main Instance (192.222.51.151)                 │
│  • Type: GH200 (96GB GPU)                      │
│  • Services: Backend API, MCP Servers          │
│  • Cost: $1.49/hour                            │
├─────────────────────────────────────────────────┤
│  Additional Instances (as needed)               │
│  • RTX 6000, A100, A6000, A10                  │
│  • Purpose: Scaling, specialized workloads     │
└─────────────────────────────────────────────────┘
```

### Service Architecture

```yaml
Services:
  Backend:
    - Main API (FastAPI)
    - Port: 8000
    - Replicas: 1-3
    
  MCP Servers:
    - Linear (9004)
    - GitHub (9103)
    - Asana (9100)
    - UI/UX Agent (9002)
    - Lambda Labs CLI (9040)
    - Lambda Labs Serverless (9025)
    
  Infrastructure:
    - PostgreSQL
    - Redis
    - Prometheus/Grafana
```

## Prerequisites

### Required Access

1. **GitHub Organization Access**
   - Member of `ai-cherry` organization
   - Write access to `sophia-main` repository

2. **Lambda Labs Access**
   - API key stored in GitHub secrets
   - SSH key configured

3. **Docker Hub Access**
   - Account: `scoobyjava15`
   - Access token in GitHub secrets

4. **Pulumi Access**
   - Organization: `scoobyjava-org`
   - Access token in GitHub secrets

### Local Setup

```bash
# 1. Clone repository
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main

# 2. Install dependencies
pip install -r requirements.txt
npm install

# 3. Configure GitHub CLI
gh auth login

# 4. Verify access
python scripts/deployment/verify_access.py
```

## Deployment Methods

### Method 1: Automated GitHub Actions (Recommended)

#### Production Deployment

```bash
# Automatic deployment on push to main
git push origin main

# Manual deployment
gh workflow run main-deployment.yml
```

#### Deployment with Options

```bash
# Deploy specific components
gh workflow run main-deployment.yml \
  -f environment=production \
  -f deploy_backend=true \
  -f deploy_mcp=true \
  -f deploy_frontend=false
```

### Method 2: Direct Deployment Script

```bash
# Full deployment
python scripts/deployment/deploy.py \
  --environment production \
  --components all

# Backend only
python scripts/deployment/deploy.py \
  --environment production \
  --components backend

# MCP servers only
python scripts/deployment/deploy.py \
  --environment production \
  --components mcp
```

### Method 3: Emergency Manual Deployment

```bash
# SSH to Lambda Labs
ssh -i ~/.ssh/lambda_labs_sophia_key ubuntu@192.222.51.151

# Pull latest images
docker pull scoobyjava15/sophia-backend:latest
docker pull scoobyjava15/sophia-mcp-linear:latest

# Stop existing containers
docker stop sophia-backend sophia-mcp-linear

# Start new containers
docker run -d \
  --name sophia-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  scoobyjava15/sophia-backend:latest

docker run -d \
  --name sophia-mcp-linear \
  --restart unless-stopped \
  -p 9004:9004 \
  -e ENVIRONMENT=production \
  scoobyjava15/sophia-mcp-linear:latest
```

## Security

### Secret Management

All secrets are managed through:

1. **GitHub Organization Secrets** → 2. **GitHub Actions** → 3. **Pulumi ESC** → 4. **Application Runtime**

#### Required Secrets

```yaml
# AI Services
OPENAI_API_KEY
ANTHROPIC_API_KEY
PORTKEY_API_KEY
OPENROUTER_API_KEY

# Infrastructure
LAMBDA_API_KEY
LAMBDA_SSH_PRIVATE_KEY
DOCKER_HUB_ACCESS_TOKEN
PULUMI_ACCESS_TOKEN

# Data Services
SNOWFLAKE_ACCOUNT
SNOWFLAKE_USERNAME
SNOWFLAKE_PASSWORD
POSTGRES_PASSWORD

# Integrations
GITHUB_TOKEN
LINEAR_API_KEY
ASANA_ACCESS_TOKEN
SLACK_BOT_TOKEN
```

### Security Checklist

- [ ] No secrets in code
- [ ] All secrets in GitHub org secrets
- [ ] Pre-commit hooks installed
- [ ] Secret scanning enabled
- [ ] Access logs reviewed

## Monitoring

### Health Check Endpoints

```yaml
Backend API:
  URL: http://192.222.51.151:8000/health
  Expected: {"status": "healthy"}
  
MCP Servers:
  Linear: http://192.222.51.151:9004/health
  GitHub: http://192.222.51.151:9103/health
  Asana: http://192.222.51.151:9100/health
```

### Monitoring Commands

```bash
# Check all services
python scripts/deployment/health_check.py --all

# Check specific service
python scripts/deployment/health_check.py --service backend

# Continuous monitoring
python scripts/deployment/monitor.py --interval 60
```

### Metrics & Dashboards

- **Prometheus**: http://192.222.51.151:9090
- **Grafana**: http://192.222.51.151:3000
- **Logs**: Via SSH and `docker logs`

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker logs sophia-backend

# Common fixes:
# - Verify environment variables
# - Check port conflicts
# - Validate image exists
```

#### 2. Health Check Failing

```bash
# Test connectivity
curl http://192.222.51.151:8000/health

# Check container status
docker ps -a

# Restart container
docker restart sophia-backend
```

#### 3. Secret Loading Issues

```bash
# Verify Pulumi ESC
pulumi env get scoobyjava-org/default/sophia-ai-production

# Check environment in container
docker exec sophia-backend env | grep -E "(API_KEY|TOKEN)"
```

### Debug Commands

```bash
# Full system diagnostics
python scripts/deployment/diagnose.py

# Container inspection
docker inspect sophia-backend

# Network debugging
docker network ls
docker network inspect bridge
```

## Emergency Procedures

### Rollback Procedure

```bash
# 1. Identify last working version
docker images | grep sophia-backend

# 2. Stop current container
docker stop sophia-backend

# 3. Start previous version
docker run -d \
  --name sophia-backend-rollback \
  -p 8000:8000 \
  scoobyjava15/sophia-backend:previous-tag

# 4. Verify health
curl http://192.222.51.151:8000/health
```

### Disaster Recovery

```bash
# 1. Launch new Lambda Labs instance
python scripts/deployment/launch_emergency_instance.py

# 2. Deploy core services
python scripts/deployment/emergency_deploy.py \
  --instance <new-ip> \
  --components core

# 3. Update DNS (if applicable)
python scripts/deployment/update_dns.py --ip <new-ip>

# 4. Restore data from backups
python scripts/deployment/restore_data.py
```

### Emergency Contacts

- **On-Call**: Check GitHub organization settings
- **Lambda Labs Support**: support@lambdalabs.com
- **Escalation**: Via Slack #sophia-alerts

## Appendix

### Useful Commands

```bash
# View all running containers
docker ps

# View container logs
docker logs -f sophia-backend

# Execute command in container
docker exec -it sophia-backend /bin/bash

# Copy files from container
docker cp sophia-backend:/app/logs ./local-logs

# System resource usage
docker stats

# Clean up old images
docker system prune -a
```

### Environment Variables

```bash
# Required for all services
ENVIRONMENT=production
PULUMI_ORG=scoobyjava-org

# Service-specific (loaded from Pulumi ESC)
# Do not hardcode these!
```

### Version History

- v2.0 (2025-07-08): Complete restructure, Lambda Labs focus
- v1.5 (2025-07-01): Added MCP servers deployment
- v1.0 (2025-06-01): Initial deployment guide

---

**Remember**: Always follow the security guidelines. Never commit secrets. When in doubt, ask for help! 