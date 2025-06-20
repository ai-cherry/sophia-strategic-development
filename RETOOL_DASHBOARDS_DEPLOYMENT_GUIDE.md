# Sophia AI Retool Dashboards - Complete Deployment Guide

## 🚀 Overview

This guide will help you deploy all three Sophia AI dashboards in Retool:
1. **CEO Dashboard** - Executive command center with strategic intelligence
2. **Knowledge Admin** - Knowledge base management and curation
3. **Project Intelligence** - Unified project management across all tools

All dashboards use a consistent dark theme design system with shared components.

## 📋 Prerequisites

Before starting, ensure you have:
- [ ] Retool account (free tier is sufficient for testing)
- [ ] Docker and Docker Compose installed
- [ ] API keys for integrations (Snowflake, Gong, Slack, etc.)
- [ ] Python 3.8+ installed

## 🛠️ Step 1: Start All Services

### Option A: Automated Setup (Recommended)
```bash
# Make scripts executable
chmod +x scripts/start_all_services.sh

# Start all services
./scripts/start_all_services.sh
```

### Option B: Manual Setup
```bash
# Start backend
cd backend
python main.py &
cd ..

# Start MCP servers
docker-compose up -d gong-mcp slack-mcp snowflake-mcp pinecone-mcp linear-mcp retool-mcp

# Start MCP gateway
docker-compose up -d mcp-gateway
```

## 🔧 Step 2: Run Deployment Script

```bash
# Run the comprehensive deployment script
python scripts/deploy_all_dashboards.py
```

This script will:
- Check all prerequisites
- Verify backend is running
- Start necessary MCP servers
- Test all integrations
- Generate Retool configurations
- Create a detailed deployment guide

## 📊 Step 3: Create Retool Dashboards

### 3.1 Log into Retool
1. Go to https://retool.com
2. Sign in or create a free account

### 3.2 Create Three Apps
Create three new apps with these exact names:
1. "Sophia CEO Dashboard"
2. "Sophia Knowledge Admin"
3. "Sophia Project Intelligence"

### 3.3 Configure Each Dashboard

#### CEO Dashboard Setup
1. **Add REST API Resource**:
   - Name: `SophiaAPI`
   - Base URL: `http://localhost:8000`
   - Headers:
     - Key: `X-Admin-Key`
     - Value: `sophia_admin_2024`

2. **Import Configuration**:
   - Go to Settings → App JSON
   - Copy contents from `retool_ceo_dashboard_config.json`
   - Paste and save

3. **Key Components**:
   - Strategic Intelligence Chat
   - Client Health Portfolio
   - AI System Status Monitor

#### Knowledge Admin Setup
1. **Add REST API Resource**:
   - Name: `KnowledgeAPI`
   - Base URL: `http://localhost:8000/api/knowledge`
   - Headers:
     - Key: `Authorization`
     - Value: `Bearer {{ current_user.authToken }}`

2. **Import Configuration**:
   - Copy from `retool_knowledge_dashboard_config.json`

3. **Key Components**:
   - Document Upload Interface
   - Knowledge Curation Chat
   - Discovery Queue

#### Project Intelligence Setup
1. **Add REST API Resource**:
   - Name: `ProjectAPI`
   - Base URL: `http://localhost:8000/api/project-management`
   - Headers:
     - Key: `Authorization`
     - Value: `Bearer {{ environment.SOPHIA_API_KEY }}`

2. **Import Configuration**:
   - Copy from `retool_project_dashboard_config.json`

3. **Key Components**:
   - Portfolio Overview
   - OKR Alignment Tracker
   - Team Performance Analytics

## 🎨 Design System

All dashboards use this consistent design:

### Colors
- **Primary**: #5E6AD2 (Linear purple)
- **Secondary**: #238636 (GitHub green)
- **Accent**: #F59E0B (Warning yellow)
- **Success**: #10B981 (Green)
- **Danger**: #EF4444 (Red)
- **Background**: #1a1a1a (Dark)
- **Surface**: #2a2a2a (Cards)

