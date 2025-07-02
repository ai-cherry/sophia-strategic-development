# 🔄 SOPHIA AI MCP INTEGRATION GUIDE

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

## MCP Integration

### Agent Integration
All agents inherit from `BaseAgent` class providing:
- Standardized task execution
- Health monitoring
- Performance tracking
- Configuration management

### MCP Server Integration
Model Context Protocol servers handle all external integrations:
- Standardized interface
- Health monitoring
- Port management
- Tool schemas

### Data Flow
1. External data → MCP servers → Structured storage
2. User queries → Agent orchestration → Data retrieval
3. AI processing → Response generation → User interface

For detailed MCP integration patterns, see [AGENT_DEVELOPMENT.md](AGENT_DEVELOPMENT.md).

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
