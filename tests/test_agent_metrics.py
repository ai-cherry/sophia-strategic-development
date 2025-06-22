import importlib.util
from pathlib import Path
import pytest

@pytest.mark.asyncio
async def test_agent_pooling():
    spec = importlib.util.spec_from_file_location(
        "agno_perf",
        Path("backend/agents/core/agno_performance_optimizer.py").resolve(),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    AgnoPerformanceOptimizer = module.AgnoPerformanceOptimizer

    class DummyAgent:
        def __init__(self, name):
            self.name = name

    optimizer = AgnoPerformanceOptimizer()
    await optimizer.register_agent_class('dummy', DummyAgent)
    agent1 = await optimizer.get_or_create_agent('dummy', {'name': 'a'})
    await optimizer.release_agent('dummy', agent1)
    agent2 = await optimizer.get_or_create_agent('dummy', {'name': 'b'})
    assert agent1 is agent2
