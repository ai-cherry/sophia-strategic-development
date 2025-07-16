# Broken References Report

## Summary
Found 74 broken references across the codebase. These are primarily import statements pointing to modules that don't exist in their expected locations.

## Categories of Broken References

### 1. Core Module References (Most Common)
**Pattern**: `from core.* import` or `import core.*`
**Issue**: These should be `from backend.core.*` or the modules don't exist
**Count**: ~40+ occurrences

Examples:
- `from core.config_manager import get_config_value` → Should be `from backend.core.auto_esc_config import get_config_value`
- `from core.services.data_transformer import DataTransformer` → Module doesn't exist
- `from core.agents.base_agent import BaseAgent` → Should check if exists in backend structure
- `from core.workflows.*` → These workflow modules don't exist
- `from core.performance_monitor import performance_monitor` → Module doesn't exist
- `from core.optimized_connection_manager import connection_manager` → Module doesn't exist
- `from core.logger import logger` → Module doesn't exist

### 2. Shared Module References
**Pattern**: `from shared.* import`
**Issue**: The shared directory structure doesn't match these imports
**Count**: ~15 occurrences

Examples:
- `from shared.utils.custom_logger import logger`
- `from shared.utils.errors import APIError, RateLimitError`
- `from shared.security_config import SecurityConfig`

### 3. Config Module References
**Pattern**: `from config.* import`
**Issue**: No config directory at root level
**Count**: ~10 occurrences

Examples:
- `from config.infrastructure import InfrastructureConfig, ServiceType`
- `from config.production_infrastructure import PRODUCTION_INFRASTRUCTURE`

### 4. Infrastructure Module References
**Pattern**: Incorrect paths to infrastructure modules
**Count**: ~5 occurrences

Examples:
- `from backend.infrastructure.*` → Should be `from infrastructure.*`
- `from core.infra.cortex_gateway import get_gateway` → Module doesn't exist

### 5. Duplicate/Conflicting Imports
**Pattern**: Multiple different import attempts for the same functionality
**Count**: ~4 occurrences

Examples:
- Both `from core.config_manager` and `from backend.core.auto_esc_config` used for config

## Files with Most Broken References

1. **infrastructure/services/** - Multiple files with core.* imports
2. **libs/infrastructure/pulumi/** - Many core.* and shared.* imports
3. **infrastructure/sophia_iac_orchestrator.py** - Multiple backend.infrastructure.* imports
4. **core/agents/** - Various broken internal references

## Recommended Fixes

### 1. Standardize Configuration Imports
Replace all variations with:
```python
from backend.core.auto_esc_config import get_config_value
```

### 2. Fix Core Module Imports
Update all `from core.*` to `from backend.core.*` where applicable, or create the missing modules.

### 3. Resolve Shared Module Structure
Either:
- Create the expected shared module structure, or
- Update imports to use existing locations

### 4. Fix Config References
Move config files to expected locations or update import paths.

### 5. Create Missing Modules
The following commonly referenced modules need to be created or their imports updated:
- `core.performance_monitor`
- `core.config_manager` 
- `core.optimized_connection_manager`
- `core.logger`
- `shared.utils.custom_logger`
- `shared.utils.errors`

## Impact Assessment
- **High Priority**: Configuration and logging imports (affects entire system)
- **Medium Priority**: Service and workflow imports (affects specific features)
- **Low Priority**: Test file imports (affects testing only)

## Next Steps
1. Run automated fix script to update import paths
2. Create missing critical modules
3. Consolidate duplicate functionality
4. Update documentation with correct import patterns
5. Add pre-commit hooks to prevent future broken imports
