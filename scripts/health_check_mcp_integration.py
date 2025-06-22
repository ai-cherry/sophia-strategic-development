#!/usr/bin/env python3
"""MCP Integration Health Check for Sophia AI.

Comprehensive health check for all MCP servers and integration components.
Validates the deployment strategy requirements.
"""

import asyncio
import aiohttp
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add backend to path for importing our clean improvements
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from backend.agents.core.agent_categories import AgentCategoryManager
    from backend.agents.core.cursor_mode_optimizer import CursorModeOptimizer
    IMPORTS_AVAILABLE = True
except ImportError:
    print("⚠️  Backend imports not available - testing without integration components")
    IMPORTS_AVAILABLE = False


class MCPHealthChecker:
    """Comprehensive health checker for MCP integration components"""
    
    def __init__(self):
        self.health_status = {}
        self.start_time = time.time()
        
    async def check_mcp_server(self, name: str, url: str, timeout: int = 5) -> bool:
        """Check if an MCP server is responding"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get(f"{url}/health") as resp:
                    return resp.status == 200
        except aiohttp.ClientError:
            # Try alternative endpoints
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                    async with session.get(f"{url}/status") as resp:
                        return resp.status == 200
            except:
                return False
        except Exception:
            return False
    
    async def check_agno_mcp_server(self) -> Dict[str, Any]:
        """Check Agno MCP server health"""
        print("🔍 Checking Agno MCP Server...")
        
        server_healthy = await self.check_mcp_server("agno", "http://localhost:8090")
        
        result = {
            "healthy": server_healthy,
            "url": "http://localhost:8090",
            "expected_features": [
                "Agent instantiation (< 3μs)",
                "Agno Team 2.0 coordination",
                "Performance optimization"
            ]
        }
        
        if server_healthy:
            print("  ✅ Agno MCP Server responding")
        else:
            print("  ❌ Agno MCP Server not accessible")
            
        return result
    
    async def check_pulumi_mcp_server(self) -> Dict[str, Any]:
        """Check Pulumi MCP server health"""
        print("🔍 Checking Pulumi MCP Server...")
        
        server_healthy = await self.check_mcp_server("pulumi", "http://localhost:8091")
        
        result = {
            "healthy": server_healthy,
            "url": "http://localhost:8091", 
            "expected_features": [
                "Infrastructure deployment",
                "Stack management",
                "Automation API integration"
            ]
        }
        
        if server_healthy:
            print("  ✅ Pulumi MCP Server responding")
        else:
            print("  ❌ Pulumi MCP Server not accessible")
            
        return result
    
    async def check_sophia_mcp_servers(self) -> Dict[str, Any]:
        """Check Sophia AI MCP servers"""
        print("🔍 Checking Sophia AI MCP Servers...")
        
        servers = {
            "sophia_intelligence": "http://localhost:8092",
            "sophia_business_intelligence": "http://localhost:8093",
            "sophia_data_intelligence": "http://localhost:8094",
            "sophia_infrastructure": "http://localhost:8095"
        }
        
        results = {}
        healthy_count = 0
        
        for name, url in servers.items():
            healthy = await self.check_mcp_server(name, url)
            results[name] = {
                "healthy": healthy,
                "url": url
            }
            
            if healthy:
                healthy_count += 1
                print(f"  ✅ {name} responding")
            else:
                print(f"  ❌ {name} not accessible")
        
        return {
            "servers": results,
            "healthy_count": healthy_count,
            "total_count": len(servers),
            "overall_healthy": healthy_count > 0
        }
    
    def check_agent_categorization(self) -> Dict[str, Any]:
        """Check agent categorization system from our clean improvements"""
        print("🔍 Checking Agent Categorization System...")
        
        if not IMPORTS_AVAILABLE:
            print("  ⚠️  Backend imports not available - skipping categorization check")
            return {"healthy": False, "reason": "imports_unavailable"}
        
        try:
            stats = AgentCategoryManager.get_category_stats()
            
            result = {
                "healthy": stats['total_agents'] > 0,
                "total_agents": stats['total_agents'],
                "total_categories": stats['total_categories'],
                "category_distribution": stats['category_distribution']
            }
            
            if result["healthy"]:
                print(f"  ✅ Agent categorization working - {stats['total_agents']} agents in {stats['total_categories']} categories")
            else:
                print("  ❌ Agent categorization system has no agents")
                
            return result
            
        except Exception as e:
            print(f"  ❌ Agent categorization system error: {e}")
            return {"healthy": False, "error": str(e)}
    
    def check_cursor_mode_optimization(self) -> Dict[str, Any]:
        """Check Cursor mode optimization from our clean improvements"""
        print("🔍 Checking Cursor Mode Optimization...")
        
        if not IMPORTS_AVAILABLE:
            print("  ⚠️  Backend imports not available - skipping optimization check")
            return {"healthy": False, "reason": "imports_unavailable"}
        
        try:
            # Test mode hint generation
            test_commands = [
                "show me the status",
                "analyze recent calls",
                "deploy to production"
            ]
            
            hints_working = 0
            total_tests = len(test_commands)
            
            for command in test_commands:
                hint = CursorModeOptimizer.get_mode_hint(command)
                if hint:
                    hints_working += 1
            
            result = {
                "healthy": hints_working > 0,
                "hints_working": hints_working,
                "total_tests": total_tests,
                "success_rate": f"{(hints_working/total_tests)*100:.1f}%"
            }
            
            if result["healthy"]:
                print(f"  ✅ Cursor mode optimization working - {hints_working}/{total_tests} commands optimized")
            else:
                print("  ❌ Cursor mode optimization not generating hints")
                
            return result
            
        except Exception as e:
            print(f"  ❌ Cursor mode optimization error: {e}")
            return {"healthy": False, "error": str(e)}
    
    async def check_basic_connectivity(self) -> Dict[str, Any]:
        """Check basic network connectivity for MCP integration"""
        print("🔍 Checking Basic Connectivity...")
        
        # Test local ports that should be available
        test_ports = [8000, 8090, 8091, 8092]
        available_ports = []
        
        for port in test_ports:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    available_ports.append(port)
                    print(f"  ✅ Port {port} accessible")
                else:
                    print(f"  ❌ Port {port} not accessible")
                    
            except Exception as e:
                print(f"  ❌ Port {port} error: {e}")
        
        return {
            "healthy": len(available_ports) > 0,
            "available_ports": available_ports,
            "tested_ports": test_ports,
            "connectivity_rate": f"{(len(available_ports)/len(test_ports))*100:.1f}%"
        }
    
    async def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run all health checks and provide comprehensive status"""
        print("🚀 SOPHIA AI MCP INTEGRATION HEALTH CHECK")
        print("=" * 60)
        
        # Run all health checks
        self.health_status = {
            "timestamp": time.time(),
            "agno_mcp": await self.check_agno_mcp_server(),
            "pulumi_mcp": await self.check_pulumi_mcp_server(), 
            "sophia_mcp": await self.check_sophia_mcp_servers(),
            "agent_categorization": self.check_agent_categorization(),
            "cursor_optimization": self.check_cursor_mode_optimization(),
            "basic_connectivity": await self.check_basic_connectivity()
        }
        
        # Calculate overall health
        component_health = []
        for component, status in self.health_status.items():
            if component == "timestamp":
                continue
            if isinstance(status, dict) and "healthy" in status:
                component_health.append(status["healthy"])
        
        overall_healthy = any(component_health)  # At least one component working
        critical_healthy = (
            self.health_status["agent_categorization"]["healthy"] and 
            self.health_status["cursor_optimization"]["healthy"]
        ) if IMPORTS_AVAILABLE else False
        
        print("\n" + "=" * 60)
        print("📊 HEALTH CHECK SUMMARY")
        print("=" * 60)
        
        if overall_healthy:
            print("✅ OVERALL STATUS: Some components operational")
        else:
            print("❌ OVERALL STATUS: No components responding")
            
        if IMPORTS_AVAILABLE and critical_healthy:
            print("✅ CRITICAL COMPONENTS: Clean structural improvements working")
        else:
            print("⚠️  CRITICAL COMPONENTS: Some improvements need attention")
        
        # Deployment readiness assessment
        print("\n🎯 DEPLOYMENT READINESS ASSESSMENT:")
        
        if critical_healthy:
            print("✅ Phase 1 (Foundation): Ready - Agent categorization and Cursor optimization working")
        else:
            print("❌ Phase 1 (Foundation): Not ready - Clean improvements need fixing")
            
        mcp_servers_ready = (
            self.health_status["agno_mcp"]["healthy"] or
            self.health_status["pulumi_mcp"]["healthy"] or  
            self.health_status["sophia_mcp"]["overall_healthy"]
        )
        
        if mcp_servers_ready:
            print("✅ Phase 2 (MCP Servers): Partially ready - Some MCP servers responding")
        else:
            print("❌ Phase 2 (MCP Servers): Not ready - No MCP servers accessible")
            
        if overall_healthy and critical_healthy and mcp_servers_ready:
            print("🎉 Phase 3 (Integration): Ready for integration validation")
        else:
            print("⏳ Phase 3 (Integration): Prerequisites not met")
        
        print(f"\n⏱️  Health check completed in {time.time() - self.start_time:.2f} seconds")
        
        return {
            "overall_healthy": overall_healthy,
            "critical_healthy": critical_healthy,
            "mcp_servers_ready": mcp_servers_ready,
            "components": self.health_status,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on health check results"""
        recommendations = []
        
        if not IMPORTS_AVAILABLE:
            recommendations.append("Install backend dependencies: cd backend && pip install -r requirements.txt")
        
        if not self.health_status["agent_categorization"]["healthy"]:
            recommendations.append("Verify agent categorization: python3 scripts/standalone_demo.py")
            
        if not self.health_status["agno_mcp"]["healthy"]:
            recommendations.append("Start Agno MCP server: ag ws up --env dev --infra docker")
            
        if not self.health_status["pulumi_mcp"]["healthy"]:
            recommendations.append("Start Pulumi MCP server: cd mcp-servers/pulumi && docker-compose up -d")
            
        if not self.health_status["sophia_mcp"]["overall_healthy"]:
            recommendations.append("Start Sophia MCP servers: python3 mcp-servers/sophia_ai_intelligence/sophia_ai_intelligence_mcp_server.py")
            
        if not self.health_status["basic_connectivity"]["healthy"]:
            recommendations.append("Check network configuration and firewall settings")
        
        if not recommendations:
            recommendations.append("All systems operational - proceed with integration testing")
            
        return recommendations


async def main():
    """Run the comprehensive health check"""
    
    checker = MCPHealthChecker()
    results = await checker.run_comprehensive_health_check()
    
    # Print recommendations
    if results["recommendations"]:
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")
    
    # Exit with appropriate code
    if results["overall_healthy"]:
        print("\n🎉 Health check completed - some components operational")
        sys.exit(0)
    else:
        print("\n⚠️  Health check completed - intervention required")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 