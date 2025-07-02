# Comprehensive Refactoring and Code Quality Remediation Prompt

## Overview
You are tasked with implementing a systematic refactoring and cleanup pass across the Sophia AI repository. The codebase currently contains oversized modules (2000+ lines), business logic in API controllers, functions exceeding 200+ lines, numerous backup files, and 3000+ code quality issues.

Your goal is to decompose monolithic modules, extract business logic, refactor large functions, clean up deprecated files, and address code quality issues while maintaining 100% backward compatibility and functionality.

## Prerequisites
- Python 3.11+ environment with all dependencies installed
- Git repository with clean working directory
- Pre-commit hooks configured (ruff, black, isort, mypy)
- Backup strategy in place before making changes

## Task 1: Split Monolithic Snowflake Cortex Service (Priority: CRITICAL)

### Current State
- File: `backend/utils/snowflake_cortex_service.py` (~2237 lines)
- Contains: Database connections, AI operations, caching, monitoring, business logic
- Issue: Violates Single Responsibility Principle, difficult to maintain and test

### Implementation Steps

#### Step 1.1: Create Core Module
```bash
# Create: backend/utils/snowflake_cortex_service_core.py
```
Move the following classes and methods:
- `SnowflakeCortexService` main class (constructor, connection management)
- Core database connection methods: `_create_connection()`, `_execute_query()`, `_close_connection()`
- Basic configuration loading and validation
- Essential error handling and logging setup

#### Step 1.2: Create Models Module
```bash
# Create: backend/utils/snowflake_cortex_service_models.py
```
Move the following:
- All dataclasses and Pydantic models (CortexOperation, ProcessingMode, CortexResult, etc.)
- Enum definitions (OperationType, ProcessingStatus, etc.)
- Type definitions and constants
- Configuration schemas and validation models

#### Step 1.3: Create Utils Module
```bash
# Create: backend/utils/snowflake_cortex_service_utils.py
```
Move the following:
- Helper functions: `_escape_sql()`, `_generate_cache_key()`, `_format_query()`
- Utility classes: CortexUtils, QueryBuilder, ResultFormatter
- Performance monitoring and metrics collection
- Cache management utilities

#### Step 1.4: Create Handlers Module
```bash
# Create: backend/utils/snowflake_cortex_service_handlers.py
```
Move the following:
- AI operation handlers: `generate_embeddings()`, `analyze_sentiment()`, `search_vectors()`
- Business-specific methods: `store_business_embedding()`, `search_business_table()`
- Batch processing methods and workflow orchestration
- Integration-specific handlers (HubSpot, Gong, etc.)

#### Step 1.5: Create Facade
Update `backend/utils/snowflake_cortex_service.py`:
```python
"""
Snowflake Cortex Service - Main Interface
Facade pattern implementation for backward compatibility
"""

from .snowflake_cortex_service_core import SnowflakeCortexService
from .snowflake_cortex_service_models import *
from .snowflake_cortex_service_utils import CortexUtils
from .snowflake_cortex_service_handlers import *

# Re-export main class for backward compatibility
__all__ = ['SnowflakeCortexService', 'CortexUtils', 'CortexOperation', 'CortexResult']
```

#### Step 1.6: Update Imports
Search and update imports across the codebase:
```bash
# Find all files importing from snowflake_cortex_service
grep -r "from.*snowflake_cortex_service import" . --include="*.py"
grep -r "import.*snowflake_cortex_service" . --include="*.py"

# Update imports to use the facade (most should work unchanged)
# Only update if specific internal classes are imported
```

## Task 2: Decompose Sales Intelligence Agent (Priority: HIGH)

### Current State
- File: `backend/agents/specialized/sales_intelligence_agent.py` (~1300 lines)
- Contains: Agent logic, data processing, API integrations, business rules

### Implementation Steps

#### Step 2.1: Create Agent Core
```bash
# Create: backend/agents/specialized/sales_intelligence_agent_core.py
```
Move:
- `SalesIntelligenceAgent` main class
- Core agent initialization and configuration
- Main orchestration methods: `execute_task()`, `process_request()`
- Agent lifecycle management

