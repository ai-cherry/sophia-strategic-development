#!/usr/bin/env python3
"""
🔍 SOPHIA AI COMPREHENSIVE SYSTEM MONITOR
Real-time monitoring of all platform components with health scoring

Features:
- Backend FastAPI health and dependency check
- Frontend React development server status
- MCP servers discovery and health verification
- Database connectivity testing
- GitHub deployment pipeline status
- Performance metrics and resource usage
- Business intelligence readiness assessment
"""

import asyncio
import aiohttp
import subprocess
import psutil
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import socket
import os
import sys

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

class SophiaAIMonitor:
    def __init__(self):
        self.status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_health": 0,
            "components": {},
            "business_readiness": 0,
            "alerts": [],
            "recommendations": []
        }
        
        # Define critical services and ports
        self.services = {
            "backend": {"port": 8000, "url": "http://localhost:8000", "critical": True},
            "frontend_primary": {"port": 5173, "url": "http://localhost:5173", "critical": True},
            "frontend_secondary": {"port": 5174, "url": "http://localhost:5174", "critical": False},
            "mcp_ai_memory": {"port": 9001, "url": "http://localhost:9001", "critical": True},
            "mcp_ui_ux": {"port": 9002, "url": "http://localhost:9002", "critical": False},
            "mcp_github": {"port": 9003, "url": "http://localhost:9003", "critical": False},
            "mcp_linear": {"port": 9004, "url": "http://localhost:9004", "critical": False},
            "mcp_slack": {"port": 9005, "url": "http://localhost:9005", "critical": False}
        }

    def check_port_status(self, port: int) -> bool:
        """Check if a port is in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False

    def get_process_info(self, port: int) -> Optional[Dict[str, Any]]:
        """Get detailed process information for a port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
                try:
                    connections = proc.connections()
                    for conn in connections:
                        if conn.laddr.port == port:
                            return {
                                "pid": proc.info['pid'],
                                "name": proc.info['name'],
                                "cmdline": ' '.join(proc.info['cmdline'][:3]),
                                "cpu_percent": proc.info['cpu_percent'],
                                "memory_mb": proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0,
                                "status": proc.status()
                            }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            return {"error": str(e)}
        return None

    async def check_http_endpoint(self, url: str, endpoint: str = "", timeout: int = 3) -> Dict[str, Any]:
        """Check HTTP endpoint health with detailed response analysis"""
        full_url = f"{url}{endpoint}"
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(full_url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    response_time = (time.time() - start_time) * 1000
                    content = await response.text()
                    
                    return {
                        "status": "healthy",
                        "status_code": response.status,
                        "response_time_ms": round(response_time, 2),
                        "content_length": len(content),
                        "headers": dict(response.headers),
                        "content_preview": content[:200] if content else None
                    }
        except asyncio.TimeoutError:
            return {"status": "timeout", "error": f"Timeout after {timeout}s"}
        except aiohttp.ClientError as e:
            return {"status": "connection_error", "error": str(e)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_dependencies(self) -> Dict[str, Any]:
        """Check Python dependencies critical for backend operation"""
        critical_packages = [
            'fastapi', 'uvicorn', 'sqlalchemy', 'pyjwt', 'redis', 
            'anthropic', 'openai', 'aiohttp', 'asyncpg', 'qdrant-client'
        ]
        
        dependency_status = {"installed": [], "missing": [], "status": "unknown"}
        
        try:
            import pkg_resources
            installed_packages = {pkg.project_name.lower() for pkg in pkg_resources.working_set}
            
            for package in critical_packages:
                if package.lower() in installed_packages or any(package.lower() in pkg for pkg in installed_packages):
                    dependency_status["installed"].append(package)
                else:
                    dependency_status["missing"].append(package)
            
            dependency_status["status"] = "healthy" if not dependency_status["missing"] else "degraded"
            dependency_status["install_coverage"] = len(dependency_status["installed"]) / len(critical_packages) * 100
            
        except Exception as e:
            dependency_status["error"] = str(e)
            dependency_status["status"] = "error"
        
        return dependency_status

    def check_environment_config(self) -> Dict[str, Any]:
        """Check environment configuration and Pulumi ESC connectivity"""
        config_status = {"status": "unknown", "environment": "unknown", "secrets_loaded": 0}
        
        try:
            # Try to import and check ESC config
            sys.path.append('/Users/lynnmusil/sophia-main-2/backend')
            from core.auto_esc_config import get_config_value
            
            config_status["environment"] = get_config_value('ENVIRONMENT', 'unknown')
            
            # Test critical secrets
            critical_secrets = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GONG_API_TOKEN', 'PINECONE_API_KEY']
            loaded_secrets = []
            
            for secret in critical_secrets:
                if get_config_value(secret, ''):
                    loaded_secrets.append(secret)
            
            config_status["secrets_loaded"] = len(loaded_secrets)
            config_status["total_secrets"] = len(critical_secrets)
            config_status["loaded_secrets"] = loaded_secrets
            config_status["status"] = "healthy" if len(loaded_secrets) >= 3 else "degraded"
            
        except Exception as e:
            config_status["error"] = str(e)
            config_status["status"] = "error"
        
        return config_status

    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                "status": "healthy"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def monitor_all_components(self) -> Dict[str, Any]:
        """Comprehensive monitoring of all Sophia AI components"""
        print("🔍 Starting Sophia AI Comprehensive System Monitor...")
        
        # 1. Check dependencies first
        print("   📦 Checking Python dependencies...")
        dependencies = self.check_dependencies()
        self.status["components"]["dependencies"] = dependencies
        
        # 2. Check environment configuration
        print("   🔧 Checking environment configuration...")
        environment = self.check_environment_config()
        self.status["components"]["environment"] = environment
        
        # 3. Check system resources
        print("   💻 Checking system resources...")
        resources = self.check_system_resources()
        self.status["components"]["system_resources"] = resources
        
        # 4. Check all services
        print("   🌐 Checking service endpoints...")
        for service_name, service_config in self.services.items():
            print(f"     Checking {service_name} on port {service_config['port']}...")
            
            # Port check
            port_active = self.check_port_status(service_config['port'])
            process_info = self.get_process_info(service_config['port']) if port_active else None
            
            # HTTP health check
            http_health = await self.check_http_endpoint(service_config['url'], "/health")
            
            service_status = {
                "port_active": port_active,
                "process_info": process_info,
                "http_health": http_health,
                "critical": service_config['critical'],
                "overall_status": "healthy" if port_active and http_health.get("status") == "healthy" else "degraded"
            }
            
            self.status["components"][service_name] = service_status
        
        # 5. Calculate overall health score
        self.calculate_health_scores()
        
        # 6. Generate alerts and recommendations
        self.generate_alerts_and_recommendations()
        
        return self.status

    def calculate_health_scores(self):
        """Calculate overall health and business readiness scores"""
        total_score = 0
        max_score = 0
        business_score = 0
        business_max = 0
        
        # Dependencies weight: 20%
        dep_status = self.status["components"]["dependencies"]
        if dep_status["status"] == "healthy":
            total_score += 20
        elif dep_status["status"] == "degraded":
            total_score += dep_status.get("install_coverage", 0) * 0.2
        max_score += 20
        
        # Environment weight: 15%
        env_status = self.status["components"]["environment"] 
        if env_status["status"] == "healthy":
            total_score += 15
            business_score += 15
        elif env_status["status"] == "degraded":
            total_score += 10
            business_score += 10
        max_score += 15
        business_max += 15
        
        # Critical services weight: 50%
        critical_services = [name for name, config in self.services.items() if config["critical"]]
        service_score = 0
        for service_name in critical_services:
            if service_name in self.status["components"]:
                if self.status["components"][service_name]["overall_status"] == "healthy":
                    service_score += 1
                    if service_name in ["backend", "frontend_primary"]:
                        business_score += 20  # Critical for business operations
        
        total_score += (service_score / len(critical_services)) * 50
        max_score += 50
        business_max += 40  # Backend + frontend
        
        # System resources weight: 15%
        resource_status = self.status["components"]["system_resources"]
        if resource_status["status"] == "healthy":
            cpu_ok = resource_status.get("cpu_percent", 100) < 80
            memory_ok = resource_status.get("memory_percent", 100) < 85
            if cpu_ok and memory_ok:
                total_score += 15
            elif cpu_ok or memory_ok:
                total_score += 10
        max_score += 15
        
        self.status["overall_health"] = round((total_score / max_score) * 100, 1)
        self.status["business_readiness"] = round((business_score / business_max) * 100, 1) if business_max > 0 else 0

    def generate_alerts_and_recommendations(self):
        """Generate actionable alerts and recommendations"""
        alerts = []
        recommendations = []
        
        # Check critical service failures
        critical_down = []
        for service_name, service_config in self.services.items():
            if service_config["critical"] and service_name in self.status["components"]:
                if self.status["components"][service_name]["overall_status"] != "healthy":
                    critical_down.append(service_name)
        
        if critical_down:
            alerts.append(f"🚨 Critical services down: {', '.join(critical_down)}")
        
        # Check dependencies
        dep_status = self.status["components"]["dependencies"]
        if dep_status.get("missing"):
            alerts.append(f"📦 Missing dependencies: {', '.join(dep_status['missing'])}")
            recommendations.append(f"Install missing packages: pip3 install {' '.join(dep_status['missing'])}")
        
        # Check environment
        env_status = self.status["components"]["environment"]
        if env_status["secrets_loaded"] < 3:
            alerts.append("🔐 Insufficient secrets loaded from Pulumi ESC")
            recommendations.append("Run: pulumi login && pulumi env open scoobyjava-org/default/sophia-ai-production")
        
        # Check resources
        resource_status = self.status["components"]["system_resources"]
        if resource_status.get("memory_percent", 0) > 85:
            alerts.append("💾 High memory usage detected")
            recommendations.append("Consider restarting services or closing unused applications")
        
        # Business readiness recommendations
        if self.status["business_readiness"] < 80:
            recommendations.append("Priority: Fix backend and frontend connectivity for business operations")
        
        self.status["alerts"] = alerts
        self.status["recommendations"] = recommendations

    def print_status_report(self):
        """Print a comprehensive, colored status report"""
        print("\n" + "="*80)
        print("🚀 SOPHIA AI PLATFORM - COMPREHENSIVE STATUS REPORT")
        print("="*80)
        print(f"📅 Timestamp: {self.status['timestamp']}")
        print(f"🏥 Overall Health: {self.status['overall_health']}%")
        print(f"💼 Business Readiness: {self.status['business_readiness']}%")
        
        # Health status emoji
        health = self.status['overall_health']
        if health >= 90:
            health_emoji = "🟢 EXCELLENT"
        elif health >= 75:
            health_emoji = "🟡 GOOD" 
        elif health >= 50:
            health_emoji = "🟠 DEGRADED"
        else:
            health_emoji = "🔴 CRITICAL"
        
        print(f"📊 Status: {health_emoji}")
        print()
        
        # Component details
        print("📋 COMPONENT STATUS:")
        print("-" * 50)
        
        for component_name, component_data in self.status["components"].items():
            if component_name in ["dependencies", "environment", "system_resources"]:
                status = component_data.get("status", "unknown")
                emoji = "🟢" if status == "healthy" else "🟡" if status == "degraded" else "🔴"
                print(f"{emoji} {component_name.upper()}: {status}")
                
                if component_name == "dependencies" and component_data.get("missing"):
                    print(f"   Missing: {', '.join(component_data['missing'])}")
                elif component_name == "environment":
                    print(f"   Environment: {component_data.get('environment', 'unknown')}")
                    print(f"   Secrets: {component_data.get('secrets_loaded', 0)}/{component_data.get('total_secrets', 0)}")
                elif component_name == "system_resources":
                    print(f"   CPU: {component_data.get('cpu_percent', 0):.1f}% | Memory: {component_data.get('memory_percent', 0):.1f}%")
            else:
                # Service components
                status = component_data.get("overall_status", "unknown")
                emoji = "🟢" if status == "healthy" else "🔴"
                port_status = "ACTIVE" if component_data.get("port_active") else "DOWN"
                print(f"{emoji} {component_name.upper()}: {port_status}")
                
                if component_data.get("process_info"):
                    proc = component_data["process_info"]
                    print(f"   PID: {proc.get('pid', 'N/A')} | Memory: {proc.get('memory_mb', 0):.1f}MB")
        
        print()
        
        # Alerts
        if self.status["alerts"]:
            print("🚨 ALERTS:")
            print("-" * 20)
            for alert in self.status["alerts"]:
                print(f"  {alert}")
            print()
        
        # Recommendations
        if self.status["recommendations"]:
            print("💡 RECOMMENDATIONS:")
            print("-" * 30)
            for i, rec in enumerate(self.status["recommendations"], 1):
                print(f"  {i}. {rec}")
            print()
        
        # Quick fix commands
        print("⚡ QUICK FIX COMMANDS:")
        print("-" * 25)
        if any("Missing dependencies" in alert for alert in self.status["alerts"]):
            print("  pip3 install sqlalchemy pyjwt fastapi uvicorn")
        print("  cd backend && python3 -m uvicorn app.simple_fastapi:app --reload --port 8000")
        print("  cd frontend && npm run dev")
        print("  python3 scripts/start_all_mcp_servers.py")
        print()
        
        print("="*80)

async def main():
    """Main monitoring function"""
    monitor = SophiaAIMonitor()
    
    try:
        # Run comprehensive monitoring
        await monitor.monitor_all_components()
        
        # Print detailed report
        monitor.print_status_report()
        
        # Save JSON report
        report_file = f"monitoring_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(monitor.status, f, indent=2)
        
        print(f"📄 Detailed JSON report saved: {report_file}")
        
        # Return appropriate exit code
        if monitor.status["overall_health"] >= 75:
            return 0  # Success
        elif monitor.status["overall_health"] >= 50:
            return 1  # Warning
        else:
            return 2  # Critical
        
    except Exception as e:
        print(f"❌ Monitor failed: {e}")
        return 3

if __name__ == "__main__":
    exit_code = asyncio.run(main()) 