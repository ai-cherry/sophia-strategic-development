# ADR-001: Circular Dependencies Resolution

## Status
Proposed

## Context
During Week 1 of our quality-first development phase, we conducted a comprehensive dependency analysis of the Sophia AI codebase. The analysis revealed significant architectural issues:

### Key Findings:
1. **120 circular dependencies** detected, primarily in the `backend.core` module
2. **Most problematic module**: `backend.core.auto_esc_config` (imported 62 times)
3. **Deep circular chains**: Some circular dependency chains are 25+ modules deep
4. **Service coupling**: Multiple services importing from 7-8 other services

### Most Critical Circular Dependencies:
- `auto_esc_config` ↔ `security_config` ↔ `config` (configuration triangle)
- `optimized_connection_manager` ↔ `data_flow_manager` ↔ `snowflake_config_override`
- `snowflake_cortex_service` ↔ `snowflake_cortex_service_handlers`

## Decision
We will implement a phased approach to eliminate circular dependencies:

### Phase 1: Configuration Layer Refactoring
1. **Extract interfaces**: Create abstract base classes for configuration
2. **Dependency injection**: Use dependency injection instead of direct imports
3. **Configuration hierarchy**: Establish clear configuration layers:
   - Base configuration (no dependencies)
   - Security configuration (depends only on base)
   - Service configuration (depends on base and security)

### Phase 2: Service Layer Decoupling
1. **Service registry pattern**: Implement a central service registry
2. **Event-driven communication**: Use events instead of direct service calls
3. **Clear service boundaries**: Each service should have a single responsibility

### Phase 3: Connection Management
1. **Singleton pattern**: Use a proper singleton for connection management
2. **Lazy initialization**: Initialize connections only when needed
3. **Clear ownership**: Each connection type managed by one module

## Consequences

### Positive:
- Eliminates circular import errors
- Improves code maintainability
- Makes testing easier
- Reduces startup time
- Clearer architecture

### Negative:
- Requires significant refactoring
- May temporarily break some functionality
- Learning curve for dependency injection

## Implementation Plan

### Week 1 Actions:
1. Create `backend/core/base/` directory for base classes
2. Extract configuration interfaces
3. Implement dependency injection framework
4. Refactor `auto_esc_config` to break circular dependencies

### Success Metrics:
- Zero circular dependencies
- All imports resolve correctly
- No runtime import errors
- Faster application startup

## References
- Dependency analysis report: `dependency_analysis_report.json`
- Python circular import best practices
- Dependency injection patterns 