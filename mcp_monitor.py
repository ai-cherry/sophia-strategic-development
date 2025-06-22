#!/usr/bin/env python3
"""
Sophia AI MCP Server Monitor
Comprehensive monitoring, health checking, and auto-restart system for MCP servers.
"""

import asyncio
import json
import logging
import subprocess
import time
import signal
import sys
from datetime import datetime
from typing import Dict, List, Optional
import requests
import psutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServerMonitor:
    def __init__(self):
        self.services = {
            "backend_api": {
                "name": "Sophia Backend API",
                "script": "simple_backend_api.py",
                "port": 8000,
                "health_endpoint": "/health",
                "process": None,
                "pid": None,
                "status": "stopped",
                "restart_count": 0,
                "last_check": None
            },
            "mcp_servers": {
                "name": "Sophia MCP Servers",
                "script": "simple_mcp_server.py", 
                "port": 8092,  # Base port, serves 8092-8095
                "health_endpoint": "/health",
                "process": None,
                "pid": None,
                "status": "stopped",
                "restart_count": 0,
                "last_check": None
            }
        }
        self.monitoring = True
        self.check_interval = 10  # seconds
        
    def find_running_processes(self):
        """Find any already running services by process name."""
        for service_key, service in self.services.items():
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if service['script'] in cmdline and 'python' in cmdline:
                        service['pid'] = proc.info['pid']
                        service['status'] = 'running'
                        logger.info(f"✅ Found running {service['name']} (PID: {proc.info['pid']})")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
    
    async def check_health(self, service_key: str) -> bool:
        """Check if a service is healthy via HTTP health check."""
        service = self.services[service_key]
        
        if service_key == "mcp_servers":
            # Check all MCP server ports
            ports = [8092, 8093, 8094, 8095]
            healthy_count = 0
            for port in ports:
                try:
                    response = requests.get(f"http://localhost:{port}/health", timeout=5)
                    if response.status_code == 200:
                        healthy_count += 1
                except:
                    pass
            
            is_healthy = healthy_count >= 3  # At least 3/4 servers healthy
            service['last_check'] = datetime.now()
            
            if is_healthy:
                service['status'] = 'healthy'
                return True
            else:
                service['status'] = f'unhealthy ({healthy_count}/4 servers)'
                return False
        
        else:
            # Single service health check
            try:
                response = requests.get(f"http://localhost:{service['port']}{service['health_endpoint']}", timeout=5)
                service['last_check'] = datetime.now()
                
                if response.status_code == 200:
                    service['status'] = 'healthy'
                    return True
                else:
                    service['status'] = f'unhealthy (HTTP {response.status_code})'
                    return False
            except Exception as e:
                service['status'] = f'unreachable ({str(e)[:50]})'
                service['last_check'] = datetime.now()
                return False
    
    def start_service(self, service_key: str) -> bool:
        """Start a service."""
        service = self.services[service_key]
        
        try:
            logger.info(f"🚀 Starting {service['name']}...")
            
            # Start the service
            process = subprocess.Popen(
                [sys.executable, service['script']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd='.'
            )
            
            service['process'] = process
            service['pid'] = process.pid
            service['status'] = 'starting'
            
            # Wait a moment for startup
            time.sleep(3)
            
            # Verify it's actually running
            if process.poll() is None:  # Still running
                logger.info(f"✅ {service['name']} started successfully (PID: {process.pid})")
                return True
            else:
                logger.error(f"❌ {service['name']} failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start {service['name']}: {e}")
            return False
    
    def stop_service(self, service_key: str):
        """Stop a service."""
        service = self.services[service_key]
        
        if service['pid']:
            try:
                # Try graceful shutdown first
                proc = psutil.Process(service['pid'])
                proc.terminate()
                proc.wait(timeout=10)
                logger.info(f"🛑 {service['name']} stopped gracefully")
            except psutil.TimeoutExpired:
                # Force kill if needed
                proc.kill()
                logger.info(f"🛑 {service['name']} force stopped")
            except psutil.NoSuchProcess:
                logger.info(f"🛑 {service['name']} already stopped")
            
            service['pid'] = None
            service['process'] = None
            service['status'] = 'stopped'
    
    def restart_service(self, service_key: str):
        """Restart a service."""
        service = self.services[service_key]
        logger.info(f"🔄 Restarting {service['name']}...")
        
        self.stop_service(service_key)
        time.sleep(2)
        
        if self.start_service(service_key):
            service['restart_count'] += 1
            logger.info(f"✅ {service['name']} restarted (restart #{service['restart_count']})")
        else:
            logger.error(f"❌ Failed to restart {service['name']}")
    
    async def monitor_loop(self):
        """Main monitoring loop."""
        logger.info("🔍 Starting MCP Server Monitor...")
        
        # Find any already running processes
        self.find_running_processes()
        
        # Start services that aren't running
        for service_key, service in self.services.items():
            if service['status'] == 'stopped':
                self.start_service(service_key)
        
        # Wait for services to fully start
        await asyncio.sleep(5)
        
        # Main monitoring loop
        while self.monitoring:
            try:
                logger.info("🔍 Checking service health...")
                
                for service_key, service in self.services.items():
                    if service['pid']:
                        # Check if process is still alive
                        try:
                            proc = psutil.Process(service['pid'])
                            if not proc.is_running():
                                logger.warning(f"⚠️  {service['name']} process died")
                                self.restart_service(service_key)
                                continue
                        except psutil.NoSuchProcess:
                            logger.warning(f"⚠️  {service['name']} process not found")
                            self.restart_service(service_key)
                            continue
                        
                        # Check health endpoint
                        is_healthy = await self.check_health(service_key)
                        if not is_healthy:
                            logger.warning(f"⚠️  {service['name']} health check failed")
                            if service['restart_count'] < 3:  # Max 3 restarts
                                self.restart_service(service_key)
                            else:
                                logger.error(f"❌ {service['name']} max restarts exceeded")
                
                # Print status summary
                self.print_status()
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitor interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitor error: {e}")
                await asyncio.sleep(5)
    
    def print_status(self):
        """Print current status of all services."""
        print("\n" + "="*80)
        print(f"📊 SOPHIA AI MCP MONITOR STATUS - {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)
        
        for service_key, service in self.services.items():
            status_icon = "✅" if service['status'] in ['healthy', 'running'] else "❌"
            last_check = service['last_check'].strftime('%H:%M:%S') if service['last_check'] else 'Never'
            
            print(f"{status_icon} {service['name']:<25} | Status: {service['status']:<20} | PID: {service['pid'] or 'None':<8} | Restarts: {service['restart_count']:<3} | Last Check: {last_check}")
        
        print("="*80)
        
        # Quick health summary
        healthy_services = sum(1 for s in self.services.values() if s['status'] in ['healthy', 'running'])
        total_services = len(self.services)
        print(f"🎯 Services: {healthy_services}/{total_services} healthy | Next check in {self.check_interval}s")
        print()
    
    def stop_all(self):
        """Stop all services and monitoring."""
        logger.info("🛑 Stopping all services...")
        self.monitoring = False
        
        for service_key in self.services:
            self.stop_service(service_key)
        
        logger.info("✅ All services stopped")
    
    async def test_integration(self):
        """Test MCP server integration functionality."""
        logger.info("🧪 Testing MCP server integration...")
        
        tests = [
            ("Backend API Health", "http://localhost:8000/health"),
            ("Backend API Agents", "http://localhost:8000/api/v1/agents/status"),
            ("Backend API MCP Status", "http://localhost:8000/api/v1/mcp/servers"),
            ("MCP Server 8092", "http://localhost:8092/health"),
            ("MCP Server 8093", "http://localhost:8093/health"),
            ("MCP Server 8094", "http://localhost:8094/health"),
            ("MCP Server 8095", "http://localhost:8095/health"),
        ]
        
        results = []
        for test_name, url in tests:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    results.append((test_name, "✅ PASS", response.json().get('status', 'OK')))
                else:
                    results.append((test_name, "❌ FAIL", f"HTTP {response.status_code}"))
            except Exception as e:
                results.append((test_name, "❌ FAIL", str(e)[:50]))
        
        print("\n" + "="*80)
        print("🧪 MCP INTEGRATION TEST RESULTS")
        print("="*80)
        for test_name, status, details in results:
            print(f"{status} {test_name:<25} | {details}")
        print("="*80)
        
        passed = sum(1 for _, status, _ in results if "PASS" in status)
        total = len(results)
        print(f"🎯 Test Results: {passed}/{total} tests passed")
        print()
        
        return passed == total


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    global monitor
    if monitor:
        monitor.stop_all()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    monitor = MCPServerMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run tests only
        asyncio.run(monitor.test_integration())
    else:
        # Run monitoring
        try:
            asyncio.run(monitor.monitor_loop())
        except KeyboardInterrupt:
            logger.info("🛑 Monitor stopped by user")
        finally:
            monitor.stop_all() 