#!/usr/bin/env python3
"""
🚀 DISTRIBUTED SYSTEMD DEPLOYMENT SCRIPT
========================================
Production-aligned deployment for Sophia AI distributed infrastructure.

This script deploys to the ACTUAL production infrastructure:
- 5 Lambda Labs instances with direct Python processes
- systemd service management with auto-restart
- nginx load balancing on primary instance
- Direct inter-instance HTTP communication

REPLACES: All Docker/K8s deployment scripts that conflict with production.
"""

import asyncio
import asyncssh
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.production_infrastructure import (
    PRODUCTION_INFRASTRUCTURE, 
    DEPLOYMENT_CONFIG,
    SECURITY_CONFIG,
    get_all_service_endpoints,
    generate_nginx_upstream_config
)

# 🔧 LOGGING CONFIGURATION
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'deployment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DeploymentResult:
    """Result of deployment operation"""
    instance_name: str
    success: bool
    services_deployed: List[str]
    errors: List[str]
    deployment_time: float

class DistributedSystemdDeployer:
    """Production deployment to distributed systemd infrastructure"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.deployment_start = time.time()
        self.results: List[DeploymentResult] = []
        self.project_root = Path(__file__).parent.parent
        
        logger.info(f"🚀 Initializing Distributed systemd Deployment")
        logger.info(f"📍 Project Root: {self.project_root}")
        logger.info(f"🧪 Dry Run: {self.dry_run}")
    
    async def deploy_all_instances(self) -> bool:
        """Deploy to all production instances"""
        logger.info("🌐 Starting deployment to all instances...")
        
        deployment_tasks = []
        for instance_name, instance_config in PRODUCTION_INFRASTRUCTURE.instances.items():
            task = self.deploy_to_instance(instance_name, instance_config)
            deployment_tasks.append(task)
        
        # Deploy in batches to avoid overwhelming the network
        batch_size = DEPLOYMENT_CONFIG["deployment_batch_size"]
        for i in range(0, len(deployment_tasks), batch_size):
            batch = deployment_tasks[i:i + batch_size]
            results = await asyncio.gather(*batch, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"❌ Deployment batch failed: {result}")
                else:
                    self.results.append(result)
        
        # Validate all deployments
        success = await self.validate_deployment()
        
        # Generate deployment report
        self.generate_deployment_report()
        
        return success
    
    async def deploy_to_instance(self, instance_name: str, instance_config) -> DeploymentResult:
        """Deploy to a single instance"""
        start_time = time.time()
        errors = []
        deployed_services = []
        
        logger.info(f"🎯 Deploying to {instance_name} ({instance_config.ip})")
        
        try:
            async with asyncssh.connect(
                instance_config.ip, 
                username=instance_config.ssh_user,
                client_keys=[instance_config.ssh_key_path],
                known_hosts=None,
                server_host_key_algs=['ssh-rsa', 'rsa-sha2-256', 'rsa-sha2-512']
            ) as conn:
                
                # 1. Sync code to instance
                await self.sync_code_to_instance(conn, instance_name)
                
                # 2. Create systemd service files
                await self.create_systemd_services(conn, instance_config)
                
                # 3. Deploy services for this instance
                for service_name in instance_config.services:
                    try:
                        await self.deploy_service(conn, service_name, instance_config)
                        deployed_services.append(service_name)
                        logger.info(f"✅ {service_name} deployed on {instance_name}")
                    except Exception as e:
                        error_msg = f"Failed to deploy {service_name}: {e}"
                        errors.append(error_msg)
                        logger.error(f"❌ {error_msg}")
                
                # 4. Update nginx configuration on primary instance
                if instance_name == "ai_core":
                    await self.update_nginx_configuration(conn)
                
                # 5. Restart and validate services
                await self.restart_services(conn, instance_config.services)
                
        except Exception as e:
            error_msg = f"Failed to connect to {instance_name}: {e}"
            errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        deployment_time = time.time() - start_time
        success = len(errors) == 0
        
        return DeploymentResult(
            instance_name=instance_name,
            success=success,
            services_deployed=deployed_services,
            errors=errors,
            deployment_time=deployment_time
        )
    
    async def sync_code_to_instance(self, conn, instance_name: str):
        """Sync code to remote instance"""
        logger.info(f"📂 Syncing code to {instance_name}...")
        
        if self.dry_run:
            logger.info("🧪 DRY RUN: Would sync code")
            return
        
        # Create remote directory structure
        await conn.run("mkdir -p /home/ubuntu/sophia-main")
        await conn.run("mkdir -p /home/ubuntu/sophia-main/logs")
        
        # Sync critical directories
        critical_dirs = [
            "backend/",
            "mcp-servers/", 
            "config/",
            "scripts/",
            "requirements/"
        ]
        
        for dir_name in critical_dirs:
            local_path = self.project_root / dir_name
            if local_path.exists():
                # Use rsync for efficient sync
                cmd = f"rsync -av --delete {local_path}/ ubuntu@{conn.get_transport().get_extra_info('peername')[0]}:/home/ubuntu/sophia-main/{dir_name}/"
                if not self.dry_run:
                    result = await asyncio.create_subprocess_shell(cmd)
                    await result.wait()
                logger.info(f"📂 Synced {dir_name}")
    
    async def create_systemd_services(self, conn, instance_config):
        """Create systemd service files for this instance"""
        logger.info(f"🔧 Creating systemd services for {instance_config.role}...")
        
        for service_name in instance_config.services:
            service_port = instance_config.ports.get(service_name)
            if not service_port:
                logger.warning(f"⚠️ No port configured for {service_name}, skipping")
                continue
            
            service_template = self.generate_systemd_service_template(
                service_name, 
                service_port, 
                instance_config.ip
            )
            
            service_file_path = f"/etc/systemd/system/sophia-{service_name}.service"
            
            if self.dry_run:
                logger.info(f"🧪 DRY RUN: Would create {service_file_path}")
                continue
            
            # Write service file
            await conn.run(f"sudo tee {service_file_path}", input=service_template)
            logger.info(f"📝 Created systemd service: sophia-{service_name}")
        
        # Reload systemd daemon
        if not self.dry_run:
            await conn.run("sudo systemctl daemon-reload")
    
    def generate_systemd_service_template(self, service_name: str, port: int, instance_ip: str) -> str:
        """Generate systemd service file content"""
        
        # Determine service path based on service name
        if service_name == "unified_memory_service":
            service_path = "backend/services/sophia_unified_memory_service.py"
        elif service_name.endswith("_mcp"):
            service_path = f"mcp-servers/{service_name}/server.py"
        else:
            service_path = f"backend/services/{service_name}.py"
        
        template = f"""[Unit]
