# 🧠 Sophia AI Unified Memory Architecture

**Date:** July 9, 2025  
**Status:** DEFINITIVE ARCHITECTURE  
**Version:** 1.0  
**Authority:** This document supersedes ALL other memory architecture documentation

---

## Executive Summary

The Sophia AI platform implements a unified 6-tier memory architecture that consolidates all memory operations through a single service. This architecture eliminates the fragmentation caused by multiple vector databases and establishes Snowflake as the center of all intelligent operations.

### Key Principles

1. **Single Source of Truth**: All memory operations go through `UnifiedMemoryService`
2. **Snowflake is the Center**: All vector operations use Snowflake Cortex
3. **No Direct Database Access**: Applications never access memory stores directly
4. **Date Awareness**: The system knows today is July 9, 2025

---

## 🏗️ The 6-Tier Memory Architecture

### Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│                  (Uses UnifiedMemoryService)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  UnifiedMemoryService                        │
│            (Single Entry Point for ALL Memory)               │
└──┬──────────┬──────────┬──────────┬──────────┬─────────────┘
   │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼
┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
│  L1  │  │  L2  │  │  L3  │  │  L4  │  │  L5  │
│Redis │  │ Mem0 │  │Cortex│  │Tables│  │ AI   │
│Cache │  │Agent │  │Vector│  │ Data │  │Intel │
└──────┘  └──────┘  └──────┘  └──────┘  └──────┘
```

### Tier Details

#### L0: GPU Cache (Lambda Labs)
- **Purpose**: Hardware-level caching on GPU instances
- **Management**: Automatic by CUDA/hardware
- **Sophia Involvement**: None (transparent to application)
- **Use Cases**: Model weights, computation caching

#### L1: Redis (Ephemeral Cache)
- **Purpose**: Short-term session data and caching
- **TTL**: < 24 hours (configurable)
- **Access Pattern**: Key-value lookups
- **Use Cases**:
  - Session state
  - API response caching
  - Pub/sub messaging
  - Rate limiting counters
- **Methods**:
  ```python
  memory.cache_get(key)
  memory.cache_set(key, value, ttl=3600)
  memory.cache_delete(key)
  ```

#### L2: Mem0 (Agent Conversational Memory)
- **Purpose**: Agent-specific conversational context
- **Persistence**: Medium-term (days to weeks)
- **Access Pattern**: User/session-based retrieval
- **Use Cases**:
  - Chat history
  - User preferences
  - Conversation context
  - Agent learning
- **Methods**:
  ```python
  memory.remember_conversation(user_id, content, metadata)
  memory.recall_conversations(user_id, query, limit=10)
  ```

#### L3: Snowflake Cortex (Vector Knowledge Base)
- **Purpose**: Primary semantic search and knowledge storage
- **Persistence**: Long-term
- **Access Pattern**: Vector similarity search
- **Use Cases**:
  - Document search
  - Knowledge retrieval
  - Semantic matching
  - Content recommendations
- **Methods**:
  ```python
  memory.search_knowledge(query, limit=10, metadata_filter)
  memory.add_knowledge(content, source, metadata)
  ```

#### L4: Snowflake Tables (Structured Data)
- **Purpose**: Traditional relational data storage
- **Persistence**: Permanent
- **Access Pattern**: SQL queries
- **Use Cases**:
  - Business data
  - Transaction records
  - User profiles
  - System configuration
- **Methods**:
  ```python
  memory.query_warehouse(sql, params)
  ```

#### L5: Snowflake Cortex AI (Intelligence Layer)
- **Purpose**: AI-powered data operations
- **Functions**: SQL generation, sentiment analysis, summarization
- **Access Pattern**: Natural language to insights
- **Use Cases**:
  - Natural language SQL
  - Content analysis
  - Automatic summarization
  - Sentiment scoring
- **Methods**:
  ```python
  memory.generate_sql_from_natural_language(query, schema)
  memory.analyze_sentiment(text)
  ```

---

## 🚫 Forbidden Technologies

The following vector databases are **BANNED** from the Sophia AI codebase:

### ❌ Pinecone
- **Status**: DEPRECATED - Being migrated to Snowflake
- **Migration Tool**: `scripts/migrate_vectors_to_snowflake.py --source pinecone`
- **Replacement**: Use `memory.search_knowledge()` instead

### ❌ Weaviate
- **Status**: DEPRECATED - Being migrated to Snowflake
- **Migration Tool**: `scripts/migrate_vectors_to_snowflake.py --source weaviate`
- **Replacement**: Use `memory.search_knowledge()` instead

### ❌ ChromaDB
- **Status**: FORBIDDEN - Never part of architecture
- **Action**: Remove immediately if found

### ❌ Qdrant
- **Status**: FORBIDDEN (except internal Mem0 use)
- **Note**: Mem0 uses Qdrant internally, but we never access it directly

### ❌ Others (Milvus, FAISS, etc.)
- **Status**: FORBIDDEN
- **Action**: Use Snowflake Cortex instead

---

## 📋 Implementation Guide

### Getting the Service

```python
from backend.services.unified_memory_service import get_unified_memory_service

