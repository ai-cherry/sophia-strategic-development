# AI SQL and Cortex Agent Interaction Lifecycle

## Overview

This document provides a comprehensive guide to the AI SQL query lifecycle in Sophia AI, from natural language input to execution via Lambda GPU, including the roles and interaction patterns of each Cortex Agent.

## Architecture Principles

### Modern Stack as the Center of the Universe
- **Data Locality**: AI processing happens where data lives
- **Cost Optimization**: Eliminates data movement costs (60-80% savings)
- **Performance**: Sub-100ms query execution with native AI functions
- **Security**: Enterprise-grade data governance and compliance

## AI SQL Query Lifecycle

### Phase 1: Natural Language Input Processing

```mermaid
flowchart TD
    A[User Query: "What are our top deals?"] --> B[SophiaUnifiedChatService]
    B --> C[Modern StackCortexService Intent Detection]
    C --> D[Query Classification]
    D --> E[Context Retrieval from AI Memory]
    E --> F[Task Routing Decision]
```

**Components:**
- **Input Handler**: `SophiaUnifiedChatService.process_query()`
- **Intent Detection**: `Modern StackCortexService.classify_intent()`
- **Context Retrieval**: `EnhancedAiMemoryMCPServer.recall_context()`

### Phase 2: Cortex Agent Selection and Orchestration

```python
# Intelligent routing based on query type
async def route_to_cortex_agent(query: str, intent: QueryIntent) -> CortexAgent:
    """
    Route queries to specialized Cortex Agents based on intent and complexity
    """
    routing_map = {
        QueryIntent.DATA_ANALYSIS: "snowflake_ops",
        QueryIntent.BUSINESS_INTELLIGENCE: "business_intelligence",
        QueryIntent.SEMANTIC_SEARCH: "semantic_memory",
        QueryIntent.SQL_OPTIMIZATION: "snowflake_ops",
        QueryIntent.SCHEMA_MANAGEMENT: "snowflake_ops"
    }

    return await get_cortex_agent(routing_map[intent])
```

### Phase 3: SQL Generation and Optimization

**Modern Stack Ops Agent** (`snowflake_ops`):
```sql
-- Native Cortex AI SQL generation
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mistral-large',
    'Generate SQL for: ' || :user_query,
    {'schema_context': :schema_info, 'optimization_hints': :performance_hints}
) as generated_sql;
```

**Business Intelligence Agent** (`business_intelligence`):
```sql
-- Advanced analytics with Cortex
SELECT
    deal_name,
    SNOWFLAKE.CORTEX.SENTIMENT(description) as sentiment_score,
    SNOWFLAKE.CORTEX.SUMMARIZE(notes) as deal_summary,
    SNOWFLAKE.CORTEX.EXTRACT_ANSWER(description, 'What is the deal value?') as extracted_value
FROM enriched_hubspot_deals;
```

### Phase 4: Execution and Result Processing

```python
class Modern StackCortexQueryExecutor:
    """
    Executes AI-generated SQL with performance monitoring and optimization
    """

    async def execute_ai_sql(self, sql: str, context: QueryContext) -> QueryResult:
        """
        Execute SQL with Cortex AI enhancements
        """
        # 1. Query validation and optimization
        optimized_sql = await self.optimize_query(sql)

        # 2. Execute with performance tracking
        start_time = time.time()
        result = await self.snowflake_connection.execute(optimized_sql)
        execution_time = time.time() - start_time

        # 3. AI enhancement of results
        enhanced_result = await self.enhance_with_cortex(result, context)

        # 4. Cache for future queries
        await self.cache_result(sql, enhanced_result, ttl=3600)

        return enhanced_result
```

## Cortex Agent Specifications

### 1. Modern Stack Ops Agent

**Role**: Database operations, query optimization, schema management

**Cortex Functions Used**:
- `SNOWFLAKE.CORTEX.COMPLETE()` - SQL generation
- `SNOWFLAKE.CORTEX.EXTRACT_ANSWER()` - Data extraction
- `SNOWFLAKE.CORTEX.CLASSIFY()` - Query classification

