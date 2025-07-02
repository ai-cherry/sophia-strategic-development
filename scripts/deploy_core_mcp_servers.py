#!/usr/bin/env python3
"""Deploy core coding MCP servers with health monitoring."""

import asyncio
import subprocess
import time
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

CORE_SERVERS = [
    {"name": "ai_memory", "port": 9000, "priority": 1},
    {"name": "codacy", "port": 3008, "priority": 2},
    {"name": "github", "port": 9003, "priority": 3},
    {"name": "linear", "port": 9004, "priority": 4}
]

async def deploy_server(server):
    """Deploy individual MCP server."""
    server_dir = Path(f"mcp-servers/{server['name']}")
    server_file = server_dir / f"{server['name']}_mcp_server.py"
    
    if not server_file.exists():
        print(f"❌ {server['name']}: Server file not found at {server_file}")
        return False
    
    try:
        print(f"🚀 Starting {server['name']} on port {server['port']}...")
        
        # Start server in background
        process = subprocess.Popen([
            sys.executable, str(server_file)
        ], cwd=Path.cwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for startup
        await asyncio.sleep(5)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ {server['name']}: Process died")
            print(f"   stdout: {stdout.decode()[:200]}...")
            print(f"   stderr: {stderr.decode()[:200]}...")
            return False
        
        # Health check
        health_ok = await check_server_health(server['port'])
        
        if health_ok:
            print(f"✅ {server['name']}: Running on port {server['port']}")
            return True
        else:
            print(f"❌ {server['name']}: Failed health check")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ {server['name']}: Deployment failed - {e}")
        return False

async def check_server_health(port):
    """Check if MCP server is responding."""
    try:
        import aiohttp
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Try health endpoint first
            try:
                async with session.get(f"http://localhost:{port}/health") as response:
                    return response.status == 200
            except:
                # Try root endpoint as fallback
                try:
                    async with session.get(f"http://localhost:{port}/") as response:
                        return response.status in [200, 404]  # 404 is ok for MCP servers
                except:
                    return False
    except Exception as e:
        print(f"   Health check error: {e}")
        return False

def check_port_availability(port):
    """Check if port is available."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

async def main():
    """Deploy all core MCP servers."""
    print("=== Deploying Core MCP Servers ===\n")
    
    # Check port availability first
    print("Checking port availability...")
    for server in CORE_SERVERS:
        if not check_port_availability(server['port']):
            print(f"⚠️  Port {server['port']} is already in use (may be from previous run)")
    
    print()
    
    results = []
    for server in sorted(CORE_SERVERS, key=lambda x: x['priority']):
        result = await deploy_server(server)
        results.append((server['name'], result))
        
        if not result:
            print(f"⚠️  Continuing with next server despite {server['name']} failure\n")
        else:
            print()
    
    # Summary
    successful = sum(1 for _, success in results if success)
    print(f"=== Deployment Complete ===")
    print(f"Successful: {successful}/{len(CORE_SERVERS)} servers")
    
    if successful >= 2:
        print("✅ Core development infrastructure operational")
        print("\nRunning servers:")
        for name, success in results:
            if success:
                server = next(s for s in CORE_SERVERS if s['name'] == name)
                print(f"  - {name}: http://localhost:{server['port']}")
    else:
        print("❌ Critical deployment failure - manual intervention required")
    
    print(f"\nTo test services:")
    print(f"  python scripts/test_core_infrastructure.py")
    
    return successful >= 2

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
