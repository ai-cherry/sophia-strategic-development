# Snowflake Migration Guide

## Overview

This guide covers the migration of Sophia AI to use the unified CortexGateway pattern for all Snowflake operations. The migration consolidates 7 different connection implementations into a single, governed gateway with credit tracking, intelligent routing, and comprehensive monitoring.

## Architecture

### Before Migration
```
Multiple Connection Patterns:
├── snowflake.connector.connect() - Direct connections
├── SnowflakeCortexService - Service wrapper
├── ConnectionPoolManager - Threaded pool
├── OptimizedConnectionManager - Async pool
├── UnifiedConnectionManager - Multi-DB pool
├── Various ad-hoc pools
└── MCP server-specific connections
```

### After Migration
```
Single Gateway Pattern:
└── CortexGateway (Singleton)
    ├── OptimizedConnectionManager (Internal)
    ├── Credit Tracking
    ├── Intelligent Warehouse Routing
    ├── Prometheus Metrics
    └── Redis Caching
```

## Quick Start

### 1. Test CortexGateway
```bash
# Run all tests
python scripts/test_cortex_gateway.py

# Run specific test
python scripts/test_cortex_gateway.py --test health
```

### 2. Deploy Snowflake Foundation
```bash
# Deploy initial setup
python scripts/deploy_snowflake_foundation.py

# Verify deployment
python scripts/deploy_snowflake_foundation.py --verify-only
```

### 3. Start Monitoring
```bash
# Start monitoring service (runs on port 8003)
python scripts/start_snowflake_monitoring.py

# Run single check
python scripts/start_snowflake_monitoring.py --check-only
```

### 4. Analyze Current Usage
```bash
# Analyze codebase for Snowflake usage
python scripts/snowflake_migration/analyze_snowflake_usage.py
```

### 5. Migrate Files
```bash
# Dry run (see what would change)
python scripts/snowflake_migration/migrate_to_gateway.py

# Apply changes to specific file
python scripts/snowflake_migration/migrate_to_gateway.py --apply --file path/to/file.py

# Migrate entire directory
python scripts/snowflake_migration/migrate_to_gateway.py --apply --directory backend/services
```

## Migration Pattern Examples

### Basic Query Execution

**Before:**
```python
import snowflake.connector

conn = snowflake.connector.connect(**config)
cursor = conn.cursor()
cursor.execute("SELECT * FROM my_table")
results = cursor.fetchall()
cursor.close()
conn.close()
```

**After:**
```python
from core.infra.cortex_gateway import get_gateway

gateway = get_gateway()
results = await gateway.execute_sql("SELECT * FROM my_table")
```

### Cortex AI Functions

**Before:**
```python
cursor.execute("SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', ?)", (prompt,))
result = cursor.fetchone()[0]
```

**After:**
```python
result = await gateway.complete(prompt, model='mixtral-8x7b')
```

### Embeddings

**Before:**
```python
cursor.execute("SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', ?)", (text,))
embedding = json.loads(cursor.fetchone()[0])
```

**After:**
```python
embedding = await gateway.embed(text, model='e5-base-v2')
```

## Key Features

### 1. Credit Governance
- Daily credit limits (default: 100)
- Per-query credit estimation
- Automatic enforcement
- Usage tracking and reporting

### 2. Intelligent Warehouse Routing
- **CORTEX_COMPUTE_WH**: AI/ML workloads
- **AI_COMPUTE_WH**: Analytics queries
- **COMPUTE_WH**: General queries
- **LOADING_WH**: ETL operations

### 3. Monitoring & Observability
- Prometheus metrics on port 8003
- Grafana dashboards
- Real-time alerts
- Cost optimization recommendations

### 4. Caching
- Redis integration
- Configurable TTL
- Query result caching
- Cache hit rate tracking

## Configuration