**Capabilities**:
```python
class Modern StackOpsAgent:
    """
    Specialized agent for PostgreSQL database operations
    """

    async def generate_sql(self, natural_language_query: str) -> str:
        """Generate optimized SQL from natural language"""

    async def optimize_query(self, sql: str) -> str:
        """Optimize SQL for performance"""

    async def manage_schema(self, operation: SchemaOperation) -> Result:
        """Handle schema modifications and validation"""
```

### 2. Semantic Memory Agent

**Role**: Multi-tiered memory system management and retrieval

**Architecture**:
- **L1 Cache**: Session context (<50ms)
- **L2 Cortex**: Lambda GPU Search (<100ms)
- **L3 Memory**: Persistent AI Memory (<200ms)
- **L4 Knowledge**: Knowledge Graph (<300ms)
- **L5 Workflow**: LangGraph patterns (<400ms)

**Cortex Functions Used**:
- `SNOWFLAKE.CORTEX.EMBED_TEXT()` - Vector generation
- `SNOWFLAKE.CORTEX.VECTOR_SIMILARITY()` - Semantic search
- `SNOWFLAKE.CORTEX.COMPLETE()` - Context synthesis

### 3. Business Intelligence Agent

**Role**: Executive insights, KPI analysis, predictive analytics

**Cortex Functions Used**:
- `SNOWFLAKE.CORTEX.SENTIMENT()` - Sentiment analysis
- `SNOWFLAKE.CORTEX.SUMMARIZE()` - Executive summaries
- `SNOWFLAKE.CORTEX.COMPLETE()` - Insight generation
- `SNOWFLAKE.CORTEX.FORECAST()` - Predictive modeling

**Sample Workflows**:
```sql
-- Executive Deal Analysis
WITH deal_insights AS (
    SELECT
        deal_name,
        amount,
        SNOWFLAKE.CORTEX.SENTIMENT(sales_notes) as sentiment,
        SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
            sales_notes,
            'What are the main risks for this deal?'
        ) as risk_factors,
        SNOWFLAKE.CORTEX.CLASSIFY(
            stage,
            ['qualified', 'proposal', 'negotiation', 'closed']
        ) as normalized_stage
    FROM hubspot_deals
    WHERE amount > 50000
)
SELECT
    deal_name,
    amount,
    sentiment,
    risk_factors,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mistral-large',
        'Based on this deal data, provide executive recommendations: ' ||
        OBJECT_CONSTRUCT(
            'amount', amount,
            'sentiment', sentiment,
            'risks', risk_factors,
            'stage', normalized_stage
        )::STRING
    ) as executive_recommendations
FROM deal_insights;
```

## Performance Optimization Patterns

### 1. Connection Pooling
```python
class OptimizedModern StackConnection:
    """
    95% overhead reduction through connection pooling
    """
    def __init__(self):
        self.pool_size = 20
        self.max_overflow = 30
        self.pool_timeout = 30
```

### 2. Batch Processing
```python
# 10-20x performance improvement through batching
async def batch_cortex_operations(operations: List[CortexOperation]) -> List[Result]:
    """
    Process multiple Cortex operations in optimized batches
    """
    batch_size = 50
    results = []

    for i in range(0, len(operations), batch_size):
        batch = operations[i:i + batch_size]
        batch_results = await execute_batch_cortex(batch)
        results.extend(batch_results)

    return results
```

### 3. Intelligent Caching
```python
class CortexResultCache:
    """
    85% cache hit ratio target with semantic similarity
    """

    async def get_cached_result(self, query: str, similarity_threshold: float = 0.85):
        """Check cache with semantic similarity matching"""

    async def cache_result(self, query: str, result: Any, ttl: int = 3600):
        """Cache result with intelligent TTL based on query type"""
```

## Error Handling and Fallback Strategies

### Cortex Function Fallbacks
```python
async def cortex_complete_with_fallback(prompt: str, model: str = 'mistral-large'):
    """
    Robust Cortex completion with intelligent fallbacks
    """
    try:
        return await cortex_complete(prompt, model)
    except CortexCapacityError:
        # Fallback to alternative Cortex model
        return await cortex_complete(prompt, 'llama2-70b-chat')
    except CortexUnavailableError:
        # Fallback to external LLM via Portkey
        return await portkey_complete(prompt)
```

### Circuit Breaker Pattern
```python
class CortexCircuitBreaker:
    """
    Prevent cascade failures in Cortex operations
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
```

## Integration with Unified Chat Interface

