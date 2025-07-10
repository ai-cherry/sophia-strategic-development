# 🧠 SOPHIA AI MEMORY ECOSYSTEM MODERNIZATION PLAN (INTEGRATED)

**Status:** Ready for Execution  
**Date:** July 10, 2025  
**Version:** 4.0 - Unified & Enhanced  
**Supersedes:** All previous memory upgrade documents  

---

## 📋 Executive Summary

This plan integrates advanced memory modernization recommendations with our current Phase 2 Week 2 state, providing a clear path to a unified, high-performance memory ecosystem. We build on the successful n8n workflow automation implementation to add comprehensive memory improvements.

### Key Objectives
- **Eliminate ALL data silos** (especially MCP in-memory storage)
- **Remove Pinecone completely** (70% cost savings expected)
- **Implement advanced features**: RAG pipelines, hybrid search, observability
- **Add enterprise governance**: PII detection, archiving, audit trails
- **Achieve sub-250ms p95 latency** for all memory operations

---

## 🔍 Current State Analysis

### ✅ What's Working Well
1. **UnifiedMemoryService** implemented with 6-tier architecture
2. **Snowflake Cortex** integration functional (L3-L5)
3. **Redis** connected for L1 caching
4. **Memory Service Adapter** bridging orchestrator needs
5. **n8n workflow automation** (Phase 2 Week 2 complete)

### ❌ Critical Violations Identified

| ID | Component | Severity | Impact |
|----|-----------|----------|---------|
| V-1 | AI Memory MCP Server | **CRITICAL** | In-memory dict, no persistence, data loss risk |
| V-2 | Pinecone Dependencies | **CRITICAL** | 20+ files reference forbidden tech, cost bloat |
| V-3 | Scripts with Direct Imports | **HIGH** | Violates architecture rules |
| V-4 | Config: `pinecone_enabled: true` | **HIGH** | Encourages forbidden usage |
| V-5 | Missing Redis Helpers | **MEDIUM** | Inconsistent caching patterns |
| V-6 | No Hybrid Search | **MEDIUM** | 3-5x slower BI queries |
| V-7 | No RAG Pipelines | **MEDIUM** | Underutilizes Cortex capabilities |
| V-8 | No Observability | **MEDIUM** | Blind to performance issues |

---

## 🎯 Target Architecture

### Memory Tiers (Enhanced)
```
L0: GPU Cache (Lambda Labs) - Not managed
L1: Redis (Hot Cache) - Sub-ms vector caching + TTL management
L2: Mem0 (Agent Memory) - Conversational context
L3: Snowflake Cortex (Vectors) - Primary store with hybrid search
L4: Snowflake Tables (Data) - Structured + archive tier
L5: Snowflake Cortex AI (Intelligence) - RAG pipelines + governance
```

### Key Enhancements
- **Hybrid Retrieval**: Keyword pre-filter + vector similarity
- **RAG Pipelines**: Chunk → Embed → Cache → Search → Summarize
- **Observability**: Prometheus metrics + Cortex tracing
- **Governance**: PII classification, retention policies
- **Interoperability**: Apache Iceberg support for open formats

---

## 🚀 Implementation Phases

### Phase 1: Compliance & Safety (1 unit)
**Goal:** Remove all violations and forbidden technology

#### 1.1 Purge Pinecone & Legacy Code
```bash
# Files to delete/archive
infrastructure/services/comprehensive_memory_service.py → archive/
mcp-servers/mem0_*/* → archive/
scripts/*pinecone*.py → delete
scripts/*weaviate*.py → delete
```

#### 1.2 Update Configuration
```yaml
# config/unified_mcp_configuration.yaml
ai-memory:
  config:
    pinecone_enabled: false  # Changed from true
    persistence: "snowflake"  # New field
```

#### 1.3 Pre-commit Validation
```python
# scripts/validate_memory_architecture.py - Add to existing
FORBIDDEN_IMPORTS = ['pinecone', 'weaviate', 'chromadb', 'qdrant']

def check_imports(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    for forbidden in FORBIDDEN_IMPORTS:
        if f"import {forbidden}" in content or f"from {forbidden}" in content:
            raise ValueError(f"Forbidden import '{forbidden}' in {file_path}")
```

### Phase 2: MCP Refactor to Unified Proxy (1 unit)
**Goal:** Convert AI Memory MCP from in-memory to UnifiedMemoryService proxy

