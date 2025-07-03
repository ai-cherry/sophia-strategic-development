# Performance-First Coding Standards

## Core Philosophy

**Every line of code must be written with performance in mind.** This doesn't mean premature optimization, but rather making informed decisions that support our goals of 1000x scalability.

## Python Performance Standards

### 1. Async Everything
```python
# ❌ AVOID: Synchronous code
def get_user_data(user_id):
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    profile = db.query(f"SELECT * FROM profiles WHERE user_id = {user_id}")
    return {"user": user, "profile": profile}

# ✅ PREFER: Async with concurrent execution
async def get_user_data(user_id: str) -> Dict[str, Any]:
    async with asyncio.TaskGroup() as tg:
        user_task = tg.create_task(
            db.async_query("SELECT * FROM users WHERE id = $1", user_id)
        )
        profile_task = tg.create_task(
            db.async_query("SELECT * FROM profiles WHERE user_id = $1", user_id)
        )
    
    return {"user": user_task.result(), "profile": profile_task.result()}
```

### 2. Connection Pooling
```python
# ✅ ALWAYS use connection pools
class DatabaseService:
    def __init__(self):
        self.pool = asyncpg.create_pool(
            min_size=10,
            max_size=100,
            max_inactive_connection_lifetime=300,
            command_timeout=60
        )
    
    async def query(self, sql: str, *args) -> List[Dict]:
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, *args)
```

### 3. Batch Operations
```python
# ❌ AVOID: N+1 queries
for user_id in user_ids:
    user = await get_user(user_id)
    process_user(user)

# ✅ PREFER: Batch fetching
users = await get_users_batch(user_ids)
await asyncio.gather(*[process_user(user) for user in users])
```

### 4. Caching Decorators
```python
from functools import lru_cache
from aiocache import cached

# ✅ Memory caching for pure functions
@lru_cache(maxsize=10000)
def calculate_score(data: frozenset) -> float:
    return complex_calculation(data)

# ✅ Redis caching for async functions
@cached(ttl=300, key_builder=lambda f, *args, **kwargs: f"{f.__name__}:{args[0]}")
async def get_user_preferences(user_id: str) -> Dict:
    return await db.fetch_preferences(user_id)
```

### 5. Generator Patterns
```python
# ❌ AVOID: Loading everything into memory
def get_all_records():
    return db.query("SELECT * FROM huge_table")  # Could be millions

# ✅ PREFER: Streaming with generators
async def stream_records():
    async with db.transaction():
        async for record in db.stream("SELECT * FROM huge_table"):
            yield record
```

## TypeScript/React Performance Standards

### 1. Component Memoization
```typescript
// ❌ AVOID: Re-rendering on every parent update
const ExpensiveComponent = ({ data }) => {
    const processed = heavyComputation(data);
    return <div>{processed}</div>;
};

// ✅ PREFER: Memoized components
const ExpensiveComponent = React.memo(({ data }) => {
    const processed = useMemo(() => heavyComputation(data), [data]);
    return <div>{processed}</div>;
}, (prevProps, nextProps) => {
    return prevProps.data.id === nextProps.data.id;
});
```

### 2. Virtual Scrolling
```typescript
// ✅ ALWAYS use virtual scrolling for large lists
import { FixedSizeList } from 'react-window';

const BigList = ({ items }) => (
    <FixedSizeList
        height={600}
        itemCount={items.length}
        itemSize={50}
        width="100%"
    >
        {({ index, style }) => (
            <div style={style}>
                {items[index].name}
            </div>
        )}
    </FixedSizeList>
);
```

### 3. Code Splitting
```typescript
// ✅ Dynamic imports for routes
const Dashboard = lazy(() => 
    import(/* webpackChunkName: "dashboard" */ './Dashboard')
);

// ✅ Conditional loading
const AdminPanel = lazy(() => 
    userRole === 'admin' 
        ? import('./AdminPanel')
        : Promise.resolve({ default: () => null })
);
```

### 4. Image Optimization
```typescript
// ✅ Next.js Image component with optimization
import Image from 'next/image';

<Image
    src="/hero.jpg"
    alt="Hero"
    width={1200}
    height={600}
    priority
    placeholder="blur"
    blurDataURL={blurDataUrl}
/>
```

## Database Query Standards

### 1. Index Usage
```sql
-- ✅ ALWAYS check query plans
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM users 
WHERE created_at > '2024-01-01' 
AND status = 'active';

-- ✅ Create appropriate indexes
CREATE INDEX CONCURRENTLY idx_users_created_status 
ON users(created_at, status) 
WHERE status = 'active';
```

