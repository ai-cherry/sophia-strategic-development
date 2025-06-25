#!/usr/bin/env python3
"""
Sophia AI MCP Server Testing and Monitoring Suite
"""

import asyncio
import aiohttp
import time
import sys
from datetime import datetime
from typing import Dict, Any
import psutil

class MCPServerMonitor:
    def __init__(self):
        self.servers = {
            "ai_memory": {"name": "AI Memory", "port": 9000},
            "sophia_intelligence": {"name": "Sophia AI Intelligence", "port": 8092},
            "codacy": {"name": "Codacy", "port": 3008},
            "asana": {"name": "Asana", "port": 3006},
            "notion": {"name": "Notion", "port": 3007}
        }
    
    async def check_server_health(self, server_id: str) -> Dict[str, Any]:
        """Check health of a specific MCP server"""
        server = self.servers[server_id]
        result = {
            "server": server["name"],
            "port": server["port"],
            "status": "unknown",
            "response_time": None,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            start_time = time.time()
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                url = f"http://localhost:{server['port']}/health"
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000
                    result["response_time"] = round(response_time, 2)
                    
                    if response.status == 200:
                        result["status"] = "healthy"
                        try:
                            result["data"] = await response.json()
                        except:
                            result["data"] = await response.text()
                    else:
                        result["status"] = "unhealthy"
                        result["error"] = f"HTTP {response.status}"
                        
        except Exception as e:
            result["status"] = "unreachable"
            result["error"] = str(e)
            
        return result
    
    def check_port_status(self) -> Dict[str, Any]:
        """Check which ports are in use"""
        port_status = {}
        
        for server_id, server_info in self.servers.items():
            port = server_info["port"]
            port_status[server_id] = {
                "name": server_info["name"],
                "port": port,
                "in_use": False,
                "process": None
            }
            
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    port_status[server_id]["in_use"] = True
                    if conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            port_status[server_id]["process"] = {
                                "pid": conn.pid,
                                "name": proc.name()
                            }
                        except:
                            pass
                    break
        
        return port_status
    
    async def run_health_check(self):
        """Run health check on all servers"""
        print("🧪 MCP Server Health Check")
        print("=" * 40)
        
        port_status = self.check_port_status()
        
        print("\n🔌 Port Status:")
        for server_id, info in port_status.items():
            status = "🟢 IN USE" if info["in_use"] else "🔴 AVAILABLE"
            print(f"   {info['name']}: Port {info['port']} - {status}")
            if info["process"]:
                print(f"      Process: {info['process']['name']} (PID: {info['process']['pid']})")
        
        print("\n🏥 Health Checks:")
        healthy_count = 0
        
        for server_id in self.servers:
            health = await self.check_server_health(server_id)
            status_emoji = "🟢" if health["status"] == "healthy" else "🔴"
            print(f"   {status_emoji} {health['server']}: {health['status']}")
            
            if health["response_time"]:
                print(f"      Response time: {health['response_time']}ms")
            if health["error"]:
                print(f"      Error: {health['error']}")
            
            if health["status"] == "healthy":
                healthy_count += 1
        
        print(f"\n📊 Summary: {healthy_count}/{len(self.servers)} servers healthy")
        return healthy_count == len(self.servers)

def main():
    monitor = MCPServerMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        # Continuous monitoring
        async def continuous_monitor():
            while True:
                await monitor.run_health_check()
                print("\n⏰ Next check in 30 seconds... (Ctrl+C to stop)")
                try:
                    await asyncio.sleep(30)
                except KeyboardInterrupt:
                    print("\n🛑 Monitoring stopped")
                    break
        
        asyncio.run(continuous_monitor())
    else:
        # Single health check
        asyncio.run(monitor.run_health_check())

if __name__ == "__main__":
    main()
