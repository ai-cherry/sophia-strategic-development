from unittest.mock import AsyncMock, patch

import pytest

# Ensure event loop pytest plugin works

@pytest.mark.asyncio
async def test_complete_calls_execute():
    # TODO: Update this import to correct location
    # from core.infra.cortex_gateway import get_gateway
    pass

    gw = get_gateway()

    fake_rows = [{"COMPLETION": "Hello world"}]

    with patch.object(
        gw.connection_manager,
        "execute_query",
        new=AsyncMock(return_value=fake_rows),
    ) as mocked_exec:
        result = await gw.complete("Say hi")
        assert result == "Hello world"
        mocked_exec.assert_awaited()

@pytest.mark.asyncio
async def test_embed_parses_json():
    # TODO: Update this import to correct location
    # from core.infra.cortex_gateway import get_gateway
    pass

    gw = get_gateway()
    fake_rows = [{"EMBED": "[1.0, 2.0, 3.0]"}]

    with patch.object(
        gw.connection_manager,
        "execute_query",
        new=AsyncMock(return_value=fake_rows),
    ) as mocked_exec:
        vec = await gw.embed("hello")
        assert vec == [1.0, 2.0, 3.0]
        mocked_exec.assert_awaited()
