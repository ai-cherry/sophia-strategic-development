# Snowflake Cortex Unified Implementation Plan
## Sophia AI Repository Transformation

**Mission**: Transform Sophia AI into a single-pool, Snowflake-first, credit-governed, fully-observable platform while maintaining Lambda Labs production continuity.

**Timeline**: 8-week implementation with immediate P0 fixes
**Priority**: Quality → Stability → Maintainability → Performance → Cost
**Infrastructure**: $3,117.60/month Lambda Labs (192.222.58.232:8000, 104.171.202.117:8001)

## Executive Summary

This plan consolidates multiple Snowflake connection patterns into a single, governed gateway while fixing critical CI/CD issues and maintaining zero downtime on production Lambda Labs infrastructure. The implementation follows a phased approach prioritizing immediate fixes, then systematic refactoring, and finally advanced optimization.

## Current State Analysis

### Connection Chaos
- **7 different connection implementations** across the codebase
- **4 competing pool managers** with no unified governance
- **75+ files** directly calling Snowflake Cortex functions
- **No credit tracking** or usage limits
- **Mixed authentication** (PAT, password, ESC)

### Critical Issues
- CI/CD broken due to `anthropic-mcp-python-sdk>=0.4.1` dependency
- Import errors from deprecated pools blocking development
- No unified monitoring or cost control
- Lambda Labs infrastructure underutilized (<15% GPU usage)

## Phase 0: Emergency Fixes (Day 0) ✅

### 0.1 Fix Dependency Chain
```bash
# Remove broken dependency
# anthropic-mcp-python-sdk>=0.4.1

# Add compatible alternatives
mcp-python>=0.3.0
snowflake-connector-python>=3.7.0
snowflake-sqlalchemy>=1.5.0
pulumi>=3.100.0
pulumi-snowflake>=0.50.0
```

### 0.2 Create CI/CD Rehabilitation Flag
```bash
touch .techdebt/ci_cd_rehab.flag
echo "SNOWFLAKE_GATEWAY_MIGRATION" >> .techdebt/active_migrations.txt
```

### 0.3 Fix GitHub Actions
- Update workflow to use Python 3.12 + Node 20
- Add proper caching and quality gates
- Ensure `passed=true` output for downstream jobs

## Phase 1: CortexGateway Foundation (Week 1)

### 1.1 Core Gateway Implementation
Already created `core/infra/cortex_gateway.py` with:
- Singleton async pattern
- Unified API: `complete()`, `embed()`, `search()`, `sentiment()`, `execute_sql()`
- Prometheus metrics decorators
- Credit limit enforcement
- Health check endpoint

### 1.2 Deprecation Guards
- ✅ `infrastructure/core/connection_pool.py` - raises ImportError
- ✅ `shared/utils/snowflake_cortex/pool.py` - raises ImportError

### 1.3 Integration Points
```python
# Example migration pattern
# BEFORE:
conn = snowflake.connector.connect(**config)
cursor = conn.cursor()
cursor.execute("SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', ?)", (prompt,))

# AFTER:
from core.infra.cortex_gateway import get_gateway
gateway = get_gateway()
result = await gateway.complete(prompt, model='mixtral-8x7b')
```

## Phase 2: Repository-wide Refactor (Weeks 2-3)

### 2.1 Service Migration Priority
1. **Unified Chat Service** (`backend/services/unified_chat_service.py`)
   - Replace direct Snowflake calls with gateway
   - Implement parallel LangGraph edges

2. **Core Agents**
   - `SalesIntelligenceAgentCore`
   - `MarketingAnalysisAgent`
   - `SnowflakeAdminAgent`
   - Update `initialize()` to use `self.cortex = get_gateway()`

3. **ETL Pipelines**
   - Gong webhook handlers
   - Estuary Flow connectors
   - Batch embedding scripts

### 2.2 Migration Tracking
Create `reports/snowflake_migration_tracker.json`:
```json
{
  "total_files": 75,
  "migrated": 0,
  "in_progress": [],
  "blocked": [],
  "metrics": {
    "direct_connections_removed": 0,
    "gateway_calls_added": 0
  }
}
```

