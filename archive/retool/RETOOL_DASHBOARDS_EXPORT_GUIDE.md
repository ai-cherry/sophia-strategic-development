# Retool Dashboards Export Guide

## 📦 Dashboard Files

All dashboard JSON files are ready for export. You have three options:

### Option 1: Individual Dashboard Files
- **CEO Dashboard**: `retool_ceo_dashboard.json`
- **Knowledge Dashboard**: `retool_knowledge_dashboard.json`
- **Project Dashboard**: `retool_project_dashboard.json`

### Option 2: Formatted Versions (Pretty-printed)
- **CEO Dashboard**: `retool_ceo_dashboard_formatted.json`
- **Knowledge Dashboard**: `retool_knowledge_dashboard_formatted.json`
- **Project Dashboard**: `retool_project_dashboard_formatted.json`

### Option 3: Copy from Terminal
```bash
# Copy CEO Dashboard to clipboard (macOS)
cat retool_ceo_dashboard.json | pbcopy

# Copy Knowledge Dashboard to clipboard (macOS)
cat retool_knowledge_dashboard.json | pbcopy

# Copy Project Dashboard to clipboard (macOS)
cat retool_project_dashboard.json | pbcopy
```

## 🚀 Import Instructions

### Step 1: Prepare Retool Environment
1. Log into your Retool account
2. Navigate to **Settings > Environment Variables**
3. Add these required variables:
   ```
   API_BASE_URL=https://your-sophia-backend.com/api/v1
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USERNAME=your_username
   SNOWFLAKE_PASSWORD=your_password
   GONG_API_KEY=your_gong_api_key
   LINEAR_API_KEY=your_linear_api_key
   GITHUB_TOKEN=your_github_token
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_INDEX=your_index_name
   PINECONE_ENVIRONMENT=us-east1-gcp
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_REGION=us-east-1
   S3_BUCKET=your_bucket_name
   ```

### Step 2: Import Each Dashboard
1. In Retool, click **Create new** → **From JSON**
2. Copy the entire content of one dashboard JSON file
3. Paste into the import dialog
4. Click **Import**
5. Repeat for each dashboard

### Step 3: Configure Resources
After import, verify each resource connection:
1. Go to **Resources** tab in each app
2. Test each connection:
   - Snowflake Database
   - Sophia AI Backend API
   - Gong API
   - Linear GraphQL
   - GitHub API
   - Pinecone Vector DB
   - S3 Storage

### Step 4: Set Authentication
For the Sophia API resource:
1. Edit the resource
2. Ensure the Authorization header uses: `Bearer {{ localStorage.values.authToken }}`
3. You'll need to implement login flow to set this token

## 📊 Dashboard Overview

### CEO Strategic Intelligence Dashboard
- **File**: `retool_ceo_dashboard.json`
- **Tabs**: Strategic Overview, Strategic Chat, AI Insights
- **Key Metrics**: Revenue, MRR, Client Health
- **Integrations**: Snowflake, Gong, Sophia AI

### Knowledge Admin Dashboard
- **File**: `retool_knowledge_dashboard.json`
- **Tabs**: Upload & Create, Discovery Queue, Test & Refine, Manage Entries
- **Features**: Document processing, AI insight curation
- **Integrations**: Pinecone, S3, Sophia AI

### Project Intelligence Dashboard
- **File**: `retool_project_dashboard.json`
- **Tabs**: Portfolio Overview, OKR Alignment, Blockers & Actions, Team Performance, Analytics
- **Features**: Cross-platform project tracking, AI recommendations
- **Integrations**: Linear, GitHub, Sophia AI

## 🔧 Troubleshooting

### Common Issues

1. **"Resource not found" errors**
   - Ensure all environment variables are set
   - Test each resource connection individually

2. **"Authentication failed" errors**
   - Verify API keys are correct
   - Check if APIs require additional setup (OAuth, etc.)

3. **"Query timeout" errors**
   - Increase timeout in resource settings
   - Check if backend services are running

4. **Dark theme not applying**
   - In Retool app settings, set Theme to "Dark"
   - Custom CSS may need adjustment for your Retool version

### Backend Requirements

Ensure your Sophia AI backend has these endpoints:
```
GET  /api/v1/executive/client-health
GET  /api/v1/executive/revenue-metrics
POST /api/v1/executive/strategic-chat
GET  /api/v1/knowledge/entries
GET  /api/v1/knowledge/pending-insights
POST /api/v1/knowledge/upload
POST /api/v1/knowledge/test
GET  /api/v1/projects/portfolio
GET  /api/v1/projects/okr-alignment
GET  /api/v1/projects/blockers
GET  /api/v1/projects/team-performance
POST /api/v1/projects/ai-recommendations
```

## 📝 Customization

### Modify Colors
Search for color codes in the JSON:
- Background: `#0f0f0f` (main), `#1a1a1a` (cards)
- Success: `#10b981`
- Warning: `#f59e0b`
- Danger: `#ef4444`
- Primary: `#3b82f6`

### Add New Queries
1. Add to the `queries` array in the JSON
2. Reference in components using `{{ queryName.data }}`

### Modify Components
1. Find the component by `id` in the JSON
2. Update `properties` as needed
3. Add new components to `children` arrays

## 🎯 Next Steps

1. **Import all three dashboards** into Retool
2. **Configure environment variables** with your actual credentials
3. **Test each dashboard** thoroughly
4. **Customize** colors, layouts, and queries as needed
5. **Share with team** using Retool's permission system

## 💡 Pro Tips

- Use Retool's version control to track dashboard changes
- Set up scheduled queries for data refresh
- Create custom components for repeated UI patterns
- Use Retool's built-in caching for better performance
- Enable audit logs for compliance tracking

---

For support, refer to:
- [Retool Documentation](https://docs.retool.com)
- [Sophia AI Backend Documentation](./docs/API_DOCUMENTATION.md)
- [Integration Guides](./docs/)
