# Long Function Refactoring Strategy for Sophia AI

## Overview
Lizard code complexity analyzer has identified **200+ functions exceeding the 50-line limit**, ranging from 51 to 313 lines. This document provides a systematic approach to refactor these functions for improved maintainability.

## Critical Issues Identified

### Highest Priority (>150 lines)
1. **`enhance_sophia_intelligence_mcp`** (313 lines) - MCP orchestration
2. **`create_chrome_extension`** (291 lines) - Chrome extension setup  
3. **`JSON.stringify` instances** (214-277 lines) - Infrastructure configs
4. **`pulumi.output` functions** (170-223 lines) - Infrastructure deployment
5. **`create_transformation_procedures`** (233 lines) - ETL procedures

### High Priority (100-150 lines)
1. **`create_application_router`** (129 lines) - Core API routing
2. **`generate_marketing_content`** (109 lines) - Marketing agent
3. **`vector_search_business_table`** (128 lines) - Snowflake search
4. **`setup_prompt_management`** (124 lines) - Prompt configuration
5. **`_initialize_default_alert_rules`** (133 lines) - Monitoring setup

### Medium Priority (75-99 lines)
1. **`unified_chat_endpoint`** (60 lines) - Chat API
2. **`process_request`** (73 lines) - Orchestrator core
3. **`get_issue_details`** (64 lines) - Linear integration
4. **`main` functions** (71+ lines) - Multiple deployment scripts
5. **`__init__` methods** (76-113 lines) - Service initialization

## Refactoring Patterns

### 1. Extract Method Pattern
Break monolithic functions into focused helper methods:

```python
# BEFORE: 129-line create_application_router
def create_application_router() -> APIRouter:
    router = APIRouter()
    # 129 lines of router.include_router calls...
    return router

# AFTER: Refactored with helper methods
def create_application_router() -> APIRouter:
    """Create and configure the main application router"""
    router = APIRouter()
    
    _setup_core_routes(router)
    _setup_integration_routes(router)
    _setup_data_routes(router)
    _setup_admin_routes(router)
    
    return router

def _setup_core_routes(router: APIRouter) -> None:
    """Setup core application routes"""
    router.include_router(enhanced_cortex_routes.router, prefix="/api/v1/cortex")
    router.include_router(sophia_universal_chat_routes.router, prefix="/api/v1/chat")
    # ... other core routes

def _setup_integration_routes(router: APIRouter) -> None:
    """Setup third-party integration routes"""
    router.include_router(asana_integration_routes.router, prefix="/api/v1/integrations/asana")
    # ... other integration routes
```

### 2. Configuration Object Pattern
For complex initialization:

```python
# BEFORE: 104-line __init__
def __init__(self, param1, param2, param3, ...):
    # 104 lines of mixed initialization logic

# AFTER: Structured initialization
@dataclass
class ServiceConfig:
    database_url: str
    api_keys: Dict[str, str]
    feature_flags: Dict[str, bool]

def __init__(self, config: ServiceConfig):
    self._setup_core_components(config)
    self._initialize_connections(config)
    self._configure_features(config)
    self._finalize_setup(config)
```

### 3. Builder Pattern
For complex object construction:

```python
# BEFORE: 200+ line JSON.stringify
infrastructure_config = JSON.stringify({
    # 200+ lines of nested configuration
})

# AFTER: Builder pattern
class InfrastructureConfigBuilder:
    def __init__(self):
        self.config = {}
    
    def with_networking(self, vpc_config): 
        self.config['networking'] = vpc_config
        return self
    
    def with_storage(self, storage_config):
        self.config['storage'] = storage_config
        return self
    
    def build(self):
        return JSON.stringify(self.config)

# Usage
config = (InfrastructureConfigBuilder()
          .with_networking(vpc_config)
          .with_storage(storage_config)
          .build())
```

### 4. Template Method Pattern
For ETL procedures:

```python
# BEFORE: 233-line create_transformation_procedures
def create_transformation_procedures(self) -> None:
    # 233 lines of mixed procedure creation

# AFTER: Template method approach
def create_transformation_procedures(self) -> None:
    """Create all transformation procedures"""
    self._create_data_validation_procedures()
    self._create_enrichment_procedures()
    self._create_aggregation_procedures()
    self._create_quality_check_procedures()

def _create_data_validation_procedures(self) -> None:
    """Create data validation procedures"""
    # Focused validation logic

def _create_enrichment_procedures(self) -> None:
    """Create data enrichment procedures"""
    # Focused enrichment logic
```

## Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1)
**Target**: Reduce 20 highest-impact functions

1. **Router Configuration**
   - Refactor `create_application_router` (129 lines → 4 functions of ~30 lines)
   - Extract route grouping logic
   - Create middleware setup helpers

2. **Infrastructure Config**
   - Break down large `JSON.stringify` configurations
   - Create configuration builders
   - Separate networking, storage, compute configs

3. **Service Initialization**
   - Refactor large `__init__` methods
   - Create setup helper methods
   - Use configuration objects

### Phase 2: Data Processing (Week 2)
**Target**: ETL and data transformation functions

