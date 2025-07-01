#!/usr/bin/env python3
"""
Sophia AI MCP Server Orchestrator
Starts all MCP servers in the correct order with health monitoring and dependency management.
"""
import asyncio
import json
import subprocess
import sys
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
MCP_SERVERS_DIR = PROJECT_ROOT / "mcp-servers"
PORT_REGISTRY_PATH = PROJECT_ROOT / "config" / "unified_mcp_port_registry.json"

class MCPServerOrchestrator:
    def __init__(self):
        self.servers: Dict[str, Dict] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.port_registry = self._load_port_registry()
        
    def _load_port_registry(self) -> Dict:
        """Load the unified port registry"""
        try:
            with open(PORT_REGISTRY_PATH) as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load port registry: {e}")
            return {}
    
    def _get_server_config(self) -> Dict[str, Dict]:
        """Get server configuration with startup order and dependencies"""
        return {
            # Core AI servers (start first)
            "ai_memory": {
                "path": "ai_memory",
                "port": self.port_registry["port_allocation"]["ai_core"]["ai_memory"],
                "priority": 1,
                "dependencies": [],
                "startup_command": ["python", "ai_memory_mcp_server.py"],
                "health_endpoint": "/health"
            },
            
            # Data infrastructure (start second)
            "snowflake_admin": {
                "path": "snowflake_admin", 
                "port": self.port_registry["port_allocation"]["data_infrastructure"]["snowflake_admin"],
                "priority": 2,
                "dependencies": [],
                "startup_command": ["python", "snowflake_admin_mcp_server.py"],
                "health_endpoint": "/health"
            },
            
            # Business intelligence (start third)
            "ui_ux_agent": {
                "path": "ui_ux_agent",
                "port": self.port_registry["port_allocation"]["business_intelligence"]["ui_ux_agent"], 
                "priority": 3,
                "dependencies": ["ai_memory"],
                "startup_command": ["python", "ui_ux_agent_mcp_server.py"],
                "health_endpoint": "/health"
            },
            
            "hubspot": {
                "path": "hubspot",
                "port": self.port_registry["port_allocation"]["business_intelligence"]["hubspot"],
                "priority": 3,
                "dependencies": ["snowflake_admin"],
                "startup_command": ["python", "hubspot_mcp_server.py"],
                "health_endpoint": "/health"
            },
            
            "linear": {
                "path": "linear",
                "port": self.port_registry["port_allocation"]["business_intelligence"]["linear"],
                "priority": 3,
                "dependencies": ["ai_memory"],
                "startup_command": ["python", "linear_mcp_server.py"],
                "health_endpoint": "/health"
            },
            
            "asana": {
                "path": "asana",
                "port": self.port_registry["port_allocation"]["business_intelligence"]["asana"],
                "priority": 3,
                "dependencies": ["ai_memory"],
                "startup_command": ["python", "asana_mcp_server.py"],
                "health_endpoint": "/health"
            },
            
            # Development tools (start fourth)
            "codacy": {
                "path": "codacy",
                "port": self.port_registry["port_allocation"]["development_tools"]["codacy"],
                "priority": 4,
                "dependencies": [],
                "startup_command": ["python", "codacy_mcp_server.py"],
                "health_endpoint": "/health"
            },
            
            "github": {
                "path": "github",
                "port": self.port_registry["port_allocation"]["development_tools"]["github"],
                "priority": 4,
                "dependencies": [],
                "startup_command": ["python", "github_mcp_server.py"],
                "health_endpoint": "/health"
            },
            
            # Infrastructure (start last)
            "lambda_labs_cli": {
                "path": "lambda_labs_cli",
                "port": self.port_registry["port_allocation"]["infrastructure"]["lambda_labs_cli"],
                "priority": 5,
                "dependencies": [],
                "startup_command": ["python", "lambda_labs_cli_mcp_server.py"],
                "health_endpoint": "/health"
            }
        }
    
    async def check_health(self, server_name: str, port: int, timeout: int = 5) -> bool:
        """Check if a server is healthy"""
        url = f"http://localhost:{port}/health"
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False
    
    async def start_server(self, server_name: str, config: Dict) -> bool:
        """Start a single MCP server"""
        server_dir = MCP_SERVERS_DIR / config["path"]
        
        if not server_dir.exists():
            print(f"⚠️ Server directory not found: {server_dir}")
            return False
            
        print(f"🚀 Starting {server_name} on port {config['port']}...")
        
        try:
            # Change to server directory and start
            process = subprocess.Popen(
                config["startup_command"],
                cwd=server_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[server_name] = process
            
            # Wait for startup and health check
            for attempt in range(10):
                await asyncio.sleep(1)
                if await self.check_health(server_name, config["port"]):
                    print(f"✅ {server_name} started successfully on port {config['port']}")
                    return True
                    
            print(f"❌ {server_name} failed to start or become healthy")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start {server_name}: {e}")
            return False
    
    async def wait_for_dependencies(self, dependencies: List[str]) -> bool:
        """Wait for dependency servers to be healthy"""
        if not dependencies:
            return True
            
        print(f"⏳ Waiting for dependencies: {', '.join(dependencies)}")
        
        for dep in dependencies:
            if dep not in self.servers:
                continue
                
            config = self.servers[dep]
            for attempt in range(30):  # 30 second timeout
                if await self.check_health(dep, config["port"]):
                    break
                await asyncio.sleep(1)
            else:
                print(f"❌ Dependency {dep} not healthy")
                return False
                
        return True
    
    async def start_all_servers(self) -> Dict[str, bool]:
        """Start all MCP servers in dependency order"""
        self.servers = self._get_server_config()
        results = {}
        
        # Group servers by priority
        priority_groups = {}
        for name, config in self.servers.items():
            priority = config["priority"]
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append((name, config))
        
        # Start servers by priority group
        for priority in sorted(priority_groups.keys()):
            print(f"\n🎯 Starting Priority {priority} servers...")
            
            # Start all servers in this priority group
            tasks = []
            for server_name, config in priority_groups[priority]:
                # Wait for dependencies first
                if await self.wait_for_dependencies(config["dependencies"]):
                    tasks.append(self.start_server(server_name, config))
                else:
                    print(f"❌ Skipping {server_name} due to dependency failures")
                    results[server_name] = False
            
            # Wait for all servers in this priority to start
            if tasks:
                group_results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, (server_name, _) in enumerate(priority_groups[priority]):
                    if i < len(group_results):
                        results[server_name] = group_results[i] if not isinstance(group_results[i], Exception) else False
        
        return results
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Run health checks on all servers"""
        health_results = {}
        
        for server_name, config in self.servers.items():
            health_results[server_name] = await self.check_health(server_name, config["port"])
            
        return health_results
    
    def stop_all_servers(self):
        """Stop all running servers"""
        print("\n🛑 Stopping all MCP servers...")
        
        for server_name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {server_name}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 Force killed {server_name}")
            except Exception as e:
                print(f"❌ Error stopping {server_name}: {e}")
    
    def print_status_report(self, start_results: Dict[str, bool], health_results: Dict[str, bool]):
        """Print a comprehensive status report"""
        print("\n" + "="*60)
        print("🏥 SOPHIA AI MCP SERVER STATUS REPORT")
        print("="*60)
        
        total_servers = len(self.servers)
        started_servers = sum(1 for result in start_results.values() if result)
        healthy_servers = sum(1 for result in health_results.values() if result)
        
        print(f"📊 Overview: {healthy_servers}/{total_servers} servers healthy")
        print(f"🚀 Started: {started_servers}/{total_servers} servers")
        print()
        
        for server_name in self.servers:
            config = self.servers[server_name]
            started = start_results.get(server_name, False)
            healthy = health_results.get(server_name, False)
            
            status_icon = "✅" if healthy else "❌" if started else "⏸️"
            status_text = "HEALTHY" if healthy else "UNHEALTHY" if started else "NOT_STARTED"
            
            print(f"{status_icon} {server_name:20} | Port {config['port']:5} | {status_text}")
        
        print("\n" + "="*60)
        
        if healthy_servers == total_servers:
            print("🎉 All MCP servers are operational!")
        elif healthy_servers > 0:
            print(f"⚠️ {total_servers - healthy_servers} servers need attention")
        else:
            print("❌ No servers are healthy - check logs and configuration")


async def main():
    """Main orchestrator function"""
    orchestrator = MCPServerOrchestrator()
    
    try:
        print("🎬 Starting Sophia AI MCP Server Orchestration...")
        print(f"📂 Project root: {PROJECT_ROOT}")
        print(f"🔧 MCP servers directory: {MCP_SERVERS_DIR}")
        
        # Start all servers
        start_results = await orchestrator.start_all_servers()
        
        # Wait a moment for final startup
        await asyncio.sleep(2)
        
        # Run health checks
        health_results = await orchestrator.health_check_all()
        
        # Print status report
        orchestrator.print_status_report(start_results, health_results)
        
        # Keep servers running
        print("\n🔄 MCP servers are running. Press Ctrl+C to stop all servers...")
        
        try:
            while True:
                await asyncio.sleep(10)
                # Periodic health check
                current_health = await orchestrator.health_check_all()
                unhealthy = [name for name, healthy in current_health.items() if not healthy]
                if unhealthy:
                    print(f"⚠️ Unhealthy servers detected: {', '.join(unhealthy)}")
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
            
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        sys.exit(1)
    finally:
        orchestrator.stop_all_servers()
        print("👋 MCP Server Orchestration completed")


if __name__ == "__main__":
    asyncio.run(main()) 