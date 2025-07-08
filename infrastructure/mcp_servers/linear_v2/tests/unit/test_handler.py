"""Unit tests for linear_v2 handler."""

import pytest

from infrastructure.mcp_servers.linear_v2.handlers.main_handler import Linear_V2Handler


@pytest.mark.asyncio
async def test_handler_initialization():
    """Test handler initialization."""
    handler = Linear_V2Handler()
    await handler.initialize()
    # Add assertions
