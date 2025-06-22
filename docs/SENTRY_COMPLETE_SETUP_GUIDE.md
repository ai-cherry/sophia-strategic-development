# Complete Sentry Setup Guide for Sophia AI

## Overview

This guide walks you through the complete process of setting up Sentry with Sophia AI, from initial configuration to getting your first Issue ID.

## Step 1: Get Your Sentry DSN

1. **Go to Sentry**: https://sentry.io/organizations/pay-ready/
2. **Create or Select a Project**:
   - If you don't have a project yet, click "Create Project"
   - Choose "Python" as the platform
   - Name it (e.g., "sophia-ai" or "pay-ready")
3. **Get the DSN**:
   - Go to Settings → Client Keys (DSN)
   - Copy the DSN value
   - It looks like: `https://xxxxx@o123456.ingest.sentry.io/123456`

## Step 2: Run the Setup Script

We've created a script that will:
- Configure Sentry in your environment
- Create test errors to generate Issue IDs
- Save your configuration

```bash
# Install dependencies first
pip install sentry-sdk[fastapi]

# Run the setup script
python scripts/setup_sentry_and_create_error.py
```

The script will:
1. Ask for your DSN (paste the one you copied)
2. Initialize Sentry
3. Create 4 different test errors
4. Save configuration to `.env` file

## Step 3: Find Your Issue IDs

After running the script:

1. **Go to**: https://sentry.io/organizations/pay-ready/issues/
2. **You should see** 4 new issues:
   - ZeroDivisionError
   - TypeError
   - SophiaAIError
   - IndexError
3. **Click on any issue**
4. **Look at the URL**: 
   ```
   https://sentry.io/organizations/pay-ready/issues/1234567890/
                                                    ^^^^^^^^^^
                                                    This is your Issue ID
   ```

## Step 4: Test the MCP Integration

Now that you have an Issue ID:

```bash
# Edit the test script
vim scripts/test/test_sentry_agent.py

# Update these lines:
PROJECT_SLUG = "pay-ready"  # Your project slug
ISSUE_ID = "1234567890"     # Replace with your actual Issue ID

# Run the test
python scripts/test/test_sentry_agent.py
```

## Step 5: Set Up GitHub Actions Secrets

Add these secrets to your GitHub repository:

1. Go to: Settings → Secrets and variables → Actions
2. Add these secrets:
   - `SENTRY_DSN` - The DSN you got from Sentry
   - `SENTRY_API_TOKEN` - Get from Sentry Settings → API → Auth Tokens
   - `SENTRY_ORGANIZATION_SLUG` - `pay-ready`
   - `SENTRY_PROJECT_SLUG` - `pay-ready`

### Getting the API Token:
1. Go to: https://sentry.io/settings/account/api/auth-tokens/
2. Click "Create New Token"
3. Give it a name (e.g., "Sophia AI Integration")
4. Select scopes:
   - `project:read`
   - `project:write`
   - `issue:read`
   - `issue:write`
   - `alert:read`
   - `alert:write`
5. Copy the token and save it as `SENTRY_API_TOKEN`

## Step 6: Deploy the Sentry MCP Server

```bash
# Deploy the Sentry MCP server
docker-compose -f docker-compose.sentry.yml up -d

# Verify it's running
docker ps | grep sentry-mcp

# Check logs
docker logs sentry-mcp
```

## Step 7: Configure Webhooks (Optional)

For real-time error notifications:

1. **In Sentry**, go to Settings → Integrations → Webhooks
2. **Add webhook URL**:
   ```
   https://your-sophia-domain.com/webhooks/sentry
   ```
3. **Select events** to send:
   - Issue Created
   - Issue Resolved
   - Issue Assigned

## Usage Examples

Once everything is set up, you can use natural language commands:

### Query Errors
- "Show me recent Sentry errors"
- "List unresolved errors in the pay-ready project"
- "Get details about Sentry issue 1234567890"

### Manage Issues
- "Resolve Sentry issue 1234567890"
- "Create a Sentry alert for high error rates"
- "Show me the events for issue 1234567890"

### Get Insights
- "What's the most common error in the last 24 hours?"
- "Show me errors related to database connections"
- "List errors affecting user authentication"

## Troubleshooting

### No Issues Appearing in Sentry?
- Check your DSN is correct
- Verify your project exists and is active
- Check network connectivity
- Look at script output for errors

### Can't Find Issue ID?
- Make sure you're looking at the correct project
- The Issue ID is in the URL when viewing an issue
- It's a long number like `1234567890`

### API Token Issues?
- Ensure the token has the correct permissions
- Check it hasn't expired
- Verify it's for the correct organization

### MCP Server Not Working?
```bash
# Check container status
docker ps -a | grep sentry-mcp

# View logs
docker logs sentry-mcp --tail 50

# Test connectivity
curl http://localhost:9006/health
```

## Quick Reference

### Environment Variables
```bash
SENTRY_DSN=https://xxxxx@o123456.ingest.sentry.io/123456
SENTRY_API_TOKEN=your-api-token
SENTRY_ORGANIZATION_SLUG=pay-ready
SENTRY_PROJECT_SLUG=pay-ready
```

### Key Files
- Setup Script: `scripts/setup_sentry_and_create_error.py`
- Test Script: `scripts/test/test_sentry_agent.py`
- MCP Server: `mcp-servers/sentry/sentry_mcp_server.py`
- Docker Config: `docker-compose.sentry.yml`

### MCP Tools Available
1. `get_sentry_issue` - Fetch issue details
2. `list_sentry_issues` - List project issues
3. `get_issue_events` - Get issue events
4. `create_sentry_alert` - Create alerts
5. `resolve_issue` - Resolve issues

## Next Steps

1. ✅ Run the setup script to create test errors
2. ✅ Get an Issue ID from Sentry dashboard
3. ✅ Test the integration with the test script
4. ✅ Deploy the MCP server
5. ✅ Start using natural language to manage errors!

---

**Need more help?** The setup script (`scripts/setup_sentry_and_create_error.py`) will guide you through the process interactively!