#### Step 2.2: Create Models
```bash
# Create: backend/agents/specialized/sales_intelligence_agent_models.py
```
Move:
- Data models: `SalesMetrics`, `DealAnalysis`, `CompetitorInsight`
- Request/response models for API interactions
- Configuration models and validation schemas
- Enum definitions for sales processes

#### Step 2.3: Create Utils
```bash
# Create: backend/agents/specialized/sales_intelligence_agent_utils.py
```
Move:
- Utility functions: data transformation, formatting, validation
- Helper classes for calculations and analysis
- Common business logic utilities
- Integration helpers and adapters

#### Step 2.4: Create Handlers
```bash
# Create: backend/agents/specialized/sales_intelligence_agent_handlers.py
```
Move:
- Specific business handlers: `analyze_deal_risk()`, `generate_coaching_insights()`
- External API integration handlers (HubSpot, Gong, Salesforce)
- Data processing pipelines and workflows
- Report generation and formatting logic

#### Step 2.5: Update Main File
Keep `sales_intelligence_agent.py` as a facade:
```python
"""
Sales Intelligence Agent - Main Interface
"""

from .sales_intelligence_agent_core import SalesIntelligenceAgent
from .sales_intelligence_agent_models import *
from .sales_intelligence_agent_utils import SalesIntelligenceUtils
from .sales_intelligence_agent_handlers import *

__all__ = ['SalesIntelligenceAgent']
```

## Task 3: Refactor Gong Data Quality Module (Priority: HIGH)

### Current State
- File: `backend/monitoring/gong_data_quality.py`
- Contains: Data validation, quality metrics, monitoring, reporting

### Implementation Steps

#### Step 3.1: Create Core Module
```bash
# Create: backend/monitoring/gong_data_quality_core.py
```
Move:
- Main `GongDataQualityMonitor` class
- Core monitoring logic and orchestration
- Configuration and initialization methods

#### Step 3.2: Create Models Module
```bash
# Create: backend/monitoring/gong_data_quality_models.py
```
Move:
- Quality metrics models: `DataQualityReport`, `ValidationResult`
- Configuration models and schemas
- Error and warning model definitions

#### Step 3.3: Create Utils Module
```bash
# Create: backend/monitoring/gong_data_quality_utils.py
```
Move:
- Validation utilities and helper functions
- Data transformation and cleaning utilities
- Reporting and formatting helpers

#### Step 3.4: Create Handlers Module
```bash
# Create: backend/monitoring/gong_data_quality_handlers.py
```
Move:
- Specific validation handlers for different data types
- Quality check implementations
- Alert and notification handlers

## Task 4: Break Down Enhanced AI Memory MCP Server (Priority: HIGH)

### Current State
- File: `backend/mcp_servers/enhanced_ai_memory_mcp_server.py` (1500+ lines)
- Contains: MCP protocol implementation, memory operations, AI integration

### Implementation Steps

#### Step 4.1: Create Core Module
```bash
# Create: backend/mcp_servers/ai_memory_server_core.py
```
Move:
- Main `EnhancedAiMemoryMCPServer` class
- MCP protocol implementation
- Server lifecycle and connection management

#### Step 4.2: Create Memory Operations Module
```bash
# Create: backend/mcp_servers/ai_memory_operations.py
```
Move:
- Memory storage and retrieval operations
- Search and query implementations
- Memory categorization and tagging logic

#### Step 4.3: Create AI Integration Module
```bash
# Create: backend/mcp_servers/ai_memory_integration.py
```
Move:
- OpenAI API integration
- Embedding generation and management
- Vector search implementations

#### Step 4.4: Create Models Module
```bash
# Create: backend/mcp_servers/ai_memory_models.py
```
Move:
- Memory data models and schemas
- Request/response models for MCP protocol
- Configuration and validation models

## Task 5: Extract Business Logic from API Controllers (Priority: CRITICAL)