### Typography
- **Font**: Inter, system-ui, sans-serif
- **Headings**: Bold, larger sizes
- **Body**: Regular weight

### Components
- **Cards**: 8px border radius, subtle shadow
- **Spacing**: 4px, 8px, 16px, 24px, 32px
- **Icons**: Font Awesome icons

## 🔌 Integration Status

The deployment script tests all integrations:

### Required Integrations
- **Snowflake**: Data warehouse for analytics
- **Gong**: Sales call analysis
- **Slack**: Team communication
- **Pinecone**: Vector search for knowledge base
- **Linear**: Project management
- **OpenAI**: AI capabilities

### Testing Integrations
```bash
# Test all integrations
curl -H "X-Admin-Key: sophia_admin_2024" \
     http://localhost:8000/api/integrations/test-all

# Test individual integration
curl -H "X-Admin-Key: sophia_admin_2024" \
     http://localhost:8000/api/integrations/snowflake/test
```

## 📝 Common Queries

### CEO Dashboard Queries
```javascript
// Get dashboard summary
const dashboardSummary = await SophiaAPI.get('/api/retool/executive/dashboard-summary');

// Strategic chat
const chatResponse = await SophiaAPI.post('/api/retool/executive/strategic-chat', {
  message: userInput,
  mode: 'internal'
});
```

### Knowledge Admin Queries
```javascript
// Upload document
const uploadResult = await KnowledgeAPI.post('/upload', {
  file: fileInput.files[0],
  metadata: { source: 'manual', tags: tagInput.value }
});

// Search knowledge
const searchResults = await KnowledgeAPI.get('/search', {
  q: searchInput.value
});
```

### Project Management Queries
```javascript
// Get portfolio summary
const portfolio = await ProjectAPI.get('/dashboard/summary');

// Get OKR alignment
const okrs = await ProjectAPI.get('/okr/alignment', {
  quarter: quarterSelector.value
});
```

## 🚨 Troubleshooting

### Backend Not Connecting
1. Check if backend is running: `lsof -i :8000`
2. View logs: `tail -f backend.log`
3. Restart backend: `cd backend && python main.py`

### MCP Servers Not Running
1. Check Docker status: `docker ps`
2. View logs: `docker-compose logs [server-name]`
3. Restart all: `docker-compose down && docker-compose up -d`

### Integration Failures
1. Check environment variables in `.env`
2. Verify API keys are valid
3. Test individual integrations using curl commands

### Retool Issues
1. Clear browser cache
2. Check browser console for errors
3. Verify API resource configuration
4. Test queries individually

## 📈 Next Steps

1. **Customize Visualizations**: Add charts and graphs specific to your data
2. **Set Up Webhooks**: Enable real-time updates
3. **Configure Permissions**: Set up role-based access control
4. **Add Custom Actions**: Create buttons for common operations
5. **Enable Notifications**: Set up alerts for important events

## 🔗 Additional Resources

- [Retool Documentation](https://docs.retool.com)
- [Sophia AI API Docs](http://localhost:8000/docs)
- [MCP Server Guide](./docs/MCP_IMPLEMENTATION_README.md)
- [Integration Setup](./docs/INTEGRATION_SETUP_GUIDE.md)

## 💡 Tips

1. **Use Query Library**: Save common queries for reuse
2. **Enable Caching**: Improve performance for frequently accessed data
3. **Add Loading States**: Better UX during data fetching
4. **Use Transformers**: Process data before displaying
5. **Set Up Environments**: Separate dev/staging/production

## 🎯 Success Checklist

- [ ] All services running (backend, MCP servers, gateway)
- [ ] All integrations connected and tested
- [ ] Three Retool apps created
- [ ] API resources configured in each app
- [ ] Configurations imported
- [ ] Basic queries working
- [ ] Data displaying correctly

---

**Need Help?**
- Check the generated `COMPLETE_DASHBOARD_DEPLOYMENT_GUIDE.md` for detailed status
- Review logs in `backend.log` for errors
- Contact support@payready.com for assistance
