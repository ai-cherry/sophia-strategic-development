# Snowflake V2 MCP Server

Enhanced Snowflake data management server with AI integration capabilities.

## Features

- **Modern Async Architecture**: Built with FastAPI and async patterns for high performance
- **AI Integration**: Native support for Snowflake Cortex embeddings and semantic search
- **Comprehensive Data Management**: Schema creation, table management, data loading
- **Performance Optimization**: Automatic clustering, query optimization, warehouse management
- **Enterprise Security**: Integration with Pulumi ESC for secure credential management

## API Endpoints

### Core Operations
- `POST /api/v2/query` - Execute SQL queries with AI enhancement
- `POST /api/v2/schema/create` - Create schemas with AI-ready tables
- `POST /api/v2/table/create` - Create tables with automatic AI columns
- `POST /api/v2/data/load` - Load data with automatic enrichment

### AI Operations
- `POST /api/v2/ai/embed` - Generate embeddings using Snowflake Cortex
- `POST /api/v2/ai/search` - Perform semantic search

### Management Operations
- `GET /api/v2/status` - Get comprehensive system status
- `POST /api/v2/optimize` - Optimize performance
- `POST /api/v2/sync/schemas` - Sync schemas with codebase
- `POST /api/v2/warehouse/manage` - Manage warehouses

## Configuration

The server uses environment variables for configuration:

```bash
# Snowflake Connection (from Pulumi ESC)
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_USER=your-user
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_WAREHOUSE=SOPHIA_AI_COMPUTE_WH
SNOWFLAKE_DATABASE=SOPHIA_AI_PRODUCTION

# Server Configuration
SNOWFLAKE_V2_PORT=9001
```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables or use Pulumi ESC

3. Run the server:
```bash
python -m infrastructure.mcp_servers.snowflake_v2.server
```

## Docker Deployment

Build and run with Docker:

```bash
docker build -t snowflake-v2-mcp .
docker run -p 9001:9001 --env-file .env snowflake-v2-mcp
```

## Testing

Run tests:
```bash
pytest tests/
```

## AI Features

### Embedding Generation

Generate embeddings for text data:

```python
POST /api/v2/ai/embed
{
    "table": "sophia_ai_core.public.documents",
    "text_column": "content",
    "embedding_column": "ai_embeddings"
}
```

### Semantic Search

Search using natural language:

```python
POST /api/v2/ai/search
{
    "query": "customer complaints about shipping",
    "table": "sophia_ai_core.public.documents",
    "limit": 10
}
```

## Performance Optimization

The server includes automatic performance optimization:

- Clustering key management
- Query result caching
- Warehouse auto-scaling
- Statistics collection

## Integration with Sophia AI

This server integrates seamlessly with the Sophia AI platform:

- Uses Pulumi ESC for credential management
- Supports AI Memory integration
- Compatible with other MCP servers
- Provides data foundation for business intelligence
