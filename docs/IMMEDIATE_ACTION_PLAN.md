# 🎯 Sophia AI: 48-Hour Quick Start Plan

## Day 1 (First 8 Hours)

### Morning (Hours 1-4)
1. **Create Convention Files** (1 hour)
   ```bash
   # Create .cursorrules in project root
   touch .cursorrules
   # Copy convention content from final plan
   ```

2. **Set Up Documentation Structure** (30 min)
   ```bash
   mkdir -p docs/architecture
   touch docs/PROJECT_CONTEXT.md
   touch docs/architecture/SYSTEM_DESIGN.md
   touch docs/AI_MEMORY.md
   ```

3. **Initialize Citation UI Component** (2.5 hours)
   ```typescript
   // frontend/src/components/Citations.tsx
   interface Citation {
     id: number;
     source: string;
     title: string;
     excerpt: string;
     url?: string;
   }
   
   // Create basic citation display component
   // Add inline citation markers [1], [2]
   // Create collapsible sidebar
   ```

### Afternoon (Hours 5-8)
4. **Set Up Cortex Model Routing** (2 hours)
   ```python
   # backend/services/cortex_router.py
   # Implement model selection logic
   # Add temperature controls
   # Create cost tracking
   ```

5. **Create Memory Service Skeleton** (2 hours)
   ```python
   # backend/services/memory_service.py
   # Set up Mem0 configuration
   # Create conversation storage interface
   # Add Snowflake sync placeholder
   ```

## Day 2 (Next 8 Hours)

### Morning (Hours 9-12)
6. **Implement Ice Breaker Prompts** (1.5 hours)
   ```typescript
   // Add to EnhancedUnifiedChat.tsx
   const iceBreakers = [
     "What's our revenue trend this quarter?",
     "Show me top performing sales reps",
     "Analyze recent customer feedback",
     "What are our biggest opportunities?"
   ];
   ```

7. **Add Follow-up Suggestions** (2.5 hours)
   ```python
   # backend/services/suggestion_service.py
   # Create context-aware suggestion generator
   # Use Cortex for generating relevant follow-ups
   ```

### Afternoon (Hours 13-16)
8. **Basic Citation Backend** (2 hours)
   ```python
   # backend/services/citation_service.py
   # Extract sources from LLM responses
   # Format citations consistently
   # Store citation metadata
   ```

9. **Integration Testing** (2 hours)
   ```python
   # tests/test_enhanced_chat.py
   # Test citation display
   # Test ice breakers
   # Test Cortex routing
   ```

## Success Criteria for 48 Hours

### Must Have ✅
- [ ] .cursorrules file in place
- [ ] Basic citation UI working
- [ ] Ice breaker prompts displayed
- [ ] Cortex model routing configured
- [ ] Memory service skeleton ready

### Nice to Have 🎯
- [ ] Follow-up suggestions working
- [ ] Citation hover previews
- [ ] Basic memory storage
- [ ] Cost tracking active

### Can Wait ⏳
- MCP integration
- Complex multi-agent coordination
- Advanced security features
- Production monitoring

## Quick Commands

```bash
# Start development
cd /Users/lynnmusil/sophia-main

# Run frontend with citations
cd frontend && npm run dev

# Test backend routing
cd backend && pytest tests/test_cortex_router.py

# Check citation display
# Navigate to http://localhost:3000
# Type a query and verify citations appear
```

## Validation Steps

1. **Citation Test**: Ask "What's our revenue?" and verify:
   - Response includes [1], [2] markers
   - Sidebar shows source details
   - Sources are relevant

2. **Ice Breaker Test**: Load chat and verify:
   - 4 suggested prompts appear
   - Clicking a prompt sends it
   - Prompts are business-relevant

3. **Routing Test**: Check logs to verify:
   - Simple queries use mistral-7b
   - Complex queries use larger models
   - Temperature varies by query type

## Next 48 Hours (Days 3-4)

- Implement Mem0 conversation storage
- Add focus mode selector
- Create template system
- Begin MCP planning

Remember: **Ship small, ship often**. It's better to have citations working perfectly than to attempt everything at once. 