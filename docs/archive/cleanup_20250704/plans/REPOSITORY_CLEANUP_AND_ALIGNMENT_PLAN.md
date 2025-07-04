# Repository Cleanup and Alignment Plan

## Executive Summary

This plan addresses the repository fragmentation, aligns local changes with GitHub, and incorporates LangChain enhancement opportunities. The goal is to create a single source of truth for the Sophia AI platform while maintaining development velocity.

## Current State Analysis

### 1. Multiple App Files Problem
- **simple_app.py**: Basic testing (WORKING)
- **enhanced_minimal_app.py**: LangChain features (BROKEN - missing dependencies)
- **main.py**: Original unified entry (OUTDATED)
- **unified_fastapi_app.py**: Kitchen sink approach (COMPLEX)
- **fastapi_app.py**: Referenced in Dockerfiles (FRAGMENTED)

### 2. Uncommitted Changes
- Modified external submodules (8 repositories)
- Local gong_data_quality.py fixes
- Untracked test_env/ directory
- Two untracked markdown files

### 3. Dependency Issues
- PyArrow compatibility problems
- Missing snowflake_cortex_service module
- Pydantic v1 to v2 migration issues

## Phase 1: Immediate Cleanup (Today)

### 1.1 Commit Local Fixes
```bash
# Commit the gong_data_quality.py fix
git add backend/monitoring/gong_data_quality.py
git commit -m "fix: Update gong_data_quality.py for Pydantic v2 compatibility"

# Handle test_env (add to .gitignore)
echo "test_env/" >> .gitignore
git add .gitignore
git commit -m "chore: Add test_env to gitignore"

# Clean up untracked files
mkdir -p docs/archive/cleanup_2025
mv DETAILED_IMPLEMENTATION_PLAN_ALIGNED_WITH_CODEBASE.md docs/archive/cleanup_2025/
mv FOCUSED_INFRASTRUCTURE_IMPROVEMENTS_PLAN.md docs/archive/cleanup_2025/
git add docs/archive/cleanup_2025/
git commit -m "chore: Archive implementation planning documents"
```

### 1.2 Update Submodules
```bash
# Update all submodules to their latest commits
git submodule update --init --recursive
git add external/
git commit -m "chore: Update external submodules to latest versions"
```

### 1.3 Create App Consolidation Plan
- Primary App: `backend/app/app.py` (NEW - consolidated)
- Testing App: `backend/app/simple_app.py` (KEEP for testing)
- Archive others to `backend/app/archive/`

## Phase 2: App Consolidation (Week 1)

### 2.1 Create Unified App Structure
```python
# backend/app/app.py
"""
Sophia AI Unified Application
Single source of truth for all backend services
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from backend.core.config_manager import ConfigManager
from backend.api import unified_routes
from backend.services.unified_chat_service import UnifiedChatService
from backend.monitoring.health_monitor import HealthMonitor

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 Starting Sophia AI Platform...")

    # Initialize core services
    await initialize_core_services()

    # Start health monitoring
    await start_health_monitoring()

    yield

    # Cleanup
    logger.info("🛑 Shutting down Sophia AI Platform...")
    await cleanup_services()

app = FastAPI(
    title="Sophia AI Platform",
    description="Unified AI Orchestrator for Pay Ready",
    version="3.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(unified_routes.router, prefix="/api/v1")

# Health endpoint
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "sophia-ai"}
```

### 2.2 Update All References
- Update all Dockerfiles to use `backend.app.app:app`
- Update deployment scripts
- Update documentation

### 2.3 Archive Old Apps
```bash
mkdir -p backend/app/archive
mv backend/app/main.py backend/app/archive/
mv backend/app/enhanced_minimal_app.py backend/app/archive/
mv backend/app/unified_fastapi_app.py backend/app/archive/
mv backend/app/fastapi_app.py backend/app/archive/
```

## Phase 3: LangChain Enhancements Integration (Week 1-2)

### 3.1 Enhanced Semantic Caching
```python
# backend/services/enhanced_cache_service.py
class EnhancedCacheService(GPTCacheService):
    """Multi-tier semantic caching with business context"""

    def __init__(self):
        super().__init__()
        self.business_context_analyzer = BusinessContextAnalyzer()
        self.cache_tiers = {
            'hot': RedisCache(ttl=3600),      # 1 hour
            'warm': RedisCache(ttl=86400),    # 24 hours
            'cold': SnowflakeCache()           # Persistent
        }
```

