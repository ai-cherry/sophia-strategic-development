# V0.dev MCP Server

AI-driven UI component generation server for Sophia AI, integrating V0.dev's OpenAI-compatible API to enable real-time component creation, design-to-code automation, and Vercel deployment.

## Features

- 🎨 **Component Generation**: Generate React/TypeScript components from natural language prompts
- 🎯 **Design Context Integration**: Incorporate Figma design tokens and styles
- 🔄 **Live Streaming**: Real-time component generation with live preview
- 🚀 **Vercel Deployment**: Direct deployment to Vercel projects
- 📊 **Prometheus Metrics**: Performance monitoring and analytics
- 🔐 **Pulumi ESC Integration**: Secure API key management

## Prerequisites

- Python 3.12+
- Docker (for containerized deployment)
- `VERCEL_V0DEV_API_KEY` stored in Pulumi ESC
- Access to V0.dev API endpoint

## Installation

### Local Development

```bash
# Navigate to the server directory
cd mcp-servers/v0dev

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable (for local testing only)
export SOPHIA_VERCEL_V0DEV_API_KEY="your-api-key"

# Run the server
python v0dev_mcp_server.py
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t scoobyjava15/v0dev-mcp:latest .

# Push to registry
docker push scoobyjava15/v0dev-mcp:latest

# Deploy to Docker Swarm (on Lambda Labs)
docker service create \
  --name v0dev-mcp \
  --replicas 2 \
  --publish 9030:9030 \
  --secret vercel_v0dev_api_key \
  scoobyjava15/v0dev-mcp:latest
```

## Configuration

### Pulumi ESC Setup

Add the V0.dev API key to your Pulumi ESC configuration:

```yaml
values:
  sophia:
    ai:
      vercel_v0dev_api_key: "your-v0dev-api-key"
```

### MCP Configuration

Update `cursor_enhanced_mcp_config.json`:

```json
{
  "mcpServers": {
    "v0dev": {
      "command": "docker",
      "args": ["run", "-p", "9030:9030", "scoobyjava15/v0dev-mcp:latest"],
      "env": {
        "SOPHIA_VERCEL_V0DEV_API_KEY": "${env:VERCEL_V0DEV_API_KEY}"
      }
    }
  }
}
```

## API Endpoints

### Health Check
```bash
curl http://localhost:9030/health
```

### Generate Component
```bash
curl -X POST http://localhost:9030/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a modern card component with title, description, and action button",
    "design_context": {
      "colors": {"primary": "#3B82F6", "secondary": "#1F2937"},
      "typography": {"heading": "font-bold text-2xl", "body": "text-gray-600"}
    },
    "styling": "tailwind",
    "typescript": true,
    "include_tests": true
  }'
```

### Stream Component (SSE)
```bash
curl -X POST http://localhost:9030/api/v1/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "prompt": "Create a data table with sorting and filtering",
    "design_context": {...}
  }'
```

### Deploy Component
```bash
curl -X POST http://localhost:9030/api/v1/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "sophia-ai-ui",
    "component_code": "...",
    "component_name": "DataTable",
    "branch": "feature/ui"
  }'
```

## MCP Tools

The server exposes the following MCP tools:

### generateComponent
Generate a UI component from a natural language prompt.

```typescript
{
  prompt: string;
  design_context?: {
    colors?: Record<string, string>;
    typography?: Record<string, string>;
    spacing?: Record<string, string>;
    components?: string[];
  };
}
```

### streamComponent
Stream component generation for live preview.

```typescript
{
  prompt: string;
  design_context?: DesignContext;
}
```

### deployComponent
Deploy a generated component to Vercel.

```typescript
{
  project_id: string;
  component_code: string;
  component_name: string;
}
```

## Integration with Sophia AI

### Backend Orchestrator

The V0.dev MCP server integrates with the Sophia Unified Chat Service:

```python
# In SophiaUnifiedChatService
if intent == "UI_GENERATION":
    result = await self.mcp_client.call_tool(
        server="v0dev",
        tool="generateComponent",
        arguments={
            "prompt": user_message,
            "design_context": figma_context
        }
    )
```

### Frontend Integration

```typescript
// In EnhancedUnifiedChat component
const generateComponent = async (prompt: string) => {
  const response = await fetch('/api/v1/chat', {
    method: 'POST',
    body: JSON.stringify({
      message: `Generate UI: ${prompt}`,
      intent: 'UI_GENERATION'
    })
  });
  
  const result = await response.json();
  setGeneratedComponent(result.component_code);
};
```

## Monitoring

### Prometheus Metrics

- `v0dev_component_generations_total`: Total component generation requests
- `v0dev_component_generation_duration_seconds`: Generation duration histogram
- `v0dev_api_errors_total`: API error counter

Access metrics at: `http://localhost:9030/metrics`

### Grafana Dashboard

Import the V0.dev dashboard from `monitoring/dashboards/v0dev-dashboard.json`

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `VERCEL_V0DEV_API_KEY` is set in Pulumi ESC
   - Check GitHub Actions secrets sync
   - Verify Docker secret mounting

2. **Connection Timeout**
   - Check V0.dev API status
   - Verify network connectivity from Lambda Labs
   - Review firewall rules

3. **Component Generation Fails**
   - Check API response in logs
   - Verify prompt length (max 4000 tokens)
   - Ensure design context is valid JSON

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG python v0dev_mcp_server.py
```

## Development

### Running Tests

```bash
pytest tests/test_v0dev_mcp_server.py -v
```

### Code Quality

```bash
# Linting
ruff check v0dev_mcp_server.py

# Type checking
mypy v0dev_mcp_server.py

# Format code
black v0dev_mcp_server.py
```

## License

Part of Sophia AI Platform - Enterprise License 