#### 2.1 Refactor AI Memory MCP Server
```python
# mcp-servers/ai_memory/server_v3.py
from backend.services.unified_memory_service import get_unified_memory_service

class AIMemoryServer(StandardizedMCPServer):
    def __init__(self):
        super().__init__(config)
        self.memory = get_unified_memory_service()
        
    async def _store_memory(self, params: dict[str, Any]) -> dict[str, Any]:
        """Store using UnifiedMemoryService with BI enrichment"""
        # Add BI source tracking
        metadata = params.get("metadata", {})
        metadata["mcp_source"] = "ai_memory"
        metadata["bi_type"] = params.get("bi_type", "general")
        
        # Chunk for large content (e.g., Notion docs)
        content = params["content"]
        if len(content) > 2000:  # ~512 tokens
            chunks = self._chunk_text(content, max_tokens=512)
            ids = []
            for chunk in chunks:
                memory_id = await self.memory.add_knowledge(
                    content=chunk,
                    source=params.get("source", "mcp"),
                    metadata=metadata
                )
                ids.append(memory_id)
            return {"status": "success", "memory_ids": ids}
        else:
            memory_id = await self.memory.add_knowledge(
                content=content,
                source=params.get("source", "mcp"),
                metadata=metadata
            )
            return {"status": "success", "memory_id": memory_id}
```

#### 2.2 Kubernetes Deployment Update
```yaml
# infrastructure/kubernetes/mcp/ai-memory-deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: ai-memory
        env:
        - name: UNIFIED_MEMORY_BACKEND
          value: "snowflake"
        - name: ENABLE_PERSISTENCE
          value: "true"
```

### Phase 3: Redis Layer Enhancement (1 unit)
**Goal:** Add generic cache helpers with vector support

#### 3.1 Create Redis Helper Module
```python
# backend/core/redis_helper.py
import json
import logging
from typing import Any, Optional
from datetime import timedelta
import redis
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

# Metrics
cache_hits = Counter('redis_cache_hits', 'Cache hit count')
cache_misses = Counter('redis_cache_misses', 'Cache miss count')
cache_latency = Histogram('redis_cache_latency_seconds', 'Cache operation latency')

class RedisHelper:
    def __init__(self, client: redis.Redis):
        self.client = client
        self.default_ttl = 3600  # 1 hour
        
    @cache_latency.time()
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get from cache with metrics"""
        try:
            value = self.client.get(key)
            if value:
                cache_hits.inc()
                return json.loads(value)
            else:
                cache_misses.inc()
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
            
    @cache_latency.time()
    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set in cache with TTL"""
        try:
            self.client.setex(
                key,
                ttl or self.default_ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            
    async def cache_vector(self, key: str, vector: list[float], metadata: dict):
        """Cache vector with metadata for fast retrieval"""
        cache_data = {
            "vector": vector,
            "metadata": metadata,
            "cached_at": datetime.utcnow().isoformat()
        }
        await self.cache_set(f"vector:{key}", cache_data, ttl=7200)  # 2 hours
```

#### 3.2 Integrate into UnifiedMemoryService
```python
# backend/services/unified_memory_service.py - Add to class
from backend.core.redis_helper import RedisHelper

def __init__(self):
    # ... existing init ...
    self.redis_helper = RedisHelper(self.redis_client) if self.redis_client else None
    
async def search_knowledge(self, query: str, limit: int = 10, **kwargs):
    """Enhanced search with Redis caching"""
    # Check cache first
    cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}"
    if self.redis_helper:
        cached = await self.redis_helper.cache_get(cache_key)
        if cached:
            return cached
            
    # Perform search (existing logic)
    results = await self._perform_search(query, limit, **kwargs)
    
    # Cache results
    if self.redis_helper and results:
        await self.redis_helper.cache_set(cache_key, results, ttl=1800)
        
    return results
```

### Phase 4: Hybrid Search & Tiering (2 units)
**Goal:** Implement keyword+vector search and automatic archiving

