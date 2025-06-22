import pytest
import fakeredis.aioredis
from backend.security.security_manager import SophiaSecurityManager, SecurityConfig
import backend.security.security_manager as sm_mod

@pytest.mark.asyncio
async def test_store_and_get_api_key(monkeypatch):
    fake = fakeredis.aioredis.FakeRedis()
    monkeypatch.setattr(sm_mod.redis, 'from_url', lambda url: fake)
    async def noop(self):
        pass
    monkeypatch.setattr(SophiaSecurityManager, '_initialize_security_monitoring', noop)
    manager = SophiaSecurityManager(SecurityConfig())
    await manager.start()
    await manager.store_api_key('service', 'secret')
    key = await manager.get_api_key('service')
    assert key == 'secret'
    await manager.stop()