### Query Processing Pipeline
```python
class UnifiedChatCortexIntegration:
    """
    Integration between chat interface and Cortex agents
    """

    async def process_chat_query(self, query: str, user_context: UserContext):
        """
        Complete pipeline from chat input to Cortex-enhanced response
        """
        # 1. Intent detection using Cortex
        intent = await self.cortex_classify_intent(query)

        # 2. Context retrieval from AI Memory
        context = await self.ai_memory.recall_relevant_context(query, intent)

        # 3. Route to appropriate Cortex agent
        agent = await self.select_cortex_agent(intent)

        # 4. Execute with context
        result = await agent.process_query(query, context)

        # 5. Enhance response with additional Cortex insights
        enhanced_result = await self.enhance_response(result, intent)

        # 6. Store in AI Memory for future context
        await self.ai_memory.store_interaction(query, enhanced_result)

        return enhanced_result
```

## Monitoring and Analytics

### Performance Metrics
```python
class CortexPerformanceMetrics:
    """
    Comprehensive monitoring for Cortex operations
    """

    metrics = {
        "query_execution_time": Histogram("cortex_query_duration_seconds"),
        "cache_hit_ratio": Gauge("cortex_cache_hit_ratio"),
        "agent_utilization": Counter("cortex_agent_requests_total"),
        "error_rate": Counter("cortex_errors_total"),
        "cost_per_query": Gauge("cortex_cost_per_query_dollars")
    }
```

### Quality Assurance
```python
async def validate_cortex_response(response: str, query_context: QueryContext) -> ValidationResult:
    """
    Validate Cortex responses for quality and relevance
    """
    validations = [
        await check_response_completeness(response),
        await check_business_context_accuracy(response, query_context),
        await check_sql_syntax_validity(response) if query_context.expects_sql else None,
        await check_data_consistency(response, query_context.expected_data_types)
    ]

    return ValidationResult(
        valid=all(v.passed for v in validations if v),
        quality_score=calculate_quality_score(validations),
        improvement_suggestions=extract_suggestions(validations)
    )
```

## Best Practices and Guidelines

### 1. Query Design Patterns
- **Specific Context**: Always provide business context with queries
- **Performance Hints**: Include optimization hints for complex queries
- **Error Resilience**: Design queries with fallback strategies

### 2. Agent Selection Logic
```python
def select_optimal_cortex_agent(query_intent: QueryIntent, complexity: int) -> str:
    """
    Select the most appropriate Cortex agent based on query characteristics
    """
    if query_intent in [QueryIntent.DATA_ANALYSIS, QueryIntent.SQL_GENERATION]:
        return "snowflake_ops"
    elif query_intent == QueryIntent.BUSINESS_INSIGHTS:
        return "business_intelligence"
    elif query_intent == QueryIntent.SEMANTIC_SEARCH:
        return "semantic_memory"
    else:
        return "snowflake_ops"  # Default fallback
```

### 3. Cost Optimization
- **Data Locality**: Keep AI processing close to data
- **Caching Strategy**: Implement intelligent caching with semantic similarity
- **Batch Operations**: Group similar operations for efficiency
- **Model Selection**: Use appropriate Cortex models for task complexity

## Troubleshooting Guide

### Common Issues and Solutions

**Issue**: Slow Cortex query performance
**Solution**:
- Check warehouse size and scaling policies
- Implement query result caching
- Optimize SQL query structure
- Use batch processing for multiple operations

**Issue**: Cortex function errors
**Solution**:
- Implement circuit breaker pattern
- Add fallback to alternative models
- Validate input parameters
- Monitor Cortex service status

**Issue**: Inconsistent AI responses
**Solution**:
- Improve prompt engineering with better context
- Implement response validation
- Use consistent model parameters
- Add quality scoring mechanisms

## Future Enhancements

1. **Advanced Multi-Modal Support**: Integration with Cortex's multi-modal capabilities
2. **Automated Query Optimization**: Machine learning-based query optimization
3. **Predictive Caching**: AI-powered cache warming based on usage patterns
4. **Cross-Database Intelligence**: Extend Cortex patterns to other data sources

---

This comprehensive lifecycle documentation serves as the definitive guide for understanding and implementing AI SQL and Cortex Agent interactions within the Sophia AI platform.
