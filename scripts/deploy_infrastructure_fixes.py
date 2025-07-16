#!/usr/bin/env python3
"""
Deploy Infrastructure Fixes to Lambda Labs Instances
Automatically deploys all fixes from the infrastructure issue resolution to production

This script will:
1. Deploy fixed Qdrant import configurations
2. Update systemd service ports across instances
3. Deploy service discovery configuration
4. Update nginx load balancer configuration
5. Validate deployment success

Usage: python scripts/deploy_infrastructure_fixes.py [--instance=all|core|orchestrator|pipeline|dev|production]
"""

import asyncio
import json
from pathlib import Path
from typing import Dict
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InfrastructureDeployer:
    """Deploys infrastructure fixes to Lambda Labs instances"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.ssh_key = Path.home() / ".ssh" / "lambda_private_key"
        
        # Instance configuration (from deployment report)
        self.instances = {
            "core": {
                "name": "sophia-ai-core",
                "ip": "192.222.58.232",
                "gpu": "GH200",
                "user": "ubuntu",
                "services": ["vector_search_mcp", "real_time_chat_mcp"]
            },
            "orchestrator": {
                "name": "sophia-mcp-orchestrator",
                "ip": "104.171.202.117", 
                "gpu": "A6000",
                "user": "ubuntu",
                "services": ["gong_mcp", "hubspot_mcp", "linear_mcp", "asana_mcp"]
            },
            "pipeline": {
                "name": "sophia-data-pipeline",
                "ip": "104.171.202.134",
                "gpu": "A100",
                "user": "ubuntu", 
                "services": ["github_mcp", "notion_mcp", "slack_mcp", "postgres_mcp"]
            },
            "dev": {
                "name": "sophia-development",
                "ip": "155.248.194.183",
                "gpu": "A10",
                "user": "ubuntu",
                "services": ["filesystem_mcp", "brave_search_mcp", "everything_mcp"]
            },
            "production": {
                "name": "sophia-production-instance",
                "ip": "104.171.202.103",
                "gpu": "RTX6000",
                "user": "ubuntu",
                "services": ["legacy_support_mcp"]
            }
        }
        
        self.deployment_results = {
            "timestamp": datetime.now().isoformat(),
            "deployments": {},
            "errors": [],
            "summary": {}
        }

    async def deploy_all_instances(self):
        """Deploy fixes to all Lambda Labs instances"""
        logger.info("🚀 Starting infrastructure fix deployment to all instances")
        
        # Deploy to all instances in parallel
        deployment_tasks = []
        for instance_id, instance_config in self.instances.items():
            task = self.deploy_to_instance(instance_id, instance_config)
            deployment_tasks.append(task)
        
        await asyncio.gather(*deployment_tasks, return_exceptions=True)
        
        # Deploy nginx configuration to primary instance
        await self.deploy_nginx_configuration()
        
        # Validate deployment
        await self.validate_deployment()
        
        # Generate deployment report
        await self.generate_deployment_report()

    async def deploy_to_instance(self, instance_id: str, instance_config: Dict):
        """Deploy fixes to a specific instance"""
        logger.info(f"🔧 Deploying to {instance_config['name']} ({instance_config['ip']})")
        
        try:
            # 1. Sync repository
            await self._sync_repository(instance_config)
            
            # 2. Update Qdrant imports
            await self._fix_qdrant_imports(instance_config)
            
            # 3. Update service ports
            await self._update_service_ports(instance_config)
            
            # 4. Deploy service discovery
            await self._deploy_service_discovery(instance_config)
            
            # 5. Restart MCP services
            await self._restart_mcp_services(instance_config)
            
            # 6. Validate services
            await self._validate_instance_services(instance_config)
            
            self.deployment_results["deployments"][instance_id] = {
                "status": "success",
                "instance": instance_config["name"],
                "ip": instance_config["ip"],
                "services_deployed": len(instance_config["services"])
            }
            
            logger.info(f"✅ Successfully deployed to {instance_config['name']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy to {instance_config['name']}: {e}")
            self.deployment_results["deployments"][instance_id] = {
                "status": "failed",
                "instance": instance_config["name"],
                "error": str(e)
            }
            self.deployment_results["errors"].append(f"{instance_config['name']}: {e}")

    async def _sync_repository(self, instance_config: Dict):
        """Sync repository code to instance"""
        logger.info(f"   📦 Syncing repository to {instance_config['name']}")
        
        # Use rsync to sync the repository
        cmd = [
            "rsync", "-avz", "--delete",
            "--exclude=.git",
            "--exclude=__pycache__", 
            "--exclude=.venv",
            "--exclude=node_modules",
            "-e", f"ssh -i {self.ssh_key}",
            f"{self.root_dir}/",
            f"{instance_config['user']}@{instance_config['ip']}:~/sophia-main/"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Repository sync failed: {stderr.decode()}")

    async def _fix_qdrant_imports(self, instance_config: Dict):
        """Fix Qdrant imports on remote instance"""
        logger.info(f"   🔧 Fixing Qdrant imports on {instance_config['name']}")
        
        # Run the Qdrant import fix script remotely
        fix_script = """
