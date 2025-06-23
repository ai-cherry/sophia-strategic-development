"""Tests for the AI Memory MCP server."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.mcp.ai_memory_mcp_server import AiMemoryMCPServer
from backend.core.comprehensive_memory_manager import ComprehensiveMemoryManager
from backend.core.contextual_memory_intelligence import ContextualMemoryIntelligence


@pytest.fixture
def memory_server():
    """Create an AI Memory MCP server for testing."""
    server = AiMemoryMCPServer()
    server.memory_manager = AsyncMock(spec=ComprehensiveMemoryManager)
    server.memory_intelligence = AsyncMock(spec=ContextualMemoryIntelligence)
    server.initialized = True
    return server


@pytest.mark.asyncio
async def test_store_conversation(memory_server):
    """Test storing a conversation."""
    memory_server.get_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
    memory_server.pinecone_index = MagicMock()

    content = "We decided to use PostgreSQL for the database"
    category = "architecture"
    tags = ["database", "decision"]

    result = await memory_server.store_memory(content, category, tags)

    assert "id" in result
    assert result["status"] == "stored"
    memory_server.memory_manager.append.assert_called_once()
    memory_server.pinecone_index.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_recall_memory(memory_server):
    """Test recalling a memory."""
    memory_server.get_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
    mock_match = MagicMock()
    mock_match.id = "architecture_20250101000000"
    mock_match.score = 0.95
    mock_match.metadata = {
        "category": "architecture",
        "tags": json.dumps(["database", "decision"]),
        "created_at": "2025-01-01T00:00:00",
    }
    mock_response = MagicMock()
    mock_response.matches = [mock_match]
    memory_server.pinecone_index = MagicMock()
    memory_server.pinecone_index.query.return_value = mock_response
    memory_server._get_memory_content = AsyncMock(
        return_value="We decided to use PostgreSQL for the database"
    )

    results = await memory_server.recall_memory("database decision", "architecture")

    assert len(results) == 1
    assert results[0]["id"] == "architecture_20250101000000"
    assert results[0]["category"] == "architecture"
    assert results[0]["relevance_score"] == 0.95
    assert results[0]["content"] == "We decided to use PostgreSQL for the database"
    memory_server.pinecone_index.query.assert_called_once()


@pytest.mark.asyncio
async def test_get_tools(memory_server):
    """Test getting the list of tools."""
    tools = memory_server.get_tools()
    assert len(tools) == 2
    assert tools[0]["name"] == "store_conversation"
    assert tools[1]["name"] == "recall_memory"
    assert "content" in tools[0]["parameters"]["properties"]
    assert "category" in tools[0]["parameters"]["properties"]
    assert "tags" in tools[0]["parameters"]["properties"]
    assert "query" in tools[1]["parameters"]["properties"]
    assert "category" in tools[1]["parameters"]["properties"]
    assert "limit" in tools[1]["parameters"]["properties"]


@pytest.mark.asyncio
async def test_execute_tool_store(memory_server):
    """Test executing the store_conversation tool."""
    memory_server.store_memory = AsyncMock(
        return_value={"id": "test_id", "status": "stored"}
    )
    params = {
        "content": "We decided to use PostgreSQL for the database",
        "category": "architecture",
        "tags": ["database", "decision"],
    }
    result = await memory_server.execute_tool("store_conversation", params)
    assert result["id"] == "test_id"
    assert result["status"] == "stored"
    memory_server.store_memory.assert_called_once_with(
        params["content"], params["category"], params["tags"]
    )


@pytest.mark.asyncio
async def test_execute_tool_recall(memory_server):
    """Test executing the recall_memory tool."""
    mock_results = [{"id": "test_id", "content": "test content"}]
    memory_server.recall_memory = AsyncMock(return_value=mock_results)
    params = {
        "query": "database decision",
        "category": "architecture",
        "limit": 5,
    }
    result = await memory_server.execute_tool("recall_memory", params)
    assert "results" in result
    assert result["results"] == mock_results
    memory_server.recall_memory.assert_called_once_with(
        params["query"], params["category"], params["limit"]
    )


@pytest.mark.asyncio
async def test_health_check(memory_server):
    """Test the health check."""
    status = await memory_server.health_check()
    assert status["status"] == "operational"
    assert "timestamp" in status