### 3.2 Auto-Evaluation Framework
```python
# backend/monitoring/auto_evaluator.py
class AutoEvaluator:
    """Automated quality scoring and bias detection"""

    async def evaluate_response(self, response, context):
        quality_score = await self.score_quality(response)
        bias_check = await self.check_bias(response)
        business_relevance = await self.assess_relevance(response, context)

        return EvaluationResult(
            quality=quality_score,
            bias=bias_check,
            relevance=business_relevance
        )
```

### 3.3 LangGraph State Management
```python
# backend/orchestration/langgraph_state_manager.py
class LangGraphStateManager:
    """Stateful multi-agent workflow management"""

    def __init__(self):
        self.state_store = StateStore()
        self.workflow_engine = WorkflowEngine()

    async def manage_business_process(self, process_type, initial_state):
        # Long-running business process orchestration
        pass
```

## Phase 4: Dependency Resolution (Week 2)

### 4.1 Fix Missing Services
Either implement or remove imports for:
- `snowflake_cortex_service.py`
- Other missing dependencies

### 4.2 PyArrow Resolution
```toml
# pyproject.toml
[tool.uv.pip]
# Specific PyArrow handling
extra-index-urls = ["https://pypi.org/simple"]

[project.dependencies]
pyarrow = ">=16.1.0,<17.0.0"  # Pin to stable version
```

### 4.3 Create Dependency Test Script
```python
# scripts/test_dependencies.py
"""Test all critical dependencies"""
import sys

def test_imports():
    try:
        import pyarrow
        print(f"✅ PyArrow {pyarrow.__version__}")
    except ImportError as e:
        print(f"❌ PyArrow: {e}")

    # Test other critical imports
```

## Phase 5: Documentation Update (Week 2-3)

### 5.1 Create Clear App Documentation
```markdown
# docs/APPLICATION_STRUCTURE.md

## Application Entry Points

### Production Application
- **File**: `backend/app/app.py`
- **Purpose**: Main production application
- **Usage**: `uvicorn backend.app.app:app`

### Testing Application
- **File**: `backend/app/simple_app.py`
- **Purpose**: Minimal app for testing
- **Usage**: `uvicorn backend.app.simple_app:app`

### Archived Applications
Located in `backend/app/archive/` for historical reference.
```

### 5.2 Update README
- Clear instructions on which app to use
- Development setup guide
- Deployment instructions

## Phase 6: Production Excellence (Week 3-4)

### 6.1 Implement Monitoring
- Prometheus metrics
- Grafana dashboards
- Health check endpoints

### 6.2 Security Enhancements
- Authentication improvements
- API rate limiting
- Security headers

### 6.3 Performance Optimization
- Connection pooling
- Query optimization
- Caching strategies

## Implementation Timeline

### Week 1: Foundation
- [ ] Day 1: Immediate cleanup (Phase 1)
- [ ] Day 2-3: App consolidation (Phase 2)
- [ ] Day 4-5: Begin LangChain enhancements (Phase 3)

### Week 2: Enhancement
- [ ] Day 1-2: Complete LangChain integration
- [ ] Day 3-4: Dependency resolution (Phase 4)
- [ ] Day 5: Documentation update (Phase 5)

### Week 3-4: Excellence
- [ ] Production monitoring
- [ ] Security enhancements
- [ ] Performance optimization

## Success Metrics

### Technical Metrics
- Single app.py file as entry point
- All tests passing
- No import errors
- Clean git status

### Business Metrics
- 40-60% reduction in LLM costs
- 50-70% faster response times
- 25-40% improvement in accuracy
- Foundation for 10x user growth

## Risk Mitigation

### Rollback Plan
- Keep archive of old apps for 30 days
- Tag current state before changes
- Incremental deployment approach

### Testing Strategy
- Unit tests for each phase
- Integration tests for app changes
- Load testing before production

## Next Steps

1. **Immediate**: Start Phase 1 cleanup
2. **Today**: Complete local changes commit
3. **This Week**: Consolidate app files
4. **Next Week**: Implement enhancements

This plan provides a clear path from the current fragmented state to a clean, unified, and enhanced Sophia AI platform that incorporates the best of LangChain patterns while maintaining the existing sophisticated architecture.
