# COMPLETE SECRET MANAGEMENT SOLUTION FOR SOPHIA AI

## THE DEFINITIVE GUIDE - NO MORE CONFUSION

### 🔴 CRITICAL: Docker Hub Credentials

The Docker Hub credentials have been the source of daily pain. Here's the PERMANENT fix:

#### GitHub Organization Secrets (SOURCE OF TRUTH)
```
DOCKER_USERNAME = scoobyjava15
DOCKER_TOKEN = <your-docker-hub-personal-access-token>
```

**NOT** `DOCKER_HUB_USERNAME`, **NOT** `DOCKER_HUB_ACCESS_TOKEN`, **NOT** `DOCKER_PASSWORD`

#### Pulumi ESC Mapping
```yaml
docker_username: scoobyjava15
docker_token: <encrypted-token>
```

#### Application Access (backend/core/auto_esc_config.py)
```python
# Use the dedicated function
from backend.core.auto_esc_config import get_docker_hub_config
config = get_docker_hub_config()
# Returns: {"username": "scoobyjava15", "access_token": "...", "registry": "docker.io"}
```

### 📋 Complete Secret Mapping

| GitHub Secret | Pulumi ESC Key | Description |
|---------------|----------------|-------------|
| `DOCKER_USERNAME` | `docker_username` | Docker Hub username |
| `DOCKER_TOKEN` | `docker_token` | Docker Hub access token |
| `SNOWFLAKE_ACCOUNT` | `snowflake_account` | Snowflake account |
| `SNOWFLAKE_USER` | `snowflake_user` | Snowflake username |
| `SNOWFLAKE_PASSWORD` | `snowflake_password` | Snowflake PAT |
| `SNOWFLAKE_WAREHOUSE` | `snowflake_warehouse` | Snowflake warehouse |
| `SNOWFLAKE_DATABASE` | `snowflake_database` | Snowflake database |
| `SNOWFLAKE_SCHEMA` | `snowflake_schema` | Snowflake schema |
| `SNOWFLAKE_ROLE` | `snowflake_role` | Snowflake role |
| `LAMBDA_API_KEY` | `lambda_api_key` | Lambda Labs API key |
| `LAMBDA_SSH_PRIVATE_KEY` | `lambda_ssh_private_key` | Lambda SSH key |
| `OPENAI_API_KEY` | `openai_api_key` | OpenAI API key |
| `ANTHROPIC_API_KEY` | `anthropic_api_key` | Anthropic API key |
| `PINECONE_API_KEY` | `pinecone_api_key` | Pinecone API key |
| `GH_API_TOKEN` | `github_token` | GitHub API token |
| `LINEAR_API_KEY` | `linear_api_key` | Linear API key |
| `NOTION_API_KEY` | `notion_api_key` | Notion API key |
| `FIGMA_PAT` | `figma_pat` | Figma PAT |
| `VERCEL_TOKEN` | `vercel_token` | Vercel token |
| `GONG_ACCESS_KEY` | `gong_access_key` | Gong API key |
| `GONG_ACCESS_KEY_SECRET` | `gong_access_key_secret` | Gong secret |
| `HUBSPOT_API_KEY` | `hubspot_api_key` | HubSpot API key |
| `SLACK_WEBHOOK` | `slack_webhook_url` | Slack webhook |
| `SLACK_BOT_TOKEN` | `slack_bot_token` | Slack bot token |
| `ASANA_API_TOKEN` | `asana_api_token` | Asana token |

### 🔄 The Complete Flow

```
1. GitHub Organization Secrets (ai-cherry)
   ↓
2. GitHub Actions Workflow (sync_secrets_comprehensive.yml)
   ↓
3. Pulumi ESC (scoobyjava-org/default/sophia-ai-production)
   ↓
4. Sophia AI Backend (auto_esc_config.py)
   ↓
5. Your Application
```

### 🛠️ Tools and Scripts

#### 1. Comprehensive Secret Mapping Script
```bash
python3 scripts/comprehensive_secret_mapping.py
```
- Maps ALL secrets from GitHub to Pulumi ESC
- Validates critical secrets
- Generates mapping report

#### 2. Fix GitHub Workflows Script
```bash
python3 scripts/fix_github_workflows_secrets.py
```
- Fixes all workflows to use consistent secret names
- Already run and committed

#### 3. Validate All Secrets Script
```bash
python3 scripts/validate_all_secrets.py
```
- Shows what's missing
- Validates the complete path
- Generates fix commands

#### 4. Test Docker Config
```bash
python3 test_docker_config.py
```
- Tests if Docker credentials are working
- Shows the complete credential path

### 🚨 Common Problems and Solutions

#### Problem: "invalid access token" from Docker
**Solution**: The token name is `DOCKER_TOKEN`, not `DOCKER_HUB_ACCESS_TOKEN`

#### Problem: Secrets not syncing to Pulumi ESC
**Solution**: Run the comprehensive sync workflow:
```bash
gh workflow run sync_secrets_comprehensive.yml
```

#### Problem: Application can't find secrets
**Solution**: Check these in order:
1. Is `PULUMI_ORG=scoobyjava-org` set?
2. Is `ENVIRONMENT=prod` set?
3. Run `pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets`

### 📝 GitHub Actions Configuration

All workflows now use consistent secret names:
- `${{ secrets.DOCKER_USERNAME }}`
- `${{ secrets.DOCKER_TOKEN }}`

### 🔧 Local Development

For local testing, set these environment variables:
```bash
export PULUMI_ACCESS_TOKEN='pul-...'
export PULUMI_ORG='scoobyjava-org'
export ENVIRONMENT='prod'

# If Pulumi ESC isn't working, set these directly:
export DOCKER_USERNAME='scoobyjava15'
export DOCKER_TOKEN='your-docker-hub-token'
```

### ✅ Verification Checklist

1. **GitHub Secrets**: Check at https://github.com/organizations/ai-cherry/settings/secrets/actions
2. **Pulumi ESC**: `pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets | grep docker`
3. **Application**: `python3 test_docker_config.py`
4. **Deployment**: GitHub Actions should now work

### 🎯 The Golden Rules

1. **NEVER** create new Docker secret variations
2. **ALWAYS** use `DOCKER_USERNAME` and `DOCKER_TOKEN`
3. **ALWAYS** check this document when confused
4. **NEVER** hardcode secrets
5. **ALWAYS** use the automated sync

### 📊 Status Dashboard

Run this to see current status:
```bash
python3 scripts/validate_all_secrets.py
```

This will show:
- ✅ What's working
- ❌ What's missing
- 🔧 How to fix it

## THIS IS THE PERMANENT SOLUTION

No more daily battles. No more confusion. This is the way. 