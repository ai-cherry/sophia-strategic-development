# Sophia AI Monorepo Transition Guide

⚠️ **TRANSITION IN PROGRESS** ⚠️

## Current Status

We are transitioning from the old structure to a new monorepo structure. During this transition:
- **USE THE OLD STRUCTURE** for all new code
- **DO NOT USE THE NEW STRUCTURE** until migration is complete
- Target completion: ~~February 2025~~ **May 2025** (Extended for enhancement phases)

## Directory Structure During Transition

### Current (Active) Structure - USE THIS
```
sophia-main/
├── backend/          # ✅ PUT NEW BACKEND CODE HERE
├── frontend/         # ✅ PUT NEW FRONTEND CODE HERE
├── mcp-servers/      # ✅ PUT NEW MCP SERVERS HERE
├── scripts/          # ✅ PUT NEW SCRIPTS HERE
├── docs/             # ✅ PUT NEW DOCS HERE
└── infrastructure/   # ✅ PUT NEW INFRA CODE HERE
```

### Future Structure - DO NOT USE YET
```
sophia-main/
├── apps/             # ❌ DO NOT USE YET
│   ├── api/
│   ├── frontend/
│   └── mcp-servers/
├── libs/             # ❌ DO NOT USE YET
│   ├── core/
│   └── shared/
└── config/           # ❌ DO NOT USE YET
```

## Updated Transition Timeline

### Phase 0: Infrastructure Setup ✅ COMPLETE
- Turborepo configuration
- PNPM workspace setup
- CI/CD templates
- Migration tooling

### Phase 1: Foundation Enhancement (January 2025)
- Mem0 integration for persistent memory
- Prompt optimization MCP deployment
- Advanced LangGraph patterns
- Unified MCP gateway

### Phase 2: Data Pipeline Automation (February 2025)
- N8N workflow automation
- Automated data ingestion
- Real-time transformations
- Executive dashboards

### Phase 3: Intelligence Enhancement (March 2025)
- Multi-agent learning system
- Conversational training
- Self-improving responses
- Natural language workflows

### Phase 4: Monorepo Migration (April 2025)
- Move backend/ → apps/api/
- Move frontend/ → apps/frontend/
- Extract shared code → libs/
- Update all imports

### Phase 5: Production Optimization (May 2025)
- Performance tuning
- Monitoring enhancement
- Documentation finalization
- Team onboarding

## Migration Rules

1. **All new features** go in the OLD structure
2. **No manual moves** - use migration scripts only
3. **Update imports** will be done automatically
4. **Test everything** after each migration phase

## For AI Coders

When working on Sophia AI:
1. **ALWAYS** use the current structure (backend/, frontend/, etc.)
2. **IGNORE** the apps/ and libs/ directories
3. **FOLLOW** the enhancement phases for new features
4. **CHECK** this guide if confused about where to put code

## Quality Standards During Transition

- **Code Quality**: Every line must be correct
- **No Duplication**: Check existing code first
- **Clean Dependencies**: Use config_manager pattern
- **Delete One-Time Scripts**: After successful use

## Questions?

If you're unsure:
1. Use the OLD structure
2. Check recent commits for patterns
3. Follow existing code organization
4. Ask before creating new top-level directories

---

*Last updated: January 2025 - Extended timeline for enhancement phases*
