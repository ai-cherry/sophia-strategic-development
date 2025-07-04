# Phase 2.5 Integration Notes

## Existing Components to Integrate With

### 1. **Cortex Services**
- **Existing**: `SnowflakeCortexService` - Direct Cortex API operations
- **New**: `CortexRouter` - Intelligent model selection
- **Integration**: CortexRouter will use SnowflakeCortexService for actual API calls

```python
# In CortexRouter
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

class CortexRouter:
    def __init__(self):
        self.cortex_service = SnowflakeCortexService()

    async def execute_with_routing(self, query, model, temperature):
        # Use the existing service for actual execution
        return await self.cortex_service.complete_text_with_cortex(
            prompt=query,
            model=model,
            temperature=temperature
        )
```

### 2. **Memory Services**
- **Existing**:
  - `Mem0IntegrationService` - Full Mem0 integration
  - `ComprehensiveMemoryService` - Comprehensive memory management
  - `MockMem0Service` - Local development mock
- **Plan**: Use existing `Mem0IntegrationService` instead of creating new

### 3. **Chat Services**
- **Existing**:
  - `EnhancedUnifiedChatService` (backend)
  - `EnhancedUnifiedChat.tsx` (frontend)
- **Plan**: Enhance existing components with citation support

### 4. **Frontend Structure**
- **Dashboard**: `UnifiedDashboard.tsx` - The ONLY dashboard
- **Chat**: `EnhancedUnifiedChat.tsx` - The ONLY chat interface
- **Rule**: Never create new dashboards or chat interfaces

## Integration Points

### Backend Integration

```python
# backend/services/enhanced_unified_chat_service.py
from .citation_service import CitationService
from .cortex_router import CortexRouter
from .mem0_integration_service import get_mem0_service

class EnhancedUnifiedChatService(UnifiedChatService):
    def __init__(self):
        super().__init__()
        self.citation_service = CitationService()
        self.cortex_router = CortexRouter()
        self.memory_service = get_mem0_service()
```

### Frontend Integration

```typescript
// frontend/src/components/shared/EnhancedUnifiedChat.tsx
import { CitationSidebar, MessageWithCitations } from '../Citations';
import { IceBreakerPrompts } from '../IceBreakerPrompts';

// Add to existing component
```

## Next Steps

1. **Hour 5**: Integrate with existing Mem0IntegrationService
2. **Hour 6**: Enhance existing EnhancedUnifiedChat with citations
3. **Hour 7**: Update existing API routes
4. **Hour 8**: Test integration

## Important Rules

1. **NO NEW DASHBOARDS** - Only extend UnifiedDashboard.tsx
2. **NO NEW CHAT SERVICES** - Only enhance existing ones
3. **USE EXISTING MEMORY** - Don't create duplicate memory services
4. **INTEGRATE, DON'T DUPLICATE** - Always check for existing components first
