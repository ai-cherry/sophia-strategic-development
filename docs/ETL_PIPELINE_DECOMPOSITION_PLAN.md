# ETL Pipeline Decomposition Plan

**Date:** July 9, 2025  
**Priority:** HIGH  
**Timeline:** 1 week

## Executive Summary

The current ETL pipeline (`infrastructure/etl/enhanced_unified_data_pipeline.py`) is a 900+ line monolith that needs decomposition. Additionally, redundant standalone scripts like `gong_api_extractor_clean.py` create maintenance burden and potential data inconsistencies.

## Current State

### Problems
1. **Monolithic Design**: Single 900+ line file handling all ETL operations
2. **Redundant Scripts**: 
   - `gong_api_extractor_clean.py` duplicates Estuary functionality
   - `estuary_adapter.py` unclear relationship with main pipeline
3. **Hardcoded Configurations**: Source schemas embedded in Python code
4. **Poor Testability**: Difficult to unit test individual components
5. **Tight Coupling**: All data sources mixed in single class

## Decomposition Strategy

### New Architecture
```
infrastructure/etl/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── base_pipeline.py         # Abstract base classes
│   ├── pipeline_orchestrator.py  # Main orchestration logic
│   └── exceptions.py            # Custom exceptions
├── models/
│   ├── __init__.py
│   ├── source_config.py         # Source configuration models
│   ├── pipeline_state.py        # Pipeline state tracking
│   └── data_models.py           # Pydantic models for data
├── connectors/
│   ├── __init__.py
│   ├── gong_connector.py        # Gong-specific logic
│   ├── hubspot_connector.py     # HubSpot-specific logic
│   ├── slack_connector.py       # Slack-specific logic
│   └── estuary_connector.py     # Estuary Flow wrapper
├── transformers/
│   ├── __init__.py
│   ├── base_transformer.py      # Abstract transformer
│   ├── gong_transformer.py      # Gong data transformations
│   └── unified_transformer.py   # Cross-source transformations
├── utils/
│   ├── __init__.py
│   ├── monitoring.py            # Metrics and logging
│   ├── validation.py            # Data validation
│   └── config_loader.py         # Configuration loading
└── configs/
    ├── sources/
    │   ├── gong.yaml           # Gong source config
    │   ├── hubspot.yaml        # HubSpot source config
    │   └── slack.yaml          # Slack source config
    └── pipeline.yaml           # Main pipeline config
```

## Implementation Steps

### Phase 1: Setup (Day 1)
1. Create new directory structure
2. Set up base classes and interfaces
3. Create configuration schemas
4. Set up testing framework

### Phase 2: Extract Core (Day 2)
1. Extract orchestration logic to `pipeline_orchestrator.py`
2. Create abstract base classes
3. Extract monitoring and metrics
4. Set up dependency injection

### Phase 3: Extract Connectors (Day 3)
1. Create connector interface
2. Extract Gong connector logic
3. Extract HubSpot connector logic
4. Extract other source connectors

### Phase 4: Extract Configurations (Day 4)
1. Convert hardcoded configs to YAML
2. Create configuration loader
3. Validate all configurations
4. Update deployment scripts

### Phase 5: Migration (Day 5)
1. Update imports in dependent code
2. Create migration script
3. Test end-to-end pipeline
4. Update documentation

### Phase 6: Cleanup (Day 6-7)
1. Remove old monolithic file
2. Delete redundant scripts
3. Update CI/CD pipelines
4. Performance testing

## Code Examples

### Base Pipeline Class
```python
# infrastructure/etl/core/base_pipeline.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePipeline(ABC):
    """Abstract base class for all pipelines"""
    
    @abstractmethod
    async def extract(self) -> Dict[str, Any]:
        """Extract data from source"""
        pass
    
    @abstractmethod
    async def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform extracted data"""
        pass
    
    @abstractmethod
    async def load(self, data: Dict[str, Any]) -> None:
        """Load transformed data"""
        pass
```

### Configuration Example
```yaml
# infrastructure/etl/configs/sources/gong.yaml
source:
  name: gong
  type: estuary
  connector: source-gong
  config:
    api_endpoint: ${GONG_API_ENDPOINT}
    api_token: ${GONG_API_KEY}
    start_date: "2024-01-01"
  
destination:
  type: snowflake
  schema: GONG_DATA
  tables:
    - calls
    - transcripts
    - users
```

## Migration of Redundant Scripts

### Scripts to Remove
1. **gong_api_extractor_clean.py**
   - Functionality moved to `connectors/gong_connector.py`
   - Staging tables consolidated into unified schema
   
2. **One-time migration scripts**
   - Archive after successful migration
   - Document in migration log

### Data Migration
```sql
-- Migrate standalone Gong tables to unified schema
INSERT INTO unified_data.gong_calls
SELECT * FROM gong_staging.stg_gong_calls;

-- Drop old tables after validation
DROP TABLE IF EXISTS gong_staging.stg_gong_calls;
```

## Testing Strategy

1. **Unit Tests**: Each module independently testable
2. **Integration Tests**: Test connector interfaces
3. **E2E Tests**: Full pipeline execution
4. **Performance Tests**: Ensure no degradation

## Success Metrics

1. **Code Metrics**:
   - No file > 200 lines
   - Test coverage > 80%
   - Cyclomatic complexity < 10

2. **Performance Metrics**:
   - Pipeline execution time unchanged
   - Memory usage reduced by 20%
   - Easier parallel execution

3. **Maintenance Metrics**:
   - 50% reduction in bug fix time
   - New connector addition < 2 hours
   - Configuration changes without code changes

## Risk Mitigation

1. **Parallel Running**: Keep old pipeline during migration
2. **Feature Flags**: Gradual rollout of new pipeline
3. **Rollback Plan**: Quick revert to monolithic version
4. **Data Validation**: Checksum comparisons between old/new

## Next Steps

1. Review and approve plan
2. Create feature branch
3. Begin Phase 1 implementation
4. Daily progress updates

## Appendix: Dependency Analysis

Current dependencies on the monolithic pipeline:
- Airflow DAGs
- Monitoring dashboards
- Data quality checks
- Downstream consumers

All will need updates during migration. 