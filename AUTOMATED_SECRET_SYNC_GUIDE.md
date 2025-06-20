# Automated Secret Sync Guide

## The Simplest Way to Sync Secrets

No more manual secret entry! This guide shows you how to automatically sync all secrets from GitHub organization to everywhere they're needed.

## Quick Start (30 seconds)

```bash
# Just run this one command:
python scripts/trigger_github_sync.py
```

That's it! This command:
- ✅ Pulls all secrets from GitHub organization
- ✅ Syncs them to Pulumi ESC
- ✅ Updates all configuration files
- ✅ No manual secret entry required

## How It Works

```
GitHub Organization Secrets
         │
         ├─── Triggered by script
         │
         ▼
   GitHub Actions Workflow
         │
         ├─── Pulls all secrets
         ├─── Creates .env file
         ├─── Runs setup script
         │
         ▼
    Pulumi ESC Updated
         │
         ├─── MCP servers configured
         ├─── Production systems ready
         └─── Local development ready
```

## Prerequisites

1. **GitHub Token**: You need a GitHub token with workflow permissions
   - Set as `GITHUB_TOKEN` environment variable
   - Or it will be pulled from Pulumi ESC automatically

2. **Pulumi Access**: The Pulumi token is already in GitHub org secrets

## What Gets Synced

All these secrets are automatically synced:
- Linear API credentials
- Gong API keys
- Snowflake database credentials
- Pinecone vector database keys
- Slack bot tokens
- AI service API keys (OpenAI, Anthropic, etc.)
- And many more...

## Monitoring Progress

After running the trigger script:
1. Check the GitHub Actions tab in your repository
2. Look for the "Unified Secret Sync" workflow
3. Watch it pull and sync all secrets automatically

## Troubleshooting

### "No GitHub token found"
```bash
# Set your GitHub token
export GITHUB_TOKEN=your_github_token_here

# Then run again
python scripts/trigger_github_sync.py
```

### "Workflow failed"
- Check the GitHub Actions logs for details
- Ensure all required secrets exist in GitHub org settings
- Verify you have permissions to trigger workflows

## Manual Alternative

If you need to sync secrets manually (not recommended):
```bash
# Create .env file with secrets
cp .env.template .env
# Edit .env file...

# Run manual sync
python scripts/setup_all_secrets_once.py
```

## Summary

The automated sync is the easiest way to manage secrets:
- **One command** to sync everything
- **No manual entry** of secrets
- **Automatic updates** when secrets change
- **Works everywhere** (local, CI/CD, production)

Just run `python scripts/trigger_github_sync.py` and you're done! 🎉
