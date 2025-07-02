# 🤖 SOPHIA AI AGENT DEVELOPMENT GUIDE

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- UV package manager
- Cursor AI IDE (recommended)

### Setup
```bash
# Clone repository
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main

# Install dependencies
uv sync

# Configure environment
export ENVIRONMENT=prod
export PULUMI_ORG=scoobyjava-org

# Start services
python scripts/run_all_mcp_servers.py
uvicorn backend.app.fastapi_app:app --reload --port 8000
```

## Agent Development

### Agent Types
- **BaseAgent**: Standardized task execution
- **SpecializedAgent**: Customized for specific business functions

### Development Workflow
1. **Agent Creation**: Define agent capabilities and configuration
2. **Agent Implementation**: Implement agent logic
3. **Agent Deployment**: Deploy agent to MCP servers

### Agent Types
- **BaseAgent**: Standardized task execution
- **SpecializedAgent**: Customized for specific business functions

### Development Workflow
1. **Agent Creation**: Define agent capabilities and configuration
2. **Agent Implementation**: Implement agent logic
3. **Agent Deployment**: Deploy agent to MCP servers

## MCP Server Development

### MCP Server Types
- **AI Memory**: Structured storage and data retrieval
- **Snowflake Admin**: Data management and analysis
- **Gong Intelligence**: Sales intelligence and CRM integration
- **HubSpot CRM**: Customer relationship management
- **Slack Integration**: Communication and project management
- **Linear Projects**: Linear project management and integration

### Development Workflow
1. **MCP Server Creation**: Define server capabilities and configuration
2. **MCP Server Implementation**: Implement server logic
3. **MCP Server Deployment**: Deploy server to MCP network

## Cursor AI Integration

### Configuration
Update `.cursor/mcp_servers.json`:
```json
{
  "mcpServers": {
    "ai_memory": {
      "command": "python",
      "args": ["backend/mcp_servers/ai_memory_mcp_server.py"],
      "env": {"PORT": "9000"}
    }
  }
}
```

### Natural Language Commands
- "Show agent status" → Health checks
- "Analyze business data" → Complex workflows
- "Deploy changes" → Autonomous operations

For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