# Fix Qdrant imports in all Python files
find ~/sophia-main -name "*.py" -type f -exec sed -i 's/QDRANT_client/qdrant_client/g' {} +
find ~/sophia-main -name "*.py" -type f -exec sed -i 's/from QDRANT_client import/from qdrant_client import/g' {} +
find ~/sophia-main -name "*.py" -type f -exec sed -i 's/import QDRANT_client/import qdrant_client/g' {} +
echo "✅ Qdrant imports fixed"
"""
        
        await self._run_remote_command(instance_config, fix_script)

    async def _update_service_ports(self, instance_config: Dict):
        """Update service ports on remote instance"""
        logger.info(f"   🔧 Updating service ports on {instance_config['name']}")
        
        # Get port mappings
        port_updates = {
            "ai_memory_mcp": {"old_port": 8001, "new_port": 8101},
            "ai_memory": {"old_port": 9000, "new_port": 9001}
        }
        
        update_script = "#!/bin/bash\n"
        update_script += "# Update systemd service ports\n"
        
        for service, port_info in port_updates.items():
            update_script += f"""
if [ -f /etc/systemd/system/sophia-{service}.service ]; then
    sudo sed -i 's/--port {port_info['old_port']}/--port {port_info['new_port']}/g' /etc/systemd/system/sophia-{service}.service
    echo "✅ Updated {service} port to {port_info['new_port']}"
fi
"""
        
        update_script += """
# Reload systemd daemon
sudo systemctl daemon-reload
echo "✅ Systemd daemon reloaded"
"""
        
        await self._run_remote_command(instance_config, update_script)

    async def _deploy_service_discovery(self, instance_config: Dict):
        """Deploy service discovery configuration"""
        logger.info(f"   🔧 Deploying service discovery to {instance_config['name']}")
        
        # Copy service registry to instance
        scp_cmd = [
            "scp", "-i", str(self.ssh_key),
            str(self.root_dir / "config" / "service_registry.json"),
            f"{instance_config['user']}@{instance_config['ip']}:~/sophia-main/config/"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *scp_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()

    async def _restart_mcp_services(self, instance_config: Dict):
        """Restart MCP services on instance"""
        logger.info(f"   🔄 Restarting MCP services on {instance_config['name']}")
        
        restart_script = "#!/bin/bash\n"
        restart_script += "# Restart all Sophia AI MCP services\n"
        
        for service in instance_config["services"]:
            restart_script += f"""
if systemctl is-active --quiet sophia-{service}.service; then
    sudo systemctl restart sophia-{service}.service
    echo "✅ Restarted sophia-{service}.service"
else
    echo "⚠️ sophia-{service}.service not found or not active"
fi
"""
        
        restart_script += """
# Wait for services to start
sleep 5
echo "✅ All services restarted"
"""
        
        await self._run_remote_command(instance_config, restart_script)

    async def _validate_instance_services(self, instance_config: Dict):
        """Validate services are running on instance"""
        logger.info(f"   ✅ Validating services on {instance_config['name']}")
        
        validate_script = """
# Check service status
echo "=== Service Status ==="
for service in $(systemctl list-units --type=service --state=active | grep sophia- | awk '{print $1}'); do
    echo "Service: $service - $(systemctl is-active $service)"
done

# Check health endpoints
echo "=== Health Endpoints ==="
for port in 8001 8002 8101 8110 8111 8112 8113 8210 8211 8212 8213 8310 8311 8312 8410; do
    if curl -s -f http://localhost:$port/health >/dev/null 2>&1; then
        echo "Port $port: ✅ Healthy"
    else
        echo "Port $port: ❌ Not responding"
    fi
done
"""
        
        await self._run_remote_command(instance_config, validate_script)

    async def deploy_nginx_configuration(self):
        """Deploy updated nginx configuration to primary instance"""
        logger.info("🔧 Deploying nginx configuration to primary instance")
        
        primary_instance = self.instances["core"]
        
        # Copy nginx configuration
        nginx_config = self.root_dir / "config" / "nginx_updated.conf"
        if nginx_config.exists():
            scp_cmd = [
                "scp", "-i", str(self.ssh_key),
                str(nginx_config),
                f"{primary_instance['user']}@{primary_instance['ip']}:~/nginx_updated.conf"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *scp_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            # Update nginx configuration
            nginx_update_script = """
