# Phase 2.5: Hours 5-8 Implementation Plan

## Hour 5: Memory Service Integration (Not Skeleton!)

Since we discovered existing memory services, we'll INTEGRATE, not create new.

### Tasks:

1. **Enhance Existing Mem0IntegrationService**
   ```python
   # backend/services/mem0_integration_service_enhanced.py
   from backend.services.mem0_integration_service import Mem0IntegrationService
   
   class EnhancedMem0Service(Mem0IntegrationService):
       async def store_conversation_with_citations(
           self,
           user_id: str,
           conversation: dict,
           citations: List[Citation]
       ):
           """Store conversation with citation context"""
           
       async def get_relevant_memories_for_query(
           self,
           user_id: str,
           query: str,
           include_citations: bool = True
       ):
           """Get memories relevant to query with citations"""
   ```

2. **Add Citation-Aware Memory Categories**
   ```python
   # Add to existing memory categories
   CITATION_MEMORY_CATEGORIES = [
       "cited_sources",
       "trusted_documents",
       "frequently_referenced",
       "fact_checked_claims"
   ]
   ```

3. **Create Memory-Citation Bridge**
   ```python
   # backend/services/memory_citation_bridge.py
   class MemoryCitationBridge:
       def __init__(self):
           self.memory_service = get_mem0_service()
           self.citation_service = CitationService()
           
       async def process_and_store(self, conversation, citations):
           # Extract key facts from cited sources
           # Store in memory with source tracking
   ```

## Hour 6: Enhanced Chat Integration

### Tasks:

1. **Update EnhancedUnifiedChat.tsx**
   ```typescript
   // frontend/src/components/shared/EnhancedUnifiedChat.tsx
   import { CitationSidebar, MessageWithCitations } from '../Citations';
   import { IceBreakerPrompts } from '../IceBreakerPrompts';
   
   // Add to existing component:
   const [citations, setCitations] = useState<Citation[]>([]);
   const [showCitations, setShowCitations] = useState(true);
   const [focusMode, setFocusMode] = useState<'business' | 'code' | 'data'>('business');
   const [showIceBreakers, setShowIceBreakers] = useState(true);
   ```

2. **Add Focus Mode Selector**
   ```typescript
   const FocusModeSelector = () => (
     <div className="flex space-x-2 mb-4">
       <button
         onClick={() => setFocusMode('business')}
         className={`px-4 py-2 rounded ${
           focusMode === 'business' ? 'bg-blue-600 text-white' : 'bg-gray-200'
         }`}
       >
         Business Intelligence
       </button>
       <button onClick={() => setFocusMode('code')}>Code Assistant</button>
       <button onClick={() => setFocusMode('data')}>Data Analysis</button>
     </div>
   );
   ```

3. **Integrate Citation Display**
   ```typescript
   // Update message rendering
   {messages.map((message) => (
     <MessageWithCitations
       key={message.id}
       content={message.content}
       citations={message.citations || []}
       onCitationClick={handleCitationClick}
     />
   ))}
   
   // Add citation sidebar
   <CitationSidebar
     citations={citations}
     isOpen={showCitations}
     onToggle={() => setShowCitations(!showCitations)}
     highlightedCitation={highlightedCitationId}
   />
   ```

## Hour 7: API Routes Enhancement

### Tasks:

1. **Update Existing Chat Routes**
   ```python
   # backend/api/unified_routes.py
   from backend.services.citation_service import CitationService
   from backend.services.cortex_router import CortexRouter
   
   @router.post("/chat/message")
   async def chat_message_with_citations(
       request: ChatRequest,
       chat_service: EnhancedUnifiedChatService = Depends(get_chat_service),
       citation_service: CitationService = Depends(get_citation_service),
       cortex_router: CortexRouter = Depends(get_cortex_router)
   ):
       # Route to appropriate model
       model, temperature, routing_metadata = await cortex_router.route_request(
           request.message,
           intent=request.intent,
           complexity=request.complexity
       )
       
       # Process with citations
       response = await chat_service.process_message(
           request.message,
           model=model,
           temperature=temperature,
           focus_mode=request.focus_mode
       )
       
       # Extract citations
       formatted_response, citations = await citation_service.extract_citations(
           response.content,
           response.sources
       )
       
       return {
           "response": formatted_response,
           "citations": citation_service.format_citations_for_display(citations),
           "routing_metadata": routing_metadata
       }
   ```

