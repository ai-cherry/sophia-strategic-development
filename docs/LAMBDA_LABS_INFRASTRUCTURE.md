# Lambda Labs Infrastructure Documentation

**Last Updated**: July 7, 2025
**Status**: 5 Instances Active
**Total Cost**: $4.83/hour ($115.92/day)

## 🏗️ Infrastructure Overview

Sophia AI runs on a 5-instance Lambda Labs infrastructure designed for enterprise-grade AI operations, monitoring, and development with complete Pulumi ESC secret management.

### Active Instance Configuration

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOPHIA AI INFRASTRUCTURE                     │
├─────────────────────────────────────────────────────────────────┤
│ sophia-ai-core          │ 192.222.58.232  │ GH200 96GB │ $1.49/hr │
│ sophia-production       │ 104.171.202.103 │ RTX6000 24GB│ $0.50/hr │
│ sophia-mcp-orchestrator │ 104.171.202.117 │ A6000 48GB │ $0.80/hr │
│ sophia-data-pipeline    │ 104.171.202.134 │ A100 40GB  │ $1.29/hr │
│ sophia-development      │ 155.248.194.183 │ A10 24GB   │ $0.75/hr │
└─────────────────────────────────────────────────────────────────┘
```

## 🔐 Secret Management Integration

### Pulumi ESC Configuration

All Lambda Labs credentials are managed through the unified secret pipeline:

```
GitHub Organization Secrets → Pulumi ESC → Backend Auto-Loading
```

**Required Secrets in GitHub Organization (ai-cherry):**
- `LAMBDA_API_KEY`: Lambda Labs API authentication key
- `LAMBDA_SSH_KEY`: SSH public key for instance access
- `LAMBDA_PRIVATE_SSH_KEY`: SSH private key for deployment
- `LAMBDA_API_ENDPOINT`: https://cloud.lambda.ai/api/v1/instances

### Backend Integration

```python
# Automatic secret loading in backend
from backend.core.auto_esc_config import get_lambda_labs_config

config = get_lambda_labs_config()
api_key = config['api_key']
ssh_key_path = config['ssh_key_path']
```

## 🖥️ Instance Details

### 1. sophia-ai-core (CRITICAL)
- **IP**: 192.222.58.232
- **Type**: GH200 (96GB GPU Memory)
- **Region**: us-east-3
- **Cost**: $1.49/hour
- **Purpose**: Core AI Services & Lambda GPU
- **Services**: AI Memory MCP (9001), FastAPI Backend (8000)
- **SSH**: `ssh -i ~/.ssh/sophia_lambda_key ubuntu@192.222.58.232`

### 2. sophia-production-instance
- **IP**: 104.171.202.103
- **Type**: RTX6000 (24GB GPU)
- **Region**: us-south-1
- **Cost**: $0.50/hour
- **Purpose**: Monitoring & Operations
- **Services**: Prometheus (9090), Grafana (3000), Health Monitoring
- **SSH**: `ssh -i ~/.ssh/sophia_lambda_key ubuntu@104.171.202.103`

### 3. sophia-mcp-orchestrator
- **IP**: 104.171.202.117
- **Type**: A6000 (48GB GPU)
- **Region**: us-south-1
- **Cost**: $0.80/hour
- **Purpose**: MCP Server Orchestration & Business Intelligence
- **Services**: MCP Gateway (8080), Business Intelligence APIs
- **SSH**: `ssh -i ~/.ssh/sophia_lambda_key ubuntu@104.171.202.117`

### 4. sophia-data-pipeline
- **IP**: 104.171.202.134
- **Type**: A100 (40GB GPU)
- **Region**: us-south-1
- **Cost**: $1.29/hour
- **Purpose**: Data Processing & ETL Operations
- **Services**: Modern Stack Connections, ETL Pipelines, Data Ingestion
- **SSH**: `ssh -i ~/.ssh/sophia_lambda_key ubuntu@104.171.202.134`

### 5. sophia-development
- **IP**: 155.248.194.183
- **Type**: A10 (24GB GPU)
- **Region**: us-west-1
- **Cost**: $0.75/hour
- **Purpose**: Development & Testing Environment
- **Services**: Development MCP Servers, Testing Infrastructure
- **SSH**: `ssh -i ~/.ssh/sophia_lambda_key ubuntu@155.248.194.183`

## 🔑 SSH Key Management

### Unified SSH Strategy
- **Key Name**: `sophia2025` (configured in Lambda Labs)
- **Local Path**: `~/.ssh/sophia_lambda_key`
- **Public Key**: Stored in `LAMBDA_SSH_KEY` (GitHub → Pulumi ESC)
- **Private Key**: Stored in `LAMBDA_PRIVATE_SSH_KEY` (GitHub → Pulumi ESC)

### SSH Connection Commands
```bash
# Core AI Services (CRITICAL)
ssh -i ~/.ssh/sophia_lambda_key ubuntu@192.222.58.232

# Production Monitoring
ssh -i ~/.ssh/sophia_lambda_key ubuntu@104.171.202.103

