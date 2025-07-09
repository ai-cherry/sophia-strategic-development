# MCP Server Quick Start Guide

## 🚀 Create Your First Production MCP Server in 5 Minutes

### Step 1: Generate the Server Scaffold

```bash
# Create a new MCP server (e.g., for Slack integration)
python scripts/scaffold_mcp_server.py slack

# Output:
# ✅ Created slack MCP server on port 9002
# 📁 Files created at infrastructure/mcp_servers/slack/
```

### Step 2: Customize the Business Logic

Edit `infrastructure/mcp_servers/slack/handlers/main_handler.py`:

```python
class SlackHandler:
    """Handler for Slack operations."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None

    async def initialize(self):
        """Initialize Slack client."""
        from slack_sdk.web.async_client import AsyncWebClient
        self.client = AsyncWebClient(token=self.api_key)

    async def send_message(self, channel: str, text: str):
        """Send a message to Slack."""
        response = await self.client.chat_postMessage(
            channel=channel,
            text=text
        )
        return response["ts"]  # Message timestamp

    async def sync_data(self, batch_size: int = 100):
        """Sync recent messages."""
        # Get conversations
        conversations = await self.client.conversations_list()

        messages_synced = 0
        for channel in conversations["channels"][:batch_size]:
            # Get messages from each channel
            history = await self.client.conversations_history(
                channel=channel["id"],
                limit=10
            )
            messages_synced += len(history["messages"])

        return {
            "status": "success",
            "records_synced": messages_synced
        }
```

### Step 3: Add Data Models

Edit `infrastructure/mcp_servers/slack/models/data_models.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class SlackMessage(BaseModel):
    """Slack message model."""
    ts: str = Field(..., description="Message timestamp ID")
    channel: str = Field(..., description="Channel ID")
    user: str = Field(..., description="User ID")
    text: str = Field(..., description="Message text")
    thread_ts: Optional[str] = Field(None, description="Thread timestamp")

class SlackChannel(BaseModel):
    """Slack channel model."""
    id: str = Field(..., description="Channel ID")
    name: str = Field(..., description="Channel name")
    is_private: bool = Field(False, description="Is private channel")
    members: List[str] = Field(default_factory=list, description="Member IDs")
```

### Step 4: Configure Environment

Create `.env` file (copy from `.env.example`):

```bash
# Slack MCP Server Configuration
SLACK_PORT=9002
SLACK_LOG_LEVEL=INFO
SLACK_API_KEY=xoxb-your-slack-bot-token
SLACK_ENABLE_METRICS=true
```

### Step 5: Run the Server

#### Option A: Direct Python
```bash
cd infrastructure/mcp_servers/slack
pip install -r requirements.txt
python -m server
```

#### Option B: Docker
```bash
cd infrastructure/mcp_servers/slack
docker-compose up --build
```

### Step 6: Test the Server

```bash
# Health check
curl http://localhost:9002/health

# View API docs
open http://localhost:9002/docs

# Trigger sync
curl -X POST http://localhost:9002/sync

# Send a test message
curl -X POST http://localhost:9002/api/send \
  -H "Content-Type: application/json" \
  -d '{"channel": "#test", "text": "Hello from MCP!"}'
```

## 🎯 Production Deployment

### 1. Build Docker Image
```bash
docker build -t scoobyjava15/slack-mcp:latest .
docker push scoobyjava15/slack-mcp:latest
```

### 2. Deploy to Lambda Labs
```bash
# SSH to Lambda Labs
ssh ubuntu@192.222.58.232

# Deploy with Docker Swarm
docker stack deploy -c docker-compose.production.yml slack-mcp
```

### 3. Monitor
- Metrics: `http://192.222.58.232:9002/metrics`
- Health: `http://192.222.58.232:9002/health`
- Logs: `docker service logs slack-mcp_slack`

## 📊 Available Endpoints

Every MCP server automatically gets:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with component status |
| `/capabilities` | GET | Server capabilities (self-knowledge) |
| `/features` | GET | Available features and configuration |
| `/sync` | POST | Trigger data synchronization |
| `/data` | GET | Get paginated data |
| `/docs` | GET | OpenAPI documentation |
| `/redoc` | GET | ReDoc documentation |
| `/metrics` | GET | Prometheus metrics |

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# Coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Example Test
```python
# tests/unit/test_handler.py
@pytest.mark.asyncio
async def test_send_message():
    handler = SlackHandler(api_key="test")
    handler.client = AsyncMock()
    handler.client.chat_postMessage.return_value = {"ts": "123.456"}

    result = await handler.send_message("#test", "Hello")

    assert result == "123.456"
    handler.client.chat_postMessage.assert_called_once()
```

## 🔧 Advanced Features

### 1. Add Custom Endpoints

In `server.py`:
```python
def _add_custom_routes(self):
    """Add Slack-specific routes."""
    self.app.add_api_route(
        "/api/send",
        self.send_message_endpoint,
        methods=["POST"],
        summary="Send Slack message"
    )

async def send_message_endpoint(self, channel: str, text: str):
    """Send a message to Slack."""
    ts = await self.handler.send_message(channel, text)
    return {"success": True, "timestamp": ts}
```

### 2. Add Scheduled Tasks

```python
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def server_specific_init(self):
    # ... existing init code ...

    # Setup scheduler
    self.scheduler = AsyncIOScheduler()
    self.scheduler.add_job(
        self.sync_data,
        'interval',
        minutes=30,
        id='sync_job'
    )
    self.scheduler.start()
```

### 3. Add WebSocket Support

```python
from fastapi import WebSocket

@self.app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Process and respond
        await websocket.send_text(f"Echo: {data}")
```

## 🎉 That's It!

You now have a production-ready MCP server with:
- ✅ Async/await architecture
- ✅ Health monitoring
- ✅ Prometheus metrics
- ✅ JSON logging
- ✅ Docker support
- ✅ Comprehensive testing
- ✅ Auto-generated documentation

Next steps:
1. Implement your specific business logic
2. Add integration tests
3. Deploy to staging
4. Monitor metrics
5. Deploy to production
