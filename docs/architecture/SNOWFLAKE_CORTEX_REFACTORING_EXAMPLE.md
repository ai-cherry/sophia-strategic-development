# Modern StackCortexService Refactoring Example

This document demonstrates the step-by-step refactoring of the monolithic `Modern StackCortexService` (2,134 lines) into a clean, modular architecture.

## Current Monolithic Structure

```python
# backend/utils/snowflake_cortex_service.py (2,134 lines)
class Modern StackCortexService:
    def __init__(self):
        # Connection management
        self.connection = snowflake.connector.connect(...)

    async def summarize_text_in_snowflake(self, ...):
        # Text summarization logic

    async def analyze_sentiment_in_snowflake(self, ...):
        # Sentiment analysis logic

    async def generate_embedding_in_snowflake(self, ...):
        # Embedding generation logic

    async def vector_search_in_snowflake(self, ...):
        # Vector search logic

    async def search_hubspot_deals_with_ai_memory(self, ...):
        # HubSpot-specific business logic

    async def search_gong_calls_with_ai_memory(self, ...):
        # Gong-specific business logic

    async def log_etl_job_status(self, ...):
        # ETL logging logic
```

## Refactored Clean Architecture

### 1. Domain Layer

```python
# backend/domain/entities/text_analysis.py
from dataclasses import dataclass
from typing import Optional
from backend.domain.value_objects import Sentiment, TextSummary

@dataclass
class TextAnalysis:
    """Domain entity for text analysis results."""
    id: str
    original_text: str
    summary: Optional[TextSummary] = None
    sentiment: Optional[Sentiment] = None

    def needs_review(self) -> bool:
        """Business rule: Negative sentiment texts need human review."""
        return self.sentiment and self.sentiment.is_negative()
```

```python
# backend/domain/value_objects/sentiment.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Sentiment:
    """Value object representing sentiment analysis."""
    score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0

    def is_positive(self) -> bool:
        return self.score > 0.1

    def is_negative(self) -> bool:
        return self.score < -0.1

    def is_neutral(self) -> bool:
        return -0.1 <= self.score <= 0.1
```

### 2. Application Layer

```python
# backend/application/ports/ai_service.py
from abc import ABC, abstractmethod
from typing import List
from backend.domain.value_objects import Sentiment, TextSummary, Embedding

class AIService(ABC):
    """Port for AI operations."""

    @abstractmethod
    async def summarize_text(self, text: str, max_length: int = 200) -> TextSummary:
        """Generate a summary of the given text."""
        pass

    @abstractmethod
    async def analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment of the given text."""
        pass

    @abstractmethod
    async def generate_embedding(self, text: str) -> Embedding:
        """Generate vector embedding for the text."""
        pass
```

```python
# backend/application/ports/vector_search_service.py
from abc import ABC, abstractmethod
from typing import List
from backend.domain.entities import SearchResult

class VectorSearchService(ABC):
    """Port for vector similarity search."""

    @abstractmethod
    async def search_similar(
        self,
        query_embedding: Embedding,
        collection: str,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[SearchResult]:
        """Search for similar items using vector similarity."""
        pass
```

```python
# backend/application/use_cases/analyze_text_use_case.py
from backend.application.ports import AIService, TextRepository
from backend.domain.entities import TextAnalysis

class AnalyzeTextUseCase:
    """Use case for comprehensive text analysis."""

    def __init__(
        self,
        ai_service: AIService,
        text_repository: TextRepository
    ):
        self._ai_service = ai_service
        self._text_repository = text_repository

    async def execute(self, text_id: str, text_content: str) -> TextAnalysis:
        """Analyze text and store results."""
        # Create domain entity
        analysis = TextAnalysis(id=text_id, original_text=text_content)

        # Perform AI analysis
        analysis.summary = await self._ai_service.summarize_text(text_content)
        analysis.sentiment = await self._ai_service.analyze_sentiment(text_content)

        # Apply business rules
        if analysis.needs_review():
            await self._notify_review_team(analysis)

        # Persist results
        await self._text_repository.save(analysis)

        return analysis
```

### 3. Infrastructure Layer

```python
# backend/infrastructure/ai/snowflake_cortex_client.py
import snowflake.connector
from backend.application.ports import AIService
from backend.domain.value_objects import Sentiment, TextSummary, Embedding

class Modern StackCortexClient(AIService):
    """Lambda GPU implementation of AI operations."""

    def __init__(self, connection_pool):
        self._pool = connection_pool

    async def summarize_text(self, text: str, max_length: int = 200) -> TextSummary:
        """Use Lambda GPU SUMMARIZE function."""
        async with self._pool.get_connection() as conn:
            query = f"""
            SELECT SNOWFLAKE.CORTEX.SUMMARIZE(?, ?) as summary
            """
            result = await conn.execute(query, (text, max_length))
            return TextSummary(
                content=result[0]['summary'],
                original_length=len(text),
                summary_length=len(result[0]['summary'])
            )

    async def analyze_sentiment(self, text: str) -> Sentiment:
        """Use Lambda GPU SENTIMENT function."""
        async with self._pool.get_connection() as conn:
            query = """
            SELECT SNOWFLAKE.CORTEX.SENTIMENT(?) as sentiment_score
            """
            result = await conn.execute(query, (text,))
            return Sentiment(
                score=result[0]['sentiment_score'],
                confidence=0.85  # Cortex doesn't provide confidence
            )

    async def generate_embedding(self, text: str) -> Embedding:
        """Use Lambda GPU EMBED_TEXT function."""
        async with self._pool.get_connection() as conn:
            query = """
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', ?) as embedding
            """
            result = await conn.execute(query, (text,))
            return Embedding(
                vector=result[0]['embedding'],
                model='e5-base-v2',
                dimensions=768
            )
```

