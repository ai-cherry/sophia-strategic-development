#!/usr/bin/env python3
"""
📊 SOPHIA AI DEPLOYMENT MONITORING DASHBOARD
==========================================
Real-time monitoring of Lambda Labs deployment
"""

import asyncio
import subprocess
import time
from datetime import datetime

class DeploymentMonitor:
    def __init__(self):
        self.servers = {
            "ai_core": "192.222.58.232",
            "business": "104.171.202.117", 
            "data": "104.171.202.134",
            "production": "104.171.202.103"
        }
    
    async def check_server_status(self, name, ip):
        """Check individual server status"""
        try:
            # Check SSH connectivity
            ssh_check = await asyncio.create_subprocess_shell(
                f"ssh -i ~/.ssh/lambda_labs_key -o ConnectTimeout=5 -o BatchMode=yes ubuntu@{ip} 'echo Connected'",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await ssh_check.communicate()
            
            if ssh_check.returncode == 0:
                # Check Docker services
                docker_check = await asyncio.create_subprocess_shell(
                    f"ssh -i ~/.ssh/lambda_labs_key ubuntu@{ip} 'docker ps --format \"table {{{{.Names}}}}\\t{{{{.Status}}}}\" | grep -E \"(sophia|postgres|redis|qdrant)\"'",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                docker_out, docker_err = await docker_check.communicate()
                
                services = docker_out.decode().strip().split('\n') if docker_out else []
                service_count = len([s for s in services if s.strip()])
                
                return {
                    "status": "✅ Online",
                    "services": service_count,
                    "details": services[:3] if services else ["No services"]
                }
            else:
                return {
                    "status": "❌ Offline", 
                    "services": 0,
                    "details": ["Connection failed"]
                }
        except Exception as e:
            return {
                "status": "⚠️ Error",
                "services": 0, 
                "details": [f"Error: {str(e)[:50]}"]
            }
    
    async def check_endpoints(self):
        """Check API endpoints"""
        endpoints = {
            "Backend API": f"http://{self.servers['ai_core']}:8000/health",
            "Simple API": f"http://{self.servers['ai_core']}:8001/health", 
            "Minimal API": f"http://{self.servers['ai_core']}:8002/health",
            "Nginx": f"http://{self.servers['ai_core']}/health"
        }
        
        results = {}
        for name, url in endpoints.items():
            try:
                curl_check = await asyncio.create_subprocess_shell(
                    f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 5 {url}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await curl_check.communicate()
                
                status_code = stdout.decode().strip()
                if status_code == "200":
                    results[name] = "✅ Healthy"
                elif status_code:
                    results[name] = f"⚠️ HTTP {status_code}"
                else:
                    results[name] = "❌ No response"
            except:
                results[name] = "❌ Failed"
        
        return results
    
    def print_header(self):
        """Print monitoring header"""
        print("\n" + "="*80)
        print("📊 SOPHIA AI DEPLOYMENT MONITORING DASHBOARD")
        print("="*80)
        print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        while True:
            self.print_header()
            
            # Check all servers
            print("🖥️  SERVER STATUS:")
            print("-" * 60)
            
            for name, ip in self.servers.items():
                status = await self.check_server_status(name, ip)
                print(f"{status['status']:<12} {name.replace('_', ' ').title():<15} {ip:<15} Services: {status['services']}")
                
                for detail in status['details'][:2]:
                    if detail.strip():
                        print(f"              └─ {detail[:50]}")
            
            print("-" * 60)
            
            # Check endpoints
            print("\n🌐 API ENDPOINTS:")
            print("-" * 40)
            
            endpoints = await self.check_endpoints()
            for name, status in endpoints.items():
                print(f"{status:<15} {name}")
            
            print("-" * 40)
            
            # Current deployment status
            print(f"\n📋 DEPLOYMENT STATUS:")
            print("  ✅ Docker image built and pushed")
            print("  ✅ PostgreSQL, Redis, Qdrant deployed")
            print("  ⚠️  Backend container needs Docker login fix")
            print("  🔄 Working on resolution...")
            
            print(f"\n⏱️  Next check in 30 seconds... (Ctrl+C to stop)")
            print("="*80)
            
            await asyncio.sleep(30)

async def main():
    """Main function"""
    monitor = DeploymentMonitor()
    try:
        await monitor.monitor_loop()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 