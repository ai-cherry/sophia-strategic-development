# Unified Chat and Dashboard - Next Steps Action Plan

## Date: July 9, 2025

## Quick Start Guide

### Step 1: Verify Backend Integration (15 minutes)

1. **Start the backend**:
   ```bash
   cd sophia-main
   python backend/app/unified_chat_backend.py
   ```

2. **Run integration tests**:
   ```bash
   python scripts/test_v4_orchestrator_integration.py
   ```

3. **Check results**:
   - All health endpoints should return 200
   - v4 orchestration should work
   - v3 compatibility should work

### Step 2: Fix Any Issues (30 minutes)

If tests fail, common fixes:

1. **Import errors**:
   ```python
   # In backend/services/sophia_unified_orchestrator.py
   # The MCPOrchestrationService import is wrapped in try/except
   # Mock fallback is already implemented
   ```

2. **Missing dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Port conflicts**:
   - Ensure port 8001 is free
   - Or change in `unified_chat_backend.py`

### Step 3: Test Frontend Integration (30 minutes)

1. **Start frontend**:
   ```bash
   cd frontend
   npm start
   ```

2. **Test chat functionality**:
   - Open http://localhost:3000
   - Send a test message
   - Verify response comes from v4 orchestrator

3. **Check browser console**:
   - Should see calls to `/api/v4/orchestrate`
   - Fallback to `/api/v3/chat` if needed

### Step 4: Complete MCP Integration (45 minutes)

1. **Fix MCPOrchestrationService import**:
   ```python
   # The adapter pattern is already in place
   # Just need to ensure infrastructure/services/mcp_orchestration_service.py exists
   ```

2. **Test one MCP server**:
   ```python
   # Start with a simple one like Linear or Asana
   # In mcp_orchestration_adapter.py, update capability mapping
   ```

3. **Verify data flow**:
   - Query → Orchestrator → MCP Adapter → MCP Service → Response

### Step 5: Create Unified Dashboard (This Week)

#### Day 1: Executive Overview Tab
```typescript
// frontend/src/components/dashboard/ExecutiveOverview.tsx
- KPI cards (Revenue, Users, Health Score)
- Quick metrics
- System status
```

#### Day 2: Knowledge Management Tab
```typescript
// frontend/src/components/dashboard/KnowledgeManagement.tsx
- Document list
- Search interface
- Recent insights
```

#### Day 3: Projects & OKRs Tab
```typescript
// frontend/src/components/dashboard/ProjectsOKRs.tsx
- Project status cards
- OKR progress
- Team metrics
```

#### Day 4: Sales Intelligence Tab
```typescript
// frontend/src/components/dashboard/SalesIntelligence.tsx
- Pipeline visualization
- Gong insights
- Revenue forecasts
```

#### Day 5: Integration & Testing
- Wire all tabs to v4 orchestrator
- End-to-end testing
- Performance optimization

## File Structure After Implementation

```
frontend/src/components/
├── UnifiedDashboard.tsx         # Main tabbed container
├── UnifiedChatDashboard.tsx     # Chat tab (existing)
└── dashboard/
    ├── ExecutiveOverview.tsx    # KPIs and metrics
    ├── KnowledgeManagement.tsx  # Documents and insights
    ├── ProjectsOKRs.tsx        # Projects and objectives
    └── SalesIntelligence.tsx   # Sales data and forecasts

backend/
├── app/
│   └── unified_chat_backend.py  # Updated with v4
├── api/
│   └── orchestrator_v4_routes.py # New v4 routes
└── services/
    ├── sophia_unified_orchestrator.py  # Main orchestrator
    ├── mcp_orchestration_adapter.py    # MCP bridge
    └── memory_service_adapter.py       # Memory bridge
```

## Validation Checklist

Before considering complete:

- [ ] Backend starts without errors
- [ ] All tests in `test_v4_orchestrator_integration.py` pass
- [ ] Frontend connects to v4 endpoints
- [ ] At least one MCP server returns real data
- [ ] Executive Overview tab shows real metrics
- [ ] No deprecation warnings in logs
- [ ] Documentation is updated

## Common Issues & Solutions

### Issue: "MCPOrchestrationService not found"
**Solution**: The orchestrator has mock fallback. Real MCP integration optional for initial testing.

### Issue: "Frontend still calling v3"
**Solution**: Clear browser cache, restart frontend dev server.

### Issue: "No data in dashboard"
**Solution**: Start with mock data, then wire real endpoints incrementally.

## Success Criteria

You'll know you're done when:
1. Single dashboard with 5 tabs
2. All data flows through v4 orchestrator
3. Real-time updates working
4. No duplicate code or services
5. Clean architecture matches system handbook vision

---

**Remember**: The goal is a clean, unified system. Take it step by step. Test each phase before moving to the next. 