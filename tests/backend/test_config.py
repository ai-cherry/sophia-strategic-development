import pytest

from backend.core.auto_esc_config import AutoESCConfig
from backend.core.secure_credential_manager import SecureCredentialManager


@pytest.mark.asyncio
async def test_secure_credential_manager_reads_from_config():
    cfg = AutoESCConfig()
    cfg._config = {"openai_api_key": "test"}
    manager = SecureCredentialManager(cfg)
    assert await manager.get_openai_api_key() == "test"
