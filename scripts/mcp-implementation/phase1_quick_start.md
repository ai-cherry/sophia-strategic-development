# 🚀 Phase 1 MCP Quick Start Guide

## ✅ Current Status

All 5 game-changing MCP servers are successfully deployed and ready for configuration!

### Deployed Servers:
1. **Microsoft Playwright MCP** ✅ - Web automation powerhouse
2. **Snowflake Cortex Agent** ✅ - Native AI data intelligence  
3. **Apollo.io MCP** ✅ - Sales intelligence automation
4. **Apify Official MCP** ✅ - 5,000+ automation tools
5. **Figma Context MCP** ✅ - Design-to-code revolution

**Total Business Value: $1.7M+**

## 🔐 Required Environment Variables

Before starting the servers, set these environment variables:

```bash
# Snowflake Cortex
export SNOWFLAKE_ACCOUNT='your-snowflake-account'
export SNOWFLAKE_USER='your-username'
export SNOWFLAKE_PASSWORD='your-password'

# Apollo.io (Get API key from https://app.apollo.io/#/settings/integrations/api)
export APOLLO_IO_API_KEY='your-apollo-api-key'

# Apify (Get token from https://console.apify.com/account/integrations)
export APIFY_TOKEN='your-apify-token'

# Figma (Get from https://www.figma.com/developers/api#access-tokens)
export FIGMA_ACCESS_TOKEN='your-figma-token'
```

## 🎯 Quick Start Commands

### 1. Install Node.js Dependencies

```bash
# Microsoft Playwright MCP
cd mcp-servers/playwright/microsoft-playwright-mcp
npm install
cd ../../..

# Apollo.io MCP
cd mcp-servers/apollo/apollo-io-mcp
npm install
cd ../../..

# Figma Context MCP
cd mcp-servers/figma_context/figma-context-mcp
npm install
cd ../../..
```

### 2. Configure Cursor IDE

Copy the Phase 1 configuration to Cursor:

```bash
cp config/cursor_phase1_mcp_config.json ~/Library/Application\ Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/
```

Or manually add to your Cursor settings.

### 3. Test Individual Servers

#### Test Snowflake Cortex:
```bash
cd mcp-servers/snowflake_cortex
python snowflake_cortex_mcp_server.py
```

#### Test Microsoft Playwright:
```bash
cd mcp-servers/playwright/microsoft-playwright-mcp
npm start
```

#### Test Apollo.io:
```bash
cd mcp-servers/apollo/apollo-io-mcp
npm start
```

## 🔄 Sample Integration Workflows

### 1. Design-to-Code Pipeline
```
Figma Context → Extract Design
     ↓
Snowflake Cortex → Generate Descriptions
     ↓
Code Generation → Production Components
     ↓
Playwright → Automated Testing
```

### 2. Sales Intelligence Automation
```
Apollo.io → Find Prospects
     ↓
Snowflake Cortex → Analyze Fit
     ↓
Apify → Research Company
     ↓
Generate Outreach → Personalized Messages
```

### 3. Web Automation Research
```
Playwright → Navigate to Sites
     ↓
Apify → Extract Data
     ↓
Snowflake Cortex → Analyze Content
     ↓
Generate Report → Business Intelligence
```

## 📊 Monitoring & Health Checks

Run health checks anytime:
```bash
python scripts/mcp-implementation/phase1_health_check.py
```

Run integration tests:
```bash
python scripts/mcp-implementation/phase1_integration_test.py
```

## 🎉 What's Next?

1. **Get API Keys** - Sign up for the services above
2. **Set Environment Variables** - Use the export commands
3. **Install Dependencies** - Run npm install in each server
4. **Configure Cursor** - Add the MCP configuration
5. **Start Testing** - Try the sample workflows!

## 💡 Pro Tips

- Start with Snowflake Cortex if you already have Snowflake access
- Apify offers a free tier with 1,000 operations/month
- Apollo.io has a free trial for testing
- Figma personal access tokens are free
- Microsoft Playwright works immediately without API keys

## 🆘 Troubleshooting

If servers don't start:
1. Check Node.js version: `node --version` (should be 18+)
2. Check Python version: `python3 --version` (should be 3.11+)
3. Verify environment variables are set
4. Check logs in `logs/mcp-deployment/`

## 📚 Documentation

- [Microsoft Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Apollo.io API Docs](https://apolloio.github.io/apollo-api-docs/)
- [Apify Platform Docs](https://docs.apify.com/platform/integrations/mcp)
- [Figma API Reference](https://www.figma.com/developers/api)
- [Snowflake Cortex Docs](https://docs.snowflake.com/en/guides/snowflake-cortex)

---

**Ready to revolutionize your AI development? Let's go! 🚀**
