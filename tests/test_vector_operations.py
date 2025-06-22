import asyncio
import pytest

from backend.vector.vector_integration import VectorIntegration, VectorConfig, VectorDBType

@pytest.mark.asyncio
async def test_vector_memory_index_and_search():
    config = VectorConfig(db_type=VectorDBType.MEMORY, index_name="test")
    vi = VectorIntegration(config)
    await vi.initialize()
    await vi.index_content("1", "hello world")
    results = await vi.search("hello")
    assert results
    assert results[0].id == "1"
