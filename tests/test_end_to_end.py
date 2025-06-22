import importlib.util
from pathlib import Path
import pytest
import fakeredis.aioredis
from backend.security.security_manager import SophiaSecurityManager, SecurityConfig
from backend.vector.vector_integration import VectorIntegration, VectorConfig, VectorDBType
import backend.security.security_manager as sm_mod

@pytest.mark.asyncio
async def test_end_to_end(monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "agno_perf",
        Path("backend/agents/core/agno_performance_optimizer.py").resolve(),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    AgnoPerformanceOptimizer = module.AgnoPerformanceOptimizer
    async def noop(self):
        pass
    monkeypatch.setattr(SophiaSecurityManager, '_initialize_security_monitoring', noop)

    class DummyAgent:
        def __init__(self, name):
            self.name = name

    optimizer = AgnoPerformanceOptimizer()

    fake = fakeredis.aioredis.FakeRedis()
    monkeypatch.setattr(sm_mod.redis, 'from_url', lambda url: fake)
    sec = SophiaSecurityManager(SecurityConfig())
    await sec.start()
    await sec.store_api_key('test', 'key123')
    assert await sec.get_api_key('test') == 'key123'

    vi = VectorIntegration(VectorConfig(db_type=VectorDBType.MEMORY, index_name='e2e'))
    await vi.initialize()
    await vi.index_content('1', 'hello world')
    results = await vi.search('hello')
    assert results and results[0].id == '1'

    await optimizer.register_agent_class('dummy', DummyAgent)
    agent1 = await optimizer.get_or_create_agent('dummy', {'name': 'a'})
    await optimizer.release_agent('dummy', agent1)
    agent2 = await optimizer.get_or_create_agent('dummy', {'name': 'b'})
    assert agent1 is agent2

    await sec.stop()
