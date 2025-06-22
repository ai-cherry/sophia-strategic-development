# Sentry MCP Integration Guide for Sophia AI

## Overview

This guide helps you set up and use the Sentry MCP (Model Context Protocol) integration with Sophia AI for error tracking, monitoring, and automated debugging.

## What You Need

### 1. Sentry Issue ID
A Sentry Issue ID is a unique identifier for each error/exception tracked in Sentry. 

#### How to Find a Sentry Issue ID:

**Method 1: From Sentry Web UI**
1. Go to: `https://sentry.io/organizations/pay-ready/issues/`
2. Click on any issue in your project
3. Look at the URL - it will be something like:
   ```
   https://sentry.io/organizations/pay-ready/issues/1234567890/
   ```
   The number `1234567890` is your Issue ID

**Method 2: From Issue Details Page**
- On the issue page, the Issue ID is often shown in the header or metadata section
- Look for a field labeled "ID" or similar

**Method 3: Using Sentry API**
```bash
curl -H "Authorization: Bearer YOUR_SENTRY_API_TOKEN" \
  "https://sentry.io/api/0/projects/pay-ready/YOUR_PROJECT_SLUG/issues/"
```
This returns a JSON array where each issue has an `"id"` field.

### 2. Project Slug
You've already saved this as `pay-ready` in GitHub Actions secrets.

### 3. Organization Slug
This is also `pay-ready` based on your organization.

## Environment Variables Required

You need to set these in GitHub Actions secrets:
- `SENTRY_API_TOKEN` - Your Sentry API token (you mentioned you already saved this)
- `SENTRY_ORGANIZATION_SLUG` - Set to `pay-ready`
- `SENTRY_PROJECT_SLUG` - Set to `pay-ready`

## Webhook Configuration

For the Sentry webhook URL field, you'll need to provide:
```
https://your-sophia-domain.com/webhooks/sentry
```

Replace `your-sophia-domain.com` with your actual Sophia AI deployment domain.

### Alert Rule Action Configuration
When creating alert rules in Sentry, you can configure webhook actions:
1. Go to your project settings in Sentry
2. Navigate to "Alerts" → "Alert Rules"
3. Create a new rule or edit existing
4. In the "Actions" section, add "Send a webhook to..."
5. Enter your Sophia webhook URL

## Testing the Integration

### 1. Update the Test Script
Edit `scripts/test/test_sentry_agent.py`:

```python
# Replace these with your actual values
PROJECT_SLUG = "pay-ready"  # Your project slug
ISSUE_ID = "1234567890"     # Replace with a real issue ID from Sentry
```

### 2. Run the Test
```bash
python scripts/test/test_sentry_agent.py
```

## Using Sentry MCP in Sophia AI

### Available MCP Tools

1. **get_sentry_issue** - Fetch detailed information about a specific issue
   ```
   Parameters:
   - project_slug: "pay-ready"
   - issue_id: "1234567890"
   ```

2. **list_sentry_issues** - List recent issues from your project
   ```
   Parameters:
   - project_slug: "pay-ready"
   - limit: 10 (optional)
   - status: "unresolved" (optional: unresolved/resolved/ignored)
   ```

3. **get_issue_events** - Get events associated with an issue
   ```
   Parameters:
   - issue_id: "1234567890"
   - limit: 5 (optional)
   ```

4. **create_sentry_alert** - Create alert rules
   ```
   Parameters:
   - project_slug: "pay-ready"
   - name: "Alert name"
   - conditions: {...}
   - actions: [...]
   ```

5. **resolve_issue** - Mark an issue as resolved
   ```
   Parameters:
   - issue_id: "1234567890"
   ```

### Natural Language Commands

Once integrated, you can use natural language commands like:
- "Show me recent Sentry errors"
- "Get details about Sentry issue 1234567890"
- "List unresolved errors in the pay-ready project"
- "Create a Sentry alert for high error rates"
- "Resolve Sentry issue 1234567890"

## Deployment

### 1. Deploy with Docker Compose
```bash
# Deploy the Sentry MCP server
docker-compose -f docker-compose.sentry.yml up -d

# Or include it with your main deployment
docker-compose -f docker-compose.yml -f docker-compose.sentry.yml up -d
```

### 2. Verify Deployment
```bash
# Check if the container is running
docker ps | grep sentry-mcp

# Check logs
docker logs sentry-mcp
```

### 3. Test MCP Connection
```bash
# Test the MCP server is responding
curl http://localhost:9006/health
```

## Integration with Sophia Agents

The `SentryAgent` in `backend/agents/specialized/sentry_agent.py` is already configured to:
- Connect to the Sentry MCP server
- Fetch issue context
- Trigger Seer AI fixes (if available in your Sentry plan)
- Support Agno stateful workflows

## Troubleshooting

### Common Issues

1. **Can't find Issue ID**
   - Make sure you have at least one error logged in your Sentry project
   - Check that you're looking in the correct project
   - Verify your API token has read permissions

2. **Authentication Errors**
   - Verify your `SENTRY_API_TOKEN` is correct
   - Check token permissions in Sentry settings
   - Ensure the token hasn't expired

3. **Connection Issues**
   - Verify the Sentry MCP container is running
   - Check Docker network connectivity
   - Review container logs for errors

### Debug Commands
```bash
# Check environment variables
docker exec sentry-mcp env | grep SENTRY

# Test API connection
docker exec sentry-mcp python -c "
import os
import httpx
token = os.getenv('SENTRY_API_TOKEN')
org = os.getenv('SENTRY_ORGANIZATION_SLUG')
resp = httpx.get(f'https://sentry.io/api/0/organizations/{org}/', 
                 headers={'Authorization': f'Bearer {token}'})
print(f'Status: {resp.status_code}')
"
```

## Next Steps

1. Find a real Issue ID from your Sentry dashboard
2. Update the test script with your Issue ID
3. Run the test to verify the integration works
4. Deploy the Sentry MCP server
5. Start using natural language commands to interact with Sentry through Sophia AI

## Security Notes

- Never commit API tokens to version control
- Use GitHub Actions secrets for all sensitive data
- Rotate API tokens regularly
- Monitor API usage in Sentry settings
