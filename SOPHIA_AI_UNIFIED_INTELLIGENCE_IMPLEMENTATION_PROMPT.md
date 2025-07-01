# Sophia AI Unified Intelligence Implementation Prompt

## OBJECTIVE
Implement intelligent enhancements to Sophia AI that seamlessly integrate with the existing Universal Chat Interface and CEO Dashboard, creating a unified executive intelligence experience.

## CRITICAL CONTEXT
- Sophia AI has 100% infrastructure readiness with enterprise-grade CI/CD
- Existing system has 98/100 production readiness with unified orchestration
- Core value: Cross-domain synthesis for executive decision support
- **DO NOT** break existing unified architecture - enhance it

## IMPLEMENTATION PHASES

### PHASE 1: Enhanced Group-Aware Orchestration with Chat/Dashboard Integration

**File:** `backend/services/enhanced_group_aware_orchestration.py`

```python
class EnhancedGroupAwareOrchestration(MCPOrchestrationService):
    """Enhanced orchestration that updates both chat and dashboard"""
    
    async def execute_group_aware_task(self, task: BusinessTask) -> OrchestrationResult:
        # Group-aware execution
        result = await super().execute_business_task(task)
        
        # Auto-update dashboard widgets based on task type
        if task.updates_dashboard:
            await self._update_dashboard_widgets(result)
            
        # Generate chat-friendly response
        result.chat_message = await self._generate_executive_summary(result)
        
        return result
```

**File:** `config/mcp_server_groups.json`
- Define 5 logical groups: sophia_core, business_intelligence, ai_orchestration, data_platform, development_tools
- Each group includes dashboard_widgets and chat_capabilities properties

### PHASE 2: Advanced NLP Query Processing for Universal Chat

**File:** `backend/services/advanced_nlp_query_processor.py`

```python
class AdvancedNLPQueryProcessor:
    """Processes natural language queries from chat interface"""
    
    async def parse_executive_query(self, query: str, context: UserContext) -> ParsedQuery:
        # Parse intent and required capabilities
        intent = await self._classify_intent(query)
        
        # Map to dashboard widgets that need updating
        dashboard_targets = await self._identify_dashboard_targets(intent)
        
        # Determine if predictive analysis needed
        requires_prediction = await self._check_predictive_requirements(intent)
        
        return ParsedQuery(
            intent=intent,
            capabilities=capabilities,
            dashboard_targets=dashboard_targets,
            requires_prediction=requires_prediction
        )
```

### PHASE 3: Enhanced Unified Chat Service

**File:** `backend/services/enhanced_unified_chat_service.py`

```python
class EnhancedUnifiedChatService(UnifiedChatService):
    """Chat service that orchestrates all intelligent features"""
    
    async def process_executive_query(self, query: str, user_context: UserContext) -> ChatResponse:
        # 1. Parse with NLP
        parsed = await self.nlp_processor.parse_executive_query(query, user_context)
        
        # 2. Execute with group-aware orchestration
        result = await self.group_orchestrator.execute_group_aware_task(
            BusinessTask.from_parsed_query(parsed)
        )
        
        # 3. Get predictions if needed
        if parsed.requires_prediction:
            predictions = await self.predictive_engine.generate_predictions(parsed)
            
        # 4. Update CEO Dashboard
        await self._update_ceo_dashboard(result, predictions)
        
        # 5. Return unified response
        return ChatResponse(
            message=result.chat_message,
            data=result.data,
            dashboard_updates=result.dashboard_updates,
            predictions=predictions,
            suggested_queries=self._generate_follow_up_queries(result)
        )
```

### PHASE 4: CEO Dashboard Integration

**File:** `frontend/src/components/dashboard/EnhancedCEODashboard.tsx`

```typescript
const EnhancedCEODashboard: React.FC = () => {
    // Embedded chat interface
    const EmbeddedChat = () => (
        <div className="chat-widget">
            <UniversalChatInterface
                mode="embedded"
                onQueryResult={updateDashboardFromChat}
                suggestions={contextualSuggestions}
            />
        </div>
    );
    
    // Dashboard widgets that update from chat
    const updateDashboardFromChat = (result: ChatResponse) => {
        if (result.dashboard_updates) {
            result.dashboard_updates.forEach(update => {
                updateWidget(update.widgetId, update.data);
            });
        }
    };
    
    // Click on widget triggers chat query
    const handleWidgetClick = (widget: Widget) => {
        chatInterface.setQuery(`Tell me more about ${widget.title}`);
    };
```