# Get singleton instance
memory = get_unified_memory_service()

# Check health
health = memory.health_check()
print(f"Memory system status: {health['status']}")
print(f"Date awareness: {health['actual_date']}")  # July 9, 2025
```

### Common Operations

#### 1. Adding Knowledge

```python
# Add a document to the knowledge base
doc_ids = memory.add_knowledge(
    content="Q2 2025 revenue exceeded targets by 15%, reaching $5.2M",
    source="quarterly_report_q2_2025.pdf",
    metadata={
        "department": "finance",
        "quarter": "Q2",
        "year": "2025",
        "confidential": True
    }
)
```

#### 2. Searching Knowledge

```python
# Search for relevant information
results = memory.search_knowledge(
    query="What were our Q2 revenue results?",
    limit=5,
    metadata_filter={"department": "finance"}
)

for result in results:
    print(f"Content: {result['content']}")
    print(f"Similarity: {result['similarity']}")
    print(f"Source: {result['source']}")
```

#### 3. Conversational Memory

```python
# Store conversation
memory.remember_conversation(
    user_id="ceo@payready.com",
    content="User asked about Q2 revenue performance",
    metadata={"topic": "finance", "sentiment": "positive"}
)

# Recall conversations
history = memory.recall_conversations(
    user_id="ceo@payready.com",
    query="revenue discussions",
    limit=10
)
```

#### 4. Caching

```python
# Cache expensive computation results
result = expensive_operation()
memory.cache_set("analysis:q2:revenue", result, ttl=3600)

# Retrieve from cache
cached = memory.cache_get("analysis:q2:revenue")
if cached:
    return cached
```

#### 5. AI-Powered Operations

```python
# Generate SQL from natural language
schema = "Tables: customers(id, name, revenue), orders(id, customer_id, amount)"
sql = memory.generate_sql_from_natural_language(
    "Show me top 10 customers by revenue this quarter",
    schema
)

# Analyze sentiment
sentiment = memory.analyze_sentiment(
    "The Q2 results were fantastic! We crushed our targets!"
)
print(f"Sentiment: {sentiment['classification']}")  # positive
```

---

## 🔄 Migration Strategy

### Phase 1: Audit Current Usage
```bash
python scripts/audit_vector_databases.py
```

### Phase 2: Validate Architecture Compliance
```bash
python scripts/validate_memory_architecture.py
```

### Phase 3: Migrate Existing Vectors
```bash
# Dry run first
python scripts/migrate_vectors_to_snowflake.py --dry-run

