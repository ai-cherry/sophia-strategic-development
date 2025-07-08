# Unified Secret Management Strategy for Sophia AI

## Overview

This document outlines the **UNIFIED** secret management strategy for Sophia AI, implementing a clean GitHub → Pulumi ESC → Application flow with zero manual intervention.

## Key Achievements

### 1. **Legacy Cleanup**
- ✅ Removed ALL Vultr references (deleted 4 files)
- ✅ Removed ALL Terraform references
- ✅ Standardized on single `VERCEL_ACCESS_TOKEN` name
- ✅ Updated Lambda Labs secrets to match ACTUAL GitHub organization secret names

### 2. **Unified Secret Flow**
```
GitHub Organization Secrets
         ↓
GitHub Actions Workflow (sync_secrets.yml)
         ↓
Pulumi ESC Environment (default/sophia-ai-production)
         ↓
Docker Swarm Secrets / Application Environment
```

### 3. **Critical Files**

#### **GitHub Actions Workflow**: `.github/workflows/sync_secrets.yml`
- Runs on push to main or manual trigger
- Injects ALL organization secrets as environment variables
- Executes `scripts/ci/sync_from_gh_to_pulumi.py`

#### **Sync Script**: `scripts/ci/sync_from_gh_to_pulumi.py`
- Maps GitHub secrets to Pulumi ESC structure
- Uses EXACT GitHub secret names (e.g., `LAMBDA_LABS_API_KEY` not `LAMBDA_API_KEY`)
- Creates structured JSON for Pulumi ESC

#### **Backend Integration**: `backend/core/auto_esc_config.py`
- Automatically loads secrets from Pulumi ESC
- Provides fallback to environment variables
- Single source of truth for application secrets

#### **Docker Secret Creation**: `create_docker_secrets_direct.sh`
- Extracts secrets from Pulumi ESC using `esc env open`
- Creates Docker Swarm secrets for container deployment
- Maps ESC keys to Docker secret names

## Lambda Labs Secrets (CORRECT Names)

```yaml
LAMBDA_LABS_API_KEY          # NOT Lambda_API_KEY
LAMBDA_LABS_SSH_PRIVATE_KEY  # NOT LAMBDA_LABS_SSH_KEY
LAMBDA_LABS_SSH_KEY_NAME
LAMBDA_LABS_REGION
LAMBDA_LABS_INSTANCE_TYPE
LAMBDA_LABS_CLUSTER_SIZE
LAMBDA_LABS_MAX_CLUSTER_SIZE
LAMBDA_LABS_SHARED_FS_ID
LAMBDA_LABS_SHARED_FS_MOUNT
LAMBDA_LABS_ASG_NAME
```

## Standardized Secrets

### AI Services
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `MEM0_API_KEY`
- `OPENROUTER_API_KEY`
- `PORTKEY_API_KEY`

### Data Infrastructure
- `SNOWFLAKE_ACCOUNT/USERNAME/PASSWORD/WAREHOUSE/DATABASE/ROLE`
- `POSTGRES_PASSWORD`
- `PINECONE_API_KEY/ENVIRONMENT`
- `WEAVIATE_API_KEY/URL`
- `ESTUARY_API_TOKEN`

### Business Intelligence
- `GONG_ACCESS_KEY/GONG_ACCESS_KEY_SECRET`
- `HUBSPOT_API_KEY`
- `LINEAR_API_KEY`
- `ASANA_ACCESS_TOKEN`
- `NOTION_API_TOKEN`

### Communication
- `SLACK_BOT_TOKEN/APP_TOKEN/WEBHOOK_URL/SIGNING_SECRET`

### Cloud Infrastructure
- `VERCEL_ACCESS_TOKEN` (NOT vercel_v0dev_api_key)
- `PULUMI_ACCESS_TOKEN`
- `DOCKER_TOKEN/DOCKER_HUB_ACCESS_TOKEN`

### Development Tools
- `GITHUB_TOKEN/APP_ID/APP_PRIVATE_KEY`
- `CODACY_API_TOKEN`

### Design
- `FIGMA_PAT/PROJECT_ID`

### Monitoring
- `GRAFANA_PASSWORD`

## Testing & Validation

### 1. **Test Secret Access**
```bash
python scripts/test_secret_access.py
```

### 2. **Run Unified Audit**
```bash
python scripts/unified_secret_management_audit.py
```

### 3. **Create Docker Secrets**
```bash
./create_docker_secrets_direct.sh
```

### 4. **Monitor Swarm Health**
```bash
./monitor_swarm.sh
```

## Key Principles

1. **Single Source of Truth**: GitHub Organization Secrets
2. **Automatic Sync**: GitHub Actions → Pulumi ESC
3. **Zero Manual Management**: No .env files, no manual updates
4. **Standardized Names**: Consistent naming across all systems
5. **Secure by Default**: Encrypted storage at every level

## Common Issues & Solutions

### Issue: Secrets not syncing
**Solution**: Check GitHub Actions workflow logs, ensure all secrets exist in GitHub org

### Issue: Docker secrets missing
**Solution**: Run `create_docker_secrets_direct.sh` to recreate from ESC

### Issue: Application can't find secrets
**Solution**: Ensure `PULUMI_ORG=scoobyjava-org` is set, check `auto_esc_config.py`

## Next Steps

1. Deploy the stack with proper secrets:
```bash
./deploy_swarm.sh
```

2. Monitor deployment:
```bash
./monitor_swarm.sh
```

3. Troubleshoot if needed:
```bash
./troubleshoot_swarm_network.sh
```

## Conclusion

The unified secret management system is now:
- ✅ Clean of all legacy references
- ✅ Using correct GitHub secret names
- ✅ Properly synced through Pulumi ESC
- ✅ Ready for production deployment

No more manual secret management. Ever.