### PHASE 5: Real-Time Intelligence Streaming

**File:** `backend/api/unified_intelligence_routes.py`

```python
@router.websocket("/api/v3/unified-intelligence/stream")
async def unified_intelligence_stream(websocket: WebSocket, executive_id: str):
    """Stream real-time updates to both chat and dashboard"""
    
    stream = UnifiedIntelligenceStream(executive_id)
    
    async for update in stream:
        # Send to both chat and dashboard
        await websocket.send_json({
            "chat_message": update.generate_chat_message(),
            "dashboard_updates": update.dashboard_updates,
            "alerts": update.alerts,
            "predictions": update.predictions
        })
```

### PHASE 6: Predictive Business Intelligence

**File:** `backend/services/predictive_business_intelligence.py`

```python
class PredictiveAnalyticsEngine:
    """Generates predictions that appear in both chat and dashboard"""
    
    async def generate_predictions(self, context: QueryContext) -> Predictions:
        # Generate predictions based on query context
        predictions = await self._analyze_patterns(context)
        
        # Format for chat display
        predictions.chat_summary = self._format_for_chat(predictions)
        
        # Format for dashboard widgets
        predictions.dashboard_data = self._format_for_dashboard(predictions)
        
        return predictions
```

## INTEGRATION REQUIREMENTS

### 1. Unified Query Flow
```
Chat Query → NLP Processing → Group-Aware Orchestration → Dashboard Update → Chat Response
```

### 2. Dashboard-Chat Synchronization
- Every chat query updates relevant dashboard widgets
- Dashboard interactions generate chat context
- Real-time streaming updates both interfaces

### 3. Natural Language Commands
```python
UNIFIED_COMMANDS = {
    "Set up my morning briefing": setup_executive_briefing,
    "Show me what needs attention": analyze_critical_items,
    "Compare this month to last": generate_comparison_view,
    "Focus on [topic]": filter_dashboard_by_topic,
    "Start board meeting view": activate_presentation_mode
}
```

### 4. API Endpoints
```python
POST   /api/v3/unified-intelligence/query
GET    /api/v3/unified-intelligence/suggestions
WS     /api/v3/unified-intelligence/stream
GET    /api/v3/unified-intelligence/dashboard-state
POST   /api/v3/unified-intelligence/configure-alerts
```

## SUCCESS CRITERIA

1. **Seamless Integration**
   - Chat queries automatically update dashboard
   - Dashboard clicks generate chat context
   - Unified state management across interfaces

2. **Performance**
   - <1 second from query to dashboard update
   - <3 seconds for complex predictions
   - Real-time streaming with <100ms latency

3. **User Experience**
   - 90% queries answered without leaving interface
   - Proactive suggestions based on context
   - Natural language for all operations

4. **Business Value**
   - 50% reduction in time to insight
   - 70% increase in proactive decisions
   - Executive satisfaction >95%

## TESTING REQUIREMENTS

```python
# Test unified experience
async def test_chat_dashboard_sync():
    # Send chat query
    response = await chat.query("Show deals at risk")
    
    # Verify dashboard updated
    assert dashboard.get_widget("deals_at_risk").is_updated
    assert dashboard.get_widget("deals_at_risk").data == response.dashboard_updates[0].data
    
    # Click dashboard widget
    await dashboard.click_widget("deals_at_risk")
    
    # Verify chat shows context
    assert chat.current_query == "Tell me more about deals at risk"
```

## IMPLEMENTATION NOTES

1. **Preserve Existing Architecture**: All enhancements extend existing classes
2. **Backward Compatibility**: Existing API endpoints continue to work
3. **Progressive Enhancement**: Features can be rolled out incrementally
4. **Configuration Driven**: Use existing config files, add new properties
5. **Security First**: All features respect existing auth/permissions

## DELIVERABLES

1. Enhanced backend services (6 files)
2. Updated frontend components (3 files)
3. New API endpoints (5 endpoints)
4. Configuration updates (2 files)
5. Comprehensive tests (4 test suites)
6. Updated documentation

This implementation creates a truly unified executive intelligence experience where the Universal Chat Interface and CEO Dashboard work as one cohesive system, anticipating needs and delivering insights seamlessly. 