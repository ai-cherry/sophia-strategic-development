"""Unit tests for perplexity_v2 handler."""

import pytest

from infrastructure.mcp_servers.perplexity_v2.handlers.main_handler import (
    Perplexity_V2Handler,
)


@pytest.mark.asyncio
async def test_handler_initialization():
    """Test handler initialization."""
    handler = Perplexity_V2Handler()
    await handler.initialize()
    # Add assertions