## Phase 3: MCP Server Consolidation (Weeks 3-4)

### 3.1 Snowflake MCP Servers
Update these MCP servers to use CortexGateway:
- `mcp-servers/snowflake_cortex/` - Complete implementation
- `infrastructure/mcp_servers/snowflake_v2/` - Refactor to enhanced
- `infrastructure/mcp_servers/cortex_aisql/` - Add gateway integration

### 3.2 MCP Configuration
Update `cursor_enhanced_mcp_config.json`:
```json
{
  "snowflake-enhanced": {
    "command": "python",
    "args": ["mcp-servers/snowflake_cortex/server.py"],
    "port": 9030,
    "features": ["complete", "embed", "search", "sentiment", "optimize"]
  }
}
```

## Phase 4: Monitoring & Observability (Weeks 4-5)

### 4.1 Prometheus Integration
```python
# In CortexGateway decorators
from prometheus_client import Counter, Histogram, Gauge

snowflake_query_duration = Histogram(
    'snowflake_query_duration_seconds',
    'Time spent on Snowflake queries',
    ['function', 'warehouse']
)

snowflake_credits_used = Counter(
    'snowflake_credits_total',
    'Total Snowflake credits consumed',
    ['function', 'user']
)

snowflake_daily_limit = Gauge(
    'snowflake_daily_limit_remaining',
    'Remaining daily credit allowance'
)
```

### 4.2 Cost Tracking Table
```sql
CREATE TABLE IF NOT EXISTS SOPHIA_AI_UNIFIED.ANALYTICS.CORTEX_USAGE_LOG (
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    user_name VARCHAR,
    function_name VARCHAR,
    model_name VARCHAR,
    input_tokens NUMBER,
    output_tokens NUMBER,
    credits_used FLOAT,
    query_tag VARCHAR,
    session_id VARCHAR
);
```

### 4.3 Daily Governor Task
```sql
CREATE TASK SOPHIA_AI_UNIFIED.ANALYTICS.DAILY_CREDIT_GOVERNOR
WAREHOUSE = COMPUTE_WH
SCHEDULE = 'USING CRON 0 */6 * * * UTC'
AS
CALL SOPHIA_AI_UNIFIED.ANALYTICS.CHECK_AND_ALERT_CREDIT_USAGE();
```

## Phase 5: Cost Optimization (Weeks 5-6)

### 5.1 Warehouse Optimization
Implement Manus AI's warehouse optimization recommendations:
- **AI_COMPUTE_WH**: For analytics and BI queries
- **CORTEX_COMPUTE_WH**: For AI/ML workloads only
- **COMPUTE_WH**: General queries
- **LOADING_WH**: ETL operations

### 5.2 Intelligent Routing
```python
class WarehouseOptimizer:
    def select_optimal_warehouse(self, query: str, workload_type: str) -> str:
        query_upper = query.upper()

        if any(kw in query_upper for kw in ['CORTEX', 'EMBED', 'COMPLETE']):
            return 'CORTEX_COMPUTE_WH'
        elif any(kw in query_upper for kw in ['AGGREGATE', 'GROUP BY']):
            return 'AI_COMPUTE_WH'
        elif any(kw in query_upper for kw in ['COPY', 'INSERT']):
            return 'LOADING_WH'

        return 'COMPUTE_WH'
```

### 5.3 Resource Monitors
```sql
CREATE RESOURCE MONITOR SOPHIA_AI_DAILY_LIMIT
WITH CREDIT_QUOTA = 100
FREQUENCY = DAILY
START_TIMESTAMP = IMMEDIATELY
TRIGGERS
  ON 80 PERCENT DO NOTIFY
  ON 95 PERCENT DO SUSPEND
  ON 100 PERCENT DO SUSPEND_IMMEDIATE;
```

## Phase 6: Lambda Labs Integration (Weeks 6-7)

