# Sophia AI Improvement Recommendations

## Overview
Based on the codebase review, here are actionable recommendations to improve code quality, reduce redundancy, and resolve conflicts.

## Phase 1: Critical Fixes (Week 1)

### 1.1 Fix Syntax Errors
**Files to fix:**
- `backend/app/routes/retool_api_routes.py` (line 24)
- `backend/mcp/tools/vector_tools.py` (line 131)
- `backend/agents/core/agent_framework.py and infrastructure/kubernetes/developer_tools_mcp_stack.py`

**Action:** Review and fix syntax errors, likely caused by merge conflicts or incomplete edits.

### 1.2 Fix Import Issues
**Script to run:**
```bash
python scripts/fix_imports.py
```

**Manual fixes needed for:**
- Replace all `from ...core.secret_manager` with `from backend.core.auto_esc_config`
- Replace all `from ..integrations.*` with `from backend.integrations.*`
- Replace all `from ..agents.*` with `from backend.agents.*`

### 1.3 Resolve Filename Conflict
**Issue:** `backend/agents/core/agent_framework.py and infrastructure/kubernetes/developer_tools_mcp_stack.py`
**Action:** This appears to be two files merged into one name. Separate them properly.

## Phase 2: Consolidation (Week 2)

### 2.1 Consolidate Main Entry Points
**Current state:**
- `backend/main.py`
- `backend/main_simple.py`
- `backend/main_dashboard.py`

**Recommendation:**
Create a single `backend/main.py` with environment-based configuration:
```python
import os
from backend.core.auto_esc_config import config

app_mode = os.getenv("APP_MODE", "full")  # full, simple, dashboard

if app_mode == "simple":
    # Load simple configuration
elif app_mode == "dashboard":
    # Load dashboard configuration
else:
    # Load full configuration
```

### 2.2 Merge Duplicate Integrations
**Gong Integration:**
- Keep: `backend/integrations/gong/enhanced_gong_integration.py`
- Remove: `backend/integrations/gong_integration.py`
- Update all imports

**Vector Integration:**
- Keep: `backend/vector/vector_integration_updated.py` (rename to `vector_integration.py`)
- Remove: `backend/vector/vector_integration.py`

**Estuary Integration:**
- Keep: `backend/integrations/estuary_flow_integration_updated.py` (rename to `estuary_integration.py`)
- Remove: `backend/integrations/estuary_flow_integration.py`

### 2.3 Consolidate Retool Routes
**Action:** Merge all Retool endpoints into a single router:
```python
# backend/app/routes/retool_routes.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/retool", tags=["retool"])

# Include all Retool endpoints here
# Executive dashboard endpoints
# Standard API endpoints
# WebSocket endpoints
```

## Phase 3: Standardization (Week 3)

### 3.1 Migrate to New Agent Framework
**Current agents using old base class:**
- `backend/agents/specialized/hr_agent.py`
- `backend/agents/specialized/marketing_agent.py`
- `backend/agents/specialized/client_health_agent.py`
- `backend/agents/specialized/sales_coach_agent.py`
- `backend/agents/specialized/enrichment_agent.py`

**Action:** Update all agents to inherit from `AgentFramework` instead of `BaseAgent`

### 3.2 Merge Data Connectors into Integrations
**Move files:**
- `backend/data_connectors/gong_connector.py` → `backend/integrations/gong/connector.py`
- `backend/data_connectors/slack_connector.py` → `backend/integrations/slack/connector.py`
- `backend/data_connectors/snowflake_connector.py` → `backend/integrations/snowflake/connector.py`

**Remove:** `backend/data_connectors/` directory

### 3.3 Standardize Configuration
**Use only:**
```python
from backend.core.auto_esc_config import config

# Access all configuration through this single interface
api_key = config.get_secret("service_name", "api_key")
```

**Remove references to:**
- Direct environment variable access
- `backend.core.secret_manager`
- `backend.core.config_manager` (unless it wraps auto_esc_config)

## Phase 4: Architecture Improvements (Week 4)

### 4.1 Implement Dependency Injection
**Create:** `backend/core/dependencies.py`
```python
from typing import Annotated
from fastapi import Depends

def get_gong_integration():
    from backend.integrations.gong.enhanced_gong_integration import GongIntegration
    return GongIntegration()

def get_agent_framework():
    from backend.agents.core.agent_framework import AgentFramework
    return AgentFramework()

# Use in routes:
# def route(gong: Annotated[GongIntegration, Depends(get_gong_integration)]):
```

### 4.2 Create Service Registry
**Create:** `backend/core/service_registry.py`
```python
class ServiceRegistry:
    """Central registry for all services and integrations."""

    _services = {}

    @classmethod
    def register(cls, name: str, service_class):
        cls._services[name] = service_class

    @classmethod
    def get(cls, name: str):
        return cls._services.get(name)
```

### 4.3 Standardize File Naming
**Convention:**
- Integration files: `{service}_integration.py`
- Agent files: `{function}_agent.py`
- MCP servers: `{service}_mcp_server.py`
- No version suffixes (use git for versioning)

## Phase 5: Testing and Documentation (Ongoing)

### 5.1 Add Type Hints
**Priority files:**
- All files in `backend/core/`
- All files in `backend/agents/core/`
- All integration base classes

### 5.2 Create Integration Tests
**For each consolidated component:**
- Test that old imports still work (with deprecation warnings)
- Test that new structure maintains functionality
- Test configuration access patterns

### 5.3 Update Documentation
**Create/Update:**
- `docs/ARCHITECTURE.md` - Current architecture after cleanup
- `docs/MIGRATION_GUIDE.md` - For developers updating their code
- `docs/API_CHANGES.md` - Breaking changes and deprecations

## Implementation Checklist

- [ ] Fix all syntax errors
- [ ] Run import fix script
- [ ] Resolve filename conflicts
- [ ] Consolidate main.py files
- [ ] Merge duplicate integrations
- [ ] Consolidate Retool routes
- [ ] Migrate agents to new framework
- [ ] Merge data_connectors into integrations
- [ ] Standardize configuration access
- [ ] Implement dependency injection
- [ ] Create service registry
- [ ] Standardize file naming
- [ ] Add type hints to core modules
- [ ] Create integration tests
- [ ] Update documentation

## Success Metrics

1. **Import Health:** Zero deep relative imports (level > 1)
2. **No Duplicates:** Single implementation for each service
3. **Consistent Patterns:** All agents use same base class
4. **Clean Structure:** Clear separation of concerns
5. **Test Coverage:** All critical paths have tests

## Notes

- Keep backward compatibility where possible
- Add deprecation warnings for removed patterns
- Document all breaking changes
- Test thoroughly before removing old code
- Consider using feature flags for gradual rollout
