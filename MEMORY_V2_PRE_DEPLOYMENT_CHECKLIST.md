# Memory V2 Pre-Deployment Checklist

## 🚨 Critical Issues to Address Before Deployment

### 1. **Redis Connection Configuration** 🔴 HIGH PRIORITY
```python
# Current: Hardcoded Redis URL
self.redis_client = await redis.from_url(
    "redis://146.235.200.1:6379",  # ❌ Hardcoded!
    password=settings.REDIS_PASSWORD,
    encoding="utf-8",
    decode_responses=True,
)

# Fix Required:
self.redis_client = await redis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    password=settings.REDIS_PASSWORD,
    encoding="utf-8",
    decode_responses=True,
)
```

### 2. **Missing Config Settings** 🟡 MEDIUM PRIORITY
Need to add to `infrastructure/mcp_servers/ai_memory_v2/config.py`:
```python
REDIS_HOST = os.getenv("REDIS_HOST", "146.235.200.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = get_config_value("redis_password")
```

### 3. **Error Handling for Redis Connection** 🟡 MEDIUM PRIORITY
```python
# Add retry logic for Redis initialization
async def initialize(self):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Redis connection code...
            break
        except redis.ConnectionError as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to connect to Redis after {max_retries} attempts")
                raise
            await asyncio.sleep(2 ** attempt)
```

### 4. **API Endpoints Missing** 🔴 HIGH PRIORITY
Need to add routes to `infrastructure/mcp_servers/ai_memory_v2/handlers/main_handler.py`:
```python
@router.post("/api/v2/memory/store")
async def store_memory(request: MemoryStoreRequest):
    # Implementation

@router.get("/api/v2/memory/retrieve")
async def retrieve_memory(memory_id: str, memory_type: Optional[str] = None):
    # Implementation

@router.get("/api/v2/memory/search")
async def search_memories(query: SearchRequest):
    # Implementation

@router.get("/api/v2/memory/stats")
async def get_memory_stats():
    # Implementation
```

### 5. **Estuary Flow Configuration** 🟡 MEDIUM PRIORITY
Create `config/estuary/memory-persistence-flow.yaml`:
```yaml
collections:
  - name: sophia-memory-events
    source:
      redis:
        host: ${REDIS_HOST}
        port: ${REDIS_PORT}
        password: ${REDIS_PASSWORD}
        stream: "estuary:memory:events"
    destination:
      snowflake:
        account: ${SNOWFLAKE_ACCOUNT}
        database: SOPHIA_AI
        schema: AI_MEMORY
        table: MEMORY_RECORDS
```

### 6. **Snowflake Schema Missing** 🟡 MEDIUM PRIORITY
Need to create `infrastructure/snowflake_setup/ai_memory_v2_schema.sql`:
```sql
CREATE TABLE IF NOT EXISTS AI_MEMORY.MEMORY_RECORDS (
    id VARCHAR PRIMARY KEY,
    type VARCHAR NOT NULL,
    content VARIANT NOT NULL,
    metadata VARIANT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    deleted_at TIMESTAMP_NTZ,
    user_id VARCHAR,
    session_id VARCHAR,
    INDEX idx_type (type),
    INDEX idx_created (created_at),
    INDEX idx_user (user_id)
);
```

### 7. **Health Check Endpoint** 🟢 LOW PRIORITY
Add to health check:
```python
@router.get("/health")
async def health_check():
    try:
        # Check Redis
        await memory_mediator.redis_client.ping()
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"

    return {
        "status": "healthy" if redis_status == "healthy" else "degraded",
        "redis": redis_status,
        "cache_stats": await memory_mediator.get_stats()
    }
```

### 8. **Docker Configuration** 🟡 MEDIUM PRIORITY
Update `infrastructure/mcp_servers/ai_memory_v2/Dockerfile`:
```dockerfile
ENV REDIS_HOST=146.235.200.1
ENV REDIS_PORT=6379
```

## ✅ What's Already Good

1. **Memory Types & Schemas** - Well-defined Pydantic models
2. **RBAC Logic** - Basic permissions implemented
3. **Cache TTL Strategy** - Sensible defaults by memory type
4. **Estuary Integration** - Queue mechanism ready
5. **Error Logging** - Comprehensive logging throughout

## 🚀 Deployment Steps (After Fixes)

1. **Fix Redis Configuration** (15 min)
   - Update memory_mediator.py
   - Add config settings
   - Test connection

2. **Add API Endpoints** (30 min)
   - Create route handlers
   - Add request/response models
   - Update main router

3. **Create Snowflake Schema** (10 min)
   - Run DDL script
   - Verify table creation

4. **Configure Estuary Flow** (20 min)
   - Deploy flow configuration
   - Test event streaming

5. **Update Docker Image** (10 min)
   - Build new image
   - Push to registry
   - Update service

## 🎯 Minimum Viable Deployment

If time is critical, these are the MUST-HAVE fixes:

1. ✅ Fix Redis hardcoded URL
2. ✅ Add basic API endpoints (at least store/retrieve)
3. ✅ Create Snowflake table
4. ✅ Add health check

Everything else can be added iteratively after initial deployment.

## 📊 Risk Assessment

| Issue | Risk Level | Impact if Not Fixed |
|-------|------------|---------------------|
| Hardcoded Redis URL | HIGH | Won't work in different environments |
| Missing API endpoints | CRITICAL | Can't use the service at all |
| No Snowflake schema | MEDIUM | No persistence, only cache |
| No Estuary config | LOW | Can add later, cache still works |
| No retry logic | LOW | Occasional failures on startup |

## 🎉 Ready for Testing After:
- [ ] Redis configuration fixed
- [ ] Basic API endpoints added
- [ ] Health check implemented
- [ ] Docker image updated

Total estimated time: **1.5 hours** to address critical issues