### Environment Variables
```bash
# Snowflake connection
SNOWFLAKE_ACCOUNT=UHDECNO-CVB64222
SNOWFLAKE_USER=SCOOBYJAVA15
SNOWFLAKE_PAT_TOKEN=your_pat_token
SNOWFLAKE_DATABASE=SOPHIA_AI_UNIFIED
SNOWFLAKE_SCHEMA=PRODUCTION
SNOWFLAKE_WAREHOUSE=COMPUTE_WH

# Limits
SNOWFLAKE_DAILY_CREDIT_LIMIT=100
SNOWFLAKE_QUERY_TIMEOUT=300

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

### Prometheus Metrics

Available at `http://localhost:8003/metrics`:

- `snowflake_query_duration_seconds` - Query execution time
- `snowflake_queries_total` - Total queries by function/status
- `snowflake_credits_total` - Credits consumed
- `snowflake_daily_credits_remaining` - Remaining daily allowance
- `snowflake_warehouse_utilization` - Warehouse utilization %
- `snowflake_cache_hits_total` - Cache hit count
- `snowflake_errors_total` - Error count by type

## Monitoring Dashboard

### Grafana Setup
1. Import dashboard from `config/grafana/dashboards/snowflake_monitoring.json`
2. Configure Prometheus data source
3. Set refresh interval to 30s

### Key Metrics
- Daily credit usage gauge
- Query duration (p50, p95)
- Queries per minute
- Warehouse utilization
- Credit usage by warehouse
- Error rate
- Cache hit rate
- Potential cost savings

## Troubleshooting

### Common Issues

1. **Import Error: 'connection_pool' is deprecated**
   - Solution: Update imports to use `from core.infra.cortex_gateway import get_gateway`

2. **Credit Limit Exceeded**
   - Check daily usage: `python scripts/test_cortex_gateway.py --test credit`
   - Adjust limit in environment or CONFIG.SYSTEM_CONFIG table

3. **Slow Queries**
   - Check warehouse routing in monitoring dashboard
   - Consider scaling warehouse or optimizing query

4. **Connection Failures**
   - Verify PAT token is valid
   - Check network connectivity to Snowflake
   - Run health check: `python scripts/test_cortex_gateway.py --test health`

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger('core.infra.cortex_gateway').setLevel(logging.DEBUG)
logging.getLogger('infrastructure.adapters.enhanced_snowflake_adapter').setLevel(logging.DEBUG)
```

## Migration Phases

### Phase 1: Foundation (Week 1) ✅
- [x] Create CortexGateway
- [x] Add deprecation guards
- [x] Set up monitoring
- [x] Deploy Snowflake foundation

### Phase 2: Core Services (Week 2-3) 🚧
- [ ] Migrate unified chat service
- [ ] Migrate core agents
- [ ] Update ETL pipelines
- [ ] Test in dev environment

### Phase 3: MCP Servers (Week 3-4) 📋
- [ ] Update Snowflake MCP servers
- [ ] Migrate other MCP servers using Snowflake
- [ ] Update MCP configuration

### Phase 4: Advanced Features (Week 5-6) 📋
- [ ] Implement search services
- [ ] Add advanced monitoring
- [ ] Optimize caching strategy
- [ ] Performance tuning

### Phase 5: Production Rollout (Week 7-8) 📋
- [ ] Deploy to staging
- [ ] Run integration tests
- [ ] Production deployment
- [ ] Monitor and optimize

## Best Practices

1. **Always use async/await** with CortexGateway methods
2. **Specify workload_type** for optimal warehouse routing
3. **Use caching** for frequently accessed data
4. **Monitor credit usage** daily
5. **Handle errors gracefully** with try/except blocks
6. **Use batch operations** when possible (e.g., batch_embed)
7. **Set appropriate timeouts** for long-running queries

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review test output: `python scripts/test_cortex_gateway.py`
3. Check monitoring dashboard for system health
4. Review logs in `reports/` directory

## Next Steps

1. Complete remaining service migrations
2. Set up production monitoring
3. Configure alerting rules
4. Optimize warehouse sizes based on usage
5. Implement advanced caching strategies

Remember: The goal is to have ZERO direct Snowflake connections outside of CortexGateway!