```python
# backend/infrastructure/persistence/snowflake_connection_pool.py
import asyncio
from contextlib import asynccontextmanager
import snowflake.connector
from snowflake.connector.pool import ConnectionPool

class Modern StackConnectionPool:
    """Manages PostgreSQL database connections."""

    def __init__(self, config):
        self._config = config
        self._pool = None

    async def initialize(self):
        """Initialize the connection pool."""
        self._pool = ConnectionPool(
            'snowflake_pool',
            max_connections=10,
            min_connections=2,
            **self._config
        )

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool."""
        conn = self._pool.get_connection()
        try:
            yield conn
        finally:
            self._pool.put_connection(conn)
```

```python
# backend/infrastructure/search/snowflake_vector_search.py
from typing import List
from backend.application.ports import VectorSearchService
from backend.domain.entities import SearchResult
from backend.domain.value_objects import Embedding

class Modern StackVectorSearch(VectorSearchService):
    """Modern Stack implementation of vector search."""

    def __init__(self, connection_pool):
        self._pool = connection_pool

    async def search_similar(
        self,
        query_embedding: Embedding,
        collection: str,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[SearchResult]:
        """Search using Modern Stack's VECTOR_COSINE_SIMILARITY."""
        async with self._pool.get_connection() as conn:
            query = f"""
            SELECT
                id,
                content,
                metadata,
                VECTOR_COSINE_SIMILARITY(embedding_vector, ?) as similarity
            FROM {collection}
            WHERE VECTOR_COSINE_SIMILARITY(embedding_vector, ?) >= ?
            ORDER BY similarity DESC
            LIMIT ?
            """

            results = await conn.execute(
                query,
                (query_embedding.vector, query_embedding.vector, threshold, limit)
            )

            return [
                SearchResult(
                    id=row['id'],
                    content=row['content'],
                    metadata=row['metadata'],
                    similarity_score=row['similarity']
                )
                for row in results
            ]
```

### 4. Presentation Layer

```python
# backend/presentation/api/text_analysis_controller.py
from fastapi import APIRouter, Depends, HTTPException
from backend.application.use_cases import AnalyzeTextUseCase
from backend.presentation.dto import TextAnalysisRequest, TextAnalysisResponse
from backend.infrastructure.container import Container

router = APIRouter()

@router.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(
    request: TextAnalysisRequest,
    use_case: AnalyzeTextUseCase = Depends(Container.analyze_text_use_case)
):
    """Analyze text endpoint."""
    try:
        result = await use_case.execute(
            text_id=request.id,
            text_content=request.text
        )

        return TextAnalysisResponse(
            id=result.id,
            summary=result.summary.content if result.summary else None,
            sentiment_score=result.sentiment.score if result.sentiment else None,
            sentiment_label=_get_sentiment_label(result.sentiment),
            needs_review=result.needs_review()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _get_sentiment_label(sentiment):
    if not sentiment:
        return "unknown"
    if sentiment.is_positive():
        return "positive"
    elif sentiment.is_negative():
        return "negative"
    else:
        return "neutral"
```

### 5. Dependency Injection Configuration

```python
# backend/infrastructure/container.py
from dependency_injector import containers, providers
from backend.infrastructure.ai import Modern StackCortexClient
from backend.infrastructure.persistence import Modern StackConnectionPool
from backend.infrastructure.search import Modern StackVectorSearch
from backend.application.use_cases import AnalyzeTextUseCase

class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    # Configuration
    config = providers.Configuration()

    # Infrastructure - Connection Pool
    connection_pool = providers.Singleton(
        Modern StackConnectionPool,
        config=config.snowflake
    )

    # Infrastructure - AI Service
    ai_service = providers.Singleton(
        Modern StackCortexClient,
        connection_pool=connection_pool
    )

    # Infrastructure - Vector Search
    vector_search = providers.Singleton(
        Modern StackVectorSearch,
        connection_pool=connection_pool
    )

    # Application - Use Cases
    analyze_text_use_case = providers.Factory(
        AnalyzeTextUseCase,
        ai_service=ai_service,
        text_repository=providers.Dependency()  # Inject when needed
    )
```

## Benefits of This Refactoring

### 1. **Separation of Concerns**
- Connection management isolated in `Modern StackConnectionPool`
- AI operations in `Modern StackCortexClient`
- Business logic in use cases
- Each class has a single, clear responsibility

### 2. **Testability**
```python
# Easy to test with mocks
async def test_analyze_text_use_case():
    mock_ai_service = Mock(AIService)
    mock_ai_service.analyze_sentiment.return_value = Sentiment(score=-0.8, confidence=0.9)

    use_case = AnalyzeTextUseCase(mock_ai_service, mock_repository)
    result = await use_case.execute("1", "This is terrible!")

    assert result.needs_review() is True
```

### 3. **Flexibility**
- Easy to swap Lambda GPU for OpenAI or another AI service
- Can add caching, logging, or monitoring without changing business logic
- Database can be changed without affecting domain logic

### 4. **Maintainability**
- Each file is focused and under 200 lines
- Clear dependencies and interfaces
- Easy to understand and modify

### 5. **Scalability**
- Connection pooling for better performance
- Async operations throughout
- Easy to add new AI operations or search methods

## Migration Strategy

1. **Phase 1**: Create new structure alongside existing code
2. **Phase 2**: Migrate one operation at a time (e.g., sentiment analysis)
3. **Phase 3**: Update API endpoints to use new use cases
4. **Phase 4**: Deprecate and remove old monolithic service
5. **Phase 5**: Delete old code after verification period

This refactoring transforms a 2,134-line monolith into ~15 focused files, each under 200 lines, with clear responsibilities and excellent testability.
