# Snowflake + Lambda Labs Integration Plan

## Executive Summary

This document outlines the integration plan for enhancing Sophia AI with the recommended Snowflake PAT authentication and unified AI service improvements. After thorough analysis of the current codebase, we've identified what's already in place and what needs to be added or enhanced.

## Current State Analysis

### ✅ Already Implemented

1. **Lambda Labs Service** (`backend/services/lambda_labs_service.py`)
   - Intelligent model selection
   - Cost tracking and budget enforcement
   - Natural language to SQL conversion
   - Health monitoring

2. **Unified Chat Service** (`backend/services/unified_chat_service.py`)
   - Lambda Labs integration
   - Service mapping with dynamic routing
   - Multi-source data orchestration

3. **Secret Management** (`backend/core/secret_mappings.py`)
   - Clean Lambda Labs API key configuration
   - Snowflake credential mappings
   - Service dependencies defined

4. **Snowflake Services**
   - Multiple implementations exist:
     - `infrastructure/services/enhanced_snowflake_cortex_service.py`
     - `infrastructure/services/cortex_agent_service.py`
     - `shared/utils/snowflake_cortex_service.py`

### 🔄 Needs Enhancement

1. **Snowflake PAT Authentication**
   - Current implementations use standard password authentication
   - Need to update for PAT token support

2. **Unified AI Service**
   - Multiple LLM routing services exist but lack unified interface
   - Need intelligent routing between Snowflake Cortex and Lambda Labs

3. **Natural Language Infrastructure Control**
   - Exists but needs enhancement for comprehensive control

4. **Cost Optimization**
   - Basic tracking exists but needs advanced optimization

## Integration Plan

### Phase 1: Enhance Secret Management (IMMEDIATE)

#### 1.1 Update `backend/core/auto_esc_config.py`
```python
# Add these enhancements to existing file
def validate_snowflake_pat() -> bool:
    """Validate Snowflake PAT token format"""
    pat = get_config_value("snowflake_password")
    if not pat:
        return False

    # PAT tokens typically start with specific patterns
    if pat.startswith("eyJ") and len(pat) > 100:
        return True

    logger.warning("Snowflake password may not be a valid PAT token")
    return False

# Update SNOWFLAKE_CONFIG with validated values
SNOWFLAKE_CONFIG = {
    "account": "UHDECNO-CVB64222",
    "user": "SCOOBYJAVA15",
    "role": "ACCOUNTADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "SOPHIA_AI_PROD",
    "schema": "PUBLIC",
    "authenticator": "snowflake"  # For PAT authentication
}
```

#### 1.2 Create `infrastructure/services/snowflake_pat_service.py`
```python
"""
Snowflake PAT Authentication Service
Enhances existing Snowflake services with PAT support
"""

import snowflake.connector
from backend.core.auto_esc_config import get_config_value, SNOWFLAKE_CONFIG
from shared.utils.snowflake_cortex_service import SnowflakeCortexService

class SnowflakePATService(SnowflakeCortexService):
    """Enhanced Snowflake service with PAT authentication"""

    def __init__(self):
        super().__init__()
        self.pat_token = get_config_value("snowflake_password")

    async def _create_connection(self):
        """Create connection with PAT authentication"""
        return snowflake.connector.connect(
            account=SNOWFLAKE_CONFIG["account"],
            user=SNOWFLAKE_CONFIG["user"],
            password=self.pat_token,  # PAT token as password
            role=SNOWFLAKE_CONFIG["role"],
            warehouse=SNOWFLAKE_CONFIG["warehouse"],
            database=SNOWFLAKE_CONFIG["database"],
            schema=SNOWFLAKE_CONFIG["schema"],
            authenticator=SNOWFLAKE_CONFIG["authenticator"]
        )
```

### Phase 2: Create Unified AI Service (HIGH PRIORITY)

#### 2.1 Create `infrastructure/services/unified_ai_orchestrator.py`
```python
"""
Unified AI Orchestrator
Intelligent routing between Snowflake Cortex and Lambda Labs
"""

from enum import Enum
from typing import Optional
from backend.services.lambda_labs_service import LambdaLabsService
from infrastructure.services.snowflake_pat_service import SnowflakePATService
from infrastructure.services.llm_router import TaskType, TaskComplexity

class AIProvider(Enum):
    SNOWFLAKE_CORTEX = "snowflake_cortex"
    LAMBDA_LABS = "lambda_labs"
    AUTO = "auto"

class UnifiedAIOrchestrator:
    """Orchestrates AI requests between providers"""

    def __init__(self):
        self.lambda_service = LambdaLabsService()
        self.snowflake_service = SnowflakePATService()

    async def process_request(
        self,
        prompt: str,
        provider: AIProvider = AIProvider.AUTO,
        **kwargs
    ):
        """Process AI request with intelligent routing"""

        if provider == AIProvider.AUTO:
            provider = self._select_provider(prompt, kwargs)

        if provider == AIProvider.LAMBDA_LABS:
            return await self._process_lambda(prompt, **kwargs)
        else:
            return await self._process_snowflake(prompt, **kwargs)

    def _select_provider(self, prompt: str, kwargs: dict) -> AIProvider:
        """Intelligently select provider based on request"""

        # Data-local operations prefer Snowflake
        if any(kw in prompt.lower() for kw in ["sql", "query", "data", "analytics"]):
            return AIProvider.SNOWFLAKE_CORTEX

        # Complex reasoning prefers Lambda Labs
        if kwargs.get("complexity") == "high":
            return AIProvider.LAMBDA_LABS

        # Cost optimization
        if kwargs.get("cost_priority") == "low":
            return AIProvider.LAMBDA_LABS

        return AIProvider.LAMBDA_LABS  # Default
```