Description=Sophia AI {service_name.replace('_', ' ').title()} Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/sophia-main
ExecStart=/usr/bin/python3 {service_path}
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=30

# Environment Variables
Environment=ENVIRONMENT=prod
Environment=PULUMI_ORG=scoobyjava-org
Environment=INSTANCE_IP={instance_ip}
Environment=SERVICE_PORT={port}
Environment=SERVICE_NAME={service_name}
Environment=PYTHONPATH=/home/ubuntu/sophia-main

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=sophia-{service_name}

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/ubuntu/sophia-main/logs

[Install]
WantedBy=multi-user.target
"""
        return template
    
    async def deploy_service(self, conn, service_name: str, instance_config):
        """Deploy a specific service"""
        logger.info(f"🎯 Deploying {service_name}...")
        
        if self.dry_run:
            logger.info(f"🧪 DRY RUN: Would deploy {service_name}")
            return
        
        # Enable service
        await conn.run(f"sudo systemctl enable sophia-{service_name}")
        
        # Install dependencies if needed
        await self.install_service_dependencies(conn, service_name)
    
    async def install_service_dependencies(self, conn, service_name: str):
        """Install dependencies for a specific service"""
        # Install Python dependencies
        await conn.run("cd /home/ubuntu/sophia-main && pip3 install -r requirements/base.txt")
        
        # Service-specific dependencies
        if "mcp" in service_name:
            await conn.run("cd /home/ubuntu/sophia-main && pip3 install -r requirements/mcp.txt")
    
    async def update_nginx_configuration(self, conn):
        """Update nginx configuration on primary instance"""
        logger.info("🌐 Updating nginx configuration...")
        
        nginx_config = self.generate_nginx_config()
        
        if self.dry_run:
            logger.info("🧪 DRY RUN: Would update nginx configuration")
            return
        
        # Backup existing config
        await conn.run("sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup")
        
        # Write new config
        await conn.run("sudo tee /etc/nginx/sites-available/sophia-ai", input=nginx_config)
        
        # Enable site
        await conn.run("sudo ln -sf /etc/nginx/sites-available/sophia-ai /etc/nginx/sites-enabled/")
        
        # Test configuration
        result = await conn.run("sudo nginx -t")
        if result.exit_status == 0:
            await conn.run("sudo systemctl reload nginx")
            logger.info("✅ nginx configuration updated successfully")
        else:
            logger.error("❌ nginx configuration test failed")
    
    def generate_nginx_config(self) -> str:
        """Generate nginx configuration for load balancing"""
        upstream_config = generate_nginx_upstream_config()
        
        config = f"""# Sophia AI Production nginx Configuration
# Generated by deploy_distributed_systemd.py

{upstream_config}

