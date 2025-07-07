# MCP Server Migration Plan - Production-Ready Architecture

## Executive Summary

This plan outlines the migration of 38 MCP servers to a production-ready architecture with:
- **Async/await** patterns for high performance
- **Production logging** with JSON format and correlation IDs
- **Health monitoring** with detailed component checks
- **Prometheus metrics** for observability
- **Docker support** for consistent deployment
- **Comprehensive testing** (unit + integration)
- **Error handling** and circuit breakers
- **Connection pooling** for databases and APIs

## 🏗️ Architecture Overview

### Directory Structure
```
infrastructure/mcp_servers/<server-name>/
├── __init__.py              # Package marker
├── config.py                # Pydantic settings management
├── server.py                # Main server implementation
├── handlers/                # Business logic handlers
│   ├── __init__.py
│   └── main_handler.py      # Primary business logic
├── models/                  # Data models
│   ├── __init__.py
│   └── data_models.py       # Pydantic models
├── utils/                   # Utilities
│   ├── __init__.py
│   ├── logging_config.py    # JSON logging setup
│   └── db.py               # Database helpers (optional)
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── requirements.txt         # Dependencies
├── Dockerfile              # Container definition
├── docker-compose.yml      # Local development
├── .env.example            # Environment template
└── README.md               # Documentation
```

## 🚀 Migration Strategy

### Phase 1: Core Infrastructure (Week 1)
1. **Create scaffolding script** ✅
   - `scripts/scaffold_mcp_server.py` - Production-ready template generator
   - Automatically assigns ports, creates structure, updates configs

2. **Migrate 5 priority servers**
   - `ai_memory` - Critical for conversation context
   - `github` - Code repository integration
   - `snowflake` - Data warehouse access
   - `slack` - Team communication
   - `portkey_admin` - AI gateway management

### Phase 2: Business-Critical Servers (Week 2)
3. **Migrate business integrations**
   - `gong` - Call analytics
   - `hubspot` - CRM integration
   - `linear` - Project management
   - `asana` - Task management
   - `notion` - Knowledge base

### Phase 3: AI/ML Servers (Week 3)
4. **Migrate AI capabilities**
   - `cortex_aisql` - SQL generation
   - `costar` - Prompt engineering
   - `mem0_openmemory` - Long-term memory
   - `ai_code_quality` - Code analysis
   - `v0_dev` - UI generation

### Phase 4: Remaining Servers (Week 4)
5. **Complete migration**
   - All remaining servers
   - Deprecate old implementations
   - Update all references

## 📋 Server-by-Server Implementation

### Example: GitHub MCP Server

```python
# server.py - Main implementation
class GithubMCPServer(StandardizedMCPServer):
    async def server_specific_init(self):
        self.github_client = GithubClient(
            token=settings.GITHUB_TOKEN,
            org=settings.GITHUB_ORG
        )
        
    async def sync_data(self):
        repos = await self.github_client.list_repositories()
        for repo in repos:
            await self.process_with_ai(repo)
        return {"synced": len(repos)}
```

### Production Features

#### 1. Health Monitoring
```python
async def server_specific_health_check(self) -> HealthCheckResult:
    # Check GitHub API
    api_healthy = await self.github_client.check_health()
    
    # Check rate limits
    rate_limit = await self.github_client.get_rate_limit()
    
    return HealthCheckResult(
        component="github",
        status=HealthStatus.HEALTHY if api_healthy else HealthStatus.UNHEALTHY,
        metadata={"rate_limit_remaining": rate_limit}
    )
```

#### 2. Error Handling
```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_with_retry(self, endpoint: str):
    try:
        return await self.session.get(endpoint)
    except aiohttp.ClientError as e:
        logger.error(f"API request failed: {e}", extra={
            "endpoint": endpoint,
            "error_type": type(e).__name__
        })
        raise
```

#### 3. Connection Pooling
```python
# Reuse connections efficiently
self.session = aiohttp.ClientSession(
    connector=aiohttp.TCPConnector(
        limit=100,  # Total connection pool size
        limit_per_host=30,  # Per-host limit
        ttl_dns_cache=300  # DNS cache timeout
    ),
    timeout=aiohttp.ClientTimeout(total=30)
)
```

