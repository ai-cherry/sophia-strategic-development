# Sophia AI Project Context

## Project Overview

**Name**: Sophia AI
**Type**: Executive AI Orchestrator
**Company**: Pay Ready (80 employees)
**Primary User**: CEO (sole initial user)
**Purpose**: Transform decision-making through AI-powered business intelligence

## Current State

- **Phase**: Building enhanced unified chat with citation system
- **Status**: Phase 2.5 - Research complete, implementation starting
- **Timeline**: 8-week implementation plan
- **Deployment**: CEO-only for first 3-6 months

## Architecture Decisions

### Core Technology Choices
1. **Orchestration**: LangGraph (chosen over AutoGen for production stability)
2. **Memory**: Mem0 (26% better accuracy than OpenAI's system)
3. **LLM Operations**: Snowflake Cortex (all models, integrated with data)
4. **Citation System**: Perplexity-style with numbered references
5. **Frontend**: React 18 + TypeScript (existing UnifiedDashboard.tsx)
6. **Backend**: FastAPI + Python 3.11 (async architecture)

### Key Architectural Patterns
- Multi-agent system with specialized domains
- Event-driven communication via Redis
- Persistent memory via Mem0 + Snowflake
- Natural language interface with citations
- Hybrid orchestration (centralized routing, distributed execution)

## Development Priorities

1. **Quality & Correctness** - Every line must be correct
2. **Stability & Reliability** - Rock-solid for CEO usage
3. **Maintainability** - Clear, modifiable code
4. **Performance** - Sub-200ms response times
5. **Cost & Security** - Optimized but not primary focus

## Key Metrics

### Technical Targets
- Response time: < 200ms
- Citation accuracy: > 90%
- Memory recall: > 95%
- Code generation success: > 85%

### Business Targets
- CEO task completion: > 80%
- Time to insight reduction: > 50%
- Decision speed increase: > 30%
- Daily active usage by CEO

## Integration Points

### Business Systems
- **HubSpot**: CRM data and contact management
- **Gong.io**: Call analysis and sales insights
- **Slack**: Team communication and notifications
- **Snowflake**: Central data warehouse

### AI/ML Stack
- **Snowflake Cortex**: LLM operations
- **Mem0**: Conversation memory
- **Pinecone/Weaviate**: Vector search
- **Redis**: Event bus and caching

## Current Focus Areas

### Week 1-2 (Immediate)
- Citation system implementation
- Ice breaker prompts
- Cortex model routing
- Memory service skeleton

### Week 3-4 (Next)
- Mem0 integration
- Context persistence
- Follow-up suggestions
- Focus modes

## Constraints & Considerations

### Technical Constraints
- Must work within existing codebase
- Single UnifiedDashboard.tsx frontend
- Snowflake as primary data source
- Lambda Labs deployment infrastructure

### Business Constraints
- CEO as sole initial user
- Quality over features
- Gradual rollout plan
- No production data modifications without approval

## Success Criteria

### Phase 1 Success (Week 8)
- [ ] Citations working accurately
- [ ] Memory retaining context
- [ ] CEO actively using daily
- [ ] All metrics meeting targets
- [ ] Ready for super-user rollout

### Long-term Success (6 months)
- [ ] Company-wide adoption
- [ ] Measurable productivity gains
- [ ] Positive ROI demonstrated
- [ ] Platform stability proven

## Risk Mitigation

### Technical Risks
- Cortex failures → Fallback models
- Memory issues → Local caching
- Performance problems → Graceful degradation

### User Adoption Risks
- Complexity → Start simple, add gradually
- Trust issues → Transparent citations
- Learning curve → Familiar chat interface

## Notes & Learnings

- CEO values accuracy over speed
- Business context crucial for adoption
- Citations build trust significantly
- Simple UI preferred over complex features