# Backup current nginx configuration
sudo cp /etc/nginx/sites-available/sophia-mcp /etc/nginx/sites-available/sophia-mcp.backup

# Update nginx configuration
sudo cp ~/nginx_updated.conf /etc/nginx/sites-available/sophia-mcp

# Test nginx configuration
if sudo nginx -t; then
    sudo systemctl reload nginx
    echo "✅ nginx configuration updated and reloaded"
else
    echo "❌ nginx configuration test failed"
    sudo cp /etc/nginx/sites-available/sophia-mcp.backup /etc/nginx/sites-available/sophia-mcp
fi
"""
            
            await self._run_remote_command(primary_instance, nginx_update_script)

    async def validate_deployment(self):
        """Validate the overall deployment"""
        logger.info("🔍 Validating overall deployment")
        
        # Test service discovery
        validation_results = {
            "service_discovery": False,
            "qdrant_connectivity": False,
            "inter_service_communication": 0,
            "nginx_load_balancer": False
        }
        
        try:
            # Test service discovery locally
            service_registry = self.root_dir / "config" / "service_registry.json"
            if service_registry.exists():
                registry_data = json.loads(service_registry.read_text())
                if len(registry_data.get("services", {})) >= 14:
                    validation_results["service_discovery"] = True
                    logger.info("   ✅ Service discovery configuration valid")
            
            # Test nginx load balancer
            primary_instance = self.instances["core"]
            nginx_test = f"""
curl -s -f http://{primary_instance['ip']}/health >/dev/null 2>&1
echo $?
"""
            result = await self._run_remote_command(primary_instance, nginx_test, capture_output=True)
            if result and "0" in result:
                validation_results["nginx_load_balancer"] = True
                logger.info("   ✅ nginx load balancer responding")
            
        except Exception as e:
            logger.warning(f"   ⚠️ Validation error: {e}")
        
        self.deployment_results["validation"] = validation_results

    async def _run_remote_command(self, instance_config: Dict, command: str, capture_output: bool = False):
        """Run a command on a remote instance"""
        ssh_cmd = [
            "ssh", "-i", str(self.ssh_key),
            "-o", "StrictHostKeyChecking=no",
            f"{instance_config['user']}@{instance_config['ip']}",
            command
        ]
        
        if capture_output:
            process = await asyncio.create_subprocess_exec(
                *ssh_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return stdout.decode() if stdout else None
        else:
            process = await asyncio.create_subprocess_exec(*ssh_cmd)
            await process.wait()

    async def generate_deployment_report(self):
        """Generate comprehensive deployment report"""
        successful_deployments = sum(1 for d in self.deployment_results["deployments"].values() if d["status"] == "success")
        total_deployments = len(self.deployment_results["deployments"])
        
        self.deployment_results["summary"] = {
            "total_instances": total_deployments,
            "successful_deployments": successful_deployments,
            "failed_deployments": total_deployments - successful_deployments,
            "success_rate": (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0,
            "next_steps": [
                "Monitor service health using health_monitor.py",
                "Test inter-service communication with validate_service_communication.py",
                "Deploy SSL certificates using deploy_letsencrypt_ssl.sh on primary instance",
                "Run infrastructure_validation.py for comprehensive testing"
            ]
        }
        
        # Save deployment report
        report_file = self.root_dir / "infrastructure_deployment_report.json"
        report_file.write_text(json.dumps(self.deployment_results, indent=2))
        
        logger.info("✅ Infrastructure deployment report generated")
        logger.info(f"   Successful deployments: {successful_deployments}/{total_deployments}")
        logger.info(f"   Success rate: {self.deployment_results['summary']['success_rate']:.1f}%")
        logger.info(f"   Report saved: {report_file}")

async def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy infrastructure fixes to Lambda Labs instances")
    parser.add_argument("--instance", choices=["all", "core", "orchestrator", "pipeline", "dev", "production"], 
                       default="all", help="Specific instance to deploy to")
    
    args = parser.parse_args()
    
    deployer = InfrastructureDeployer()
    
    if args.instance == "all":
        await deployer.deploy_all_instances()
    else:
        instance_config = deployer.instances[args.instance]
        await deployer.deploy_to_instance(args.instance, instance_config)

if __name__ == "__main__":
    asyncio.run(main()) 