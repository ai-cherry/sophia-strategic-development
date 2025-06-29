# 🚀 SOPHIA AI PERFORMANCE OPTIMIZATION CODEX PROMPT

## **CONTEXT & OBJECTIVE**
You are tasked with implementing comprehensive performance optimizations for the Sophia AI enterprise business intelligence platform. The codebase consists of 146 Python files (79,991 lines) with critical performance bottlenecks that need immediate resolution.

**Current Performance Issues:**
- Database connection overhead: 200-500ms per connection (20 files creating individual connections)
- N+1 query patterns in 22 files causing massive database load
- Insufficient caching: Only 17% adoption rate, 15% cache hit ratio
- Memory inefficiencies and resource leaks
- Sequential agent processing causing 600ms workflow delays

**Target Performance Goals:**
- Database queries: 200-500ms → 10-50ms (90% improvement)
- Agent workflows: 600ms → 200ms (3x improvement)
- Cache hit ratio: 15% → 85% (5.7x improvement)
- Memory usage: 50% reduction
- Connection overhead: 95% reduction

---

## **TASK 1: IMPLEMENT OPTIMIZED CONNECTION POOLING**

### **Replace Individual Connections with Global Pool Manager**

**Files to Update (20 files with connection patterns):**
- `backend/utils/snowflake_cortex_service.py` (PRIORITY 1 - complexity: 712.1)
- `backend/agents/integrations/gong_data_integration.py`
- `backend/services/comprehensive_memory_service.py`
- All files containing `snowflake.connector.connect`

**Current Problematic Pattern to Replace:**
```python
# ❌ REMOVE THIS PATTERN
class ServiceClass:
    def __init__(self):
        self.connection = None
    
    async def initialize(self):
        self.connection = snowflake.connector.connect(
            user=config.get("snowflake_user"),
            password=config.get("snowflake_password"),
            account=config.get("snowflake_account"),
            warehouse=config.get("snowflake_warehouse")
        )
    
    async def execute_query(self, query: str):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
```

**Replace With Optimized Pattern:**
```python
# ✅ IMPLEMENT THIS PATTERN
from backend.core.optimized_connection_manager import connection_manager

class OptimizedServiceClass:
    async def execute_query(self, query: str, params: Optional[tuple] = None):
        return await connection_manager.execute_query(query, params)
    
    async def execute_batch_queries(self, queries: List[tuple]):
        return await connection_manager.execute_batch_queries(queries)
```

**Specific Implementation Instructions:**
1. **Import the optimized connection manager** in all 20 files
2. **Remove all individual connection initialization** code
3. **Replace all `cursor.execute()` calls** with `connection_manager.execute_query()`
4. **Add error handling** for connection failures
5. **Update all async functions** to use the connection manager context

---

## **TASK 2: FIX N+1 QUERY PATTERNS**

### **Optimize Database Access in 22 High-Usage Files**

**Critical Files with >10 DB Operations:**
- `backend/monitoring/gong_data_quality.py`
- `backend/scripts/test_gong_pipeline.py`
- `backend/core/snowflake_schema_integration.py`
- Files with loops containing individual queries

**Current N+1 Pattern to Fix:**
```python
# ❌ REMOVE THIS INEFFICIENT PATTERN
async def get_deal_insights(self, deal_ids: List[str]):
    insights = []
    for deal_id in deal_ids:  # N+1 problem!
        query = f"SELECT * FROM deals WHERE id = '{deal_id}'"
        result = await self.execute_query(query)
        insights.append(result)
    return insights

async def process_call_data(self, call_ids: List[str]):
    processed_calls = []
    for call_id in call_ids:  # Another N+1!
        call_query = f"SELECT * FROM gong_calls WHERE id = '{call_id}'"
        transcript_query = f"SELECT * FROM gong_transcripts WHERE call_id = '{call_id}'"
        call_data = await self.execute_query(call_query)
        transcript_data = await self.execute_query(transcript_query)
        processed_calls.append(combine_data(call_data, transcript_data))
    return processed_calls
```