# Then migrate
python scripts/migrate_vectors_to_snowflake.py --source all
```

### Phase 4: Update Services
Replace all direct vector database usage with UnifiedMemoryService calls.

### Phase 5: Remove Dependencies
1. Remove from `pyproject.toml`:
   - `pinecone-client`
   - `weaviate-client`
   - `chromadb`
   
2. Remove from Pulumi ESC:
   - `pinecone_api_key`
   - `pinecone_environment`
   - `weaviate_url`
   - `weaviate_api_key`

---

## 🛡️ Enforcement Mechanisms

### Pre-Commit Hooks
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: validate-memory-architecture
      name: Validate Memory Architecture
      entry: python scripts/validate_memory_architecture.py
      language: system
      files: '\.py$'
```

### CI/CD Pipeline
```yaml
# .github/workflows/ci.yml
- name: Validate Memory Architecture
  run: python scripts/validate_memory_architecture.py
```

### Runtime Validation
The UnifiedMemoryService validates on startup that no forbidden services are configured.

---

## 📊 Performance Characteristics

### Latency Targets
- **L1 Redis**: < 1ms
- **L2 Mem0**: < 10ms
- **L3 Cortex Vector**: < 100ms
- **L4 SQL Query**: < 200ms
- **L5 AI Operations**: < 1000ms

### Throughput
- **Cache Operations**: 100k+ ops/sec
- **Vector Search**: 1k+ queries/sec
- **SQL Queries**: 10k+ queries/sec
- **AI Operations**: 100+ ops/sec

### Storage Limits
- **L1 Redis**: 100GB (ephemeral)
- **L2 Mem0**: 10GB (conversational)
- **L3/L4/L5 Snowflake**: Unlimited (pay per use)

---

## 🚨 Common Pitfalls to Avoid

### ❌ DON'T: Import Vector Databases Directly
```python
# WRONG - NEVER DO THIS
import pinecone
pinecone.init(api_key="...")
index = pinecone.Index("knowledge")
```

### ✅ DO: Use UnifiedMemoryService
```python
# CORRECT
from backend.services.unified_memory_service import get_unified_memory_service
memory = get_unified_memory_service()
results = memory.search_knowledge("query")
```

### ❌ DON'T: Ignore Date Context
```python
# WRONG
created_at = datetime.now()  # Might return wrong date
```

### ✅ DO: Use Date Manager
```python
# CORRECT
from backend.core.date_time_manager import date_manager
created_at = date_manager.now()  # Always returns July 9, 2025
```

### ❌ DON'T: Store Vectors Outside Snowflake
```python
# WRONG
vectors = generate_embeddings(text)
store_in_custom_database(vectors)
```

### ✅ DO: Let UnifiedMemoryService Handle It
```python
# CORRECT
memory.add_knowledge(text, source="document.pdf")
# Embedding generation and storage handled automatically
```

---

## 🔍 Troubleshooting

### Issue: "Pinecone is FORBIDDEN!" Error
**Solution**: You have forbidden imports. Run `python scripts/validate_memory_architecture.py` to find them.

### Issue: Redis Connection Failed
**Solution**: Redis is optional. The service will work without it but with reduced performance.

### Issue: Mem0 Not Available
**Solution**: Install with `pip install mem0ai`. The service will use Snowflake fallback if unavailable.

### Issue: Snowflake Connection Failed
**Solution**: This is critical. Check:
1. Credentials in Pulumi ESC
2. Network connectivity
3. Warehouse is running

---

## 📚 Additional Resources

- **UnifiedMemoryService Source**: `backend/services/unified_memory_service.py`
- **Migration Script**: `scripts/migrate_vectors_to_snowflake.py`
- **Validation Script**: `scripts/validate_memory_architecture.py`
- **Audit Script**: `scripts/audit_vector_databases.py`

---

## 🎯 Success Criteria

The memory architecture is successful when:

1. **Zero Forbidden Imports**: `validate_memory_architecture.py` finds no violations
2. **All Vectors in Snowflake**: Migration complete with verification
3. **Services Using UnifiedMemoryService**: No direct database access
4. **Performance Targets Met**: All operations within latency bounds
5. **Date Awareness**: System knows it's July 9, 2025

---

**Remember**: Snowflake is the Center of the Universe for Sophia AI! 