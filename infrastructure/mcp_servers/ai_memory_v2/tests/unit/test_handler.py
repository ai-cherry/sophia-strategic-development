"""Unit tests for ai_memory_v2 handler."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np
from datetime import datetime

from infrastructure.mcp_servers.ai_memory_v2.handlers.main_handler import AiMemoryV2Handler
from infrastructure.mcp_servers.ai_memory_v2.models.data_models import (
    MemoryEntry, SearchRequest, SearchResult, MemoryCategory,
    BulkMemoryRequest, MemoryUpdateRequest
)

@pytest.fixture
def handler():
    """Create handler instance for testing."""
    handler = AiMemoryV2Handler()
    handler.openai_client = AsyncMock()
    return handler

@pytest.mark.asyncio
async def test_handler_initialization():
    """Test handler initialization."""
    with patch('infrastructure.mcp_servers.ai_memory_v2.config.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = "test-key"
        
        handler = AiMemoryV2Handler()
        await handler.initialize()
        
        assert handler.openai_client is not None

@pytest.mark.asyncio
async def test_store_memory_success(handler):
    """Test successful memory storage."""
    # Mock embedding generation
    mock_embedding = np.random.rand(1536)
    handler._generate_embedding = AsyncMock(return_value=mock_embedding)
    handler._check_duplicate = AsyncMock(return_value=None)
    handler._store_in_db = AsyncMock(return_value=1)
    
    # Store memory
    memory = await handler.store_memory(
        content="Test memory content",
        category=MemoryCategory.TECHNICAL,
        tags=["test", "unit-test"],
        metadata={"source": "test"}
    )
    
    # Verify
    assert memory.content == "Test memory content"
    assert memory.category == MemoryCategory.TECHNICAL
    assert memory.tags == ["test", "unit-test"]
    assert memory.metadata == {"source": "test"}
    assert memory.id == 1
    handler._generate_embedding.assert_called_once_with("Test memory content")

@pytest.mark.asyncio
async def test_store_memory_duplicate_detection(handler):
    """Test duplicate memory detection."""
    # Mock duplicate detection
    handler._generate_embedding = AsyncMock(return_value=np.random.rand(1536))
    handler._check_duplicate = AsyncMock(return_value=123)
    
    existing_memory = MemoryEntry(
        id=123,
        content="Existing memory",
        category=MemoryCategory.GENERAL,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    handler._get_memory_by_id = AsyncMock(return_value=existing_memory)
    
    # Store memory
    memory = await handler.store_memory(content="Test memory")
    
    # Should return existing memory
    assert memory.id == 123
    assert memory.content == "Existing memory"

@pytest.mark.asyncio
async def test_search_memories(handler):
    """Test memory search functionality."""
    # Mock embedding and search
    handler._generate_embedding = AsyncMock(return_value=np.random.rand(1536))
    
    mock_memory = MemoryEntry(
        id=1,
        content="Test memory about Python programming",
        category=MemoryCategory.TECHNICAL,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    handler._search_in_db = AsyncMock(return_value=[(mock_memory, 0.95)])
    
    # Search
    request = SearchRequest(query="Python", limit=10)
    results = await handler.search_memories(request)
    
    # Verify
    assert len(results) == 1
    assert results[0].memory.id == 1
    assert results[0].similarity == 0.95
    assert len(results[0].highlights) > 0

@pytest.mark.asyncio
async def test_auto_categorization(handler):
    """Test automatic categorization."""
    # Test technical content
    category = await handler._auto_categorize("This is a bug in the API function")
    assert category == MemoryCategory.TECHNICAL
    
    # Test business content
    category = await handler._auto_categorize("Revenue increased by 20% this quarter")
    assert category == MemoryCategory.BUSINESS
    
    # Test project content
    category = await handler._auto_categorize("Project milestone completed on schedule")
    assert category == MemoryCategory.PROJECT
    
    # Test learning content
    category = await handler._auto_categorize("I learned about machine learning today")
    assert category == MemoryCategory.LEARNING
    
    # Test general content
    category = await handler._auto_categorize("This is a general note")
    assert category == MemoryCategory.GENERAL

@pytest.mark.asyncio
async def test_bulk_store_memories(handler):
    """Test bulk memory storage."""
    # Mock methods
    handler.store_memory = AsyncMock(side_effect=[
        MemoryEntry(id=1, content="Memory 1", category=MemoryCategory.GENERAL, 
                   created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        MemoryEntry(id=2, content="Memory 2", category=MemoryCategory.GENERAL,
                   created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    ])
    
    # Bulk store
    request = BulkMemoryRequest(
        memories=[
            MemoryEntry(content="Memory 1", category=MemoryCategory.GENERAL,
                       created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            MemoryEntry(content="Memory 2", category=MemoryCategory.GENERAL,
                       created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        ]
    )
    
    results = await handler.bulk_store_memories(request)
    
    # Verify
    assert len(results) == 2
    assert results[0].id == 1
    assert results[1].id == 2

@pytest.mark.asyncio
async def test_update_memory(handler):
    """Test memory update."""
    # Mock existing memory
    existing = MemoryEntry(
        id=1,
        content="Old content",
        category=MemoryCategory.GENERAL,
        tags=["old"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    handler._get_memory_by_id = AsyncMock(return_value=existing)
    handler._generate_embedding = AsyncMock(return_value=np.random.rand(1536))
    handler._update_in_db = AsyncMock()
    
    # Update
    request = MemoryUpdateRequest(
        content="New content",
        category=MemoryCategory.TECHNICAL,
        tags=["new", "updated"]
    )
    
    updated = await handler.update_memory(1, request)
    
    # Verify
    assert updated.content == "New content"
    assert updated.category == MemoryCategory.TECHNICAL
    assert updated.tags == ["new", "updated"]
    handler._update_in_db.assert_called_once()

@pytest.mark.asyncio
async def test_delete_memory(handler):
    """Test memory deletion."""
    handler._delete_from_db = AsyncMock(return_value=True)
    
    result = await handler.delete_memory(1)
    
    assert result is True
    handler._delete_from_db.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_generate_highlights(handler):
    """Test highlight generation."""
    content = "Python is great. Java is also good. Python has many libraries."
    highlights = handler._generate_highlights(content, "Python")
    
    assert len(highlights) >= 1
    assert any("Python" in h for h in highlights)
