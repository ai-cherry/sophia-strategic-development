# 📅 SOPHIA AI CHANGELOG

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

## CHANGELOG

### Quick Start
- **New Features**:
  - Added new agent type: **SpecializedAgent**
  - Implemented new MCP server: **Snowflake Admin**
- **Improvements**:
  - Optimized agent deployment process
  - Improved MCP server connection stability
- **Bug Fixes**:
  - Fixed issue with cursor AI integration

### Detailed Changes
- **New Features**:
  - Added new agent type: **SpecializedAgent**
  - Implemented new MCP server: **Snowflake Admin**
- **Improvements**:
  - Optimized agent deployment process
  - Improved MCP server connection stability
- **Bug Fixes**:
  - Fixed issue with cursor AI integration

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

For more detailed CHANGELOG, see [AGENT_DEVELOPMENT.md](AGENT_DEVELOPMENT.md) and [MCP_INTEGRATION.md](MCP_INTEGRATION.md).