#### 4.1 Add Hybrid Search
```python
# backend/services/unified_memory_service.py - New method
async def search_knowledge_hybrid(
    self, 
    query: str, 
    limit: int = 10,
    keyword_filter: Optional[str] = None,
    metadata_filter: Optional[dict] = None
):
    """Hybrid search: keyword pre-filter + vector similarity"""
    if self.degraded_mode:
        return []
        
    try:
        # Extract keywords if not provided
        if not keyword_filter:
            # Simple keyword extraction (first significant word)
            keywords = [w for w in query.split() if len(w) > 3]
            keyword_filter = keywords[0] if keywords else None
            
        # Build hybrid SQL
        sql = f"""
        WITH keyword_matches AS (
            SELECT id, content, embedding, metadata, 
                   VECTOR_COSINE_SIMILARITY(
                       embedding, 
                       SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s)
                   ) as similarity_score
            FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE
            WHERE tier != 'ARCHIVED'
            {"AND content ILIKE %s" if keyword_filter else ""}
            {"AND metadata::string LIKE %s" if metadata_filter else ""}
        )
        SELECT * FROM keyword_matches
        WHERE similarity_score > 0.7
        ORDER BY similarity_score DESC
        LIMIT %s
        """
        
        # Prepare parameters
        params = [query]
        if keyword_filter:
            params.append(f"%{keyword_filter}%")
        if metadata_filter:
            params.append(f"%{json.dumps(metadata_filter)}%")
        params.append(limit)
        
        cursor = self.snowflake_conn.cursor(DictCursor)
        cursor.execute(sql, params)
        results = cursor.fetchall()
        cursor.close()
        
        # Update access counts
        if results:
            update_sql = """
            UPDATE AI_MEMORY.VECTORS.KNOWLEDGE_BASE
            SET access_count = access_count + 1,
                last_accessed = CURRENT_TIMESTAMP()
            WHERE id IN ({})
            """.format(','.join(['%s'] * len(results)))
            
            cursor = self.snowflake_conn.cursor()
            cursor.execute(update_sql, [r['id'] for r in results])
            self.snowflake_conn.commit()
            cursor.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        return []
```

#### 4.2 Create Archive Table and Task
```sql
-- Run in Snowflake
CREATE TABLE IF NOT EXISTS AI_MEMORY.VECTORS.KNOWLEDGE_BASE_ARCHIVE 
LIKE AI_MEMORY.VECTORS.KNOWLEDGE_BASE;

ALTER TABLE AI_MEMORY.VECTORS.KNOWLEDGE_BASE ADD COLUMN IF NOT EXISTS 
    tier VARCHAR DEFAULT 'HOT',
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP();

CREATE OR REPLACE TASK AI_MEMORY.TASKS.ARCHIVE_COLD_MEMORIES
    WAREHOUSE = SOPHIA_AI_COMPUTE_WH
    SCHEDULE = 'USING CRON 0 2 * * * UTC'  -- 2 AM UTC daily
AS
INSERT INTO AI_MEMORY.VECTORS.KNOWLEDGE_BASE_ARCHIVE
SELECT * FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE
WHERE last_accessed < DATEADD(day, -30, CURRENT_TIMESTAMP())
  AND access_count < 5
  AND tier = 'HOT';

DELETE FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE
WHERE id IN (
    SELECT id FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE_ARCHIVE
);

ALTER TASK AI_MEMORY.TASKS.ARCHIVE_COLD_MEMORIES RESUME;
```

### Phase 5: RAG Pipelines & Governance (2 units)
**Goal:** Add secure RAG with PII detection