### 2. Materialized Views
```sql
-- ✅ For expensive aggregations
CREATE MATERIALIZED VIEW daily_revenue AS
SELECT 
    DATE_TRUNC('day', created_at) as day,
    SUM(amount) as revenue,
    COUNT(*) as transaction_count
FROM transactions
GROUP BY 1;

-- ✅ Refresh strategy
CREATE OR REPLACE FUNCTION refresh_daily_revenue()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_revenue;
END;
$$ LANGUAGE plpgsql;
```

### 3. Partitioning
```sql
-- ✅ Partition large tables
CREATE TABLE events (
    id BIGSERIAL,
    created_at TIMESTAMP NOT NULL,
    data JSONB
) PARTITION BY RANGE (created_at);

-- Monthly partitions
CREATE TABLE events_2024_01 PARTITION OF events
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## API Design Standards

### 1. GraphQL with DataLoader
```typescript
// ✅ Batch and cache database queries
const userLoader = new DataLoader(async (userIds) => {
    const users = await db.query(
        'SELECT * FROM users WHERE id = ANY($1)',
        [userIds]
    );
    return userIds.map(id => 
        users.find(user => user.id === id)
    );
});

// In resolvers
const resolvers = {
    Post: {
        author: (post) => userLoader.load(post.authorId)
    }
};
```

### 2. Response Compression
```python
# ✅ Enable compression
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 3. Pagination
```python
# ✅ Cursor-based pagination for large datasets
async def get_items(cursor: Optional[str] = None, limit: int = 20):
    query = """
        SELECT * FROM items 
        WHERE ($1::uuid IS NULL OR id > $1)
        ORDER BY id
        LIMIT $2
    """
    items = await db.fetch(query, cursor, limit + 1)
    
    has_more = len(items) > limit
    items = items[:limit]
    
    return {
        "items": items,
        "next_cursor": items[-1]["id"] if has_more else None
    }
```

## Monitoring & Profiling Requirements

### 1. Performance Decorators
```python
import time
from prometheus_client import Histogram

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

def track_performance(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start
            request_duration.labels(
                method=func.__name__,
                endpoint=kwargs.get('path', 'unknown')
            ).observe(duration)
    return wrapper
```

### 2. Required Metrics
Every service MUST expose:
- Request latency (P50, P95, P99)
- Request rate
- Error rate
- Database query time
- Cache hit rate
- Memory usage
- CPU usage

## Code Review Checklist

### Performance Review Points
- [ ] No synchronous I/O in async functions
- [ ] Proper use of connection pooling
- [ ] Batch operations where applicable
- [ ] Appropriate caching strategy
- [ ] No N+1 query patterns
- [ ] Proper indexing for queries
- [ ] Memory-efficient data structures
- [ ] Lazy loading for large datasets
- [ ] Proper error handling without performance penalty
- [ ] Metrics and monitoring in place

### Automated Checks
```yaml
# .github/workflows/performance-check.yml
- name: Performance Regression Test
  run: |
    npm run lighthouse:ci
    python -m pytest tests/performance/ --benchmark-only
    k6 run tests/load/smoke.js
```

## Anti-Patterns to Avoid

### 1. Premature Pessimization
```python
# ❌ Making code slower for no reason
data = json.loads(json.dumps(original_data))  # Unnecessary serialization

# ✅ Direct usage
data = original_data.copy() if needed
```

### 2. Memory Leaks
```python
# ❌ Keeping references unnecessarily
class Cache:
    def __init__(self):
        self.data = {}  # Never cleaned up
    
# ✅ Bounded cache with TTL
from cachetools import TTLCache
cache = TTLCache(maxsize=10000, ttl=300)
```

### 3. Blocking the Event Loop
```python
# ❌ CPU-intensive work in async
async def process_data(data):
    result = expensive_cpu_operation(data)  # Blocks event loop
    
# ✅ Use thread pool
async def process_data(data):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, expensive_cpu_operation, data
    )
```

## Performance Budget

### Frontend Metrics
- First Contentful Paint: <1s
- Time to Interactive: <2s
- Total Bundle Size: <500KB
- Lighthouse Score: >90

### Backend Metrics
- API Response Time P95: <200ms
- Database Query Time P95: <100ms
- Background Job Processing: <5s
- Memory per Request: <50MB

## Enforcement

1. **Automated Testing**: Performance tests run on every PR
2. **Monitoring Alerts**: Automatic alerts for performance degradation
3. **Code Review**: Performance must be considered in every review
4. **Documentation**: Performance impact documented for each feature

---

**Remember**: Performance is not optional. It's a core feature of every component we build.

**Last Updated**: December 31, 2024  
**Next Review**: January 15, 2025 