**Replace With Batch Query Pattern:**
```python
# ✅ IMPLEMENT OPTIMIZED BATCH QUERIES
async def get_deal_insights_optimized(self, deal_ids: List[str]):
    if not deal_ids:
        return []
    
    # Single batch query instead of N queries
    placeholders = ','.join(['%s'] * len(deal_ids))
    query = f"SELECT * FROM deals WHERE id IN ({placeholders})"
    return await connection_manager.execute_query(query, tuple(deal_ids))

async def process_call_data_optimized(self, call_ids: List[str]):
    if not call_ids:
        return []
    
    # Batch queries for both calls and transcripts
    batch_queries = [
        (f"SELECT * FROM gong_calls WHERE id IN ({','.join(['%s'] * len(call_ids))})", tuple(call_ids)),
        (f"SELECT * FROM gong_transcripts WHERE call_id IN ({','.join(['%s'] * len(call_ids))})", tuple(call_ids))
    ]
    
    call_results, transcript_results = await connection_manager.execute_batch_queries(batch_queries)
    
    # Process results efficiently
    transcript_map = {t['call_id']: t for t in transcript_results}
    return [
        combine_data(call, transcript_map.get(call['id']))
        for call in call_results
    ]
```

**Implementation Requirements:**
1. **Identify all loops with individual queries** in the 22 files
2. **Convert to batch operations** using IN clauses or JOINs
3. **Add parameter binding** to prevent SQL injection
4. **Implement result mapping** for efficient data processing
5. **Add batch size limits** (max 1000 items per batch)

---

## **TASK 3: IMPLEMENT MULTI-LAYER CACHING SYSTEM**

### **Replace Simple Cache with Optimized Hierarchical Cache**

**Files to Update (25 files with cache usage):**
- `backend/core/hierarchical_cache.py` (replace entirely)
- All files using `cache.get()` or `cache.set()`
- Memory service and agent files

**Current Simple Cache to Replace:**
```python
# ❌ REMOVE THIS BASIC CACHE
class HierarchicalCache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    async def set(self, namespace: str, key: str, value: Any):
        self._cache.setdefault(namespace, {})[key] = value
    
    async def get(self, namespace: str, key: str):
        return self._cache.get(namespace, {}).get(key)
```

**Replace With Optimized Multi-Layer Cache:**
```python
# ✅ IMPLEMENT OPTIMIZED CACHING
from backend.core.optimized_cache import optimized_cache

# For embedding caching (high-frequency operations)
async def generate_embedding_cached(self, text: str) -> List[float]:
    cache_key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"
    
    # Check cache first
    cached_embedding = await optimized_cache.get(cache_key, "embeddings")
    if cached_embedding:
        return cached_embedding
    
    # Generate and cache
    embedding = await self.cortex_service.generate_embedding(text)
    await optimized_cache.set(cache_key, embedding, "embeddings", ttl=86400)  # 24 hours
    return embedding

# For query result caching
async def get_deal_data_cached(self, deal_id: str) -> Dict[str, Any]:
    cache_key = f"deal:{deal_id}"
    
    cached_data = await optimized_cache.get(cache_key, "deals")
    if cached_data:
        return cached_data
    
    # Fetch and cache
    deal_data = await self.fetch_deal_data(deal_id)
    await optimized_cache.set(cache_key, deal_data, "deals", ttl=3600)  # 1 hour
    return deal_data
```

**Caching Strategy Implementation:**
1. **Embedding cache**: TTL 24 hours, namespace "embeddings"
2. **Query results**: TTL 1 hour, namespace "queries"
3. **User sessions**: TTL 30 minutes, namespace "sessions"
4. **API responses**: TTL 5 minutes, namespace "api"
5. **Configuration data**: TTL 1 hour, namespace "config"

---

## **TASK 4: OPTIMIZE AGENT WORKFLOW ORCHESTRATION**

### **Convert Sequential to Concurrent Processing**

