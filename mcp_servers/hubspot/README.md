# HubSpot MCP Server

AI-friendly HubSpot CRM integration through the Model Context Protocol.

## Features

### Natural Language Query Support
- Convert natural language to HubSpot API queries automatically
- Smart pattern matching for common CRM queries
- Support for complex filters and date ranges

### Complete CRUD Operations
- Create, read, update, and delete all HubSpot objects
- Batch operations for mass data processing
- Association management between objects

### Pipeline Management
- View and manage sales pipelines
- Move deals between stages
- Track pipeline metrics and velocity

### Analytics & Insights
- Revenue analytics with custom date ranges
- Pipeline health metrics
- Contact engagement analysis
- Activity timeline tracking

### Performance Optimization
- Redis caching for frequently accessed data
- Pipeline caching with 1-hour TTL
- Query result caching with 5-minute TTL
- Rate limit tracking and management

## Configuration

Required environment variables (stored in Pulumi ESC):

```yaml
HUBSPOT_PRIVATE_APP_KEY    # Private app access token
HUBSPOT_PORTAL_ID          # HubSpot portal/account ID
```

## Tools

### search
Search HubSpot CRM using natural language:
- Natural language: "contacts at Microsoft"
- Direct search: "deals worth more than $100,000"
- Date filters: "contacts created today"

### create_object
Create new HubSpot objects with associations

### update_object
Update existing objects by ID

### delete_object
Delete objects with cascade handling

### get_pipelines
View sales pipelines and stages with probabilities

### move_deal_stage
Move deals through pipeline stages

### get_analytics
Generate analytics reports:
- Revenue metrics
- Pipeline analysis
- Contact growth
- Activity tracking

### get_timeline
View activity history for any CRM object

### batch_operation
Perform bulk create/update/archive operations

### health_check
Monitor connection status and API limits

## Natural Language Examples

```
"Find contacts at Acme Corp"
"Show deals closing this quarter"
"List companies in technology industry"
"Get deals worth more than $50,000"
"Find contacts created this week"
"Show closed won deals"
"List high-value opportunities"
```

## Prompt Templates

### deal_pipeline_analysis
Analyze pipeline health with filtering by stage and pipeline

### contact_engagement
Analyze contact engagement metrics by segment

### revenue_forecast
Generate revenue forecasts based on pipeline data

## Performance

- Average query response: <300ms (cached)
- Pipeline operations: <200ms (cached)
- Batch operations: Async with progress tracking
- Cache hit rate: ~60% for common queries

## Rate Limits

HubSpot has strict API limits:
- Daily limit: 250,000 API calls
- Per-second limit: 10 requests
- Automatic rate limit tracking
- Usage percentage in health checks

## Error Handling

- Automatic retry with exponential backoff
- Detailed error messages for debugging
- Graceful degradation without Redis
- Rate limit awareness

## Security

- Private app authentication
- Encrypted credential storage via Pulumi ESC
- No token expiration for private apps
- Secure API communication

## Integration with Sophia AI

This MCP server integrates seamlessly with:
- **Redis**: For high-performance caching
- **Frontend Dashboard**: Real-time CRM data display
- **Vector Stores**: Semantic search on CRM data
- **Workflow Automation**: N8N integration for CRM workflows

## HubSpot Object Types Supported

- Contacts
- Companies
- Deals
- Tickets
- Tasks
- Notes
- Meetings
- Calls
- Emails
- Products
- Line Items
- Quotes
