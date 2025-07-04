# Current LLM Usage Analysis - Sophia AI

## Executive Summary

The Sophia AI codebase currently has a fragmented LLM strategy with multiple integration patterns:
- Direct API calls to OpenAI, Anthropic, and Snowflake Cortex
- Basic Portkey gateway implementation (partially configured)
- OpenRouter configuration exists but underutilized
- Inconsistent model selection and routing logic
- No centralized cost tracking or performance monitoring

## Current LLM Integrations

### 1. Direct API Integrations

#### OpenAI
- **Usage**: Primary LLM for most services
- **Integration Points**:
  - `backend/mcp_servers/ai_memory_auto_discovery.py` - Memory detection
  - `backend/services/kb_management_service.py` - Knowledge base NLP
  - `backend/agents/specialized/snowflake_admin_agent.py` - SQL generation
  - `backend/infrastructure/sophia_iac_orchestrator.py` - Infrastructure automation
- **Models Used**: GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Configuration**: API keys from Pulumi ESC

#### Anthropic (Claude)
- **Usage**: Advanced reasoning and code generation
- **Integration Points**:
  - `claude-cli-integration/` - Dedicated CLI integration
  - `backend/services/portkey_gateway.py` - Via Portkey
  - Direct API calls in some services
- **Models Used**: Claude-3-opus, Claude-3-sonnet, Claude-3-haiku
- **Configuration**: Separate Claude CLI config + API keys

#### Snowflake Cortex
- **Usage**: Native SQL-based AI operations
- **Integration Points**:
  - `backend/services/enhanced_snowflake_cortex_service.py`
  - `backend/utils/snowflake_cortex_service.py`
  - Multiple MCP servers for Cortex operations
- **Functions Used**: COMPLETE, SENTIMENT, SUMMARIZE, EMBED_TEXT
- **Models**: mistral-7b, llama2-70b-chat, e5-base-v2

### 2. Gateway Implementations

#### Portkey Gateway (`backend/services/portkey_gateway.py`)
- **Status**: Partially implemented
- **Features**:
  - Multi-provider support (OpenAI, Anthropic, Google, Mistral)
  - Basic routing logic
  - Simple caching
  - Circuit breaker pattern
- **Issues**:
  - Not used consistently across codebase
  - Missing advanced features (semantic caching, cost tracking)
  - No dashboard integration

#### Smart AI Service (`backend/services/smart_ai_service.py`)
- **Status**: More advanced implementation
- **Features**:
  - Parallel Portkey/OpenRouter strategy
  - Task-based routing
  - Cost tracking to Snowflake
  - Performance monitoring
- **Good Patterns**:
  - Strategic model assignments
  - Comprehensive error handling
  - Analytics integration

### 3. Configuration Patterns

#### Scattered API Keys
```python
# Pattern 1: Direct from environment
openai_key = get_config_value("openai_api_key")

# Pattern 2: From Pulumi ESC
api_key = await get_config_value("openai_api_key")

# Pattern 3: From environment variables
api_key = os.getenv("OPENAI_API_KEY")
```

#### Model Selection Logic
- Hardcoded in individual services
- No centralized model registry
- Inconsistent selection criteria

## Problems Identified

### 1. Fragmentation
- 10+ different files making direct LLM calls
- Each service implements its own retry/error logic
- No consistent model selection strategy

### 2. Cost Management
- No unified cost tracking
- Each service calculates costs differently
- No budget controls or alerts

### 3. Performance
- No centralized caching
- Redundant API calls for similar queries
- No performance monitoring

### 4. Observability
- Limited logging of LLM interactions
- No unified metrics collection
- Difficult to debug issues

### 5. Configuration
- API keys scattered across services
- Model names hardcoded
- No easy way to switch providers

## Opportunities

### 1. Unified Gateway Benefits
- Single point of LLM access
- Consistent error handling
- Centralized monitoring
- Easy A/B testing

### 2. Cost Optimization
- Semantic caching could save 30-50%
- Intelligent routing to cheaper models
- Budget controls and alerts
- Usage analytics

### 3. Performance Improvements
- Response caching
- Parallel model calls
- Optimized routing
- Connection pooling

### 4. Dashboard Integration
- Real-time cost monitoring
- Model performance comparison
- Configuration management
- Usage analytics

## Recommended Architecture

### 1. Unified LLM Service
```python
class UnifiedLLMService:
    """Single service for all LLM interactions"""
    
    def __init__(self):
        self.gateway = PortkeyGateway()  # or OpenRouter
        self.cache = SemanticCache()
        self.analytics = LLMAnalytics()
        self.router = IntelligentRouter()
    
    async def complete(
        self,
        prompt: str,
        task_type: TaskType,
        constraints: dict = None
    ) -> LLMResponse:
        # Check cache
        # Route to optimal model
        # Track costs
        # Return response
```

### 2. Configuration Management
```yaml
# config/llm_models.yaml
models:
  gpt-4:
    provider: openai
    cost_per_1k: 0.03
    capabilities: [reasoning, code, analysis]
    
  claude-3-opus:
    provider: anthropic
    cost_per_1k: 0.015
    capabilities: [reasoning, creativity, long_context]
```

### 3. Dashboard Integration
- Model selection UI
- Cost budgets and alerts
- Performance metrics
- A/B testing controls

## Migration Strategy

### Phase 1: Gateway Selection
1. Research and select optimal gateway
2. Configure with existing providers
3. Test performance and costs

### Phase 2: Service Migration
1. Create UnifiedLLMService
2. Migrate high-usage services first
3. Maintain backward compatibility

### Phase 3: Advanced Features
1. Implement semantic caching
2. Add intelligent routing
3. Build dashboard controls

### Phase 4: Optimization
1. Analyze usage patterns
2. Optimize model selection
3. Implement cost controls

## Next Steps

1. **Execute Research**: Use the research prompt to evaluate gateways
2. **Prototype**: Build proof-of-concept with top gateway
3. **Benchmark**: Compare performance and costs
4. **Plan Migration**: Detailed migration plan for all services
5. **Build Dashboard**: Design unified control interface

## Success Metrics

- **Cost Reduction**: 30-50% through caching and routing
- **Performance**: < 50ms additional latency
- **Reliability**: 99.9% uptime
- **Coverage**: 100% of LLM calls through gateway
- **Observability**: Full visibility into all LLM operations 