#!/usr/bin/env python3
"""
🔍 LIVE DEPLOYMENT MONITORING FOR SOPHIA AI

This script monitors the real cloud deployment status on Lambda Labs
and provides access URLs for all deployed services.

Usage:
    python scripts/monitor_live_deployment.py
    python scripts/monitor_live_deployment.py --watch
"""

import subprocess
import time
import requests
from datetime import datetime
from typing import Dict
import argparse

class SophiaAIDeploymentMonitor:
    """Monitor live deployment status for Sophia AI"""
    
    def __init__(self, watch_mode: bool = False):
        self.watch_mode = watch_mode
        
        # Lambda Labs Infrastructure
        self.lambda_labs_ips = {
            "backend_k3s": "192.222.58.232",
            "mcp_cluster": "104.171.202.117", 
            "data_pipeline": "104.171.202.134",
            "production": "104.171.202.103",
            "development": "155.248.194.183"
        }
        
        # Expected service endpoints
        self.service_endpoints = {
            "backend_api": "http://192.222.58.232:8000",
            "backend_health": "http://192.222.58.232:8000/health",
            "backend_docs": "http://192.222.58.232:8000/docs",
            "frontend": "http://104.171.202.103:3000",
            "mcp_gateway": "http://104.171.202.117:9000",
            "ai_memory": "http://104.171.202.117:9001",
            "github_mcp": "http://104.171.202.117:9003",
            "linear_mcp": "http://104.171.202.117:9004",
            "asana_mcp": "http://104.171.202.117:9006"
        }
        
    def monitor_deployment(self):
        """Monitor the complete deployment status"""
        print("🔍 SOPHIA AI LIVE DEPLOYMENT MONITORING")
        print("=" * 60)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        while True:
            self._check_infrastructure_connectivity()
            self._check_service_endpoints()
            self._check_kubernetes_status()
            self._display_access_urls()
            
            if not self.watch_mode:
                break
                
            print("\n⏱️ Next check in 30 seconds... (Ctrl+C to stop)")
            try:
                time.sleep(30)
            except KeyboardInterrupt:
                print("\n👋 Monitoring stopped by user")
                break
                
            print("\n" + "="*60)
    
    def _check_infrastructure_connectivity(self):
        """Check Lambda Labs infrastructure connectivity"""
        print("🏗️ INFRASTRUCTURE CONNECTIVITY")
        print("-" * 40)
        
        for service, ip in self.lambda_labs_ips.items():
            try:
                # Ping test
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '3000', ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    print(f"  ✅ {service:<15} ({ip}) - REACHABLE")
                else:
                    print(f"  ❌ {service:<15} ({ip}) - UNREACHABLE")
                    
            except Exception as e:
                print(f"  ⚠️ {service:<15} ({ip}) - ERROR: {e}")
        print()
    
    def _check_service_endpoints(self):
        """Check service endpoint availability"""
        print("🌐 SERVICE ENDPOINTS")
        print("-" * 40)
        
        for service, url in self.service_endpoints.items():
            try:
                response = requests.get(url, timeout=10)
                status_code = response.status_code
                
                if status_code == 200:
                    print(f"  ✅ {service:<15} - HEALTHY ({status_code})")
                elif status_code in [301, 302, 404]:
                    print(f"  ⚠️ {service:<15} - PARTIAL ({status_code})")
                else:
                    print(f"  ❌ {service:<15} - ERROR ({status_code})")
                    
            except requests.exceptions.ConnectionError:
                print(f"  ❌ {service:<15} - CONNECTION REFUSED")
            except requests.exceptions.Timeout:
                print(f"  ⏱️ {service:<15} - TIMEOUT")
            except Exception as e:
                print(f"  ⚠️ {service:<15} - ERROR: {str(e)[:30]}")
        print()
    
    def _check_kubernetes_status(self):
        """Check Kubernetes deployment status"""
        print("☸️ KUBERNETES STATUS")
        print("-" * 40)
        
        try:
            # Check kubectl connectivity
            result = subprocess.run(
                ['kubectl', 'cluster-info'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("  ✅ kubectl - CONNECTED")
                
                # Check pod status
                pod_result = subprocess.run(
                    ['kubectl', 'get', 'pods', '--all-namespaces'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if pod_result.returncode == 0:
                    lines = pod_result.stdout.strip().split('\n')
                    running_pods = sum(1 for line in lines[1:] if 'Running' in line)
                    total_pods = len(lines) - 1
                    print(f"  ✅ Pods - {running_pods}/{total_pods} RUNNING")
                else:
                    print("  ⚠️ Pods - UNABLE TO CHECK")
            else:
                print("  ❌ kubectl - NOT CONNECTED")
                
        except Exception as e:
            print(f"  ⚠️ kubectl - ERROR: {e}")
        print()
    
    def _display_access_urls(self):
        """Display access URLs for deployed services"""
        print("🔗 ACCESS URLS")
        print("-" * 40)
        
        urls = {
            "🏠 Main Dashboard": "http://104.171.202.103:3000",
            "🔧 API Documentation": "http://192.222.58.232:8000/docs", 
            "❤️ Health Check": "http://192.222.58.232:8000/health",
            "🧠 AI Memory MCP": "http://104.171.202.117:9001",
            "📋 Linear MCP": "http://104.171.202.117:9004",
            "📈 Asana MCP": "http://104.171.202.117:9006",
            "💬 MCP Gateway": "http://104.171.202.117:9000",
            "🐙 GitHub MCP": "http://104.171.202.117:9003",
        }
        
        for description, url in urls.items():
            print(f"  {description:<20} - {url}")
        
        print()
        print("💡 TIP: Copy URLs above to test the deployed services")
        
    def get_deployment_summary(self) -> Dict:
        """Get a summary of deployment status"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "infrastructure": {},
            "services": {},
            "overall_status": "unknown"
        }
        
        # Quick connectivity check
        reachable_count = 0
        for service, ip in self.lambda_labs_ips.items():
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1000', ip],
                    capture_output=True,
                    timeout=3
                )
                is_reachable = result.returncode == 0
                summary["infrastructure"][service] = {
                    "ip": ip,
                    "reachable": is_reachable
                }
                if is_reachable:
                    reachable_count += 1
            except:
                summary["infrastructure"][service] = {
                    "ip": ip,
                    "reachable": False
                }
        
        # Service endpoint check
        healthy_count = 0
        for service, url in self.service_endpoints.items():
            try:
                response = requests.get(url, timeout=5)
                is_healthy = response.status_code == 200
                summary["services"][service] = {
                    "url": url,
                    "healthy": is_healthy,
                    "status_code": response.status_code
                }
                if is_healthy:
                    healthy_count += 1
            except:
                summary["services"][service] = {
                    "url": url,
                    "healthy": False,
                    "status_code": None
                }
        
        # Overall status
        infra_health = reachable_count / len(self.lambda_labs_ips)
        service_health = healthy_count / len(self.service_endpoints)
        
        if infra_health > 0.8 and service_health > 0.6:
            summary["overall_status"] = "healthy"
        elif infra_health > 0.6 and service_health > 0.3:
            summary["overall_status"] = "partial"
        else:
            summary["overall_status"] = "unhealthy"
            
        return summary

def main():
    parser = argparse.ArgumentParser(description="Monitor Sophia AI deployment")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--summary", action="store_true", help="Show deployment summary")
    args = parser.parse_args()
    
    monitor = SophiaAIDeploymentMonitor(watch_mode=args.watch)
    
    if args.summary:
        summary = monitor.get_deployment_summary()
        print(f"📊 Deployment Status: {summary['overall_status'].upper()}")
        print(f"📊 Infrastructure: {sum(1 for s in summary['infrastructure'].values() if s['reachable'])}/{len(summary['infrastructure'])} reachable")
        print(f"📊 Services: {sum(1 for s in summary['services'].values() if s['healthy'])}/{len(summary['services'])} healthy")
    else:
        monitor.monitor_deployment()

if __name__ == "__main__":
    main() 