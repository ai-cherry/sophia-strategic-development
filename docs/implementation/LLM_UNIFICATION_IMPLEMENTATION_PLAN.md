# Sophia AI LLM Unification Implementation Plan

## Executive Summary

This plan implements a unified LLM routing architecture that consolidates fragmented implementations while strictly improving stability, scalability, performance, and quality. The approach preserves existing functionality through backward-compatible shims while establishing a single, observable, cost-optimized LLM gateway.

## Current State Assessment

### Fragmentation Issues Confirmed
- **3 competing LLM services**: `unified_llm_service.py`, `enhanced_portkey_llm_gateway.py`, `advanced_llm_service.py`
- **Direct SDK usage**: 15+ files with direct OpenAI/Portkey calls
- **Missing provider files**: `core/services/chat/providers/*` referenced but non-existent
- **Duplicate configurations**: 2 Portkey JSON files with conflicting settings
- **Inconsistent routing logic**: Different services implement different model selection strategies

### Existing Strengths to Preserve
- Sophisticated routing logic in `unified_llm_service.py`
- Cost optimization in `enhanced_portkey_llm_gateway.py`
- Snowflake Cortex integration for data operations
- Prometheus metrics already instrumented

## Implementation Phases

### Phase P-1: Foundation & Router Module (Functional Milestone: Core Router Ready)

**Deliverables:**
1. Create `infrastructure/services/llm_router/` module structure
2. Implement stateless routing engine with unified interface
3. Add backward-compatible shims for existing services
4. Establish Prometheus metrics and observability

**Key Files:**
```
infrastructure/services/llm_router/
├── __init__.py              # Export LLMRouter singleton
├── enums.py                 # TaskType, TaskComplexity, Provider
├── router.py                # Core routing logic
├── gateway.py               # Portkey/OpenRouter wrapper
├── cortex_adapter.py        # Snowflake Cortex wrapper
├── fallback.py              # Provider chain logic
├── config_schema.py         # Pydantic configuration
└── cache.py                 # Semantic caching layer
```

### Phase P-2: Core Service Migration (Functional Milestone: Core Services Routed)

**Deliverables:**
1. Replace direct LLM calls in `backend/core/**`
2. Update AI Memory embeddings to use router
3. Migrate chat services to unified provider
4. Add feature flags for gradual rollout

**Migration Strategy:**
- Use codemod script for automated replacement
- Add `USE_LLM_ROUTER_V2` feature flag
- Keep old code paths for rollback capability

### Phase P-3: MCP Server Migration (Functional Milestone: All MCP Servers Unified)

**Deliverables:**
1. Migrate all V2 MCP servers to use router
2. Enable semantic caching by default
3. Implement cross-server context sharing
4. Complete performance optimization

### Phase P-4: Advanced Optimization (Functional Milestone: ML-Based Routing Live)

**Deliverables:**
1. Implement ML-based model selection
2. Add predictive cost optimization
3. Enable advanced caching strategies
4. Complete observability dashboard

### Phase P-5: Legacy Cleanup (Functional Milestone: V1 Retired)

**Deliverables:**
1. Remove deprecated services
2. Delete redundant configurations
3. Clean up unused dependencies
4. Archive legacy documentation

## Technical Implementation Details

### 1. Router Architecture

```python
# infrastructure/services/llm_router/router.py
class LLMRouter:
    """Single facade for all LLM interactions"""

    async def complete(
        self,
        prompt: str,
        task: TaskType,
        complexity: TaskComplexity = TaskComplexity.SIMPLE,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        # Route to appropriate provider based on task
        if task in {TaskType.SQL_GENERATION, TaskType.DATA_ANALYSIS}:
            return await self._cortex.run(prompt, task=task)
        return await self._gateway.run(prompt, task=task, complexity=complexity, **kwargs)
```

### 2. Configuration Consolidation

**Keep:** `config/portkey/sophia-ai-config.json`
**Delete:** `config/services/portkey.json`
**Add:** Live-reload configuration with Pydantic validation

### 3. Backward Compatibility

```python
# infrastructure/services/unified_llm_service.py (shimmed)
import warnings
from infrastructure.services.llm_router import llm_router

warnings.warn("DEPRECATED: Use llm_router directly", DeprecationWarning)

async def completion(prompt: str, **kwargs):
    """Backward compatible wrapper"""
    return await llm_router.complete(prompt=prompt, **kwargs)
```

### 4. Metrics & Observability

```python
# Prometheus metrics
llm_request_seconds = Histogram(
    "llm_request_seconds",
    "LLM response latency",
    ["provider", "model", "task_type"]
)

llm_cost_usd_total = Counter(
    "llm_cost_usd_total",
    "Accumulated cost in USD",
    ["provider", "model"]
)

llm_cache_hit_rate = Gauge(
    "llm_cache_hit_rate",
    "Cache hit rate percentage",
    ["cache_type"]
)
```

## Migration Mechanics

### 1. Automated Codemod

```bash
# Replace direct OpenAI calls
python scripts/codemod/replace_llm_clients.py \
    --pattern "openai\." \
    --replacement "llm_router.complete" \
    --glob "**/*.py"
```

### 2. CI/CD Integration

- Add `llm-regression` job to test suite
- Implement cost budget guard ($5 limit)
- Add latency regression tests (p95 < 2s)

### 3. Feature Flag Rollout

```python
# Progressive rollout
if os.getenv("LLM_ROUTER_V2", "false").lower() == "true":
    from infrastructure.services.llm_router import llm_router
else:
    from infrastructure.services.unified_llm_service import get_unified_llm_service
```

## Success Criteria

1. **Zero direct LLM SDK calls** outside router module
2. **95%+ test coverage** for router package
3. **P95 latency ≤ 2 seconds** under load
4. **35%+ cost reduction** via caching and routing
5. **No hardcoded secrets** detected by security scan
6. **100% backward compatibility** during migration

## Risk Mitigation

1. **Rollback Strategy**: Feature flags enable instant rollback
2. **Performance Monitoring**: Real-time dashboards track latency
3. **Cost Controls**: Budget guards prevent runaway costs
4. **Testing**: Comprehensive test suite with offline mocks

## Timeline (No Calendar Dates)

- **P-1**: Foundation ready for testing
- **P-2**: Core services migrated
- **P-3**: All MCP servers unified
- **P-4**: Advanced features operational
- **P-5**: Legacy code retired

Each phase gate requires:
- CI green
- Smoke tests passing
- Metrics healthy
- Documentation updated
