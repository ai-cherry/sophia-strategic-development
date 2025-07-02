# Sophia AI Clean Architecture Guide

> **User Base Assumption:**
> - **Initial deployment:** 5–10 users
> - **Maximum supported:** 100 users
>
> **Design Impact:**
> - All performance, scalability, and resource allocation decisions are optimized for this range.
> - Database, cache, and background worker pools are sized for up to 100 concurrent users.
> - Load testing, monitoring, and security controls are validated for this scale.
> - System is designed for easy scaling within this range, but not over-engineered for thousands of users.
> - Early user feedback (from first 5–10 users) will drive workflow and UX refinements.

## Overview

This guide establishes the architectural principles and patterns for the Sophia AI platform modernization. We are transitioning from a monolithic, fragile architecture to a robust, scalable system based on **Clean Architecture** principles combined with **Domain-Driven Design (DDD)**.

## Table of Contents

1. [Architectural Philosophy](#architectural-philosophy)
2. [Layer Structure](#layer-structure)
3. [Service Decomposition Strategy](#service-decomposition-strategy)
4. [Dependency Injection Standards](#dependency-injection-standards)
5. [Configuration Management](#configuration-management)
6. [Testing Strategy](#testing-strategy)
7. [Implementation Phases](#implementation-phases)
8. [Code Examples](#code-examples)
9. [Compliance Rules](#compliance-rules)

## Architectural Philosophy

### Core Principles

1. **Dependency Rule**: Source code dependencies can only point inwards. Nothing in an inner circle can know anything about an outer circle.
2. **Single Responsibility**: Each service should have one reason to change.
3. **Interface Segregation**: No client should be forced to depend on methods it doesn't use.
4. **Dependency Inversion**: Depend on abstractions, not concretions.

### Why Clean Architecture?

- **Solves Circular Dependencies**: Clear dependency direction eliminates import cycles
- **Enables Testing**: Business logic is isolated from frameworks and external services
- **Supports Growth**: New features can be added without affecting existing code
- **Framework Independence**: Business logic doesn't depend on FastAPI, databases, or external APIs

## Layer Structure

### 1. Domain Layer (Entities)
**Location**: `backend/domain/`
**Purpose**: Core business objects and rules
**Dependencies**: None (innermost layer)

```python
# backend/domain/entities.py
@dataclass
class ChatSession:
    session_id: str
    user_id: str
    created_at: datetime
    context: Dict[str, Any]

@dataclass
class SearchRequest:
    query: str
    search_type: SearchType
    user_preferences: UserPreferences
```

### 2. Use Cases Layer (Interactors)
**Location**: `backend/use_cases/`
**Purpose**: Business logic and orchestration
**Dependencies**: Domain layer only

```python
# backend/use_cases/chat_orchestration.py
class ChatOrchestrationUseCase:
    def __init__(
        self,
        user_service: UserProfileService,
        search_service: SearchCoordinatorService,
        response_service: ResponseSynthesizerService
    ):
        self._user_service = user_service
        self._search_service = search_service
        self._response_service = response_service
```

### 3. Interface Adapters Layer
**Location**: `backend/interfaces/`
**Purpose**: Abstract definitions (ports)
**Dependencies**: Domain and Use Cases layers

```python
# backend/interfaces/repositories.py
class UserProfileRepository(ABC):
    @abstractmethod
    async def get_profile(self, user_id: str) -> UserProfile: ...
    
    @abstractmethod
    async def update_profile(self, profile: UserProfile) -> None: ...
```

### 4. Infrastructure Layer
**Location**: `backend/infrastructure/`
**Purpose**: Concrete implementations (adapters)
**Dependencies**: All inner layers

```python
# backend/infrastructure/repositories/user_profile_repository.py
class SnowflakeUserProfileRepository(UserProfileRepository):
    async def get_profile(self, user_id: str) -> UserProfile:
        # Snowflake-specific implementation
        pass
```

## Service Decomposition Strategy

### Before: Monolithic Services

**Problems Identified:**
- `SophiaUniversalChatService` (968 lines) - Does everything
- `sophia_ai_orchestrator.py` (1022 lines) - God object
- `memory_preservation_service.py` (1006 lines) - Multiple concerns

### After: Focused Services

**Chat Service Decomposition:**
```
SophiaUniversalChatService (968 lines)
├── ChatOrchestrationUseCase (50 lines)
├── UserProfileService (80 lines)
├── SearchCoordinatorService (100 lines)
├── WebSearchService (150 lines)
├── InternalSearchService (120 lines)
├── CompetitiveIntelligenceService (90 lines)
└── ResponseSynthesizerService (80 lines)
```

**Benefits:**
- Each service has a single responsibility
- Services are independently testable
- Clear interfaces between components
- Easy to extend or replace individual components

## Dependency Injection Standards

### Centralized Dependencies Module

**Location**: `backend/core/dependencies.py`

```python
from functools import lru_cache
from typing import Protocol

# Abstract Interfaces
class ChatOrchestrationUseCase(Protocol):
    async def process_chat_message(self, message: str, user_id: str) -> ChatResponse: ...

# Singleton Dependencies (Stateless Services)
@lru_cache()
def get_config_service() -> ConfigurationService:
    return ConfigurationService()

@lru_cache()
def get_database_session() -> DatabaseSession:
    config = get_config_service()
    return DatabaseSession(config.database_url)

# Request-Scoped Dependencies
def get_user_profile_service(
    db: DatabaseSession = Depends(get_database_session),
    config: ConfigurationService = Depends(get_config_service)
) -> UserProfileService:
    return UserProfileService(db, config)

def get_chat_orchestration_service(
    user_service: UserProfileService = Depends(get_user_profile_service),
    search_service: SearchCoordinatorService = Depends(get_search_coordinator_service)
) -> ChatOrchestrationService:
    return ChatOrchestrationService(user_service, search_service)
```

### Usage in API Routes

```python
# backend/api/chat_routes.py
@router.post("/message")
async def process_chat_message(
    request: ChatRequest,
    chat_service: ChatOrchestrationService = Depends(get_chat_orchestration_service)
):
    return await chat_service.process_chat_message(
        request.message, 
        request.user_id, 
        request.context
    )
```

## Configuration Management

### Unified Configuration Service

**Location**: `backend/core/config.py`

```python
from pydantic import BaseSettings, Field

class DatabaseConfig(BaseSettings):
    url: str = Field(..., env="DATABASE_URL")
    pool_size: int = Field(5, env="DB_POOL_SIZE")
    
    class Config:
        env_prefix = "DB_"

class ExternalAPIConfig(BaseSettings):
    exa_api_key: str = Field(..., env="EXA_API_KEY")
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY")

class AppConfig(BaseSettings):
    app_name: str = Field("Sophia AI", env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")
    
    database: DatabaseConfig = DatabaseConfig()
    external_apis: ExternalAPIConfig = ExternalAPIConfig()
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_config() -> AppConfig:
    return AppConfig()
```

### Migration from Legacy Config

**Replace This:**
```python
# OLD - Direct os.getenv calls
api_key = os.getenv("EXA_API_KEY")
```

**With This:**
```python
# NEW - Injected configuration
def some_service(config: AppConfig = Depends(get_config)):
    api_key = config.external_apis.exa_api_key
```

## Testing Strategy

### Unit Testing for Use Cases

```python
# tests/unit/use_cases/test_chat_orchestration.py
@pytest.mark.asyncio
async def test_chat_orchestration_success():
    # Arrange
    mock_user_service = AsyncMock()
    mock_search_service = AsyncMock()
    mock_response_service = AsyncMock()
    
    service = ChatOrchestrationUseCase(
        mock_user_service, 
        mock_search_service, 
        mock_response_service
    )
    
    # Act
    result = await service.process_chat_message("test", "user123", {})
    
    # Assert
    assert isinstance(result, ChatResponse)
    mock_user_service.get_profile.assert_called_once_with("user123")
```

### Integration Testing

```python
# tests/integration/test_chat_endpoint.py
def test_chat_endpoint_integration(test_client):
    response = test_client.post(
        "/api/v1/chat/message",
        json={"message": "test", "user_id": "user123"}
    )
    assert response.status_code == 200
```

### Architectural Compliance Testing

```python
# tests/architecture/test_dependency_compliance.py
def test_domain_layer_has_no_external_dependencies():
    domain_modules = get_modules_in_package('backend.domain')
    for module in domain_modules:
        imports = get_module_imports(module)
        forbidden = [imp for imp in imports if 'infrastructure' in imp]
        assert not forbidden, f"Domain module {module} has forbidden imports"
```

## Implementation Phases

### Phase 1: Foundation and Chat Service (Weeks 1-3)

**Goals:**
- Establish Clean Architecture foundation
- Decompose `SophiaUniversalChatService`
- Create centralized dependencies

**Key Files:**
- `backend/core/dependencies.py`
- `backend/domain/entities.py`
- `backend/use_cases/chat_orchestration.py`
- `backend/infrastructure/web_search_service.py`

**Success Criteria:**
- Chat functionality works with new architecture
- 80% reduction in service complexity
- All tests pass

### Phase 2: Configuration and Testing (Weeks 4-5)

**Goals:**
- Implement unified configuration
- Establish testing framework
- Create architectural compliance tests

**Key Files:**
- `backend/core/config.py`
- `tests/architecture/test_compliance.py`
- `tests/unit/use_cases/`

**Success Criteria:**
- All `os.getenv` calls replaced
- 100% test coverage for use cases
- Architectural rules enforced

### Phase 3: Service Decomposition (Weeks 6-8)

**Goals:**
- Decompose remaining monolithic services
- Apply patterns to all services

**Target Services:**
- `sophia_ai_orchestrator.py` (1022 lines)
- `memory_preservation_service.py` (1006 lines)
- `hierarchical_caching_service.py` (850 lines)

**Success Criteria:**
- All services follow single-responsibility principle
- No service exceeds 200 lines
- Clear separation of concerns

### Phase 4: Advanced Patterns (Weeks 9-10)

**Goals:**
- Implement advanced patterns (CQRS, Event Sourcing)
- Optimize for production
- Complete documentation

**Success Criteria:**
- Production-ready architecture
- Comprehensive documentation
- Team training completed

## Code Examples

### Converting a Monolithic Service

**Before (Monolithic):**
```python
class SophiaUniversalChatService:
    def __init__(self):
        self.user_profiles = {}
        self.exa_client = None
        self.tavily_client = None
        # ... 50 more attributes
    
    async def process_chat_message(self, message, user_id):
        # 200 lines of mixed concerns
        pass
    
    async def _execute_web_search(self, query):
        # Web search logic mixed with business logic
        pass
    
    def _format_response(self, data):
        # Response formatting mixed with everything else
        pass
```

**After (Clean Architecture):**
```python
# Use Case (Business Logic)
class ChatOrchestrationUseCase:
    def __init__(
        self,
        user_service: UserProfileService,
        search_service: SearchCoordinatorService,
        response_service: ResponseSynthesizerService
    ):
        self._user_service = user_service
        self._search_service = search_service
        self._response_service = response_service
    
    async def process_chat_message(
        self, 
        message: str, 
        user_id: str, 
        context: Dict
    ) -> ChatResponse:
        user_profile = await self._user_service.get_profile(user_id)
        search_request = SearchRequest.from_message(message, user_profile)
        search_results = await self._search_service.execute_search(search_request)
        return await self._response_service.synthesize_response(
            search_results, user_profile, context
        )

# Infrastructure (External Services)
class WebSearchService:
    def __init__(self, exa_client: ExaClient, tavily_client: TavilyClient):
        self._exa_client = exa_client
        self._tavily_client = tavily_client
    
    async def search(self, query: str) -> List[SearchResult]:
        # Pure web search logic, no business rules
        pass
```

## Compliance Rules

### Mandatory Rules

1. **No Direct Database Calls in Use Cases**: Use repository interfaces
2. **No Framework Dependencies in Domain**: Domain entities must be pure Python
3. **No Business Logic in Infrastructure**: Keep adapters simple
4. **All Services Must Have Interfaces**: Use Protocol or ABC
5. **No Circular Imports**: Follow the dependency rule strictly

### Architectural Violations

**Forbidden Patterns:**
```python
# FORBIDDEN: Use case depending on infrastructure
from backend.infrastructure.databases import SnowflakeConnection

class ChatUseCase:
    def __init__(self):
        self.db = SnowflakeConnection()  # VIOLATION

# FORBIDDEN: Domain entity importing frameworks
from fastapi import HTTPException  # VIOLATION

@dataclass
class User:
    name: str
```

**Correct Patterns:**
```python
# CORRECT: Use case depending on abstraction
from backend.interfaces.repositories import UserRepository

class ChatUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo  # Dependency injection

# CORRECT: Pure domain entity
@dataclass
class User:
    name: str
    email: str
    # No framework dependencies
```

### Enforcement

Architectural compliance is enforced through:

1. **Automated Tests**: `tests/architecture/test_compliance.py`
2. **Pre-commit Hooks**: Validate imports before commits
3. **Code Reviews**: Architecture checklist required
4. **CI/CD Pipeline**: Compliance tests must pass

## Migration Guidelines

### Step-by-Step Service Migration

1. **Identify Responsibilities**: List all functions in the monolithic service
2. **Group by Concern**: Cluster related functionality
3. **Extract Interfaces**: Define protocols for each concern
4. **Create Use Cases**: Implement business logic without dependencies
5. **Build Infrastructure**: Create concrete implementations
6. **Wire Dependencies**: Connect everything in `dependencies.py`
7. **Test Thoroughly**: Unit, integration, and compliance tests
8. **Update Routes**: Modify API layer to use new services

### Common Pitfalls

1. **Creating "Helper" Services**: Avoid generic utility services
2. **Over-Engineering**: Start simple, add complexity only when needed
3. **Tight Coupling**: Always depend on interfaces, not implementations
4. **Skipping Tests**: Write tests as you decompose, not after

## Conclusion

This Clean Architecture approach will transform Sophia AI from a fragile, monolithic system into a robust, scalable platform. The clear separation of concerns, dependency injection patterns, and comprehensive testing strategy will enable rapid development while maintaining high code quality.

For questions or clarifications, refer to the team lead or create an issue in the project repository.

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Next Review**: Phase 2 Completion 