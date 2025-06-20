# Unified Secret Management Guide

## The ONE System That Works Everywhere

This is the definitive guide for managing secrets in Sophia AI. No more one-off scripts, no more confusion.

## Architecture

```
GitHub Organization Secrets (Source of Truth)
         │
         ├─── GitHub Actions ────────┐
         │                           │
         │                           ▼
         │                    Pulumi ESC
         │                    (Central Store)
         │                           │
         ▼                           ▼
   Local Development          Production Systems
   (.env file)               (MCP, Lambda Labs, etc.)
```

## The Master Script: `scripts/setup_all_secrets_once.py`

This ONE script handles ALL secret management:
- Collects secrets from environment and .env files
- Syncs everything to Pulumi ESC
- Updates MCP configuration
- Creates .env.template for new developers
- Cleans up sensitive data after use

## How It Works

### 1. For Local Development

**Option A: Sync from GitHub Organization (Recommended)**
```bash
# Trigger sync from GitHub org secrets (no manual entry needed!)
python scripts/trigger_github_sync.py

# This pulls all secrets from GitHub org and syncs to Pulumi ESC
```

**Option B: Manual Setup (if needed)**
```bash
# Step 1: Create your .env file with all secrets
cp .env.template .env
# Edit .env and add your actual secret values

# Step 2: Run the unified setup (using the Pulumi token temporarily)
python scripts/setup_all_secrets_once.py

# That's it! All secrets are now in Pulumi ESC
```

### 2. For GitHub Actions (Automated)

The workflow `.github/workflows/unified-secret-sync.yml`:
- Runs automatically when secret scripts are updated
- Can be triggered manually from GitHub Actions tab
- Pulls ALL secrets from GitHub organization
- Syncs them to Pulumi ESC
- Updates configuration files
- Commits changes back to the repo

### 3. For Production Systems

All production systems read from Pulumi ESC:
- MCP servers get secrets via environment variables
- Lambda Labs deployments use Pulumi ESC
- Docker containers inherit from Pulumi ESC

## Secret Naming Convention

All secrets follow a consistent pattern:

```
SERVICE_CREDENTIAL_TYPE

Examples:
- LINEAR_API_KEY
- GONG_CLIENT_ID
- SNOWFLAKE_PASSWORD
- PINECONE_API_KEY
```

## Adding a New Secret

1. **Add to GitHub Organization Secrets:**
   - Go to GitHub org settings
   - Add the secret with the correct name

2. **Update the unified script:**
   - Add the secret name to `env_patterns` in `setup_all_secrets_once.py`

3. **Update GitHub Actions workflow:**
   - Add the secret to the env file creation in `unified-secret-sync.yml`

4. **Run the sync:**
   - Either trigger GitHub Actions manually
   - Or run locally with the script

## Security Best Practices

1. **Never commit secrets to the repo**
   - .env is in .gitignore
   - The Pulumi token in the script is temporary

2. **Use environment variable references in configs**
   - MCP config uses `${SECRET_NAME}` format
   - Never hardcode actual values

3. **Rotate secrets regularly**
   - Update in GitHub org secrets
   - Run the sync workflow
   - Everything updates automatically

## Troubleshooting

### "Secret not found in Pulumi ESC"
- Check if the secret exists in GitHub org secrets
- Run the unified sync workflow
- Verify the secret name matches the pattern

### "MCP server can't find secret"
- Check mcp_config.json has the correct env variable reference
- Ensure the secret was synced to Pulumi ESC
- Restart the MCP server

### "Local development secret missing"
- Check your .env file has the secret
- Run `python scripts/setup_all_secrets_once.py` locally
- Verify no typos in the secret name

## The Complete Secret List

All secrets managed by this system:

### Core Services
- LINEAR_API_KEY
- GONG_API_KEY, GONG_CLIENT_ID, GONG_CLIENT_SECRET
- SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD
- PINECONE_API_KEY, PINECONE_ENVIRONMENT
- VERCEL_ACCESS_TOKEN, VERCEL_PROJECT_ID

### Communication
- SLACK_BOT_TOKEN, SLACK_APP_TOKEN
- INTERCOM_ACCESS_TOKEN

### AI Services
- ANTHROPIC_API_KEY
- OPENAI_API_KEY
- OPENROUTER_API_KEY
- LLAMAINDEX_API_KEY

### Infrastructure
- GITHUB_TOKEN, GITHUB_PAT
- PULUMI_ACCESS_TOKEN
- LAMBDA_LABS_API_KEY
- ESTUARY_API_KEY
- AIRBYTE_API_KEY

### Other Integrations
- HUBSPOT_API_KEY
- RETOOL_API_KEY
- AGNO_API_KEY

## Quick Commands

```bash
# Trigger sync from GitHub org secrets (easiest!)
python scripts/trigger_github_sync.py

# Run unified secret sync locally (manual)
python scripts/setup_all_secrets_once.py

# Trigger GitHub Actions sync via CLI
gh workflow run unified-secret-sync.yml

# Check Pulumi ESC secrets
pulumi env open ai-cherry/sophia-production

# Test a specific secret
pulumi env get ai-cherry/sophia-production linear.linear_api_key
```

## Summary

This is THE secret management system for Sophia AI:
- ONE script to rule them all
- ONE workflow for automation
- ONE source of truth (GitHub org secrets)
- ONE central store (Pulumi ESC)
- ZERO confusion

No more one-off scripts. No more scattered secrets. Just one unified system that works everywhere.
