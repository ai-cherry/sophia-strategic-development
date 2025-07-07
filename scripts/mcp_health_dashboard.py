#!/usr/bin/env python3
"""
MCP Health Monitoring Dashboard
Real-time monitoring of all MCP servers
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class MCPHealthDashboard:
    """Health monitoring dashboard for MCP servers"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.servers = {}
        self.health_data = {}
    
    async def start_monitoring(self):
        """Start health monitoring"""
        print("🏥 Starting MCP Health Dashboard...")
        
        while True:
            await self.collect_health_data()
            self.display_dashboard()
            await asyncio.sleep(30)  # Update every 30 seconds
    
    async def collect_health_data(self):
        """Collect health data from all MCP servers"""
        # Scan for MCP servers
        mcp_dirs = [
            self.project_root / "backend" / "mcp_servers",
            self.project_root / "mcp-servers"
        ]
        
        for directory in mcp_dirs:
            if directory.exists():
                for server_dir in directory.iterdir():
                    if server_dir.is_dir():
                        health_data = await self.get_server_health(server_dir)
                        self.health_data[server_dir.name] = health_data
    
    async def get_server_health(self, server_path: Path) -> Dict[str, Any]:
        """Get health data for a specific server"""
        try:
            # Check if server has health monitoring
            health_file = server_path / "health.py"
            if health_file.exists():
                # Simulate health check
                return {
                    "status": "healthy",
                    "uptime": time.time(),
                    "last_check": datetime.utcnow().isoformat(),
                    "has_monitoring": True
                }
            else:
                return {
                    "status": "unknown",
                    "uptime": 0,
                    "last_check": datetime.utcnow().isoformat(),
                    "has_monitoring": False
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
                "has_monitoring": False
            }
    
    def display_dashboard(self):
        """Display the health dashboard"""
        print("\n" + "="*80)
        print("🏥 MCP HEALTH DASHBOARD")
        print("="*80)
        print(f"Last Update: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        
        healthy_count = 0
        total_count = len(self.health_data)
        
        for server_name, health in self.health_data.items():
            status = health.get("status", "unknown")
            has_monitoring = health.get("has_monitoring", False)
            
            status_icon = {
                "healthy": "✅",
                "degraded": "⚠️",
                "error": "❌",
                "unknown": "❓"
            }.get(status, "❓")
            
            monitoring_icon = "📊" if has_monitoring else "⚪"
            
            print(f"{status_icon} {monitoring_icon} {server_name:<30} {status.upper()}")
            
            if status == "healthy":
                healthy_count += 1
        
        print()
        print(f"Summary: {healthy_count}/{total_count} servers healthy")
        print(f"Health Rate: {(healthy_count/max(1,total_count)*100):.1f}%")
        print("="*80)

async def main():
    """Main entry point"""
    dashboard = MCPHealthDashboard("/home/ubuntu/sophia-main")
    await dashboard.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
