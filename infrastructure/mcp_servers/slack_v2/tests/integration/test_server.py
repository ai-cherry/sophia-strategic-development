"""Integration tests for slack_v2 server."""

import pytest
from httpx import AsyncClient

from infrastructure.mcp_servers.slack_v2.server import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
