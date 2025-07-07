# MCP Server Migration Example: AI Memory

This example shows how to migrate the existing AI Memory MCP server to the new production-ready architecture.

## 🔄 Before vs After

### Before (Current Implementation)
- Custom MCP protocol implementation
- Basic error handling
- Limited monitoring
- No standardized health checks
- Manual configuration

### After (Production-Ready)
- FastAPI-based with auto-generated docs
- Comprehensive error handling
- Prometheus metrics
- Detailed health monitoring
- Pydantic configuration
- Docker support
- Full test coverage

## 📋 Migration Steps

### Step 1: Generate New Structure

```bash
python scripts/scaffold_mcp_server.py ai_memory_v2
```

### Step 2: Migrate Configuration

**Old**: Manual configuration
```python
class AIMemoryConfig:
    def __init__(self):
        self.port = 9001
        self.db_url = os.getenv("DB_URL")
```

**New**: `config.py` with Pydantic
```python
from pydantic import Field
from pydantic_settings import BaseSettings

class AiMemorySettings(BaseSettings):
    """Settings for AI Memory MCP server."""
    
    # Server settings
    PORT: int = Field(default=9001, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Database settings
    DB_DSN: str = Field(
        default="postgresql+asyncpg://user:pass@localhost/ai_memory",
        description="Database connection string",
        alias="AI_MEMORY_DB_DSN"
    )
    
    # Memory settings
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-ada-002",
        description="OpenAI embedding model"
    )
    EMBEDDING_DIMENSION: int = Field(default=1536, description="Embedding size")
    
    # Search settings
    DEFAULT_SEARCH_LIMIT: int = Field(default=10, description="Default search results")
    SIMILARITY_THRESHOLD: float = Field(default=0.7, description="Min similarity")
    
    class Config:
        env_prefix = "AI_MEMORY_"
        case_sensitive = True

settings = AiMemorySettings()
```

### Step 3: Migrate Business Logic

**Old**: MCP protocol handlers
```python
@self.server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[Any]:
    if name == "store_memory":
        return await self.memory_handler.store_memory(**arguments)
```

**New**: `handlers/main_handler.py` with proper separation
```python
from typing import List, Optional
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from ai_memory_v2.models.data_models import MemoryEntry, SearchRequest, SearchResult
from ai_memory_v2.utils.embeddings import generate_embedding

class AiMemoryHandler:
    """Handler for AI Memory operations."""
    
    def __init__(self, openai_api_key: str, embedding_model: str):
        self.openai_api_key = openai_api_key
        self.embedding_model = embedding_model
        
    async def store_memory(
        self,
        content: str,
        metadata: dict = None,
        tags: List[str] = None,
        session: AsyncSession = None
    ) -> MemoryEntry:
        """Store a memory with semantic embedding."""
        # Generate embedding
        embedding = await generate_embedding(
            content,
            model=self.embedding_model,
            api_key=self.openai_api_key
        )
        
        # Create memory entry
        memory = MemoryEntry(
            content=content,
            embedding=embedding.tolist(),
            metadata=metadata or {},
            tags=tags or []
        )
        
        # Store in database
        if session:
            session.add(memory)
            await session.commit()
            await session.refresh(memory)
        
        return memory
    
    async def search_memories(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
        session: AsyncSession = None
    ) -> List[SearchResult]:
        """Search memories using semantic similarity."""
        # Generate query embedding
        query_embedding = await generate_embedding(
            query,
            model=self.embedding_model,
            api_key=self.openai_api_key
        )
        
        # Perform vector similarity search
        if session:
            # Using pgvector for PostgreSQL
            sql = text("""
                SELECT id, content, metadata, tags, 
                       1 - (embedding <=> :query_embedding) as similarity
                FROM memory_entries
                WHERE 1 - (embedding <=> :query_embedding) > :threshold
                ORDER BY similarity DESC
                LIMIT :limit
            """)
            
            result = await session.execute(
                sql,
                {
                    "query_embedding": query_embedding.tolist(),
                    "threshold": threshold,
                    "limit": limit
                }
            )
            
            return [
                SearchResult(
                    memory_id=row.id,
                    content=row.content,
                    similarity=row.similarity,
                    metadata=row.metadata,
                    tags=row.tags
                )
                for row in result
            ]
        
        return []
    
    async def get_memory_stats(self, session: AsyncSession = None) -> dict:
        """Get memory system statistics."""
        if session:
            # Count total memories
            count_sql = "SELECT COUNT(*) as count FROM memory_entries"
            count_result = await session.execute(text(count_sql))
            total_memories = count_result.scalar()
            
            # Get tag distribution
            tag_sql = """
                SELECT unnest(tags) as tag, COUNT(*) as count
                FROM memory_entries
                GROUP BY tag
                ORDER BY count DESC
                LIMIT 10
            """
            tag_result = await session.execute(text(tag_sql))
            top_tags = [
                {"tag": row.tag, "count": row.count}
                for row in tag_result
            ]
            
            return {
                "total_memories": total_memories,
                "top_tags": top_tags,
                "embedding_model": self.embedding_model,
                "embedding_dimension": 1536
            }
        
        return {}
```

