# Phase 2.5: LLM Gateway Implementation Plan

## Overview

This plan implements a unified LLM strategy using Portkey as the primary gateway with OpenRouter for experimental models and Snowflake Cortex for data-local operations. The focus is on performance optimization and centralized control.

## Current State Assessment

### What We Have
- Direct OpenAI API calls scattered across 10+ files
- Basic Portkey configuration (partially used)
- OpenRouter configured but underutilized
- Snowflake Cortex for some AI operations
- No unified cost tracking or performance monitoring

### What We Need
- Single UnifiedLLMService for all LLM interactions
- Centralized routing and model selection
- Performance-optimized configuration
- CEO dashboard for control and monitoring
- Comprehensive observability

## Implementation Components

### 1. Portkey Configuration Setup

**Virtual Keys Structure:**
```
prod-gpt4-primary         → GPT-4 for critical tasks
prod-claude-primary       → Claude for complex reasoning
prod-openrouter-exp      → Experimental models
staging-all-providers    → Staging environment
dev-test-keys           → Development testing
```

**Performance Configuration:**
- Semantic cache with 0.95 threshold
- 3 retry attempts with exponential backoff
- 30s request timeout
- Connection pooling (100 max connections)
- Distributed caching with Redis

### 2. UnifiedLLMService Implementation

```python
# Core service structure
UnifiedLLMService
├── Portkey client (primary)
├── OpenRouter client (secondary)
├── Snowflake connector (embeddings)
├── Model routing logic
├── Performance tracking
└── Cost monitoring
```

**Task-Based Routing:**
- Code Generation → Tier 1 (GPT-4/Claude via Portkey)
- Business Intelligence → Tier 1 (GPT-4/Claude via Portkey)
- Chat Conversations → Tier 2 (GPT-3.5/Haiku via Portkey)
- Embeddings → Snowflake Cortex
- Experimental → OpenRouter

### 3. CEO Dashboard Components

**LLM Management Tab:**
- Model routing configuration (dropdowns)
- Real-time performance metrics
- Cost tracking and projections
- Cache hit rate visualization
- Provider health status
- A/B test results

**Key Metrics:**
- Average latency by provider/model
- Cache hit rate (target: 20%+)
- Error rate and fallback usage
- Cost per 1K requests
- Token usage trends

### 4. Integration Points

**Unified Chat Service:**
- Replace direct OpenAI calls with UnifiedLLMService
- Implement streaming with fallback support
- Add conversation-level cost tracking

**MCP Servers:**
- Update all MCP servers to use UnifiedLLMService
- Add performance metadata to requests
- Implement request batching where applicable

**n8n Workflows:**
- Configure OpenAI nodes to use Portkey endpoint
- Add workflow-level cost tracking
- Implement intelligent retry logic

### 5. Snowflake Cortex Hybrid Strategy

**Use Cortex For:**
- Embedding generation (data stays local)
- Batch processing of Snowflake data
- Simple text operations on sensitive data

**Use Portkey For:**
- Complex reasoning tasks
- Real-time chat interactions
- Code generation and analysis
- Cross-domain knowledge queries

### 6. Monitoring and Observability

**Prometheus Metrics:**
- `llm_requests_total` (by provider, model, task)
- `llm_request_duration_seconds` (latency tracking)
- `llm_cache_hit_rate` (cache effectiveness)
- `llm_cost_per_request_dollars` (cost tracking)

**Grafana Dashboards:**
- Provider comparison dashboard
- Cost optimization dashboard
- Performance trending dashboard
- Cache effectiveness dashboard

## Implementation Steps

### Phase 1: Foundation Setup

1. **Configure Portkey Account**
   - Create virtual keys for all environments
   - Set up performance-optimized config
   - Configure semantic caching
   - Enable request logging

2. **Implement UnifiedLLMService**
   - Create base service class
   - Implement Portkey integration
   - Add OpenRouter fallback
   - Integrate Snowflake Cortex

3. **Update Configuration Management**
   - Add Portkey API keys to Pulumi ESC
   - Create environment-specific configs
   - Set up virtual key mappings

### Phase 2: Service Integration

1. **Migrate Existing Services**
   - Replace direct OpenAI calls
   - Update all MCP servers
   - Modify chat service
   - Update knowledge base service

2. **Implement Streaming Support**
   - Add streaming to UnifiedLLMService
   - Update frontend for streaming
   - Handle fallback during streams

3. **Add Cost Tracking**
   - Track costs per request
   - Aggregate by user/session
   - Store in Snowflake analytics

### Phase 3: Dashboard and Control

1. **Build CEO Dashboard**
   - Create LLMManagementTab component
   - Implement model routing UI
   - Add real-time metrics display
   - Build cost projection tools

2. **Implement A/B Testing**
   - Create experiment framework
   - Add canary deployment support
   - Build comparison analytics

3. **Set Up Alerts**
   - Cost threshold alerts
   - Performance degradation alerts
   - Error rate monitoring

### Phase 4: Optimization

1. **Cache Optimization**
   - Analyze cache hit patterns
   - Implement cache warming
   - Optimize similarity threshold

2. **Performance Tuning**
   - Benchmark all models
   - Optimize routing rules
   - Tune connection pools

3. **Cost Optimization**
   - Analyze usage patterns
   - Implement intelligent routing
   - Set up budget controls

## File Changes Required

### New Files
- `backend/services/unified_llm_service.py`
- `backend/monitoring/llm_metrics_exporter.py`
- `frontend/src/components/dashboard/LLMManagementTab.tsx`
- `infrastructure/llm-gateway/index.ts`
- `docs/llm-gateway/operational-guide.md`

### Modified Files
- `backend/services/unified_chat_service.py` → Use UnifiedLLMService
- `backend/services/kb_management_service.py` → Use UnifiedLLMService
- `backend/mcp_servers/*.py` → Update all to use UnifiedLLMService
- `backend/core/config_manager.py` → Add LLM configuration
- `.cursorrules` → Add LLM strategy guidelines

## Success Metrics

### Performance
- Sub-100ms gateway overhead
- 20%+ cache hit rate
- <1% error rate
- 99.9% availability

### Cost
- 30-50% cost reduction via caching
- Clear cost attribution
- Budget compliance
- Optimization insights

### Operations
- Single point of configuration
- Comprehensive monitoring
- Easy model switching
- A/B testing capability

## Risk Mitigation

### Fallback Strategy
- Direct API access if Portkey fails
- Multiple provider redundancy
- Graceful degradation
- Circuit breaker patterns

### Security
- All keys in Pulumi ESC
- Virtual key rotation
- Audit logging
- PII detection

### Performance
- Regional gateway deployment
- Connection pool tuning
- Cache warming
- Load testing

This implementation provides a robust, scalable LLM infrastructure that prioritizes performance while maintaining flexibility and control. 