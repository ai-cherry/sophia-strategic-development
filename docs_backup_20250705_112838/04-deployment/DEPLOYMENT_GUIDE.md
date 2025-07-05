# Sophia AI Deployment Guide

**Last Updated**: 2025-07-04

## 🚀 Production Deployment

### Prerequisites

- Snowflake account with Cortex AI enabled
- Lambda Labs API key and SSH access
- Vercel account for frontend
- Pulumi ESC for secrets
- Docker Hub account

### Infrastructure Overview

```
┌─────────────────────────────────────────┐
│         Vercel Edge Network             │
│         (Frontend Deployment)           │
└────────────────┬───────────────────────┘
                 │
┌────────────────▼───────────────────────┐
│        Lambda Labs GPU Instances        │
│   ┌─────────────┬─────────────┬──────┐│
│   │Platform     │MCP Servers  │AI    ││
│   │(Main API)   │(27 servers) │(GPU) ││
│   └─────────────┴─────────────┴──────┘│
└────────────────┬───────────────────────┘
                 │
┌────────────────▼───────────────────────┐
│           Snowflake Cortex              │
│    (Data + AI + Vector Search)          │
└─────────────────────────────────────────┘
```

### Deployment Steps

#### 1. Snowflake Setup

```bash
# Run alignment script
snowsql -f snowflake_complete_alignment.sql

# Verify setup
python scripts/verify_and_align_snowflake.py
```

#### 2. Lambda Labs Deployment

```bash
# Quick deployment
export LAMBDA_API_KEY="your-key"
export LAMBDA_SSH_KEY_PATH=~/.ssh/lambda_labs_sophia
./scripts/quick_lambda_deploy.sh
```

#### 3. Vercel Frontend

```bash
# Deploy frontend
cd frontend
vercel --prod
```

#### 4. Configure DNS

Point your domain to:
- Frontend: Vercel domains
- API: Lambda Labs IPs

### Production URLs

- Frontend: https://app.sophia-ai.com
- API: https://api.sophia-ai.com
- Docs: https://api.sophia-ai.com/docs

### Monitoring

- Grafana: https://monitoring.sophia-ai.com
- Prometheus: Internal only
- Snowflake: Query history dashboard

### Security Checklist

- [ ] All secrets in Pulumi ESC
- [ ] SSL certificates configured
- [ ] Firewall rules set
- [ ] Snowflake roles configured
- [ ] API rate limiting enabled

### Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.