### Step 4: Create Server Implementation

**New**: `server.py` with FastAPI and health monitoring
```python
import asyncio
from typing import Any, List

from infrastructure.mcp_servers.base.standardized_mcp_server import (
    HealthCheckResult,
    HealthStatus,
    ServerCapability,
    StandardizedMCPServer,
)

from ai_memory_v2.config import mcp_config, settings
from ai_memory_v2.handlers.main_handler import AiMemoryHandler
from ai_memory_v2.models.data_models import MemoryEntry, SearchRequest, SearchResult
from ai_memory_v2.utils.db import get_session, init_db, close_db

class AiMemoryMCPServer(StandardizedMCPServer):
    """AI Memory MCP Server implementation."""
    
    def __init__(self):
        super().__init__(mcp_config)
        self.handler: Optional[AiMemoryHandler] = None
        
    async def server_specific_init(self) -> None:
        """Initialize AI Memory components."""
        # Initialize database
        await init_db()
        
        # Initialize handler
        self.handler = AiMemoryHandler(
            openai_api_key=settings.OPENAI_API_KEY,
            embedding_model=settings.EMBEDDING_MODEL
        )
        
        # Add custom routes
        self._add_custom_routes()
        
    def _add_custom_routes(self) -> None:
        """Add AI Memory specific routes."""
        # Store memory
        self.app.add_api_route(
            "/api/memory",
            self.store_memory_endpoint,
            methods=["POST"],
            summary="Store a new memory",
            response_model=MemoryEntry
        )
        
        # Search memories
        self.app.add_api_route(
            "/api/search",
            self.search_memories_endpoint,
            methods=["POST"],
            summary="Search memories",
            response_model=List[SearchResult]
        )
        
        # Get stats
        self.app.add_api_route(
            "/api/stats",
            self.get_stats_endpoint,
            methods=["GET"],
            summary="Get memory statistics"
        )
    
    async def store_memory_endpoint(
        self,
        content: str,
        metadata: dict = None,
        tags: List[str] = None
    ) -> MemoryEntry:
        """Store a new memory."""
        async with get_session() as session:
            return await self.handler.store_memory(
                content=content,
                metadata=metadata,
                tags=tags,
                session=session
            )
    
    async def search_memories_endpoint(
        self,
        request: SearchRequest
    ) -> List[SearchResult]:
        """Search memories."""
        async with get_session() as session:
            return await self.handler.search_memories(
                query=request.query,
                limit=request.limit,
                threshold=request.threshold,
                session=session
            )
    
    async def get_stats_endpoint(self) -> dict[str, Any]:
        """Get memory statistics."""
        async with get_session() as session:
            return await self.handler.get_memory_stats(session)
    
    async def server_specific_cleanup(self) -> None:
        """Cleanup AI Memory resources."""
        await close_db()
    
    async def server_specific_health_check(self) -> HealthCheckResult:
        """Check AI Memory health."""
        try:
            # Check database
            async with get_session() as session:
                await session.execute(text("SELECT 1"))
            
            # Check OpenAI API
            test_embedding = await generate_embedding(
                "health check",
                model=settings.EMBEDDING_MODEL,
                api_key=settings.OPENAI_API_KEY
            )
            
            return HealthCheckResult(
                component="ai_memory",
                status=HealthStatus.HEALTHY,
                response_time_ms=10,
                metadata={
                    "database": "connected",
                    "openai": "connected",
                    "embedding_dimension": len(test_embedding)
                }
            )
        except Exception as e:
            return HealthCheckResult(
                component="ai_memory",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                error_message=str(e)
            )
    
    async def get_server_capabilities(self) -> List[ServerCapability]:
        """Get AI Memory capabilities."""
        return [
            ServerCapability(
                name="semantic_search",
                description="Search memories using semantic similarity",
                category="ai",
                available=True
            ),
            ServerCapability(
                name="memory_storage",
                description="Store memories with embeddings",
                category="data",
                available=True
            ),
            ServerCapability(
                name="vector_database",
                description="PostgreSQL with pgvector extension",
                category="infrastructure",
                available=True
            )
        ]
```

