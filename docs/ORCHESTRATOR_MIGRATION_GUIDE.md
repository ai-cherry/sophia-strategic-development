# Orchestrator Migration Guide

**Date:** July 9, 2025  
**Version:** 1.0

## Overview

This guide helps developers migrate from the deprecated orchestrators to the new **SophiaUnifiedOrchestrator**.

## Migration Timeline

- **July 9, 2025**: Deprecation warnings added to all old orchestrators
- **July 16, 2025**: New unified orchestrator fully functional with all capabilities
- **August 1, 2025**: Old orchestrators will be removed from codebase

## What's Changing

### Old Architecture (DEPRECATED)
- 5 separate orchestrators with overlapping functionality
- Multiple entry points for similar operations
- 6+ configuration files with conflicts
- Inconsistent response formats

### New Architecture (REQUIRED)
- Single unified orchestrator: **SophiaUnifiedOrchestrator**
- One entry point for all operations
- Single configuration file: `config/sophia_mcp_unified.yaml`
- Consistent response format with metadata

## Migration Steps

### Step 1: Update Imports

#### Old Way (DEPRECATED)
```python
# UnifiedChatService
from backend.services.unified_chat_service import UnifiedChatService

# SophiaAIOrchestrator
from infrastructure.services.sophia_ai_orchestrator import SophiaAIOrchestrator

# EnhancedMultiAgentOrchestrator
from backend.services.enhanced_multi_agent_orchestrator import EnhancedMultiAgentOrchestrator

# SophiaAgentOrchestrator
from infrastructure.services.sophia_agent_orchestrator import SophiaAgentOrchestrator
```

#### New Way (REQUIRED)
```python
from backend.services.sophia_unified_orchestrator import (
    SophiaUnifiedOrchestrator,
    get_unified_orchestrator
)
```

### Step 2: Update Service Initialization

#### Old Way (DEPRECATED)
```python
# Each service had its own initialization
chat_service = UnifiedChatService()
await chat_service.initialize()

sophia_orchestrator = SophiaAIOrchestrator()
await sophia_orchestrator.initialize()

# etc...
```

#### New Way (REQUIRED)
```python
# Single service with lazy initialization
orchestrator = get_unified_orchestrator()
# No explicit initialization needed - happens automatically on first use
```

### Step 3: Update Method Calls

#### Old Way: UnifiedChatService
```python
# Old
response = await chat_service.process_query(
    query="What are our Q2 sales?",
    user_id="ceo_user",
    session_id="session_123"
)
```

#### New Way: SophiaUnifiedOrchestrator
```python
# New
response = await orchestrator.process_request(
    query="What are our Q2 sales?",
    user_id="ceo_user",
    session_id="session_123",
    context={"source": "chat"}  # Optional context
)
```

#### Old Way: SophiaAIOrchestrator
```python
# Old
from infrastructure.services.sophia_ai_orchestrator import (
    OrchestrationRequest,
    RequestType
)

request = OrchestrationRequest(
    request_type=RequestType.KNOWLEDGE_QUERY,
    query="Revenue forecast",
    user_id="ceo_user"
)
response = await sophia_orchestrator.process_request(request)
```

#### New Way: Unified
```python
# New - Simplified!
response = await orchestrator.process_request(
    query="Revenue forecast",
    user_id="ceo_user",
    session_id="session_123"
)
# Intent detection happens automatically
```

### Step 4: Handle Response Format

#### Old Response Formats (Variable)
```python
# UnifiedChatService
{
    "response": "...",
    "citations": [...],
    "metadata": {...}
}

# SophiaAIOrchestrator
{
    "content": "...",
    "confidence": 0.95,
    "sources": [...]
}
```

#### New Unified Response Format
```python
{
    "response": "The actual response text",
    "citations": [  # Optional
        {"source": "...", "content": "..."}
    ],
    "sources": ["gong", "hubspot"],  # Which MCP servers were used
    "metadata": {
        "processing_time": 0.234,
        "intent": {
            "type": "business_intelligence",
            "confidence": 0.9,
            "capabilities": ["CRM", "ANALYTICS"]
        },
        "orchestrator": "unified",
        "version": "1.0.0",
        "date": "2025-07-09T10:30:00Z",
        "health_score": 98.5
    }
}
```

## Intent Types

The unified orchestrator automatically detects intent from queries:

- **BUSINESS_INTELLIGENCE**: Revenue, sales, CRM, Gong, HubSpot queries
- **CODE_ANALYSIS**: Code review, security, quality, testing queries
- **INFRASTRUCTURE**: Deployment, servers, cloud, Docker queries
- **MEMORY_QUERY**: Previous conversations, history, context queries
- **GENERAL**: Everything else

## Configuration Migration

### Old Configuration Files (DEPRECATED)
```
config/unified_mcp_config.json
config/cursor_enhanced_mcp_config.json
config/consolidated_mcp_ports.json
config/unified_mcp_ports.json
config/mcp_server_inventory.json
```

### New Configuration File (REQUIRED)
```
config/sophia_mcp_unified.yaml
```

All MCP server configurations are now in this single file.

## Error Handling

### Old Way
```python
try:
    response = await chat_service.process_query(...)
except Exception as e:
    # Handle error
```

### New Way
```python
response = await orchestrator.process_request(...)

# Check for errors in response
if response.get("error"):
    # Handle error
    error_message = response["response"]
    # Metadata will contain error details
```

## Monitoring and Metrics

The unified orchestrator provides built-in metrics:

```python
# Get current metrics
metrics = orchestrator.get_metrics()

print(f"Requests processed: {metrics['request_count']}")
print(f"Average response time: {metrics['average_response_time']}s")
print(f"Health score: {metrics['health_score']}")
print(f"Active users: {metrics['active_users']}")
print(f"MCP server usage: {metrics['mcp_server_usage']}")
```

## Common Migration Patterns

### Pattern 1: Simple Query Processing
```python
# Old (UnifiedChatService)
response = await chat_service.process_query(query, user_id, session_id)

# New
response = await orchestrator.process_request(query, user_id, session_id)
```

### Pattern 2: Complex Orchestration
```python
# Old (Multiple orchestrators)
knowledge = await knowledge_service.query(...)
sales = await sales_coach.analyze(...)
memory = await memory_service.recall(...)

# New (Single orchestrator handles all)
response = await orchestrator.process_request(
    query="Analyze sales performance with historical context",
    user_id="ceo_user",
    session_id="session_123",
    context={
        "include_history": True,
        "analysis_depth": "detailed"
    }
)
```

### Pattern 3: Infrastructure Operations
```python
# Old (SophiaIaCOrchestrator)
# Keep using SophiaIaCOrchestrator for now - it remains separate

# Future (Phase 2)
# Infrastructure operations will be integrated into unified orchestrator
```

## Testing Your Migration

1. **Run with deprecation warnings**:
   ```bash
   python -W default::DeprecationWarning your_script.py
   ```

2. **Validate configuration**:
   ```bash
   python scripts/validate_sophia_config.py
   ```

3. **Check health status**:
   ```bash
   python scripts/sophia_health_check.py
   ```

## FAQ

**Q: Why are we consolidating orchestrators?**  
A: To reduce complexity, improve performance, and provide a single, consistent interface for all Sophia AI operations.

**Q: What happens if I don't migrate by August 1?**  
A: Your code will break when the old orchestrators are removed. Start migrating now!

**Q: Can I use both old and new orchestrators during migration?**  
A: Yes, but you'll see deprecation warnings. Both will work until August 1, 2025.

**Q: What about SophiaIaCOrchestrator?**  
A: It remains separate for now since it handles infrastructure-specific operations. It will be integrated in Phase 2.

**Q: How do I report migration issues?**  
A: Create a GitHub issue with the tag `orchestrator-migration`.

## Getting Help

- **Documentation**: See `docs/SOPHIA_AI_ORCHESTRATOR_COMPREHENSIVE_REVIEW.md`
- **Examples**: Check `examples/unified_orchestrator_examples.py`
- **Support**: Post in #sophia-ai-dev Slack channel

## Checklist

Before marking your migration complete:

- [ ] Updated all imports to use `SophiaUnifiedOrchestrator`
- [ ] Replaced all old orchestrator method calls
- [ ] Updated response handling for new format
- [ ] Removed references to old configuration files
- [ ] Tested with `validate_sophia_config.py`
- [ ] Verified no deprecation warnings in logs
- [ ] Updated any documentation referencing old orchestrators

---

Remember: The goal is a simpler, more maintainable system. If something seems more complex after migration, you might be doing it wrong. The new orchestrator should make things easier! 