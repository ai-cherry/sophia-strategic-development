# Asana & Notion MCP Server Integration

## Overview

This document describes the integration of Asana and Notion MCP (Model Context Protocol) servers into the Sophia AI platform, providing comprehensive project management and knowledge base capabilities for the executive dashboard.

## Architecture

### MCP Server Architecture
```
Sophia AI Dashboard
       ↓
Backend API Routes
       ↓
MCP Gateway (Port 3000)
       ↓
┌─────────────────┬─────────────────┐
│   Asana MCP     │   Notion MCP    │
│   (Port 3006)   │   (Port 3007)   │
└─────────────────┴─────────────────┘
       ↓                   ↓
   Asana API          Notion API
```

### Integration Components

1. **MCP Servers**
   - `mcp-servers/asana/asana_mcp_server.py` - Asana project management integration
   - `mcp-servers/notion/notion_mcp_server.py` - Notion knowledge base integration

2. **Backend API Routes**
   - `backend/api/asana_integration_routes.py` - FastAPI routes for Asana data
   - `backend/api/notion_integration_routes.py` - FastAPI routes for Notion data

3. **Dashboard Integration**
   - Real-time project data in Executive Project Dashboard
   - Strategic content access in Knowledge Dashboard
   - Cross-platform tool usage analytics

## Asana MCP Server

### Features

#### Project Management
- **Project Retrieval**: Get projects with filtering by team, status, and archive state
- **Project Details**: Comprehensive project information including custom fields
- **Task Management**: Task retrieval, search, and assignment tracking
- **Team Organization**: Team structure and project distribution
- **Status Tracking**: Project status updates and progress monitoring

#### Dashboard Integration
- **Executive Summary**: Project counts, budget utilization, risk distribution
- **Progress Tracking**: Real-time project completion and milestone data
- **Resource Management**: Team allocation and workload distribution
- **Budget Analytics**: Spend tracking and budget variance analysis

### API Endpoints

#### Core Project Endpoints
```http
GET /api/v1/integrations/asana/health
GET /api/v1/integrations/asana/projects
GET /api/v1/integrations/asana/projects/{project_gid}
GET /api/v1/integrations/asana/projects/{project_gid}/tasks
```

#### Team and User Management
```http
GET /api/v1/integrations/asana/teams
GET /api/v1/integrations/asana/users/{user_gid}/tasks
```

#### Search and Analytics
```http
GET /api/v1/integrations/asana/search/tasks
GET /api/v1/integrations/asana/dashboard/summary
```

### Configuration

#### Environment Variables
```bash
ASANA_ACCESS_TOKEN=your_asana_personal_access_token
ASANA_WORKSPACE_GID=your_workspace_gid  # Optional
```

#### Docker Configuration
```yaml
asana-mcp:
  build:
    context: ./mcp-servers/asana
    dockerfile: Dockerfile
  environment:
    - ASANA_ACCESS_TOKEN=${ASANA_ACCESS_TOKEN}
    - ASANA_WORKSPACE_GID=${ASANA_WORKSPACE_GID}
    - MCP_TRANSPORT=sse
    - MCP_PORT=3006
  ports:
    - "3006:3006"
```

## Notion MCP Server

### Features

#### Knowledge Management
- **Page Search**: Full-text search across workspace pages
- **Content Retrieval**: Page content with block-level analysis
- **Database Queries**: Structured data access with filtering and sorting
- **User Management**: Workspace user information and activity

#### Strategic Planning
- **OKR Tracking**: Objectives and Key Results content discovery
- **Strategic Content**: Strategy, planning, and goal-related documents
- **Recent Activity**: Recently edited pages and collaborative updates
- **Content Analytics**: Page structure analysis and usage metrics

### API Endpoints

#### Core Content Endpoints
```http
GET /api/v1/integrations/notion/health
GET /api/v1/integrations/notion/search
GET /api/v1/integrations/notion/pages/{page_id}
GET /api/v1/integrations/notion/pages/{page_id}/content
GET /api/v1/integrations/notion/pages/{page_id}/analytics
```

#### Database Operations
```http
GET /api/v1/integrations/notion/databases/{database_id}
POST /api/v1/integrations/notion/databases/{database_id}/query
```

#### Strategic Content
```http
GET /api/v1/integrations/notion/strategic
GET /api/v1/integrations/notion/recent
GET /api/v1/integrations/notion/search/title/{title}
```

#### User Management
```http
GET /api/v1/integrations/notion/users
GET /api/v1/integrations/notion/users/{user_id}
```

### Configuration

#### Environment Variables
```bash
NOTION_ACCESS_TOKEN=your_notion_integration_token
```

#### Docker Configuration
```yaml
notion-mcp:
  build:
    context: ./mcp-servers/notion
    dockerfile: Dockerfile
  environment:
    - NOTION_ACCESS_TOKEN=${NOTION_ACCESS_TOKEN}
    - MCP_TRANSPORT=sse
    - MCP_PORT=3007
  ports:
    - "3007:3007"
```

## Dashboard Integration

### Executive Project Dashboard

#### Enhanced Features
- **Real-Time Project Data**: Live Asana project status and progress
- **Strategic Document Links**: Notion pages connected to projects
- **Cross-Platform Analytics**: Unified view of project management tools
- **Executive Summary**: High-level KPIs from both platforms