### 6.1 Hybrid Processing
Implement intelligent routing between Snowflake and Lambda Labs:
```python
class IntelligentRouter:
    async def route_query(self, message: str) -> Dict[str, Any]:
        # Business intelligence → Snowflake
        if self._is_business_query(message):
            return await self.route_to_snowflake_cortex(message)

        # AI generation → Lambda Labs GPU
        elif self._is_generation_query(message):
            return await self.route_to_lambda_labs(message)

        # Complex analysis → Both
        else:
            return await self.hybrid_processing(message)
```

### 6.2 Lambda Labs Optimization
Address the <15% GPU utilization:
- Implement request batching
- Add GPU-aware task scheduling
- Enable model caching on GPU memory

## Phase 7: Production Deployment (Week 8)

### 7.1 Deployment Checklist
- [ ] All CI/CD pipelines green
- [ ] Zero direct `snowflake.connector.connect()` calls
- [ ] Prometheus metrics exposed on :8003
- [ ] Daily credit monitoring active
- [ ] Lambda Labs health checks passing
- [ ] Rollback plan documented

### 7.2 Cutover Process
1. **Tag current state**: `git tag pre-gateway-migration`
2. **Deploy monitoring**: Start Prometheus exporters
3. **Gradual rollout**:
   - Dev environment (Week 7 Day 1)
   - Staging environment (Week 7 Day 3)
   - Production canary (Week 7 Day 5)
   - Full production (Week 8)

## Success Metrics

### Technical Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Connection Implementations | 7 | 1 |
| Direct Snowflake Calls | 75+ files | 0 |
| CI/CD Success Rate | <70% | >95% |
| Query Response Time (p95) | Unknown | <2s |
| Daily Credit Usage | Untracked | <100 |

### Business Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Snowflake Costs | ~$1,000/mo | $600/mo (40% reduction) |
| Lambda Labs GPU Utilization | <15% | >70% |
| Development Velocity | Blocked | Unblocked |
| Monitoring Coverage | 0% | 100% |

## Risk Mitigation

### Technical Risks
1. **Connection Pool Exhaustion**
   - Mitigation: Implement circuit breakers and backpressure
   - Fallback: Maintain legacy pool for emergency

2. **Credit Limit Breaches**
   - Mitigation: Hard limits with suspend triggers
   - Alert: Slack/email at 80% threshold

3. **Lambda Labs Downtime**
   - Mitigation: Implement health checks and auto-failover
   - Backup: Route to Snowflake Cortex temporarily

### Rollback Strategy
```bash
# Quick rollback procedure
git checkout pre-gateway-migration
docker-compose -f docker-compose.legacy.yml up -d
pulumi stack select prod-legacy
pulumi up --yes
```

## Implementation Team

### Roles & Responsibilities
- **Lead**: Cursor AI Agent (implementation)
- **Review**: Manus AI Agent (architecture validation)
- **Testing**: Automated test suite + manual verification
- **Deployment**: GitHub Actions automation

### Communication Plan
- Daily progress updates in implementation tracker
- Weekly architecture review sessions
- Immediate alerts for blockers or risks

## Appendix: File Migration List

### Priority 1 (Week 2)
- `backend/services/unified_chat_service.py`
- `backend/services/enhanced_unified_chat_service.py`
- `core/services/snowflake_cortex_service.py`
- `infrastructure/services/snowflake_intelligence_service.py`

### Priority 2 (Week 3)
- All files in `core/use_cases/*_agent.py`
- `infrastructure/integrations/gong_webhook_*.py`
- `infrastructure/etl/batch_embed_data.py`

### Priority 3 (Week 4)
- MCP servers in `infrastructure/mcp_servers/`
- Test files and mocks
- Documentation updates

## Conclusion

This unified implementation plan provides a clear path to consolidate Snowflake connections, reduce costs by 40%, and improve Lambda Labs utilization to >70%. The phased approach ensures zero downtime while systematically addressing technical debt and establishing enterprise-grade governance.

**Next Steps**:
1. Complete Phase 0 emergency fixes (already done ✅)
2. Begin Phase 1 CortexGateway adoption
3. Set up migration tracking dashboard
4. Schedule weekly progress reviews

The transformation will position Sophia AI as a world-class, cost-optimized, and highly automated business intelligence platform with unified Snowflake integration and efficient Lambda Labs utilization.