1. **ETL Procedures**
   - Refactor `create_transformation_procedures` (233 lines)
   - Break into procedure categories
   - Create reusable procedure templates

2. **Data Ingestion**
   - Refactor large ingestion methods
   - Extract validation logic
   - Separate transformation steps

3. **Analytics Functions**
   - Break down complex analysis methods
   - Extract calculation helpers
   - Separate reporting logic

### Phase 3: AI/ML Components (Week 3)
**Target**: Agent and intelligence functions

1. **Marketing Agent**
   - Refactor `generate_marketing_content` (109 lines)
   - Extract content generation steps
   - Separate validation and formatting

2. **Chat Endpoints**
   - Refactor `unified_chat_endpoint` (60 lines)
   - Extract request validation
   - Separate response formatting

3. **Intelligence Services**
   - Break down orchestration methods
   - Extract routing logic
   - Separate processing steps

### Phase 4: Integration & Deployment (Week 4)
**Target**: External integrations and deployment scripts

1. **Linear Integration**
   - Refactor `get_issue_details` (64 lines)
   - Extract API call logic
   - Separate data transformation

2. **Deployment Scripts**
   - Break down large `main` functions
   - Extract deployment steps
   - Create validation helpers

3. **MCP Orchestration**
   - Refactor `enhance_sophia_intelligence_mcp` (313 lines)
   - Extract feature enhancement logic
   - Create modular enhancement functions

## Automated Tools & Techniques

### 1. Static Analysis
```bash
# Install tools
uv add lizard radon

# Analyze current state
lizard . --CCN 15 --length 50 --output_file complexity_report.txt

# Track progress
radon cc . --min B --show-complexity
```

### 2. IDE Refactoring
- **PyCharm**: Select code → Refactor → Extract Method
- **VSCode**: Select code → Command Palette → "Extract Method"
- **Cursor**: Use AI-assisted refactoring suggestions

### 3. Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: function-length-check
        name: Check function length
        entry: python scripts/check_function_length.py
        language: python
        files: \.py$
```

### 4. Custom Refactoring Script
```python
# check_function_length.py
import ast
import sys

class FunctionAnalyzer(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        line_count = node.end_lineno - node.lineno + 1
        if line_count > 50:
            print(f"Function {node.name} has {line_count} lines (exceeds 50)")
            sys.exit(1)
```

## Success Metrics

### Quantitative Goals
- **Reduce functions >50 lines by 80%** (200 → 40)
- **Maximum function length: 75 lines** (down from 313)
- **Average function length: <30 lines**
- **Cyclomatic complexity: <10 per function**

### Quality Improvements
- **Maintainability Index**: Increase from current baseline
- **Test Coverage**: Easier to test smaller functions
- **Code Review Time**: Faster reviews of focused functions
- **Bug Density**: Reduction in defects per KLOC

### Developer Experience
- **Onboarding Time**: Faster for new team members
- **Feature Development**: Quicker implementation cycles
- **Debugging**: Easier to isolate and fix issues
- **Code Reuse**: Better modularity and reusability

## Best Practices

### Function Design Principles
1. **Single Responsibility**: One function, one clear purpose
2. **Descriptive Names**: Function name explains intent
3. **Parameter Limits**: Maximum 5 parameters
4. **Return Clarity**: Clear return types and documentation
5. **Error Handling**: Focused error handling per function

### Code Organization
1. **Logical Grouping**: Keep related helpers near main function
2. **Consistent Patterns**: Use similar refactoring approaches
3. **Progressive Enhancement**: Refactor incrementally
4. **Documentation**: Update docstrings and comments
5. **Testing**: Add tests for new helper functions

### Maintenance Strategy
1. **Regular Monitoring**: Weekly complexity reports
2. **Code Review Focus**: Check function length in PRs
3. **Refactoring Sprints**: Dedicated improvement cycles
4. **Team Training**: Share refactoring patterns
5. **Tool Integration**: Automated checks in CI/CD

## Expected Outcomes

### Short-term (1 month)
- ✅ 80% reduction in functions >50 lines
- ✅ Improved code review velocity
- ✅ Better test coverage for refactored areas
- ✅ Enhanced developer confidence

### Medium-term (3 months)
- ✅ Reduced bug reports in refactored modules
- ✅ Faster feature development cycles
- ✅ Improved onboarding experience
- ✅ Better code maintainability scores

### Long-term (6 months)
- ✅ Sustainable development practices
- ✅ Scalable codebase architecture
- ✅ Reduced technical debt
- ✅ Enhanced team productivity

## Conclusion

Systematic refactoring of long functions is essential for:
- **Code Quality**: More maintainable and readable code
- **Team Velocity**: Faster development and debugging
- **System Reliability**: Easier testing and validation
- **Developer Experience**: Better tooling and workflows

The phased approach outlined here will transform Sophia AI into a more maintainable, scalable, and developer-friendly platform while maintaining all existing functionality.

---

**Next Steps**: 
1. Begin Phase 1 with `create_application_router` refactoring
2. Set up automated complexity monitoring
3. Train team on refactoring patterns
4. Track progress weekly with metrics dashboard 