#### 5.1 Implement RAG Pipeline
```python
# backend/services/rag_pipeline_service.py
from typing import List, Dict, Any
import logging
from backend.services.unified_memory_service import get_unified_memory_service
from backend.core.unified_config import UnifiedConfig

logger = logging.getLogger(__name__)

class RAGPipelineService:
    def __init__(self):
        self.memory = get_unified_memory_service()
        self.chunk_size = 512  # tokens
        self.overlap = 50  # token overlap
        
    async def build_rag_pipeline(
        self,
        query: str,
        sources: List[str],
        include_citations: bool = True,
        detect_pii: bool = True
    ) -> Dict[str, Any]:
        """Complete RAG pipeline with governance"""
        
        # 1. Detect PII in query
        if detect_pii:
            pii_check = await self._detect_pii(query)
            if pii_check["has_pii"]:
                query = pii_check["redacted_text"]
                
        # 2. Search across sources with hybrid approach
        search_results = []
        for source in sources:
            results = await self.memory.search_knowledge_hybrid(
                query=query,
                limit=5,
                metadata_filter={"source": source}
            )
            search_results.extend(results)
            
        # 3. Rank and deduplicate
        ranked_results = self._rank_results(search_results, query)
        
        # 4. Generate context from top results
        context = self._build_context(ranked_results[:10])
        
        # 5. Generate response using Cortex
        response = await self._generate_response(query, context)
        
        # 6. Add citations if requested
        if include_citations:
            response["citations"] = [
                {
                    "id": r["id"],
                    "source": r["metadata"].get("source"),
                    "content": r["content"][:200] + "..."
                }
                for r in ranked_results[:3]
            ]
            
        # 7. Cache the response
        if self.memory.redis_helper:
            cache_key = f"rag:{hashlib.md5(query.encode()).hexdigest()}"
            await self.memory.redis_helper.cache_set(
                cache_key, 
                response, 
                ttl=3600
            )
            
        return response
        
    async def _detect_pii(self, text: str) -> Dict[str, Any]:
        """Use Snowflake Cortex to detect PII"""
        if not self.memory.snowflake_conn:
            return {"has_pii": False, "redacted_text": text}
            
        try:
            sql = """
            SELECT SNOWFLAKE.CORTEX.CLASSIFY_TEXT(%s, 
                ['EMAIL', 'PHONE', 'SSN', 'CREDIT_CARD']) as pii_detection
            """
            cursor = self.memory.snowflake_conn.cursor()
            cursor.execute(sql, (text,))
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0]:
                # Redact detected PII
                # This is simplified - in production use proper redaction
                redacted = text
                for entity in result[0]:
                    if entity["confidence"] > 0.8:
                        redacted = redacted.replace(entity["text"], "[REDACTED]")
                        
                return {
                    "has_pii": True,
                    "redacted_text": redacted,
                    "entities": result[0]
                }
                
        except Exception as e:
            logger.error(f"PII detection failed: {e}")
            
        return {"has_pii": False, "redacted_text": text}
```

#### 5.2 Add Observability
```python
# backend/services/unified_memory_service.py - Add metrics
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
memory_operations = Counter(
    'memory_operations_total',
    'Total memory operations',
    ['operation', 'status']
)
memory_latency = Histogram(
    'memory_operation_latency_seconds',
    'Memory operation latency',
    ['operation']
)
snowflake_credits = Gauge(
    'snowflake_credits_used',
    'Snowflake credits consumed'
)

# Decorate methods
@memory_latency.labels(operation='add_knowledge').time()
async def add_knowledge(self, content: str, source: str, metadata: dict):
    """Add knowledge with metrics"""
    try:
        result = await self._add_knowledge_impl(content, source, metadata)
        memory_operations.labels(operation='add_knowledge', status='success').inc()
        return result
    except Exception as e:
        memory_operations.labels(operation='add_knowledge', status='error').inc()
        raise
```

### Phase 6: Advanced Features (2 units)
**Goal:** Embedding versioning, SDK, and scaling

#### 6.1 Embedding Versioning
```python
# scripts/reembed_with_version.py
"""Re-embed content with new model version"""
import asyncio
from backend.services.unified_memory_service import get_unified_memory_service

async def reembed_batch(model_name: str = "e5-large-v2", batch_size: int = 100):
    memory = get_unified_memory_service(require_snowflake=True)
    
    # Create new version table
    create_sql = """
    CREATE TABLE IF NOT EXISTS AI_MEMORY.VECTORS.KNOWLEDGE_BASE_V2
    LIKE AI_MEMORY.VECTORS.KNOWLEDGE_BASE;
    
    ALTER TABLE AI_MEMORY.VECTORS.KNOWLEDGE_BASE_V2 
    ADD COLUMN embedding_model VARCHAR DEFAULT %s,
    ADD COLUMN embedding_version INTEGER DEFAULT 2;
    """
    
    cursor = memory.snowflake_conn.cursor()
    cursor.execute(create_sql, (model_name,))
    
    # Re-embed in batches
    select_sql = """
    SELECT id, content, source, metadata 
    FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE
    LIMIT %s OFFSET %s
    """
    
    offset = 0
    while True:
        cursor.execute(select_sql, (batch_size, offset))
        rows = cursor.fetchall()
        if not rows:
            break
            
        # Re-embed batch
        for row in rows:
            new_embedding_sql = """
            INSERT INTO AI_MEMORY.VECTORS.KNOWLEDGE_BASE_V2
            (id, content, embedding, source, metadata, embedding_model)
            SELECT 
                %s, %s, 
                SNOWFLAKE.CORTEX.EMBED_TEXT_768(%s, %s),
                %s, %s, %s
            """
            cursor.execute(
                new_embedding_sql,
                (row['id'], row['content'], model_name, row['content'],
                 row['source'], row['metadata'], model_name)
            )
            
        memory.snowflake_conn.commit()
        offset += batch_size
        print(f"Re-embedded {offset} records...")
        
    # Atomic swap
    cursor.execute("""
    ALTER TABLE AI_MEMORY.VECTORS.KNOWLEDGE_BASE 
    RENAME TO KNOWLEDGE_BASE_OLD;
    
    ALTER TABLE AI_MEMORY.VECTORS.KNOWLEDGE_BASE_V2 
    RENAME TO KNOWLEDGE_BASE;
    """)
    
    cursor.close()
    print("✅ Re-embedding complete!")

if __name__ == "__main__":
    asyncio.run(reembed_batch())
```