### Current State
- File: `backend/api/enhanced_ceo_chat_routes.py`
- Issue: Contains business logic mixed with HTTP handling

### Implementation Steps

#### Step 5.1: Create Use Cases
```bash
# Create: backend/application/use_cases/ceo_chat_use_cases.py
```
Extract and move:
- `_generate_suggestions()` → `GenerateCEOSuggestionsUseCase`
- `validate_ceo_access()` → `ValidateCEOAccessUseCase`
- Business validation logic → `ValidateCEORequestUseCase`
- Data processing logic → `ProcessCEOQueryUseCase`

#### Step 5.2: Create Domain Services
```bash
# Create: backend/domain/services/ceo_intelligence_service.py
```
Move:
- Core business logic for CEO operations
- Data aggregation and analysis
- Business rule implementations

#### Step 5.3: Update API Controller
Refactor `enhanced_ceo_chat_routes.py`:
```python
# Before (mixed concerns)
@router.post("/ceo/chat")
async def ceo_chat_endpoint(request: CEOChatRequest):
    # Validation logic (should be in use case)
    if not validate_ceo_access(request.user_id):
        raise HTTPException(403, "Access denied")
    
    # Business logic (should be in use case)
    suggestions = _generate_suggestions(request.query)
    
    # More business logic...
    return response

# After (clean separation)
@router.post("/ceo/chat")
async def ceo_chat_endpoint(
    request: CEOChatRequest,
    use_case: CEOChatUseCase = Depends(get_ceo_chat_use_case)
):
    try:
        result = await use_case.execute(request)
        return CEOChatResponse.from_domain(result)
    except UnauthorizedError:
        raise HTTPException(403, "Access denied")
    except ValidationError as e:
        raise HTTPException(400, str(e))
```

## Task 6: Refactor Large Functions (Priority: MEDIUM)

### Target: `deploy_asana_transformation_procedures()` (~390 lines)

#### Step 6.1: Extract Private Methods
Break down into smaller methods:
```python
# Original large function
async def deploy_asana_transformation_procedures(self) -> bool:
    # 390 lines of code...

# Refactored into smaller methods
async def deploy_asana_transformation_procedures(self) -> bool:
    """Main orchestration method"""
    try:
        await self._validate_prerequisites()
        await self._create_base_schema()
        await self._deploy_project_transformations()
        await self._deploy_task_transformations()
        await self._deploy_user_transformations()
        await self._create_ai_procedures()
        await self._validate_deployment()
        return True
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        await self._rollback_changes()
        return False

async def _validate_prerequisites(self):
    """Validate deployment prerequisites (20-30 lines)"""
    # Extracted validation logic

async def _create_base_schema(self):
    """Create base schema and tables (30-40 lines)"""
    # Extracted schema creation

async def _deploy_project_transformations(self):
    """Deploy project transformation procedures (40-50 lines)"""
    # Extracted project logic

# Continue for other extracted methods...
```

#### Step 6.2: Apply Same Pattern to Other Large Functions
Target functions from `FUNCTION_LENGTH_COMPLIANCE_REPORT.md`:
- Functions >200 lines: Extract into 3-5 smaller methods
- Functions >100 lines: Extract into 2-3 smaller methods
- Use descriptive method names that explain the purpose
- Maintain single responsibility for each extracted method

## Task 7: Clean Up Backup and Deprecated Files (Priority: LOW)

### Implementation Steps

#### Step 7.1: Remove Backup Files
```bash
# Find all backup files
find . -name "*.backup" -type f | grep -v ".venv" | grep -v ".git"

# Remove backup files (after confirming they're not needed)
find . -name "*.backup" -type f -not -path "./.venv/*" -not -path "./.git/*" -delete

# Also remove other backup patterns
find . -name "*_backup*" -type f -not -path "./.venv/*" -not -path "./.git/*"
find . -name "*.bak" -type f -not -path "./.venv/*" -not -path "./.git/*"
```