## 🔧 Implementation Details

### Scaffolding Script Usage
```bash
# Create a new MCP server
python scripts/scaffold_mcp_server.py <server-name>

# Example: Create Slack server
python scripts/scaffold_mcp_server.py slack

# Output:
# ✅ Created slack MCP server on port 9002
# 📁 Files created at infrastructure/mcp_servers/slack/
# 📝 Updated mcp_config.json
```

### Environment Configuration
```bash
# Production (Lambda Labs)
SLACK_API_KEY=${secrets.slack_api_key}  # From Pulumi ESC
SLACK_LOG_LEVEL=INFO
SLACK_ENABLE_METRICS=true

# Development (Local)
SLACK_API_KEY=xoxb-test-token
SLACK_LOG_LEVEL=DEBUG
SLACK_ENABLE_METRICS=false
```

### Docker Deployment
```bash
# Build image
docker build -t scoobyjava15/slack-mcp:latest infrastructure/mcp_servers/slack/

# Run locally
docker-compose -f infrastructure/mcp_servers/slack/docker-compose.yml up

# Deploy to Lambda Labs
docker push scoobyjava15/slack-mcp:latest
docker stack deploy -c docker-compose.production.yml slack-mcp
```

## 📊 Monitoring & Observability

### Prometheus Metrics
Each server exposes metrics at `/metrics`:
- `mcp_<server>_requests_total` - Request count
- `mcp_<server>_request_duration_seconds` - Latency histogram
- `mcp_<server>_health_status` - Health gauge (0/1)
- `mcp_<server>_sync_success_rate` - Sync reliability
- `mcp_<server>_records_processed_total` - Data volume

### Structured Logging
```json
{
  "timestamp": "2024-01-07T10:30:45.123Z",
  "level": "INFO",
  "logger": "slack.handler",
  "message": "Message sent successfully",
  "service": "slack-mcp",
  "environment": "production",
  "channel": "#alerts",
  "message_id": "msg_123",
  "duration_ms": 145
}
```

## 🧪 Testing Strategy

### Unit Tests
```python
# tests/unit/test_handler.py
@pytest.mark.asyncio
async def test_send_message():
    handler = SlackHandler()
    handler.client = AsyncMock()
    
    await handler.send_message("#test", "Hello")
    
    handler.client.chat_postMessage.assert_called_once_with(
        channel="#test",
        text="Hello"
    )
```

### Integration Tests
```python
# tests/integration/test_server.py
@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "degraded"]
```

## 🔄 Migration Checklist

For each server:
- [ ] Run scaffolding script
- [ ] Implement handler business logic
- [ ] Add server-specific models
- [ ] Configure environment variables
- [ ] Write unit tests (>80% coverage)
- [ ] Write integration tests
- [ ] Test locally with Docker
- [ ] Update documentation
- [ ] Deploy to staging
- [ ] Validate metrics and logs
- [ ] Deploy to production
- [ ] Deprecate old implementation

## 📈 Success Metrics

- **Response Time**: p99 < 200ms
- **Availability**: >99.9% uptime
- **Error Rate**: <0.1% of requests
- **Test Coverage**: >80% code coverage
- **Deployment Time**: <5 minutes per server

## 🚨 Rollback Plan

1. **Canary Deployment**: Route 10% traffic to new server
2. **Monitor Metrics**: Watch error rates and latency
3. **Quick Rollback**: Switch traffic back if issues
4. **Fix Forward**: Address issues and redeploy

## 📅 Timeline

- **Week 1**: Core infrastructure + 5 priority servers
- **Week 2**: Business-critical integrations (5 servers)
- **Week 3**: AI/ML capabilities (5 servers)
- **Week 4**: Remaining servers + cleanup
- **Week 5**: Performance optimization & documentation

## 🎯 End State

All 38 MCP servers will have:
- ✅ Consistent architecture
- ✅ Production-grade reliability
- ✅ Comprehensive monitoring
- ✅ Automated testing
- ✅ Docker deployment
- ✅ Unified configuration
- ✅ Professional documentation

This migration transforms our MCP infrastructure from prototype to production-ready, enabling reliable AI orchestration at scale. 