#### 6.2 TypeScript SDK
```typescript
// libs/utils/memoryClient.ts
export class SophiaMemoryClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(config: { baseUrl: string; apiKey: string }) {
    this.baseUrl = config.baseUrl;
    this.apiKey = config.apiKey;
  }

  async addMemory(content: string, metadata?: Record<string, any>) {
    const response = await fetch(`${this.baseUrl}/api/v4/memory/add`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content,
        metadata: {
          ...metadata,
          source: 'typescript-sdk',
          timestamp: new Date().toISOString()
        }
      })
    });
    
    return response.json();
  }

  async search(query: string, options?: {
    limit?: number;
    sources?: string[];
    useHybrid?: boolean;
  }) {
    const params = new URLSearchParams({
      q: query,
      limit: String(options?.limit || 10),
      hybrid: String(options?.useHybrid || true)
    });
    
    if (options?.sources) {
      params.append('sources', options.sources.join(','));
    }
    
    const response = await fetch(
      `${this.baseUrl}/api/v4/memory/search?${params}`,
      {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        }
      }
    );
    
    return response.json();
  }
}
```

---

## 📊 Success Metrics & Validation

### Performance Targets
| Metric | Current | Target | Measurement |
|--------|---------|---------|-------------|
| Vector Query p95 | ~800ms | <250ms | Prometheus |
| Redis Hit Ratio | 0% | >70% | Redis metrics |
| Snowflake Credits/Query | 1.0 | <0.4 | Cortex monitoring |
| Data Silos | 1+ | 0 | Audit script |
| PII Coverage | 0% | 95% | Governance report |

### Validation Script
```python
# scripts/validate_memory_modernization.py
async def validate_phase_completion(phase: int):
    """Validate phase completion criteria"""
    
    if phase == 1:
        # Check no Pinecone imports
        assert not grep_forbidden_imports()
        # Check config updated
        assert not check_pinecone_enabled()
        
    elif phase == 2:
        # Check MCP using unified memory
        assert test_mcp_persistence()
        
    elif phase == 3:
        # Check Redis metrics
        assert get_redis_hit_ratio() > 0.5
        
    elif phase == 4:
        # Check hybrid search performance
        assert test_hybrid_search_latency() < 300
        
    elif phase == 5:
        # Check RAG pipeline
        assert test_rag_with_citations()
        # Check PII detection
        assert test_pii_detection()
        
    elif phase == 6:
        # Check embedding versioning
        assert check_embedding_metadata()
        # Check SDK connectivity
        assert test_typescript_sdk()
```

---

## 🎯 Next Steps

1. **Immediate Actions** (Today)
   - Archive Pinecone code
   - Update MCP configuration
   - Deploy validation scripts

2. **This Week**
   - Complete Phase 1-2
   - Start Redis enhancements
   - Begin hybrid search implementation

3. **Next Sprint**
   - Complete Phase 3-4
   - Deploy RAG pipelines
   - Add observability dashboards

---

## 📚 References

- [Snowflake Cortex Best Practices](https://docs.snowflake.com/en/user-guide/snowflake-cortex/overview)
- [Redis Vector Similarity](https://redis.io/docs/stack/search/reference/vectors/)
- [RAG Implementation Guide](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- Current System Handbook: `/docs/system_handbook/00_SOPHIA_AI_SYSTEM_HANDBOOK.md`

---

**Remember**: Each phase builds on the previous. Validate thoroughly before proceeding. The goal is a unified, performant, governed memory ecosystem that scales with Sophia AI's growth. 