2. **Add Model Routing Endpoint**
   ```python
   @router.post("/chat/route")
   async def route_query(
       query: str,
       cortex_router: CortexRouter = Depends(get_cortex_router)
   ):
       """Preview routing decision without executing"""
       model, temperature, metadata = await cortex_router.route_request(query)
       return {
           "recommended_model": model.value,
           "temperature": temperature,
           "metadata": metadata
       }
   ```

3. **Add Citation Management Endpoints**
   ```python
   @router.get("/citations/stats")
   async def get_citation_stats(
       citation_service: CitationService = Depends(get_citation_service)
   ):
       return citation_service.get_statistics()
   
   @router.post("/citations/verify")
   async def verify_citations(
       citations: List[dict],
       citation_service: CitationService = Depends(get_citation_service)
   ):
       # Verify citations against sources
       pass
   ```

## Hour 8: Testing & Validation

### Tasks:

1. **Test Citation Extraction**
   ```python
   # tests/test_citation_extraction.py
   async def test_citation_extraction():
       service = CitationService()
       
       # Test with inline citations
       response = "This is based on [cite:source1:title1] data."
       formatted, citations = await service.extract_citations(response)
       assert "[1]" in formatted
       assert len(citations) == 1
       
       # Test with source documents
       sources = [{"id": "1", "title": "Test Doc", "content": "..."}]
       formatted, citations = await service.extract_citations(response, sources)
       assert len(citations) == 2
   ```

2. **Test Model Routing**
   ```python
   # tests/test_cortex_routing.py
   async def test_model_routing():
       router = CortexRouter()
       
       # Test simple query
       model, temp, _ = await router.route_request("What is 2+2?")
       assert model == ModelType.MISTRAL_7B
       
       # Test complex query
       model, temp, _ = await router.route_request(
           "Implement a distributed cache with Redis"
       )
       assert model == ModelType.LLAMA3_70B
       
       # Test cost constraints
       model, temp, _ = await router.route_request(
           "Complex analysis",
           max_cost=0.20
       )
       assert model != ModelType.SNOWFLAKE_ARCTIC
   ```

3. **Integration Test**
   ```python
   # tests/test_chat_integration.py
   async def test_full_chat_flow():
       # Test complete flow from UI to response
       response = await client.post("/api/chat/message", json={
           "message": "What were our top revenue drivers?",
           "focus_mode": "business"
       })
       
       assert response.status_code == 200
       data = response.json()
       assert "response" in data
       assert "citations" in data
       assert len(data["citations"]) > 0
   ```

## Success Criteria

### Hour 5 ✓
- [ ] Enhanced Mem0 service with citation support
- [ ] Memory-citation bridge operational
- [ ] Citation categories added to memory

### Hour 6 ✓
- [ ] Citations integrated into EnhancedUnifiedChat
- [ ] Focus mode selector working
- [ ] Ice breaker prompts showing

### Hour 7 ✓
- [ ] /api/chat/message returns citations
- [ ] Model routing endpoint working
- [ ] Citation stats endpoint operational

### Hour 8 ✓
- [ ] All citation extraction tests pass
- [ ] Model routing tests pass
- [ ] End-to-end integration test passes

## Important Notes

1. **NO NEW SERVICES** - Enhance existing ones
2. **USE EXISTING COMPONENTS** - Don't recreate
3. **TEST AS YOU GO** - Don't wait until hour 8
4. **INTEGRATE GRADUALLY** - Small, working changes

## Dependencies

- Existing `Mem0IntegrationService`
- Existing `EnhancedUnifiedChatService`
- Existing `EnhancedUnifiedChat.tsx`
- New `CitationService` (already created)
- New `CortexRouter` (already created) 