**Files to Update:**
- `backend/workflows/enhanced_langgraph_orchestration.py`
- Agent orchestration and workflow files
- Multi-agent processing systems

**Current Sequential Pattern to Replace:**
```python
# ❌ REMOVE SEQUENTIAL PROCESSING
async def process_workflow(self, state: WorkflowState):
    # Sequential - each waits for previous
    hubspot_data = await self.hubspot_agent.process(state.query)
    gong_data = await self.gong_agent.process(state.query)
    slack_data = await self.slack_agent.process(state.query)
    linear_data = await self.linear_agent.process(state.query)
    
    return self.combine_results(hubspot_data, gong_data, slack_data, linear_data)
```

**Replace With Concurrent Processing:**
```python
# ✅ IMPLEMENT CONCURRENT PROCESSING
async def process_workflow_optimized(self, state: WorkflowState):
    # Phase 1: Concurrent data collection
    data_collection_tasks = [
        self.hubspot_agent.process(state.query),
        self.gong_agent.process(state.query),
        self.slack_agent.process(state.query),
        self.linear_agent.process(state.query)
    ]
    
    # Wait for all data collection concurrently
    hubspot_data, gong_data, slack_data, linear_data = await asyncio.gather(
        *data_collection_tasks, return_exceptions=True
    )
    
    # Handle any exceptions
    processed_data = []
    for data in [hubspot_data, gong_data, slack_data, linear_data]:
        if isinstance(data, Exception):
            logger.error(f"Agent processing error: {data}")
            processed_data.append(None)
        else:
            processed_data.append(data)
    
    # Phase 2: Concurrent analysis
    analysis_tasks = [
        self.analyze_sales_data(processed_data[0], processed_data[1]),  # HubSpot + Gong
        self.analyze_communication_data(processed_data[2]),  # Slack
        self.analyze_project_data(processed_data[3])  # Linear
    ]
    
    analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
    
    # Phase 3: Final synthesis
    return await self.synthesize_results(processed_data, analysis_results)
```

---

## **TASK 5: OPTIMIZE VECTOR SEARCH OPERATIONS**

### **Replace Linear Search with Approximate Nearest Neighbor**

**Files to Update:**
- Memory service files with vector operations
- Embedding search functionality
- Semantic search implementations

**Current Inefficient Vector Search:**
```python
# ❌ REMOVE LINEAR SEARCH O(n)
async def recall_memories(self, query: str, top_k: int = 5):
    query_embedding = await self.generate_embedding(query)
    
    # Linear search - very slow for large datasets
    similarities = []
    for memory in self.all_memories:  # O(n) complexity!
        similarity = self.cosine_similarity(query_embedding, memory.embedding)
        similarities.append((memory, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]
```

**Replace With Optimized Vector Search:**
```python
# ✅ IMPLEMENT FAISS-BASED SEARCH O(log n)
import faiss
import numpy as np

class OptimizedVectorSearch:
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.index = faiss.IndexIVFFlat(
            faiss.IndexFlatL2(dimension), 
            dimension, 
            min(100, max(10, len(embeddings) // 100))  # Dynamic clusters
        )
        self.memory_map = {}
        self.is_trained = False
    
    async def add_memories(self, memories: List[Memory]):
        embeddings = np.array([m.embedding for m in memories]).astype('float32')
        
        if not self.is_trained and len(embeddings) > 100:
            self.index.train(embeddings)
            self.is_trained = True
        
        # Add to index
        start_id = len(self.memory_map)
        self.index.add(embeddings)
        
        # Update memory mapping
        for i, memory in enumerate(memories):
            self.memory_map[start_id + i] = memory
    
    async def search_memories(self, query_embedding: np.ndarray, top_k: int = 5):
        if not self.is_trained:
            return []
        
        # Fast approximate search
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'), 
            top_k
        )
        
        # Return memories with scores
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx in self.memory_map:
                similarity = 1.0 / (1.0 + distance)  # Convert distance to similarity
                results.append((self.memory_map[idx], similarity))
        
        return results
```

