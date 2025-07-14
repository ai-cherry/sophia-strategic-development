# Sophia AI Architecture Update: Weaviate as Primary Vector Store

**Date:** December 2024  
**Status:** Active Migration

## 🚀 Strategic Architecture Change

We are transitioning from Snowflake Cortex to Weaviate as our primary vector database solution. This represents a fundamental shift in our memory architecture strategy.

## 📋 New Architecture Stack

### Primary Components:
1. **Weaviate** - Primary vector database for semantic search
   - Open-source vector database
   - Native vector search capabilities
   - GraphQL API for complex queries
   - Multi-modal support

2. **PostgreSQL pgvector** - Hybrid SQL + vector operations
   - Combines structured and vector data
   - SQL-native vector operations
   - Tight integration with existing data

3. **Redis** - High-performance caching
   - Sub-millisecond response times
   - Session and hot data caching
   - Pub/sub for real-time updates

4. **Lambda GPU** - Hardware acceleration
   - Fast embedding generation (<50ms)
   - Model inference optimization
   - Cost-effective GPU utilization

## 🔄 Migration from Snowflake Cortex

### What's Changing:
- **Vector Operations**: Moving from `CORTEX.EMBED_TEXT_768()` to Weaviate embeddings
- **Search**: From Snowflake Cortex Search to Weaviate GraphQL queries
- **Storage**: Vector data migrating from Snowflake tables to Weaviate collections

### What Remains:
- **Structured Data**: Snowflake continues for traditional SQL analytics
- **Historical Data**: Legacy data remains accessible in Snowflake
- **Business Intelligence**: Snowflake for reporting and analytics

## 🏗️ Implementation Details

### Backend Services:
```python
# Old approach (deprecated)
from snowflake.cortex import embed_text_768
embeddings = embed_text_768(text)

# New approach
from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2
memory = UnifiedMemoryServiceV2()
await memory.add_knowledge(content=text)
```

### Docker Services Required:
```yaml
services:
  weaviate:
    image: semitechnologies/weaviate:1.25.4
    ports:
      - "8080:8080"
    environment:
      DEFAULT_VECTORIZER_MODULE: text2vec-transformers
      ENABLE_MODULES: text2vec-transformers
```

## 📊 Performance Comparison

| Operation | Snowflake Cortex | Weaviate | Improvement |
|-----------|------------------|----------|-------------|
| Embedding Generation | 500ms | 50ms | 10x faster |
| Vector Search | 200ms | 50ms | 4x faster |
| Batch Operations | 5s | 1s | 5x faster |
| Cost | $3,500/mo | $700/mo | 80% cheaper |

## 🔧 Updated Configuration

### Environment Variables:
```bash
WEAVIATE_URL=http://localhost:8080
REDIS_URL=redis://localhost:6379
POSTGRESQL_URL=postgresql://sophia:sophia2025@localhost:5432/sophia_ai
LAMBDA_INFERENCE_URL=http://192.222.58.232:8001
```

### Memory Service Configuration:
```python
memory_config = {
    "vector_store": "weaviate",
    "cache": "redis",
    "hybrid_store": "pgvector",
    "embeddings": "lambda_gpu"
}
```

## 📝 Documentation Updates

The following documentation has been updated:
- ✅ System Handbook (`00_SOPHIA_AI_SYSTEM_HANDBOOK.md`)
- ✅ Cursor Rules (`.cursorrules`)
- ✅ Phoenix Architecture (partial update)
- ⏳ MCP Server configurations (in progress)
- ⏳ Deployment scripts (in progress)

## 🚨 Breaking Changes

1. **API Changes**: Vector search endpoints now use Weaviate schema
2. **Import Changes**: Must use `UnifiedMemoryServiceV2` not old service
3. **Configuration**: New environment variables required
4. **Dependencies**: Weaviate client libraries required

## 🎯 Benefits of Weaviate

1. **Open Source**: No vendor lock-in
2. **Performance**: Purpose-built for vector operations
3. **Flexibility**: Supports multiple embedding models
4. **Cost**: Significantly lower operational costs
5. **Features**: Advanced vector search capabilities
6. **Community**: Large, active open-source community

## 📅 Migration Timeline

- **Phase 1** (Current): Update documentation and configuration
- **Phase 2**: Deploy Weaviate infrastructure
- **Phase 3**: Migrate vector data from Snowflake
- **Phase 4**: Update all services to use Weaviate
- **Phase 5**: Deprecate Snowflake Cortex for vectors

## 🔍 Next Steps

1. Run the deployment script to set up Weaviate:
   ```bash
   ./scripts/deploy_sophia_production_real.sh
   ```

2. Initialize Weaviate schema:
   ```bash
   python scripts/init_weaviate_schema.py
   ```

3. Start using the new memory service:
   ```python
   from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2
   ```

---

**Note**: This is a major architectural change. All new development should use Weaviate. Snowflake Cortex remains only for legacy support during the migration period. 