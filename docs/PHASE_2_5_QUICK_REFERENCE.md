# Phase 2.5 Quick Reference Guide

## 🎯 Core Principle: INTEGRATE, DON'T DUPLICATE

## Hour 5: Memory Integration (45 min)

### Files to Modify/Create:
1. `backend/services/mem0_integration_service_enhanced.py` (NEW - extends existing)
2. `backend/services/memory_citation_bridge.py` (NEW)

### Key Code:
```python
# Extend existing service
from backend.services.mem0_integration_service import Mem0IntegrationService

class EnhancedMem0Service(Mem0IntegrationService):
    # Add citation-aware methods
```

### Checklist:
- [ ] Import existing Mem0IntegrationService
- [ ] Add citation storage methods
- [ ] Create memory-citation bridge
- [ ] Test memory storage with citations

## Hour 6: Frontend Integration (45 min)

### Files to Modify:
1. `frontend/src/components/shared/EnhancedUnifiedChat.tsx` (MODIFY existing)

### Key Imports:
```typescript
import { CitationSidebar, MessageWithCitations } from '../Citations';
import { IceBreakerPrompts } from '../IceBreakerPrompts';
```

### State to Add:
```typescript
const [citations, setCitations] = useState<Citation[]>([]);
const [showCitations, setShowCitations] = useState(true);
const [focusMode, setFocusMode] = useState<'business' | 'code' | 'data'>('business');
```

### Checklist:
- [ ] Import citation components
- [ ] Add citation state
- [ ] Add focus mode selector
- [ ] Integrate ice breaker prompts
- [ ] Update message rendering

## Hour 7: API Routes (45 min)

### Files to Modify:
1. `backend/api/unified_routes.py` (MODIFY existing)

### Key Dependencies:
```python
from backend.services.citation_service import CitationService
from backend.services.cortex_router import CortexRouter
```

### Endpoints to Add/Modify:
- `POST /api/chat/message` - Add citation support
- `POST /api/chat/route` - Preview routing
- `GET /api/citations/stats` - Citation statistics

### Checklist:
- [ ] Update chat message endpoint
- [ ] Add routing preview endpoint
- [ ] Add citation stats endpoint
- [ ] Test with curl/httpie

## Hour 8: Testing (45 min)

### Test Files to Create:
1. `tests/test_citation_extraction.py`
2. `tests/test_cortex_routing.py`
3. `tests/test_chat_integration.py`

### Quick Test Commands:
```bash
# Test citation extraction
pytest tests/test_citation_extraction.py -v

# Test model routing
pytest tests/test_cortex_routing.py -v

# Test full integration
pytest tests/test_chat_integration.py -v

# Manual API test
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "What were our top revenue drivers?", "focus_mode": "business"}'
```

### Checklist:
- [ ] Citation extraction tests pass
- [ ] Model routing tests pass
- [ ] Integration test passes
- [ ] Manual API test works

## 🚨 Common Pitfalls to Avoid

1. **Creating New Services**: Use existing ones!
   - ❌ `class NewMemoryService`
   - ✅ `class EnhancedMem0Service(Mem0IntegrationService)`

2. **Creating New Dashboards**: Modify existing!
   - ❌ `NewChatInterface.tsx`
   - ✅ Modify `EnhancedUnifiedChat.tsx`

3. **Ignoring Existing Patterns**: Follow established patterns!
   - Check how existing services handle dependencies
   - Use existing error handling patterns

## 🔧 Debugging Tips

### If Memory Service Fails:
```python
# Check if Mem0 is running
from backend.services.mem0_integration_service import get_mem0_service
service = get_mem0_service()
print(service.initialized)
```

### If Frontend Doesn't Update:
```bash
# Clear cache and rebuild
rm -rf frontend/.next
npm run dev
```

### If API Routes 404:
```python
# Check route registration
from backend.api import unified_routes
print(unified_routes.router.routes)
```

## 📋 Final Validation

Before considering complete:
1. Can you send a message and see citations?
2. Does focus mode change the response style?
3. Do ice breaker prompts appear for new conversations?
4. Does the model routing show in response metadata?
5. Are citations stored in memory for future reference?

## 🎉 Success Indicators

- Chat shows numbered citations [1], [2]
- Citation sidebar displays source details
- Focus mode selector changes response style
- Ice breakers help start conversations
- Model routing saves costs
- Memories include citation context 