---

## **TASK 6: IMPLEMENT PERFORMANCE MONITORING**

### **Add Comprehensive Performance Tracking**

**Create Performance Monitoring Decorators:**
```python
# ✅ IMPLEMENT PERFORMANCE MONITORING
import time
import functools
from typing import Dict, Any
import asyncio

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            'database_query': 100,  # ms
            'agent_processing': 200,  # ms
            'cache_operation': 10,  # ms
            'vector_search': 50,  # ms
        }
    
    def monitor_performance(self, operation_type: str, alert_threshold: int = None):
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Log metrics
                    self.metrics[f"{operation_type}_{func.__name__}"] = {
                        'duration_ms': duration_ms,
                        'timestamp': time.time(),
                        'success': True
                    }
                    
                    # Alert on threshold breach
                    threshold = alert_threshold or self.thresholds.get(operation_type, 1000)
                    if duration_ms > threshold:
                        logger.warning(
                            f"⚠️ Performance Alert: {func.__name__} took {duration_ms:.1f}ms "
                            f"(threshold: {threshold}ms)"
                        )
                    
                    return result
                    
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    self.metrics[f"{operation_type}_{func.__name__}"] = {
                        'duration_ms': duration_ms,
                        'timestamp': time.time(),
                        'success': False,
                        'error': str(e)
                    }
                    raise
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    self.metrics[f"{operation_type}_{func.__name__}"] = {
                        'duration_ms': duration_ms,
                        'timestamp': time.time(),
                        'success': True
                    }
                    
                    threshold = alert_threshold or self.thresholds.get(operation_type, 1000)
                    if duration_ms > threshold:
                        logger.warning(
                            f"⚠️ Performance Alert: {func.__name__} took {duration_ms:.1f}ms"
                        )
                    
                    return result
                    
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    self.metrics[f"{operation_type}_{func.__name__}"] = {
                        'duration_ms': duration_ms,
                        'timestamp': time.time(),
                        'success': False,
                        'error': str(e)
                    }
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator

# Global monitor instance
performance_monitor = PerformanceMonitor()

# Usage examples to implement:
@performance_monitor.monitor_performance('database_query', 100)
async def execute_query(query: str):
    # Query implementation
    pass

@performance_monitor.monitor_performance('agent_processing', 200)
async def process_agent_request(request):
    # Agent processing
    pass
```

---

## **TASK 7: MEMORY OPTIMIZATION**

### **Implement Lazy Loading and Resource Management**

**Files to Optimize:**
- Large dataset processing files
- Memory-intensive operations
- Global variable usage

**Current Memory-Inefficient Pattern:**
```python
# ❌ REMOVE MEMORY-INTENSIVE PATTERNS
class DataProcessor:
    def __init__(self):
        self.large_datasets = {}  # Keeps everything in memory
        self.all_embeddings = []  # Grows indefinitely
    
    async def process_dataset(self, dataset_id: str):
        if dataset_id not in self.large_datasets:
            # Loads entire dataset into memory
            self.large_datasets[dataset_id] = self.load_full_dataset(dataset_id)
        return self.large_datasets[dataset_id]
```

**Replace With Memory-Optimized Pattern:**
```python
# ✅ IMPLEMENT LAZY LOADING AND LRU CACHE
from functools import lru_cache
import weakref

class OptimizedDataProcessor:
    def __init__(self, max_cache_size: int = 100):
        self._weak_cache = weakref.WeakValueDictionary()
        self.max_cache_size = max_cache_size
    
    @lru_cache(maxsize=100)
    async def process_dataset_chunk(self, dataset_id: str, chunk_id: int):
        # Process only required chunks
        return await self.load_dataset_chunk(dataset_id, chunk_id)
    
    async def process_dataset(self, dataset_id: str):
        # Stream processing instead of loading everything
        async for chunk in self.stream_dataset_chunks(dataset_id):
            yield await self.process_dataset_chunk(dataset_id, chunk.id)
    
    async def get_embeddings_batch(self, texts: List[str], batch_size: int = 100):
        # Process in batches to control memory usage
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = await self.generate_embeddings_batch(batch)
            yield embeddings
```