### Phase 3: Enhance Natural Language Control (MEDIUM PRIORITY)

#### 3.1 Enhance `core/services/natural_language_infrastructure_controller.py`
```python
# Add these methods to existing controller

async def optimize_infrastructure(self, command: str) -> dict:
    """Natural language infrastructure optimization"""

    # Parse optimization intent
    if "reduce cost" in command.lower():
        return await self._optimize_for_cost()
    elif "improve performance" in command.lower():
        return await self._optimize_for_performance()
    elif "balance" in command.lower():
        return await self._optimize_balanced()

async def _optimize_for_cost(self):
    """Optimize infrastructure for cost"""

    # Analyze current usage
    lambda_usage = await self.lambda_router.get_usage_analytics()

    # Generate recommendations
    recommendations = []

    if lambda_usage["current_usage"]["daily_cost"] > 40:
        recommendations.append({
            "action": "shift_to_smaller_models",
            "impact": "20-30% cost reduction",
            "implementation": "Update model selection thresholds"
        })

    return {
        "optimization_target": "cost",
        "current_daily_cost": lambda_usage["current_usage"]["daily_cost"],
        "projected_savings": "20-30%",
        "recommendations": recommendations
    }
```

### Phase 4: Update Documentation (LOW PRIORITY)

#### 4.1 Update System Handbook
- Add new Snowflake PAT authentication details
- Document unified AI orchestrator
- Update cost optimization strategies

#### 4.2 Create Migration Guide
- Step-by-step PAT token setup
- Testing procedures
- Rollback plan

## Implementation Strategy

### Week 1: Foundation
1. **Day 1-2**: Implement Snowflake PAT authentication
   - Update `auto_esc_config.py`
   - Create `snowflake_pat_service.py`
   - Test connection with PAT token

2. **Day 3-4**: Create Unified AI Orchestrator
   - Implement `unified_ai_orchestrator.py`
   - Add intelligent routing logic
   - Test with various workloads

3. **Day 5**: Integration Testing
   - Test PAT authentication
   - Validate AI routing
   - Performance benchmarks

### Week 2: Enhancement
1. **Day 1-2**: Natural Language Control
   - Enhance infrastructure controller
   - Add optimization commands
   - Test natural language processing

2. **Day 3-4**: Monitoring & Analytics
   - Enhanced cost tracking
   - Performance monitoring
   - Usage analytics

3. **Day 5**: Documentation
   - Update all documentation
   - Create user guides
   - Training materials

## Risk Mitigation

### Potential Issues and Solutions

1. **PAT Token Expiration**
   - Monitor token expiration dates
   - Implement automatic rotation alerts
   - Document renewal process

2. **Service Conflicts**
   - Gradually migrate services
   - Maintain backward compatibility
   - Use feature flags for rollout

3. **Cost Overruns**
   - Implement strict budget controls
   - Real-time monitoring
   - Automatic throttling

## Success Metrics

### Technical Metrics
- ✅ PAT authentication working
- ✅ <2 second response times
- ✅ 99.9% uptime
- ✅ Zero security incidents

### Business Metrics
- ✅ 85-93% cost reduction maintained
- ✅ Improved query performance
- ✅ Enhanced user satisfaction
- ✅ Reduced operational overhead

## Rollout Plan

### Phase 1: Development Environment
- Deploy all changes to dev
- Run comprehensive tests
- Monitor for 48 hours

### Phase 2: Staging Environment
- Deploy to staging
- Run integration tests
- User acceptance testing

### Phase 3: Production Rollout
- Deploy during maintenance window
- Monitor closely for 24 hours
- Have rollback plan ready

## Conclusion

This integration plan builds upon Sophia AI's existing strong foundation while adding the recommended enhancements. By focusing on what's truly needed and avoiding duplication, we can achieve the desired improvements with minimal disruption and maximum benefit.

The plan prioritizes:
1. **Immediate value**: PAT authentication and cost optimization
2. **Gradual enhancement**: Building on existing services
3. **Risk mitigation**: Careful testing and rollout
4. **Maintainability**: Clean architecture and documentation

With this approach, Sophia AI will achieve the promised 85-93% cost reduction while maintaining enterprise-grade performance and reliability.
