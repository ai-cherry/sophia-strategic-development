# Salesforce MCP Server

AI-friendly Salesforce CRM integration through the Model Context Protocol.

## Features

### Natural Language Query Support
- Convert natural language to SOQL/SOSL queries automatically
- Smart pattern matching for common query types
- Support for complex filters and date ranges

### Complete CRUD Operations
- Create, read, update, and delete records
- Bulk operations for mass data processing
- Automatic cache invalidation on data changes

### Schema Introspection
- Discover object schemas and field types
- List available standard and custom objects
- Explore object relationships

### Apex Code Management
- Execute anonymous Apex code
- Retrieve Apex class source code
- Real-time compilation and execution feedback

### Performance Optimization
- Redis caching for frequently accessed data
- Schema caching with 1-hour TTL
- Query result caching with 5-minute TTL
- Rate limit tracking and management

## Configuration

Required environment variables (stored in Pulumi ESC):

```yaml
SALESFORCE_CLIENT_ID       # OAuth App Client ID
SALESFORCE_CLIENT_SECRET   # OAuth App Client Secret  
SALESFORCE_USERNAME        # Service account username
SALESFORCE_PASSWORD        # Service account password
SALESFORCE_SECURITY_TOKEN  # Security token
SALESFORCE_INSTANCE_URL    # Your Salesforce instance URL
SALESFORCE_API_VERSION     # API version (e.g., "v60.0")
SALESFORCE_SANDBOX         # "true" for sandbox, "false" for production
```

## Tools

### query
Query Salesforce using natural language or SOQL:
- Natural language: "show me all accounts in California"
- SOQL: "SELECT Id, Name FROM Account WHERE State = 'CA'"

### create_record
Create new Salesforce records with field validation

### update_record
Update existing records by ID

### delete_record
Delete records with cascade handling

### bulk_operation
Perform mass insert/update/upsert/delete operations

### describe_object
Get detailed schema information for any object

### list_objects
List all available objects with filtering

### execute_apex
Run anonymous Apex code with debug output

### get_apex_class
Retrieve source code for Apex classes

### health_check
Monitor connection status and API limits

## Natural Language Examples

```
"Show me all open opportunities"
"List contacts at Microsoft"
"Find opportunities worth more than $100,000"
"Get hot leads"
"Show high priority cases"
"List accounts called Acme"
"Find opportunities closing this quarter"
```

## Prompt Templates

### opportunity_analysis
Analyze pipeline opportunities with filtering by stage and owner

### account_summary
Get comprehensive account information including:
- Basic details
- Recent activities
- Open opportunities
- Key contacts
- Support cases

### lead_scoring
Score and prioritize leads based on custom criteria

## Performance

- Average query response: <200ms (cached)
- Schema operations: <500ms (cached)
- Bulk operations: Async with progress tracking
- Cache hit rate: ~70% for common queries

## Error Handling

- Automatic retry with exponential backoff
- Detailed error messages for debugging
- Session refresh on expiration
- Graceful degradation without Redis

## Security

- OAuth 2.0 authentication
- Encrypted credential storage via Pulumi ESC
- Session timeout after 2 hours
- API call tracking for compliance

## Integration with Sophia AI

This MCP server integrates seamlessly with:
- **Redis**: For high-performance caching
- **Lambda Labs**: For natural language processing
- **Frontend Dashboard**: Real-time CRM data display
- **Vector Stores**: Semantic search on CRM data
