# 🛠️ SOPHIA AI DEVELOPMENT GUIDE

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

## Development Workflow

### 1. Agent Development
Follow patterns in [AGENT_DEVELOPMENT.md](AGENT_DEVELOPMENT.md):

```python
from backend.agents.core.base_agent import BaseAgent

class YourAgent(BaseAgent):
    def __init__(self, config_dict: dict = None):
        super().__init__(config_dict or {
            "name": "your_agent",
            "capabilities": ["your_capability"]
        })
    
    async def _agent_initialize(self):
        # Your initialization logic
        pass
    
    async def _execute_task(self, task: Task) -> Any:
        # Your task execution logic
        pass
```

### 2. MCP Server Development
Follow patterns in [MCP_INTEGRATION.md](MCP_INTEGRATION.md) for creating new MCP servers.

### 3. Secret Management
All secrets managed through Pulumi ESC:

```python
from backend.core.auto_esc_config import config

# Access secrets
openai_key = config.openai_api_key
snowflake_account = config.snowflake_account
```

## Code Quality Standards

### Python Standards
- Python 3.11+ with type hints
- Black formatter (88 character limit)
- Async/await patterns
- Comprehensive error handling

### Performance Requirements
- Agent instantiation: <3μs
- API response: <200ms
- Health checks: 99.9% success rate

### Testing
```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_agents.py

# Health checks
python scripts/comprehensive_health_check.py
```

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
