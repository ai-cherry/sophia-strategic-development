# Unified Secret Management Strategy for Sophia AI

Generated: 2025-07-07T00:02:04.369825

## Overview

This document defines the SINGLE, AUTHORITATIVE secret management strategy for Sophia AI.

## Secret Flow

```
GitHub Organization Secrets (ai-cherry)
           ↓
    GitHub Actions Workflow
           ↓
    sync_from_gh_to_pulumi.py
           ↓
    Pulumi ESC Environment
           ↓
    auto_esc_config.py
           ↓
    Application Code
```

## Components

### 1. GitHub Organization Secrets

Location: https://github.com/organizations/ai-cherry/settings/secrets/actions

All secrets are stored at the organization level with these exact names:

```
ANTHROPIC_API_KEY
ASANA_ACCESS_TOKEN
CODACY_API_TOKEN
DOCKER_HUB_ACCESS_TOKEN
DOCKER_TOKEN
ESTUARY_API_TOKEN
FIGMA_PAT
FIGMA_PROJECT_ID
GITHUB_APP_ID
GITHUB_APP_PRIVATE_KEY
GITHUB_TOKEN
GONG_ACCESS_KEY
GONG_ACCESS_KEY_SECRET
GRAFANA_PASSWORD
HUBSPOT_API_KEY
LAMBDA_API_KEY
LAMBDA_LABS_API_KEY
LAMBDA_LABS_SSH_KEY
LINEAR_API_KEY
MEM0_API_KEY
NOTION_API_TOKEN
OPENAI_API_KEY
OPENROUTER_API_KEY
PINECONE_API_KEY
PINECONE_ENVIRONMENT
PORTKEY_API_KEY
POSTGRES_PASSWORD
PULUMI_ACCESS_TOKEN
SLACK_APP_TOKEN
SLACK_BOT_TOKEN
SLACK_SIGNING_SECRET
SLACK_WEBHOOK_URL
SNOWFLAKE_ACCOUNT
SNOWFLAKE_DATABASE
SNOWFLAKE_PASSWORD
SNOWFLAKE_ROLE
SNOWFLAKE_USERNAME
SNOWFLAKE_WAREHOUSE
VERCEL_ACCESS_TOKEN
WEAVIATE_API_KEY
WEAVIATE_URL
```

### 2. Sync Workflow

File: `.github/workflows/sync_secrets.yml`

- Trigger: Manual dispatch or push to main
- Script: `scripts/ci/sync_from_gh_to_pulumi.py`
- All secrets must be explicitly passed as environment variables

### 3. Pulumi ESC

Environment: `scoobyjava-org/default/sophia-ai-production`

Structure:
```yaml
values:
  sophia:
    secret_name: secret_value
```

### 4. Application Access

File: `backend/core/auto_esc_config.py`

Usage:
```python
from backend.core.auto_esc_config import get_config_value

# Get a secret
api_key = get_config_value("openai_api_key")
```

## Key Mappings

Some secrets have different names between GitHub and the application:

| GitHub Secret | Pulumi/App Key |
|--------------|----------------|
| VERCEL_ACCESS_TOKEN | vercel_api_token |
| GITHUB_TOKEN | github_token |
| ASANA_API_TOKEN | asana_access_token |
| NOTION_API_KEY | notion_api_token |

## Testing

1. Run sync workflow: `gh workflow run sync_secrets.yml`
2. Check ESC: `esc env get default/sophia-ai-production`
3. Test in app: `python scripts/test_secret_access.py`

## Troubleshooting

If secrets aren't working:

1. Check GitHub org has the secret
2. Check workflow includes the secret
3. Check sync script maps the secret
4. Check auto_esc_config has the mapping
5. Check no hardcoded values override

## DO NOT

- Create .env files
- Hardcode secrets
- Use os.getenv() directly
- Create duplicate sync scripts
- Use different naming conventions

## Maintenance

Weekly: Verify all secrets are synced
Monthly: Audit for unused secrets
Quarterly: Rotate sensitive credentials