# MCP Orchestration
ssh -i ~/.ssh/sophia_lambda_key ubuntu@104.171.202.117

# Data Pipeline
ssh -i ~/.ssh/sophia_lambda_key ubuntu@104.171.202.134

# Development Environment
ssh -i ~/.ssh/sophia_lambda_key ubuntu@155.248.194.183
```

## 🚀 Deployment Workflow

### GitHub Actions Integration

```yaml
name: Lambda Labs Deployment
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Lambda Labs
        env:
          LAMBDA_API_KEY: ${{ secrets.LAMBDA_API_KEY }}
          LAMBDA_SSH_KEY: ${{ secrets.LAMBDA_SSH_KEY }}
        run: |
          python scripts/deploy_to_lambda_labs.py
```

### Automatic Secret Sync

All secrets automatically sync from GitHub → Pulumi ESC → Backend:

1. **GitHub Organization Secrets**: Manual updates via GitHub UI
2. **Pulumi ESC Sync**: Automatic via GitHub Actions workflow
3. **Backend Loading**: Automatic via `auto_esc_config.py`

## 📊 Service Monitoring

### Health Check URLs
```bash
# Production Monitoring
http://104.171.202.103:3000  # Grafana Dashboard
http://104.171.202.103:9090  # Prometheus Metrics

# Core AI Services
http://192.222.58.232:8000   # FastAPI Backend
http://192.222.58.232:9001   # AI Memory MCP

# MCP Orchestration
http://104.171.202.117:8080  # MCP Gateway

# Development Environment
http://155.248.194.183:8000  # Dev API
```

### Instance Status Validation

```python
# Use the infrastructure validation script
python scripts/validate_lambda_infrastructure.py

# Expected output:
# ✅ All 5 instances active
# ✅ SSH connectivity verified
# ✅ Secret management operational
# ✅ Total cost: $4.83/hour
```

## 💰 Cost Management

### Current Costs
- **sophia-ai-core**: $1.49/hour (GH200 - CRITICAL)
- **sophia-mcp-orchestrator**: $0.80/hour (A6000)
- **sophia-data-pipeline**: $1.29/hour (A100)
- **sophia-development**: $0.75/hour (A10)
- **sophia-production**: $0.50/hour (RTX6000)

**Total**: $4.83/hour ($115.92/day, $3,477.60/month)

### Cost Optimization
- Development instance can be stopped when not in use
- Production monitoring runs 24/7 (essential)
- Core AI services run 24/7 (business critical)
- Data pipeline runs on-demand for large operations

## 🛠️ Maintenance Procedures

### Weekly Tasks
- [ ] Verify all instances are running
- [ ] Check SSH connectivity
- [ ] Validate secret pipeline
- [ ] Review cost reports
- [ ] Update system packages

### Monthly Tasks
- [ ] Rotate SSH keys
- [ ] Review instance utilization
- [ ] Optimize costs
- [ ] Update documentation
- [ ] Security audit

### Emergency Procedures

**Instance Failure:**
1. Check Lambda Labs dashboard
2. Restart instance via API
3. Verify SSH connectivity
4. Redeploy services if needed

**SSH Key Compromise:**
1. Generate new SSH key pair
2. Update GitHub organization secrets
3. Deploy new keys to all instances
4. Update local SSH configuration

**API Key Rotation:**
1. Generate new Lambda Labs API key
2. Update `LAMBDA_API_KEY` in GitHub secrets
3. Verify automatic propagation to Pulumi ESC
4. Test API connectivity

## 📚 Related Documentation

- [Pulumi ESC Integration](./PULUMI_ESC_INTEGRATION.md)
- [GitHub Actions Workflows](../.github/workflows/)
- [Secret Management Architecture](./SECRET_MANAGEMENT.md)
- [Infrastructure Monitoring](./MONITORING.md)

## 🔧 Troubleshooting

### Common Issues

**SSH Connection Refused:**
```bash
# Check instance status
python -c "
from backend.core.auto_esc_config import get_lambda_labs_config
import requests
config = get_lambda_labs_config()
response = requests.get('https://cloud.lambda.ai/api/v1/instances',
                       headers={'Authorization': f'Bearer {config[\"api_key\"]}'})
print(response.json())
"
```

**Secret Loading Failure:**
```bash
# Verify Pulumi ESC access
pulumi whoami
pulumi stack select sophia-ai-production

# Test secret loading
python -c "
from backend.core.auto_esc_config import get_lambda_labs_config
print('✅ Secret loading successful' if get_lambda_labs_config() else '❌ Secret loading failed')
"
```

**Instance High Costs:**
- Review instance utilization
- Consider stopping development instances during off-hours
- Monitor GPU usage patterns
- Optimize workload distribution

---

**Infrastructure Status**: ✅ OPERATIONAL
**Secret Management**: ✅ AUTOMATED
**Cost Monitoring**: ✅ ACTIVE
**Documentation**: ✅ CURRENT