#### Step 7.2: Remove Deprecated Apps
```bash
# Remove deprecated FastAPI apps
rm -rf backend/app/_deprecated_apps/

# Remove other deprecated directories
find . -name "*deprecated*" -type d -not -path "./.venv/*" -not -path "./.git/*"
```

#### Step 7.3: Clean Up Temporary Files
```bash
# Remove temporary files
find . -name "*.tmp" -o -name "*.temp" -o -name "*.cache" | grep -v ".venv" | xargs rm -f

# Remove empty directories
find . -type d -empty -not -path "./.venv/*" -not -path "./.git/*" -delete
```

## Task 8: Address Code Quality Issues (Priority: HIGH)

### Implementation Steps

#### Step 8.1: Fix Syntax Errors
```bash
# Run ruff to identify syntax errors
ruff check . --select E999 --output-format=text

# Fix each syntax error manually
# Common issues: missing parentheses, incorrect indentation, invalid syntax
```

#### Step 8.2: Fix Undefined Names
```bash
# Find undefined name errors
ruff check . --select F821 --output-format=text

# Add missing imports
# Fix variable name typos
# Remove references to deleted variables/functions
```

#### Step 8.3: Apply Automated Fixes
```bash
# Run ruff with automatic fixes
ruff check . --fix --unsafe-fixes

# Run black for formatting
black .

# Run isort for import sorting
isort .
```

#### Step 8.4: Address Import Issues
```bash
# Fix import order issues
ruff check . --select I --fix

# Remove unused imports
ruff check . --select F401 --fix

# Fix circular import issues by restructuring imports
```

#### Step 8.5: Type Checking
```bash
# Run mypy for type checking
mypy backend/ --ignore-missing-imports

# Add missing type hints
# Fix type annotation errors
# Add `# type: ignore` comments where necessary
```

## Validation and Testing

### After Each Task
1. **Run Tests**: Ensure all existing tests pass
   ```bash
   pytest tests/ -v
   ```

2. **Check Imports**: Verify no import errors
   ```bash
   python -c "import backend.utils.snowflake_cortex_service; print('OK')"
   ```

3. **Run Code Quality Checks**:
   ```bash
   ruff check .
   black --check .
   mypy backend/
   ```

4. **Test Functionality**: Manually test affected features

### Final Validation
1. **Complete Test Suite**: Run full test suite
2. **Integration Tests**: Test API endpoints and MCP servers
3. **Performance Tests**: Ensure no performance regressions
4. **Documentation**: Update any affected documentation

## Expected Outcomes

### Quantitative Improvements
- **Module Size Reduction**: 4 modules from 2000+ lines to <500 lines each
- **Function Length Compliance**: 95% of functions under 50 lines
- **Code Quality Issues**: Reduction from 3000+ to <500 issues
- **Repository Cleanup**: Removal of 50+ backup files

### Qualitative Improvements
- **Maintainability**: Easier to understand and modify code
- **Testability**: Smaller, focused modules are easier to test
- **Reusability**: Extracted utilities can be reused across modules
- **Clean Architecture**: Clear separation between API, business logic, and infrastructure

## Risk Mitigation

### Backup Strategy
```bash
# Create backup before starting
git branch refactoring-backup-$(date +%Y%m%d)
git checkout -b systematic-refactoring
```

### Incremental Approach
- Complete one task at a time
- Commit after each successful task
- Test thoroughly before moving to next task

### Rollback Plan
- Each task should be in separate commits
- Use `git revert` if issues are discovered
- Maintain backward compatibility throughout

## Success Criteria

### Technical Criteria
- [ ] All modules under 1000 lines
- [ ] All functions under 100 lines (target: 50 lines)
- [ ] No business logic in API controllers
- [ ] Clean code quality report (<500 issues)
- [ ] All tests passing
- [ ] No backup files in repository

### Business Criteria
- [ ] 100% backward compatibility maintained
- [ ] No functionality lost or changed
- [ ] Performance maintained or improved
- [ ] Deployment process unchanged
- [ ] API contracts unchanged

This systematic approach will transform the codebase into a maintainable, well-structured, and high-quality system while preserving all existing functionality. 