server {{
    listen 80;
    listen [::]:80;
    server_name sophia-ai.com www.sophia-ai.com;
    
    # Frontend static files
    location / {{
        root /var/www/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }}
    
    # API routes - AI Core Services
    location /api/ai/ {{
        proxy_pass http://ai_core_services;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # API routes - Business Tools
    location /api/business/ {{
        proxy_pass http://business_tools_services;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # API routes - Data Pipeline
    location /api/data/ {{
        proxy_pass http://data_pipeline_services;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Health checks
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}
"""
        return config
    
    async def restart_services(self, conn, services: List[str]):
        """Restart all services on an instance"""
        logger.info(f"🔄 Restarting {len(services)} services...")
        
        for service_name in services:
            if self.dry_run:
                logger.info(f"🧪 DRY RUN: Would restart sophia-{service_name}")
                continue
            
            try:
                # Stop service
                await conn.run(f"sudo systemctl stop sophia-{service_name}")
                
                # Start service
                await conn.run(f"sudo systemctl start sophia-{service_name}")
                
                # Verify it's running
                result = await conn.run(f"sudo systemctl is-active sophia-{service_name}")
                if result.stdout.strip() == "active":
                    logger.info(f"✅ sophia-{service_name} is active")
                else:
                    logger.error(f"❌ sophia-{service_name} failed to start")
                    
            except Exception as e:
                logger.error(f"❌ Failed to restart sophia-{service_name}: {e}")
    
    async def validate_deployment(self) -> bool:
        """Validate that all services are running correctly"""
        logger.info("🔍 Validating deployment...")
        
        all_endpoints = get_all_service_endpoints()
        successful_checks = 0
        total_checks = len(all_endpoints)
        
        for service_name, endpoint in all_endpoints.items():
            try:
                # Simple HTTP health check
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{endpoint}/health", timeout=5) as response:
                        if response.status == 200:
                            successful_checks += 1
                            logger.info(f"✅ {service_name} health check passed")
                        else:
                            logger.error(f"❌ {service_name} health check failed: {response.status}")
            except Exception as e:
                logger.error(f"❌ {service_name} health check failed: {e}")
        
        success_rate = (successful_checks / total_checks) * 100
        logger.info(f"📊 Health check success rate: {success_rate:.1f}% ({successful_checks}/{total_checks})")
        
        return success_rate >= 80  # Require 80% success rate
    
    def generate_deployment_report(self):
        """Generate comprehensive deployment report"""
        total_time = time.time() - self.deployment_start
        successful_deployments = sum(1 for result in self.results if result.success)
        total_deployments = len(self.results)
        
        report = {
            "deployment_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_time_seconds": round(total_time, 2),
                "successful_deployments": successful_deployments,
                "total_deployments": total_deployments,
                "success_rate": round((successful_deployments / total_deployments) * 100, 1) if total_deployments > 0 else 0,
                "dry_run": self.dry_run
            },
            "instance_results": [
                {
                    "instance_name": result.instance_name,
                    "success": result.success,
                    "services_deployed": result.services_deployed,
                    "errors": result.errors,
                    "deployment_time": round(result.deployment_time, 2)
                }
                for result in self.results
            ],
            "infrastructure_config": {
                "total_instances": len(PRODUCTION_INFRASTRUCTURE.instances),
                "nginx_primary": PRODUCTION_INFRASTRUCTURE.nginx_primary,
                "port_ranges": PRODUCTION_INFRASTRUCTURE.port_ranges
            }
        }
        
        # Save report
        report_file = f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📋 Deployment report saved: {report_file}")
        
        # Print summary
        print("\n" + "="*50)
        print("🚀 DISTRIBUTED SYSTEMD DEPLOYMENT COMPLETE")
        print("="*50)
        print(f"⏱️  Total Time: {total_time:.1f}s")
        print(f"✅ Success Rate: {report['deployment_summary']['success_rate']}%")
        print(f"📊 Instances: {successful_deployments}/{total_deployments} successful")
        print(f"📋 Report: {report_file}")
        
        if not self.dry_run and successful_deployments == total_deployments:
            print("🎉 ALL DEPLOYMENTS SUCCESSFUL!")
        elif self.dry_run:
            print("🧪 DRY RUN COMPLETED - No actual changes made")
        else:
            print("⚠️  Some deployments failed - check logs for details")
        print("="*50)

async def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Sophia AI to distributed systemd infrastructure")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without making changes")
    parser.add_argument("--instance", help="Deploy to specific instance only")
    parser.add_argument("--validate-only", action="store_true", help="Only validate current deployment")
    
    args = parser.parse_args()
    
    deployer = DistributedSystemdDeployer(dry_run=args.dry_run)
    
    if args.validate_only:
        success = await deployer.validate_deployment()
        sys.exit(0 if success else 1)
    
    if args.instance:
        if args.instance not in PRODUCTION_INFRASTRUCTURE.instances:
            logger.error(f"❌ Unknown instance: {args.instance}")
            sys.exit(1)
        
        instance_config = PRODUCTION_INFRASTRUCTURE.instances[args.instance]
        result = await deployer.deploy_to_instance(args.instance, instance_config)
        deployer.results = [result]
        deployer.generate_deployment_report()
        sys.exit(0 if result.success else 1)
    
    # Deploy to all instances
    success = await deployer.deploy_all_instances()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 