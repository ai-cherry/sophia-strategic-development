# Sophia AI - Comprehensive API Documentation

## 🚀 **Overview**

The Sophia AI API provides comprehensive access to all integrated services through a unified natural language interface. This documentation covers all endpoints, authentication, and usage examples.

## 🔐 **Authentication**

All API endpoints require authentication using one of the following methods:

### **1. API Key Authentication**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.sophia.ai/v1/endpoint
```

### **2. OAuth 2.0 (Recommended)**
```bash
curl -H "Authorization: Bearer YOUR_OAUTH_TOKEN" \
     -H "Content-Type: application/json" \
     https://api.sophia.ai/v1/endpoint
```

## 📋 **Core Endpoints**

### **Natural Language Query**
Process natural language requests and route to appropriate services.

**Endpoint:** `POST /api/natural-query`

**Request:**
```json
{
  "query": "Get all deals from Gong for this month",
  "context": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "service": "gong",
    "action": "get_deals",
    "data": [...],
    "metadata": {
      "execution_time": "1.2s",
      "confidence": 0.95
    }
  }
}
```

### **Health Check**
Check the health status of all integrated services.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "snowflake": {"status": "healthy", "response_time": "45ms"},
    "gong": {"status": "healthy", "response_time": "120ms"},
    "vercel": {"status": "healthy", "response_time": "80ms"},
    "claude": {"status": "healthy", "response_time": "200ms"}
  },
  "timestamp": "2025-01-20T10:30:00Z"
}
```

## 🏗️ **Infrastructure Endpoints**

### **Secret Management**
Manage secrets through Pulumi ESC integration.

**Get Secret:** `GET /api/secrets/{service}/{key}`
**Set Secret:** `POST /api/secrets/{service}/{key}`
**Rotate Secrets:** `POST /api/secrets/rotate/{service}`

### **Configuration Management**
Manage service configurations.

**Get Config:** `GET /api/config/{service}`
**Update Config:** `PUT /api/config/{service}`
**Validate Config:** `POST /api/config/{service}/validate`

## 🤖 **Claude Integration Endpoints**

### **Code Generation**
Generate code using Claude AI.

**Endpoint:** `POST /api/claude/generate-code`

**Request:**
```json
{
  "prompt": "Create a Python function to process CSV files",
  "language": "python",
  "context": {
    "framework": "pandas",
    "style": "functional"
  }
}
```

### **Code Analysis**
Analyze code for issues and improvements.

**Endpoint:** `POST /api/claude/analyze-code`

**Request:**
```json
{
  "code": "def process_data(data): ...",
  "analysis_type": ["security", "performance", "style"]
}
```

## 📊 **Service-Specific Endpoints**

### **Gong Integration**
Access Gong CRM data and functionality.

- `GET /api/gong/calls` - Get call recordings
- `GET /api/gong/deals` - Get deal information
- `GET /api/gong/users` - Get user data
- `POST /api/gong/search` - Search across Gong data

### **Snowflake Integration**
Execute queries and manage Snowflake resources.

- `POST /api/snowflake/query` - Execute SQL queries
- `GET /api/snowflake/tables` - List available tables
- `GET /api/snowflake/schema` - Get schema information

### **Vercel Integration**
Manage deployments and projects.

- `GET /api/vercel/deployments` - List deployments
- `POST /api/vercel/deploy` - Create new deployment
- `GET /api/vercel/projects` - List projects

## 🔄 **Webhook Endpoints**

### **GitHub Webhooks**
Handle GitHub events for automated workflows.

**Endpoint:** `POST /api/webhooks/github`

### **Slack Webhooks**
Process Slack events and commands.

**Endpoint:** `POST /api/webhooks/slack`

## 📈 **Monitoring Endpoints**

### **Metrics**
Get system performance metrics.

**Endpoint:** `GET /api/metrics`

### **Logs**
Access system logs with filtering.

**Endpoint:** `GET /api/logs?service={service}&level={level}&since={timestamp}`

## 🚨 **Error Handling**

All endpoints return standardized error responses:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request is invalid",
    "details": {
      "field": "query",
      "reason": "Query cannot be empty"
    },
    "request_id": "req_123456789"
  }
}
```

### **Common Error Codes**
- `INVALID_REQUEST` (400) - Request validation failed
- `UNAUTHORIZED` (401) - Authentication required
- `FORBIDDEN` (403) - Insufficient permissions
- `NOT_FOUND` (404) - Resource not found
- `RATE_LIMITED` (429) - Too many requests
- `INTERNAL_ERROR` (500) - Server error
- `SERVICE_UNAVAILABLE` (503) - Service temporarily unavailable

## 📝 **Usage Examples**

### **Natural Language Infrastructure Management**
```bash
# Deploy infrastructure
curl -X POST https://api.sophia.ai/v1/natural-query \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"query": "Deploy the infrastructure to production"}'

# Check service health
curl -X POST https://api.sophia.ai/v1/natural-query \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"query": "Check the health of all services"}'

# Rotate secrets
curl -X POST https://api.sophia.ai/v1/natural-query \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"query": "Rotate all API keys for security"}'
```

### **Code Generation with Claude**
```bash
# Generate Python function
curl -X POST https://api.sophia.ai/v1/claude/generate-code \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "prompt": "Create a function to validate email addresses",
    "language": "python",
    "context": {"style": "modern", "include_tests": true}
  }'
```

### **Data Analysis with Snowflake**
```bash
# Execute query
curl -X POST https://api.sophia.ai/v1/snowflake/query \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "query": "SELECT COUNT(*) FROM customers WHERE created_date >= CURRENT_DATE - 30",
    "format": "json"
  }'
```

## 🔧 **SDK and Libraries**

### **Python SDK**
```python
from sophia_ai import SophiaClient

client = SophiaClient(api_key="your_api_key")

# Natural language query
result = client.query("Get all deals from Gong this month")

# Code generation
code = client.claude.generate_code(
    prompt="Create a REST API endpoint",
    language="python",
    framework="fastapi"
)

# Infrastructure management
client.infrastructure.deploy("production")
```

### **JavaScript SDK**
```javascript
import { SophiaClient } from '@sophia-ai/sdk';

const client = new SophiaClient({ apiKey: 'your_api_key' });

// Natural language query
const result = await client.query('Show me the latest deployment status');

// Health check
const health = await client.health.check();
```

## 📚 **Additional Resources**

- **Interactive API Explorer**: https://api.sophia.ai/docs
- **Postman Collection**: [Download](https://api.sophia.ai/postman)
- **OpenAPI Specification**: [Download](https://api.sophia.ai/openapi.json)
- **Rate Limits**: 1000 requests/hour for free tier, 10000/hour for pro
- **Support**: support@sophia.ai
- **Status Page**: https://status.sophia.ai
