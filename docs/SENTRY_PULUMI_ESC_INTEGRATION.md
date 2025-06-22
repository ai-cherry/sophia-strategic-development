# Sentry Integration with Pulumi ESC and GitHub Actions

## Overview

This document describes how Sentry is integrated with Sophia AI using:
- **GitHub Organization Secrets** (ai-cherry org)
- **Pulumi ESC** (Environment Secrets Configuration)
- **Automatic Secret Synchronization**

## Architecture

```
GitHub Organization Secrets (ai-cherry)
           ↓
    GitHub Actions Workflow
           ↓
    Pulumi ESC (scoobyjava-org)
           ↓
    Sentry MCP Server & Backend
```

## Required GitHub Organization Secrets

Add these secrets at the organization level in GitHub (ai-cherry):

1. **SENTRY_DSN** - Your Sentry Data Source Name
   - Get from: Sentry → Settings → Client Keys (DSN)
   - Format: `https://xxxxx@o123456.ingest.sentry.io/123456`

2. **SENTRY_API_TOKEN** - Sentry API authentication token
   - Get from: https://sentry.io/settings/account/api/auth-tokens/
   - Required scopes: `project:read`, `project:write`, `issue:read`, `issue:write`

3. **SENTRY_ORGANIZATION_SLUG** - Your Sentry organization identifier
   - Value: `pay-ready`

4. **SENTRY_PROJECT_SLUG** - Your Sentry project identifier
   - Value: `pay-ready`

5. **SENTRY_CLIENT_SECRET** - Optional webhook verification secret
   - For webhook signature verification

## Automatic Synchronization

### GitHub Actions Workflow

The workflow `.github/workflows/sync-sentry-secrets.yml`:
- Runs every 6 hours automatically
- Can be triggered manually
- Syncs all Sentry secrets from GitHub to Pulumi ESC
- Verifies configuration after sync
- Triggers Sentry MCP deployment on success

### Manual Sync

To manually sync secrets:
1. Go to Actions tab in GitHub
2. Select "Sync Sentry Secrets to Pulumi ESC"
3. Click "Run workflow"

## Pulumi ESC Configuration

### Environment Path
```
scoobyjava-org/default/sophia-ai-production
```

### Stored Secrets
- `SENTRY_DSN` (encrypted)
- `SENTRY_API_TOKEN` (encrypted)
- `SENTRY_ORGANIZATION_SLUG`
- `SENTRY_PROJECT_SLUG`
- `SENTRY_CLIENT_SECRET` (encrypted)

### Access in Code

#### Python Backend
```python
from backend.core.auto_esc_config import config

# Automatically loaded from Pulumi ESC
sentry_dsn = config.sentry_dsn
sentry_api_token = config.sentry_api_token
```

#### MCP Server
The Sentry MCP server automatically retrieves secrets using Pulumi CLI:
```python
def get_pulumi_esc_value(key: str, default: str = None) -> str:
    """Get value from Pulumi ESC using CLI."""
    result = subprocess.run(
        ["pulumi", "env", "get", "scoobyjava-org/default/sophia-ai-production", key],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()
```

## Docker Deployment

### Environment Variables
The Docker Compose configuration includes:
```yaml
environment:
  - PULUMI_ACCESS_TOKEN=${PULUMI_ACCESS_TOKEN}
  - PULUMI_ORG=scoobyjava-org
  - PULUMI_ENVIRONMENT=sophia-ai-production
```

### Automatic Configuration
1. Container starts with Pulumi CLI installed
2. Retrieves secrets from Pulumi ESC
3. Falls back to environment variables if needed

## Local Development

### Setup
```bash
# Set Pulumi organization
export PULUMI_ORG=scoobyjava-org

# Login to Pulumi
pulumi login

# Secrets will be automatically loaded
```

### Testing
```bash
# Verify Sentry configuration
pulumi env get scoobyjava-org/default/sophia-ai-production | grep -i sentry

# Test secret retrieval
python -c "from backend.core.auto_esc_config import config; print('Sentry configured' if hasattr(config, 'sentry_dsn') else 'No Sentry config')"
```

## Security Benefits

1. **No Hardcoded Secrets** - All secrets managed centrally
2. **Automatic Rotation** - Update in GitHub → Auto-sync to Pulumi
3. **Audit Trail** - All secret access logged
4. **Environment Isolation** - Different secrets per environment
5. **Zero Manual Management** - Fully automated workflow

## Troubleshooting

### Secret Not Available?
1. Check GitHub Actions workflow ran successfully
2. Verify secret exists in GitHub organization
3. Check Pulumi ESC environment:
   ```bash
   pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets
   ```

### MCP Server Can't Access Secrets?
1. Verify `PULUMI_ACCESS_TOKEN` is set
2. Check Pulumi CLI is installed in container
3. Review container logs:
   ```bash
   docker logs sentry-mcp
   ```

### Sync Workflow Failing?
1. Check `PULUMI_ACCESS_TOKEN` in GitHub secrets
2. Verify organization name is correct
3. Review workflow logs in GitHub Actions

## Best Practices

1. **Never commit secrets** - Use GitHub organization secrets
2. **Regular rotation** - Update API tokens periodically
3. **Monitor sync status** - Check workflow runs
4. **Use secret flag** - Mark sensitive values with `--secret`
5. **Verify after changes** - Always test after updating secrets

## Integration Points

### 1. Backend Initialization
```python
# backend/core/sentry_setup.py
from backend.core.auto_esc_config import config

sentry_dsn = config.sentry_dsn
sentry_sdk.init(dsn=sentry_dsn)
```

### 2. MCP Server
```python
# mcp-servers/sentry/sentry_mcp_server.py
self.api_token = get_pulumi_esc_value("SENTRY_API_TOKEN")
```

### 3. Docker Compose
```yaml
# docker-compose.sentry.yml
environment:
  - PULUMI_ACCESS_TOKEN=${PULUMI_ACCESS_TOKEN}
```

### 4. GitHub Actions
```yaml
# .github/workflows/sync-sentry-secrets.yml
pulumi env set scoobyjava-org/default/sophia-ai-production SENTRY_API_TOKEN "$SENTRY_API_TOKEN" --secret
```

## Summary

The Sentry integration leverages:
- **GitHub Organization Secrets** for centralized secret management
- **Pulumi ESC** for secure secret distribution
- **GitHub Actions** for automatic synchronization
- **Docker** with Pulumi CLI for runtime configuration

This provides a secure, automated, and maintainable approach to managing Sentry credentials across the Sophia AI platform.
