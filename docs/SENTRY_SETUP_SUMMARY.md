# Sentry MCP Setup Summary for Sophia AI

## ✅ What's Been Set Up

1. **Sentry MCP Server** (`mcp-servers/sentry/`)
   - Full MCP server implementation with all Sentry API tools
   - Docker configuration ready for deployment
   - Supports all major Sentry operations

2. **Sentry Agent** (`backend/agents/specialized/sentry_agent.py`)
   - Already configured to work with the MCP server
   - Supports fetching issue context and triggering fixes

3. **Webhook Handler** (`backend/api/webhooks/sentry_webhook.py`)
   - Processes real-time Sentry events
   - Automatic issue analysis and notifications

4. **Docker Compose** (`docker-compose.sentry.yml`)
   - Ready to deploy with `docker-compose -f docker-compose.sentry.yml up -d`

## 🔑 What You Need to Provide

### 1. **Sentry Issue ID**
To find an Issue ID:
- Go to: https://sentry.io/organizations/pay-ready/issues/
- Click on any issue
- The URL will show: `.../issues/1234567890/`
- The number `1234567890` is your Issue ID

### 2. **Environment Variables** (GitHub Actions Secrets)
You mentioned you already have:
- ✅ `SENTRY_API_TOKEN` - Already saved
- ✅ `SENTRY_PROJECT_SLUG` - Set to `pay-ready`
- ⚠️ `SENTRY_ORGANIZATION_SLUG` - Should also be `pay-ready`

### 3. **Webhook URL**
For Sentry webhook configuration, use:
```
https://your-sophia-domain.com/webhooks/sentry
```

## 🚀 Quick Start

1. **Find an Issue ID** from your Sentry dashboard
2. **Test the integration**:
   ```bash
   # Update the test script with your Issue ID
   vim scripts/test/test_sentry_agent.py
   # Change: ISSUE_ID = "your_actual_issue_id_here"
   
   # Run the test
   python scripts/test/test_sentry_agent.py
   ```

3. **Deploy the MCP server**:
   ```bash
   docker-compose -f docker-compose.sentry.yml up -d
   ```

## 💬 Natural Language Commands

Once deployed, you can use commands like:
- "Show me recent Sentry errors"
- "Get details about Sentry issue [ID]"
- "List unresolved errors in pay-ready"
- "Create a Sentry alert for high error rates"
- "Resolve Sentry issue [ID]"

## 📊 Available MCP Tools

1. `get_sentry_issue` - Get issue details
2. `list_sentry_issues` - List project issues
3. `get_issue_events` - Get issue events
4. `create_sentry_alert` - Create alert rules
5. `resolve_issue` - Mark issues as resolved

## 🔍 Finding Your First Issue ID

If you don't have any issues yet:
1. Create a test error in your application
2. Or use the Sentry dashboard to create a test issue
3. Then grab the ID from the issues list

## 📝 Next Steps

1. Get an Issue ID from Sentry
2. Update and run the test script
3. Deploy the Sentry MCP server
4. Configure webhooks in Sentry settings
5. Start using natural language to manage errors!

---

**Need help?** Check the full guide at `docs/SENTRY_MCP_INTEGRATION_GUIDE.md`