#### Data Flow
```
Asana Projects → MCP Server → Backend API → Dashboard Components
Notion Strategic Content → MCP Server → Backend API → Dashboard Components
```

### Knowledge Dashboard

#### Enhanced Features
- **Strategic Content Discovery**: OKR and planning documents from Notion
- **Recent Activity Tracking**: Latest updates across knowledge base
- **Content Analytics**: Page engagement and collaboration metrics
- **Search Integration**: Unified search across Notion workspace

## Security and Authentication

### Token Management
- **Pulumi ESC Integration**: Secure token storage and rotation
- **Environment Variables**: Centralized credential management
- **API Security**: OAuth-based authentication for both platforms

### Access Control
- **Workspace Permissions**: Respect existing Asana/Notion permissions
- **Rate Limiting**: API call throttling and quota management
- **Error Handling**: Graceful degradation on authentication failures

## Deployment

### Docker Compose Setup
```bash
# Start all MCP servers including Asana and Notion
docker-compose -f docker-compose.mcp-gateway.yml up -d

# Check MCP server health
curl http://localhost:3006/health  # Asana
curl http://localhost:3007/health  # Notion
```

### Health Monitoring
```bash
# Check integration health via backend API
curl http://localhost:8000/api/v1/integrations/asana/health
curl http://localhost:8000/api/v1/integrations/notion/health
```

### MCP Gateway Configuration
```json
[
  {"name": "asana", "url": "http://asana-mcp:3006"},
  {"name": "notion", "url": "http://notion-mcp:3007"}
]
```

## Usage Examples

### Executive Dashboard Integration

#### Get Project Summary
```python
# Via backend API
response = await fetch('/api/v1/integrations/asana/dashboard/summary')
summary = await response.json()

# Returns:
{
  "total_projects": 15,
  "active_projects": 12,
  "total_budget": 500000,
  "budget_utilization": 65,
  "risk_distribution": {"low": 8, "medium": 3, "high": 1}
}
```

#### Get Strategic Content
```python
# Via backend API
response = await fetch('/api/v1/integrations/notion/strategic?content_type=okr')
content = await response.json()

# Returns categorized OKR pages with summaries
```

### MCP Direct Integration

#### Call Asana MCP Tools
```python
# Direct MCP call
result = await asana_client.call_tool("get_projects", {
    "limit": 50,
    "archived": false
})
```

#### Call Notion MCP Tools
```python
# Direct MCP call
result = await notion_client.call_tool("search_strategic_content", {
    "content_type": "okr",
    "quarter": "Q3 2024"
})
```

## Performance Optimization

### Caching Strategy
- **API Response Caching**: 5-minute TTL for project data
- **Content Caching**: 15-minute TTL for Notion content
- **Health Check Caching**: 1-minute TTL for status endpoints

### Rate Limiting
- **Asana API**: 1,500 requests per minute per token
- **Notion API**: 3 requests per second per integration
- **MCP Gateway**: Connection pooling and request queuing

## Troubleshooting

### Common Issues

#### Authentication Errors
```bash
# Check token validity
curl -H "Authorization: Bearer $ASANA_ACCESS_TOKEN" \
     https://app.asana.com/api/1.0/users/me

curl -H "Authorization: Bearer $NOTION_ACCESS_TOKEN" \
     -H "Notion-Version: 2022-06-28" \
     https://api.notion.com/v1/users
```

#### MCP Server Connection Issues
```bash
# Check MCP server logs
docker logs asana-mcp
docker logs notion-mcp

# Test MCP gateway connectivity
curl http://localhost:3000/health
```

#### Data Synchronization Issues
```bash
# Force refresh integration data
curl -X POST http://localhost:8000/api/v1/integrations/asana/refresh
curl -X POST http://localhost:8000/api/v1/integrations/notion/refresh
```

## Monitoring and Alerting

### Health Checks
- **MCP Server Health**: Automated health endpoint monitoring
- **API Integration Health**: Backend route health validation
- **Data Freshness**: Sync timestamp monitoring

### Metrics
- **Request Volume**: API call frequency and patterns
- **Response Times**: Performance monitoring across integrations
- **Error Rates**: Failed request tracking and alerting
- **Data Quality**: Content validation and completeness checks

## Future Enhancements

### Planned Features
1. **Bi-directional Sync**: Create/update capabilities for both platforms
2. **Advanced Analytics**: ML-powered insights from project and content data
3. **Workflow Automation**: Cross-platform task and content automation
4. **Enhanced Search**: Semantic search across both platforms
5. **Real-time Notifications**: Live updates for project and content changes

### Integration Roadmap
- **Linear Integration**: Development workflow integration
- **Slack Integration**: Communication context for projects
- **Calendar Integration**: Timeline and deadline management
- **Advanced Reporting**: Custom dashboard creation and sharing

## Conclusion

The Asana and Notion MCP server integration provides comprehensive project management and knowledge base capabilities for the Sophia AI platform. This integration enables:

- **Unified Executive Visibility**: Single dashboard for all project management tools
- **Strategic Content Access**: Centralized access to planning and OKR documents  
- **Real-time Data Synchronization**: Live updates from both platforms
- **Scalable Architecture**: MCP-based design for easy extension

The implementation follows enterprise-grade patterns with proper security, monitoring, and error handling, ensuring reliable operation in production environments. 