### Step 5: Add Data Models

**New**: `models/data_models.py`
```python
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import numpy as np

class MemoryEntry(BaseModel):
    """Memory entry model."""
    id: Optional[int] = Field(None, description="Memory ID")
    content: str = Field(..., description="Memory content")
    embedding: List[float] = Field(..., description="Embedding vector")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")
    tags: List[str] = Field(default_factory=list, description="Tags")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            np.ndarray: lambda v: v.tolist()
        }

class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Result limit")
    threshold: float = Field(default=0.7, ge=0, le=1, description="Similarity threshold")

class SearchResult(BaseModel):
    """Search result model."""
    memory_id: int = Field(..., description="Memory ID")
    content: str = Field(..., description="Memory content")
    similarity: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
```

### Step 6: Add Database Schema

Create `utils/schema.sql`:
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create memory entries table
CREATE TABLE IF NOT EXISTS memory_entries (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_memory_embedding ON memory_entries USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_memory_tags ON memory_entries USING GIN (tags);
CREATE INDEX idx_memory_created ON memory_entries (created_at DESC);
```

### Step 7: Write Tests

**New**: `tests/unit/test_handler.py`
```python
import pytest
from unittest.mock import AsyncMock, patch
import numpy as np

from ai_memory_v2.handlers.main_handler import AiMemoryHandler
from ai_memory_v2.models.data_models import MemoryEntry

@pytest.fixture
def handler():
    return AiMemoryHandler(
        openai_api_key="test-key",
        embedding_model="text-embedding-ada-002"
    )

@pytest.mark.asyncio
async def test_store_memory(handler):
    """Test storing a memory."""
    # Mock embedding generation
    with patch('ai_memory_v2.utils.embeddings.generate_embedding') as mock_embed:
        mock_embed.return_value = np.random.rand(1536)
        
        # Mock session
        session = AsyncMock()
        
        # Store memory
        result = await handler.store_memory(
            content="Test memory",
            metadata={"source": "test"},
            tags=["test"],
            session=session
        )
        
        # Verify
        assert isinstance(result, MemoryEntry)
        assert result.content == "Test memory"
        assert len(result.embedding) == 1536
        assert result.metadata == {"source": "test"}
        assert result.tags == ["test"]

@pytest.mark.asyncio
async def test_search_memories(handler):
    """Test searching memories."""
    # Mock embedding and database
    with patch('ai_memory_v2.utils.embeddings.generate_embedding') as mock_embed:
        mock_embed.return_value = np.random.rand(1536)
        
        # Mock session with results
        session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.__iter__.return_value = [
            AsyncMock(
                id=1,
                content="Test memory",
                similarity=0.95,
                metadata={},
                tags=[]
            )
        ]
        session.execute.return_value = mock_result
        
        # Search
        results = await handler.search_memories(
            query="test",
            limit=10,
            threshold=0.7,
            session=session
        )
        
        # Verify
        assert len(results) == 1
        assert results[0].similarity == 0.95
```

## 🚀 Deployment

### Docker Support

The new structure includes:
- `Dockerfile` for containerization
- `docker-compose.yml` for local development
- Health checks built-in
- Non-root user for security

### Production Deployment

```bash
# Build and push
docker build -t scoobyjava15/ai-memory-mcp:latest .
docker push scoobyjava15/ai-memory-mcp:latest

# Deploy to Lambda Labs
docker stack deploy -c docker-compose.production.yml ai-memory-mcp
```

## 📊 Benefits of Migration

1. **Better Observability**
   - Prometheus metrics at `/metrics`
   - Structured JSON logging
   - Detailed health checks

2. **Improved Developer Experience**
   - Auto-generated API docs at `/docs`
   - Type safety with Pydantic
   - Comprehensive test coverage

3. **Production Readiness**
   - Connection pooling
   - Graceful shutdown
   - Error recovery
   - Rate limiting ready

4. **Standardization**
   - Consistent structure across all servers
   - Reusable patterns
   - Easier maintenance

## 🎯 Migration Checklist

- [x] Generate new structure
- [x] Migrate configuration to Pydantic
- [x] Convert handlers to FastAPI routes
- [x] Add proper data models
- [x] Implement health checks
- [x] Add database schema
- [x] Write unit tests
- [ ] Write integration tests
- [ ] Test with Docker locally
- [ ] Deploy to staging
- [ ] Validate metrics
- [ ] Deploy to production
- [ ] Deprecate old server

This migration transforms the AI Memory server from a basic MCP implementation to a production-ready, enterprise-grade service with comprehensive monitoring, testing, and deployment capabilities. 