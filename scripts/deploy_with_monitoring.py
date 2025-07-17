#!/usr/bin/env python3
"""
🚀 SOPHIA AI DEPLOYMENT WITH REAL-TIME MONITORING
===============================================
Comprehensive deployment script with real-time monitoring and status tracking
Date: July 16, 2025
"""

import asyncio
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ServerStatus:
    """Server status tracking"""
    name: str
    ip: str
    status: str = "pending"
    services: List[str] = None
    last_check: Optional[datetime] = None
    error_count: int = 0
    
    def __post_init__(self):
        if self.services is None:
            self.services = []

class DeploymentMonitor:
    """Comprehensive deployment monitoring system"""
    
    def __init__(self):
        self.servers = {
            "ai_core": ServerStatus("AI Core", "192.222.58.232"),
            "business": ServerStatus("Business Tools", "104.171.202.117"),
            "data": ServerStatus("Data Pipeline", "104.171.202.134"),
            "production": ServerStatus("Production Services", "104.171.202.103"),
            "dev": ServerStatus("Development", "155.248.194.183")
        }
        
        self.deployment_stages = [
            "🏗️  Building Docker Images",
            "🚀 Deploying AI Core Server",
            "💼 Deploying Business Tools",
            "📊 Deploying Data Pipeline",
            "⚙️  Deploying Production Services",
            "🌐 Building & Deploying Frontend",
            "✅ Validating Deployment",
            "📊 Setting Up Monitoring"
        ]
        
        self.current_stage = 0
        self.start_time = datetime.now()
        self.deployment_logs = []
        
    def log_status(self, message: str, level: str = "INFO"):
        """Log deployment status with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        if level == "ERROR":
            logger.error(log_entry)
        elif level == "WARNING":
            logger.warning(log_entry)
        else:
            logger.info(log_entry)
            
        self.deployment_logs.append(log_entry)
        
    def print_header(self):
        """Print deployment header"""
        print("\n" + "="*80)
        print("🚀 SOPHIA AI COMPLETE DEPLOYMENT WITH MONITORING")
        print("="*80)
        print(f"📅 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Target Infrastructure: 5 Lambda Labs Servers")
        print("📦 Services: Backend API + 15+ MCP Servers + Frontend")
        print("="*80 + "\n")
        
    def print_progress(self):
        """Print current deployment progress"""
        progress = (self.current_stage / len(self.deployment_stages)) * 100
        bar_length = 50
        filled_length = int(bar_length * self.current_stage // len(self.deployment_stages))
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\n📊 DEPLOYMENT PROGRESS: {progress:.1f}%")
        print(f"[{bar}] {self.current_stage}/{len(self.deployment_stages)}")
        
        if self.current_stage < len(self.deployment_stages):
            print(f"🔄 Current: {self.deployment_stages[self.current_stage]}")
        
        elapsed = datetime.now() - self.start_time
        print(f"⏱️  Elapsed: {elapsed.total_seconds():.0f}s")
        print()
        
    async def check_server_health(self, server: ServerStatus) -> bool:
        """Check individual server health"""
        try:
            # Check SSH connectivity
            ssh_cmd = f"ssh -i ~/.ssh/lambda_labs_key -o ConnectTimeout=10 -o BatchMode=yes ubuntu@{server.ip} 'echo OK'"
            process = await asyncio.create_subprocess_shell(
                ssh_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                server.status = "online"
                server.last_check = datetime.now()
                server.error_count = 0
                return True
            else:
                server.status = "unreachable"
                server.error_count += 1
                self.log_status(f"❌ {server.name} ({server.ip}) unreachable: {stderr.decode()}", "ERROR")
                return False
                
        except Exception as e:
            server.status = "error"
            server.error_count += 1
            self.log_status(f"❌ Error checking {server.name}: {str(e)}", "ERROR")
            return False
            
    async def check_docker_services(self, server: ServerStatus) -> List[str]:
        """Check Docker services on a server"""
        try:
            docker_cmd = f"ssh -i ~/.ssh/lambda_labs_key ubuntu@{server.ip} 'docker ps --format \"{{{{.Names}}}}\" | grep -E \"(sophia|mcp)\"'"
            process = await asyncio.create_subprocess_shell(
                docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                services = [s.strip() for s in stdout.decode().split('\n') if s.strip()]
                server.services = services
                return services
            else:
                server.services = []
                return []
                
        except Exception as e:
            self.log_status(f"❌ Error checking Docker services on {server.name}: {str(e)}", "ERROR")
            server.services = []
            return []
            
    async def check_endpoints(self) -> Dict[str, bool]:
        """Check API endpoints"""
        endpoints = {
            "frontend": f"http://{self.servers['ai_core'].ip}/",
            "backend_api": f"http://{self.servers['ai_core'].ip}/api/health",
            "mcp_vector": f"http://{self.servers['ai_core'].ip}:8000/health",
            "business_gong": f"http://{self.servers['business'].ip}:8100/health",
            "data_github": f"http://{self.servers['data'].ip}:8200/health",
            "prod_codacy": f"http://{self.servers['production'].ip}:8300/health"
        }
        
        results = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for name, url in endpoints.items():
                try:
                    async with session.get(url) as response:
                        results[name] = response.status == 200
                        if response.status == 200:
                            self.log_status(f"✅ {name} endpoint healthy")
                        else:
                            self.log_status(f"⚠️  {name} endpoint returned {response.status}", "WARNING")
                except Exception as e:
                    results[name] = False
                    self.log_status(f"❌ {name} endpoint failed: {str(e)}", "ERROR")
                    
        return results
        
    async def monitor_deployment_progress(self):
        """Monitor deployment progress in real-time"""
        while self.current_stage < len(self.deployment_stages):
            self.print_progress()
            
            # Check server health
            print("🔍 SERVER STATUS:")
            print("-" * 60)
            
            for server_key, server in self.servers.items():
                health = await self.check_server_health(server)
                services = await self.check_docker_services(server) if health else []
                
                status_icon = "✅" if health else "❌"
                service_count = len(services)
                
                print(f"{status_icon} {server.name:<20} {server.ip:<15} Services: {service_count}")
                
                if services:
                    for service in services[:3]:  # Show first 3 services
                        print(f"   └─ {service}")
                    if len(services) > 3:
                        print(f"   └─ ... and {len(services) - 3} more")
                        
            print("-" * 60)
            
            # Wait before next check
            await asyncio.sleep(30)
            
    async def run_deployment_script(self):
        """Run the main deployment script"""
        self.log_status("🚀 Starting deployment script execution")
        
        try:
            # Make deployment script executable
            subprocess.run(["chmod", "+x", "deploy_sophia_now.sh"], check=True)
            
            # Execute deployment script
            process = await asyncio.create_subprocess_shell(
                "./deploy_sophia_now.sh",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            # Monitor output in real-time
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                output = line.decode().strip()
                if output:
                    self.log_status(f"📜 {output}")
                    
                    # Update progress based on output
                    if "[STEP]" in output:
                        if "Building and pushing" in output:
                            self.current_stage = 0
                        elif "AI Core Server" in output:
                            self.current_stage = 1
                        elif "Business Tools" in output:
                            self.current_stage = 2
                        elif "Data Pipeline" in output:
                            self.current_stage = 3
                        elif "Production Services" in output:
                            self.current_stage = 4
                        elif "frontend" in output:
                            self.current_stage = 5
                        elif "Validating" in output:
                            self.current_stage = 6
                            
            await process.wait()
            
            if process.returncode == 0:
                self.current_stage = len(self.deployment_stages)
                self.log_status("✅ Deployment script completed successfully")
                return True
            else:
                self.log_status(f"❌ Deployment script failed with code {process.returncode}", "ERROR")
                return False
                
        except Exception as e:
            self.log_status(f"❌ Error running deployment script: {str(e)}", "ERROR")
            return False
            
    async def post_deployment_validation(self):
        """Run comprehensive post-deployment validation"""
        self.log_status("🔍 Running post-deployment validation")
        
        print("\n" + "="*80)
        print("🔍 POST-DEPLOYMENT VALIDATION")
        print("="*80)
        
        # Check all servers
        all_healthy = True
        total_services = 0
        
        for server_key, server in self.servers.items():
            health = await self.check_server_health(server)
            services = await self.check_docker_services(server) if health else []
            total_services += len(services)
            
            if not health:
                all_healthy = False
                
        # Check endpoints
        endpoints = await self.check_endpoints()
        healthy_endpoints = sum(endpoints.values())
        total_endpoints = len(endpoints)
        
        # Generate summary
        print("\n📊 DEPLOYMENT SUMMARY:")
        print("-" * 40)
        print(f"🖥️  Servers Online: {sum(1 for s in self.servers.values() if s.status == 'online')}/5")
        print(f"🐳 Docker Services: {total_services}")
        print(f"🌐 Healthy Endpoints: {healthy_endpoints}/{total_endpoints}")
        print(f"⏱️  Total Time: {(datetime.now() - self.start_time).total_seconds():.0f}s")
        
        if all_healthy and healthy_endpoints >= total_endpoints * 0.8:
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("✅ Sophia AI is now live and operational!")
        else:
            print("\n⚠️  DEPLOYMENT COMPLETED WITH ISSUES")
            print("🔧 Some services may need manual intervention")
            
        return all_healthy
        
    async def setup_continuous_monitoring(self):
        """Set up continuous monitoring after deployment"""
        self.log_status("📊 Setting up continuous monitoring")
        
        # Create monitoring script on AI Core server
        monitoring_script = '''#!/bin/bash
# Sophia AI Continuous Monitoring
while true; do
    echo "$(date): Health Check"
    docker ps --format "table {{.Names}}\\t{{.Status}}" | grep -E "(sophia|mcp)"
    echo "---"
    sleep 300  # Check every 5 minutes
done
'''
        
        # Deploy monitoring script
        ssh_cmd = f"""ssh -i ~/.ssh/lambda_labs_key ubuntu@{self.servers['ai_core'].ip} '
            echo "{monitoring_script}" > ~/monitor_sophia.sh
            chmod +x ~/monitor_sophia.sh
            nohup ./monitor_sophia.sh > ~/sophia_monitoring.log 2>&1 &
            echo "Monitoring started"
        '"""
        
        try:
            process = await asyncio.create_subprocess_shell(ssh_cmd)
            await process.wait()
            self.log_status("✅ Continuous monitoring setup complete")
        except Exception as e:
            self.log_status(f"⚠️  Could not setup continuous monitoring: {str(e)}", "WARNING")
            
    def print_final_summary(self):
        """Print final deployment summary"""
        duration = datetime.now() - self.start_time
        
        print("\n" + "="*80)
        print("🎉 SOPHIA AI DEPLOYMENT COMPLETED!")
        print("="*80)
        print(f"⏱️  Total Duration: {duration.total_seconds():.0f} seconds")
        print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("🌐 ACCESS URLS:")
        print(f"   Frontend: http://{self.servers['ai_core'].ip}/")
        print(f"   Backend API: http://{self.servers['ai_core'].ip}/api/")
        print(f"   Health Check: http://{self.servers['ai_core'].ip}/api/health")
        print()
        print("📊 MONITORING COMMANDS:")
        print(f"   ssh ubuntu@{self.servers['ai_core'].ip} 'docker ps'")
        print(f"   ssh ubuntu@{self.servers['ai_core'].ip} 'tail -f ~/sophia_monitoring.log'")
        print()
        print("🚀 Sophia AI is now live on Lambda Labs infrastructure!")
        print("="*80)
        
    async def deploy_and_monitor(self):
        """Main deployment and monitoring function"""
        self.print_header()
        
        try:
            # Start monitoring task
            monitor_task = asyncio.create_task(self.monitor_deployment_progress())
            
            # Run deployment
            deployment_success = await self.run_deployment_script()
            
            # Cancel monitoring task
            monitor_task.cancel()
            
            if deployment_success:
                # Run validation
                await self.post_deployment_validation()
                
                # Setup continuous monitoring
                await self.setup_continuous_monitoring()
                
                # Print final summary
                self.print_final_summary()
                
                return True
            else:
                self.log_status("❌ Deployment failed", "ERROR")
                return False
                
        except Exception as e:
            self.log_status(f"❌ Deployment error: {str(e)}", "ERROR")
            return False

async def main():
    """Main function"""
    monitor = DeploymentMonitor()
    success = await monitor.deploy_and_monitor()
    
    if success:
        print("\n✅ Deployment completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1) 