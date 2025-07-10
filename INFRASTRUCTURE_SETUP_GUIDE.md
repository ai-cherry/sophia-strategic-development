# Sophia AI Infrastructure Setup Guide

## Overview

This guide documents the comprehensive infrastructure setup for Sophia AI, including all services, secrets management, and deployment configurations.

## 🔐 Secrets Management

### Local Environment File

We use a `local.env` file (never committed to Git) that contains all sensitive credentials:

```bash
# Create local.env file
cp local.env.example local.env
# Edit with your credentials
```

### GitHub Organization Secrets

All secrets are stored at the organization level in GitHub:
- Organization: `ai-cherry`
- URL: https://github.com/organizations/ai-cherry/settings/secrets/actions

Run the update script:
```bash
python scripts/update_github_secrets.py
```

### Pulumi ESC Integration

Pulumi Environment Secrets Configuration provides centralized secret management:
- Organization: `scoobyjava-org`
- Environment: `default/sophia-ai-production`

## 🏗️ Infrastructure Components

### 1. Snowflake Configuration

**Account Details:**
- Primary Account: `UHDECNO-CVB64222`
- Region: AWS West Oregon
- User: `SCOOBYJAVA15`

**Infrastructure Setup:**
```bash
python scripts/setup_snowflake_infrastructure.py
```

This creates:
- Warehouses: `SOPHIA_AI_COMPUTE_WH`, `SOPHIA_AI_ETL_WH`, `SOPHIA_AI_ANALYTICS_WH`
- Databases: `AI_MEMORY`, `SOPHIA_AI_CORE`, `SOPHIA_AI_STAGING`, `SOPHIA_AI_ANALYTICS`
- Schemas: `VECTORS`, `MEMORY`, `KNOWLEDGE`, `CORTEX`, `MONITORING`
- Tables: Vector storage, memory consolidation, business data
- Roles: Admin, Developer, Analyst, Service

### 2. Lambda Labs K3s Cluster

**Configuration:**
- API Endpoint: `https://cloud.lambda.ai/api/v1/instances`
- Cluster: K3s on Lambda Labs instances
- GPU Support: GH200 instances

**Management:**
- Check instances via API
- Deploy via GitHub Actions
- Access via SSH keys stored in secrets

### 3. GitHub Actions Workflows

**Key Workflows:**
- `sync_secrets.yml` - Syncs GitHub secrets to Pulumi ESC
- `deploy-sophia-unified.yml` - Main deployment workflow
- `sophia-prod.yml` - Production deployment

**Trigger:**
```bash
gh workflow run sync_secrets.yml
```

### 4. Vercel Deployment

**Frontend Hosting:**
- Project: Sophia AI Dashboard
- Domain: Custom domains via Namecheap
- Environment Variables: Synced from GitHub secrets

### 5. Data Pipeline (Estuary Flow)

**Configuration:**
- Real-time data synchronization
- Connects to Snowflake, HubSpot, Gong
- Managed via API tokens

### 6. AI Services Configuration

**OpenAI/Anthropic:**
- Routing via Portkey for cost optimization
- Fallback configuration with OpenRouter
- Model selection based on task complexity

**Vector Databases:**
- Pinecone for legacy vectors (being migrated)
- Weaviate for specific use cases
- Snowflake Cortex as primary vector store

### 7. Business Intelligence

**Gong Integration:**
- API Base URL: `https://us-70092.api.gong.io`
- Call transcription and analysis
- Automated insights extraction

**HubSpot:**
- CRM synchronization
- Deal and contact management
- Automated workflows

### 8. Communication

**Slack:**
- Bot and app tokens configured
- Real-time notifications
- Team collaboration features

### 9. Monitoring

**Sentry:**
- Error tracking and performance monitoring
- Custom alerts for critical issues

**Arize:**
- AI model performance monitoring
- Drift detection and analytics

## 🚀 Quick Start

### Prerequisites

1. Install required tools:
```bash
# Python dependencies
pip install PyNaCl requests snowflake-connector-python

# CLI tools
brew install gh  # GitHub CLI
curl -fsSL https://get.pulumi.com | sh  # Pulumi
```

2. Authenticate:
```bash
# GitHub
gh auth login

# Pulumi
pulumi login
```

### Run Complete Setup

```bash
# Run all infrastructure setup steps
python scripts/setup_infrastructure_comprehensive.py

# Or run individual steps
python scripts/setup_infrastructure_comprehensive.py snowflake
python scripts/setup_infrastructure_comprehensive.py lambda_labs
python scripts/setup_infrastructure_comprehensive.py github_actions
```

## 📋 Infrastructure Checklist

- [ ] Create `local.env` file with all credentials
- [ ] Update `.gitignore` to exclude `local.env`
- [ ] Run GitHub secrets update script
- [ ] Configure Pulumi ESC
- [ ] Set up Snowflake infrastructure
- [ ] Verify Lambda Labs instances
- [ ] Configure GitHub Actions workflows
- [ ] Set up Vercel project
- [ ] Configure Estuary Flow pipelines
- [ ] Set up AI routing (Portkey/OpenRouter)
- [ ] Configure monitoring (Sentry/Arize)
- [ ] Test all integrations

## 🔍 Verification

### Check Infrastructure Status

```bash
# Generate infrastructure report
python scripts/setup_infrastructure_comprehensive.py report

# View the report
cat infrastructure_report.json
```

### Test Connections

```bash
# Test Snowflake
python -c "import snowflake.connector; print('Snowflake OK')"

# Test Lambda Labs API
curl -H "Authorization: Bearer $LAMBDA_API_KEY" https://cloud.lambda.ai/api/v1/instances

# Test GitHub Actions
gh workflow list
```

## 🛠️ Troubleshooting

### Common Issues

1. **Snowflake Connection Failed**
   - Verify account name format (should include organization)
   - Check if using correct password or PAT token
   - Ensure IP is whitelisted

2. **GitHub Secrets Not Updating**
   - Verify PAT has necessary permissions
   - Check organization membership
   - Ensure using correct API endpoints

3. **Pulumi ESC Not Working**
   - Run `pulumi login` first
   - Set `PULUMI_ORG` environment variable
   - Check access token validity

## 📚 Additional Resources

- [Snowflake Documentation](https://docs.snowflake.com/)
- [Lambda Labs API Docs](https://docs.lambda.ai/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Pulumi ESC Docs](https://www.pulumi.com/docs/esc/)

## 🔒 Security Best Practices

1. **Never commit secrets** - Always use environment variables or secret management
2. **Rotate credentials regularly** - Set up automated rotation where possible
3. **Use least privilege** - Grant minimum necessary permissions
4. **Audit access** - Regularly review who has access to what
5. **Enable MFA** - On all critical services

## 🎯 Next Steps

After infrastructure setup:
1. Deploy MCP servers to K3s cluster
2. Configure data pipelines
3. Set up monitoring dashboards
4. Test end-to-end workflows
5. Document operational procedures 