---

## **TASK 8: ERROR HANDLING AND RESILIENCE**

### **Add Circuit Breaker and Retry Logic**

**Implement Robust Error Handling:**
```python
# ✅ IMPLEMENT CIRCUIT BREAKER PATTERN
import asyncio
from typing import Callable, Any
import random

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            
            raise

async def retry_with_backoff(func: Callable, max_retries: int = 3, 
                           base_delay: float = 1.0, max_delay: float = 60.0):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
            await asyncio.sleep(delay)
```

---

## **IMPLEMENTATION CHECKLIST**

### **Priority 1 (Week 1) - Critical Performance Fixes:**
- [ ] **Replace all 20 individual connections** with optimized connection manager
- [ ] **Fix N+1 query patterns** in 22 high-usage files
- [ ] **Refactor snowflake_cortex_service.py** (highest complexity: 712.1)
- [ ] **Add performance monitoring** to all database operations
- [ ] **Deploy connection pooling** with health checks

### **Priority 2 (Week 2) - Caching and Concurrency:**
- [ ] **Implement multi-layer caching** system (L1/L2)
- [ ] **Convert sequential workflows** to concurrent processing
- [ ] **Add cache warming** strategies for frequently accessed data
- [ ] **Implement batch operations** for all multi-item requests
- [ ] **Add performance alerting** thresholds

### **Priority 3 (Week 3) - Advanced Optimizations:**
- [ ] **Deploy FAISS vector search** for 100x improvement
- [ ] **Implement lazy loading** for memory optimization
- [ ] **Add circuit breaker patterns** for resilience
- [ ] **Create performance dashboards** and monitoring
- [ ] **Optimize memory usage** with weak references and LRU caches

### **Testing Requirements:**
- [ ] **Load testing** with 100+ concurrent users
- [ ] **Performance benchmarking** before/after optimizations
- [ ] **Memory profiling** to verify 50% reduction
- [ ] **Database load testing** to confirm query optimization
- [ ] **Cache performance testing** to achieve 85% hit ratio

---

## **SUCCESS METRICS TO ACHIEVE**

**Database Performance:**
- Connection time: 200-500ms → 5-10ms (95% improvement)
- Query execution: Average <100ms for 99% of queries
- Connection pool utilization: <80% under normal load

**Application Performance:**
- Agent workflow time: 600ms → 200ms (3x improvement)
- API response time: Maintain <200ms for 95% of requests
- Memory usage: 50% reduction from current baseline

**Cache Performance:**
- Hit ratio: 15% → 85% (5.7x improvement)
- Cache response time: <5ms for L1, <20ms for L2
- Cache efficiency: >90% of frequently accessed data cached

**System Reliability:**
- Uptime: 99.9% → 99.95%
- Error rate: <0.1% for all operations
- Recovery time: <30 seconds for any failures

---

## **DEPLOYMENT STRATEGY**

**Phase 1: Core Infrastructure (Days 1-3)**
1. Deploy optimized connection manager
2. Update all database access patterns
3. Add basic performance monitoring

**Phase 2: Query Optimization (Days 4-7)**
1. Fix all N+1 query patterns
2. Implement batch operations
3. Add query performance tracking

**Phase 3: Caching System (Week 2)**
1. Deploy multi-layer cache
2. Implement cache warming
3. Add cache performance monitoring

**Phase 4: Advanced Features (Week 3)**
1. Concurrent processing
2. Vector search optimization
3. Memory management improvements

**Phase 5: Monitoring & Alerting (Week 4)**
1. Comprehensive dashboards
2. Performance alerting
3. Automated optimization

Execute these optimizations systematically to achieve the target 3-5x performance improvement while maintaining system reliability and sub-200ms response times.

