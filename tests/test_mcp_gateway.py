import pytest
from aiohttp.test_utils import TestClient, TestServer
from aiohttp import web
from mcp_gateway_server import SophiaMCPGateway

@pytest.mark.asyncio
async def test_gateway_health_check():
    gateway = SophiaMCPGateway()
    server = TestServer(gateway.app)
    async with server:
        client = TestClient(server)
        async with client:
            resp = await client.get('/health')
            assert resp.status == 200
            data = await resp.json()
            assert data['status'] == 'healthy'
