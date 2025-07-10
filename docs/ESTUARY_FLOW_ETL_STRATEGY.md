# Estuary Flow ETL Strategy

**Date:** July 9, 2025  
**Priority:** CRITICAL  
**Principle:** Estuary Flow is the ONLY ETL platform for Sophia AI

## Executive Summary

This document establishes Estuary Flow as the exclusive ETL platform for all data integration needs in Sophia AI. No custom ETL scripts, direct API extractions, or alternative ETL tools should be used.

## Core Principles

1. **Estuary Flow Only**: ALL data movement goes through Estuary Flow
2. **No Custom Scripts**: Deprecate all direct API extraction scripts
3. **Declarative Configuration**: Use Flow specifications, not imperative code
4. **Real-time by Default**: Leverage Estuary's CDC capabilities
5. **Unified Data Plane**: Single source of truth for all data pipelines

## Current State to Target State

### Eliminate These Patterns ❌
```python
# Direct API extraction - FORBIDDEN
async def extract_gong_data():
    response = await session.get(GONG_API_URL)
    # Process and load to database
```

### Use Estuary Flow Instead ✅
```yaml
# Estuary Flow Collection Specification
collections:
  gong_data:
    schema: GONG_DATA
    source:
      connector: source-gong
      config:
        api_key: ${GONG_API_KEY}
    destination:
      connector: destination-snowflake
      config:
        account: ${SNOWFLAKE_ACCOUNT}
```

## Implementation Architecture

### 1. Estuary Flow Components

```
┌─────────────────────────────────────────────────────────┐
│                   Estuary Flow Platform                   │
├─────────────────┬─────────────────┬────────────────────┤
│   Connectors    │   Collections   │   Materializations  │
├─────────────────┼─────────────────┼────────────────────┤
│ • source-gong   │ • gong_calls    │ • Snowflake Tables  │
│ • source-hubspot│ • hubspot_deals │ • Real-time Updates │
│ • source-slack  │ • slack_messages│ • CDC Enabled       │
│ • source-asana  │ • asana_tasks   │ • Schema Evolution  │
└─────────────────┴─────────────────┴────────────────────┘
```

### 2. Data Flow Architecture

```
External APIs → Estuary Connectors → Flow Collections → Snowflake
     ↓                                      ↓
  (Gong, HubSpot)                    (Real-time CDC)
```

## Migration Plan

### Phase 1: Inventory (Immediate)
1. Identify all non-Estuary ETL processes
2. Map to Estuary connectors
3. Create migration checklist

### Phase 2: Connector Setup (Week 1)
1. Configure Estuary connectors for each source
2. Create Flow specifications
3. Test data capture

### Phase 3: Migration (Week 2)
1. Parallel run old and new
2. Validate data quality
3. Cut over to Estuary

### Phase 4: Cleanup (Week 3)
1. Remove all custom ETL scripts
2. Archive old code
3. Update documentation

## Estuary Flow Specifications

### Gong Integration
```yaml
# estuary/collections/gong.flow.yaml
collections:
  sophia/gong-calls:
    schema:
      type: object
      properties:
        id: { type: string }
        title: { type: string }
        participants: { type: array }
        transcript: { type: string }
        sentiment: { type: number }
        created_at: { type: string, format: date-time }
      required: [id, title, created_at]
    
    key: [/id]
```

### HubSpot Integration
```yaml
# estuary/collections/hubspot.flow.yaml
collections:
  sophia/hubspot-deals:
    schema:
      type: object
      properties:
        dealId: { type: string }
        dealname: { type: string }
        amount: { type: number }
        stage: { type: string }
        closedate: { type: string, format: date-time }
      required: [dealId]
    
    key: [/dealId]
```

### Snowflake Materialization
```yaml
# estuary/materializations/snowflake.flow.yaml
materializations:
  sophia/snowflake-target:
    endpoint:
      connector:
        image: ghcr.io/estuary/materialize-snowflake:latest
        config:
          account: ${SNOWFLAKE_ACCOUNT}
          user: ${SNOWFLAKE_USER}
          password: ${SNOWFLAKE_PASSWORD}
          database: SOPHIA_AI
          schema: ESTUARY_DATA
          warehouse: COMPUTE_WH
    
    bindings:
      - source: sophia/gong-calls
        resource:
          table: gong_calls
          delta_updates: true
      
      - source: sophia/hubspot-deals
        resource:
          table: hubspot_deals
          delta_updates: true
```

## Python Integration Pattern

### Correct Pattern: Orchestration Only
```python
# infrastructure/etl/flow_orchestrator.py
from estuary_flow import FlowClient

class EstuaryFlowOrchestrator:
    """Orchestrates Estuary Flow operations"""
    
    def __init__(self):
        self.client = FlowClient(
            endpoint=get_config_value("estuary_endpoint"),
            token=get_config_value("estuary_token")
        )
    
    async def trigger_capture(self, collection: str):
        """Trigger a collection capture"""
        return await self.client.trigger_capture(collection)
    
    async def monitor_health(self):
        """Monitor Flow health"""
        return await self.client.get_collection_stats()
```

## Deprecated Patterns to Remove

### Files to Delete
1. `infrastructure/etl/gong_api_extractor_clean.py`
2. `infrastructure/etl/estuary_adapter.py` (if bypassing Flow)
3. Any direct API extraction scripts
4. Custom transformation scripts

### Code Patterns to Eliminate
```python
# ❌ REMOVE: Direct database writes
async def load_to_snowflake(data):
    conn = snowflake.connect()
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO...", data)

# ❌ REMOVE: Manual transformations
def transform_gong_data(raw_data):
    return [transform_record(r) for r in raw_data]

# ❌ REMOVE: Custom schedulers
@schedule.every(1).hour
def sync_data():
    extract_and_load()
```

## Monitoring and Operations

### Estuary Flow Dashboard
- Collection health metrics
- Throughput monitoring
- Error tracking
- Schema drift detection

### Alerting Rules
1. Collection failures
2. Materialization lag > 5 minutes
3. Schema validation errors
4. Connector errors

## Benefits of Full Estuary Adoption

1. **Real-time Data**: CDC instead of batch
2. **Automatic Retries**: Built-in reliability
3. **Schema Evolution**: Automatic handling
4. **Monitoring**: Native observability
5. **Cost Efficiency**: Pay per GB, not compute
6. **Simplicity**: Declarative > Imperative

## Governance

### New ETL Request Process
1. Check Estuary connector catalog
2. If available, use existing connector
3. If not, request custom connector
4. NO custom scripts allowed

### Review Checklist
- [ ] Is Estuary Flow being used?
- [ ] Are there any custom scripts?
- [ ] Is data flowing through collections?
- [ ] Are materializations configured?

## Success Metrics

1. **100% ETL through Estuary**: Zero custom scripts
2. **Real-time Data**: <1 minute latency
3. **Reliability**: >99.9% uptime
4. **Simplicity**: 80% code reduction

## Next Steps

1. Run ETL audit script
2. Create Estuary specifications
3. Configure connectors
4. Migrate existing pipelines
5. Remove deprecated code

## Appendix: Available Connectors

### Sources
- Gong (source-gong)
- HubSpot (source-hubspot)
- Slack (source-slack)
- Asana (source-asana)
- PostgreSQL (source-postgres)
- MySQL (source-mysql)
- MongoDB (source-mongodb)

### Destinations
- Snowflake (materialize-snowflake)
- PostgreSQL (materialize-postgres)
- Elasticsearch (materialize-elasticsearch)
- S3 (materialize-s3)

Remember: **Estuary Flow is the way**. No exceptions. 