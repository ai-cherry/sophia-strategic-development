# Unified Chat API Reference

> Documentation for the consolidated chat API system introduced in July 2025

## Overview

The Unified Chat API consolidates all chat functionality into a single, modular system that supports multiple chat modes through one endpoint. This replaces the previous fragmented implementation with separate endpoints for each chat type.

## Architecture

### API Structure
```
/api/v1/chat - Main unified endpoint
├── POST /chat - Process chat request
├── GET /chat/sessions/{session_id} - Get session info
├── DELETE /chat/sessions/{session_id} - Delete session
├── GET /chat/sessions - List sessions
└── GET /chat/health - Health check
```

### Deprecated Endpoints (Still Supported)
- `/api/v1/sophia-universal-chat` → Use `/api/v1/chat` with mode="sophia"
- `/api/v1/universal-chat` → Use `/api/v1/chat` with mode="universal"
- `/api/v1/enhanced-ceo-chat` → Use `/api/v1/chat` with mode="executive"

## Chat Modes

### Unified Mode
- **Purpose**: Basic chat functionality
- **Provider**: OpenAI (default)
- **Use Case**: General conversations and queries

### Sophia Mode
- **Purpose**: Full Sophia AI capabilities
- **Features**: Business intelligence, data analysis, strategic insights
- **Provider**: OpenAI or configured provider
- **Use Case**: Advanced business analysis and AI assistance

### Executive Mode
- **Purpose**: Unified/executive-focused chat
- **Features**: High-level strategic insights, board-ready summaries
- **Provider**: Portkey (recommended)
- **Use Case**: Executive decision support and strategic planning

## API Endpoints

### POST /api/v1/chat

Process a chat request using the appropriate mode and provider.

**Request Body:**
```json
{
  "message": "string",
  "mode": "universal" | "sophia" | "executive",
  "session_id": "string (optional)",
  "context": {
    "key": "value"
  },
  "user_role": "string (optional)",
  "provider": "openai" | "portkey" | "anthropic",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "response": "AI response content",
  "session_id": "uuid",
  "mode": "sophia",
  "provider": "openai",
  "metadata": {
    "response_type": "sophia",
    "features": ["business_intelligence", "data_analysis"],
    "sophia_version": "2.1.0"
  },
  "suggestions": [
    "Follow-up question 1",
    "Follow-up question 2"
  ],
  "timestamp": "2025-07-01T10:00:00Z",
  "tokens_used": 120,
  "cost": 0.003
}
```

### GET /api/v1/chat/sessions/{session_id}

Retrieve information about a specific chat session.

**Response:**
```json
{
  "session_id": "uuid",
  "mode": "sophia",
  "created_at": "2025-07-01T09:00:00Z",
  "last_activity": "2025-07-01T10:00:00Z",
  "message_count": 5,
  "total_tokens": 500,
  "total_cost": 0.015
}
```

### GET /api/v1/chat/sessions

List all chat sessions with pagination.

**Query Parameters:**
- `limit`: Number of sessions to return (default: 10)
- `offset`: Starting position (default: 0)

### DELETE /api/v1/chat/sessions/{session_id}

Delete a specific chat session.

**Response:**
```json
{
  "message": "Session {session_id} deleted successfully"
}
```

### GET /api/v1/chat/health

Check the health status of all chat services.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-01T10:00:00Z",
  "modes": ["universal", "sophia", "executive"],
  "providers": ["openai", "portkey", "anthropic"],
  "version": "2.0.0"
}
```

## Service Architecture

### Modular Services
```
backend/services/chat/
├── __init__.py               # Service exports
├── base_chat_service.py      # Abstract base class
├── unified_chat_service.py   # Main orchestrator
├── session_manager.py        # Session management
├── context_manager.py        # Context handling
├── sophia_chat_service.py    # Sophia mode (planned)
├── executive_chat_service.py # Executive mode (planned)
└── universal_chat_service.py # Unified mode (planned)
```

*Note: Mode-specific service implementations are currently using mock services while the actual implementations are being migrated to the new architecture.*

### Service Features
- **Dependency Injection**: Services are injected at runtime
- **Session Persistence**: Conversations maintained across requests
- **Context Management**: Business context integrated into responses
- **Error Handling**: Comprehensive error handling and graceful degradation
- **Performance Monitoring**: Built-in timing and metrics

## Integration Examples

### Python Example
```python
import requests

# Unified chat request
response = requests.post(
    "https://api.sophia-intel.ai/api/v1/chat",
    json={
        "message": "Analyze our Q3 revenue performance",
        "mode": "sophia",
        "provider": "openai",
        "context": {
            "user_department": "finance",
            "data_access": ["revenue", "sales"]
        }
    }
)

result = response.json()
print(result["response"])
```

### JavaScript Example
```javascript
const response = await fetch('https://api.sophia-intel.ai/api/v1/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Generate executive summary for board meeting',
    mode: 'executive',
    provider: 'portkey'
  })
});

const result = await response.json();
console.log(result.response);
```

## Migration Guide

### From Legacy Endpoints

Replace legacy endpoint calls with the unified endpoint:

**Before:**
```python
# Sophia Unified Chat
requests.post("/api/v1/sophia-universal-chat", {...})

# Enhanced Unified Chat
requests.post("/api/v1/enhanced-ceo-chat", {...})
```

**After:**
```python
# Unified endpoint with mode parameter
requests.post("/api/v1/chat", {
    "mode": "sophia",  # or "executive"
    ...
})
```

## Best Practices

1. **Always specify mode**: Even though "universal" is default, explicitly set the mode
2. **Use session IDs**: Maintain conversation context with session IDs
3. **Handle errors**: Implement proper error handling for failed requests
4. **Monitor costs**: Track token usage and costs through response metadata
5. **Use appropriate providers**: Executive mode works best with Portkey

## Performance Considerations

- **Response Times**: <200ms for most requests
- **Token Limits**: 4000 tokens max per request
- **Rate Limiting**: 100 requests per minute per API key
- **Session Timeout**: Sessions expire after 24 hours of inactivity

## Security

- All endpoints require authentication
- Session data is encrypted at rest
- PII is automatically redacted from logs
- Role-based access control for executive mode

---

*Last Updated: July 2025*  
*API Version: 2.0.0* 