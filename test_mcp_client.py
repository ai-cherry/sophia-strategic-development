"""
Simple test script to verify MCP client functionality
"""
import asyncio
import aiohttp
from backend.mcp.mcp_client import MCPClient

async def test_gateway_health(gateway_url: str = "http://localhost:8090"):
    """Test if the MCP gateway is healthy"""
    print(f"Testing gateway health at {gateway_url}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{gateway_url}/health") as response:
                if response.status == 200:
                    print("Gateway is healthy!")
                    data = await response.json()
                    print(f"Response: {data}")
                    return True
                else:
                    print(f"Gateway health check failed with status {response.status}")
                    return False
    except aiohttp.ClientConnectorError as e:
        print(f"Connection error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

async def test_servers_endpoint(gateway_url: str = "http://localhost:8090"):
    """Test if the MCP gateway's servers endpoint is working"""
    print(f"Testing servers endpoint at {gateway_url}/servers...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{gateway_url}/servers") as response:
                if response.status == 200:
                    print("Servers endpoint is working!")
                    data = await response.json()
                    print(f"Response: {data}")
                    return True
                else:
                    print(f"Servers endpoint failed with status {response.status}")
                    return False
    except aiohttp.ClientConnectorError as e:
        print(f"Connection error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

async def main():
    """Main function"""
    # Test gateway health
    health_ok = await test_gateway_health()
    
    if health_ok:
        # Test servers endpoint
        await test_servers_endpoint()
    
    # Try to create and connect an MCPClient
    print("\nTesting MCPClient...")
    client = MCPClient()
    try:
        await client.connect()
        print("MCPClient connected successfully!")
        print(f"Discovered servers: {client.list_servers()}")
        print(f"Discovered tools: {client.list_tools()}")
    except Exception as e:
        print(f"MCPClient connection failed: {e}")
    finally:
        if client.session:
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
