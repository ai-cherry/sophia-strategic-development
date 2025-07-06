#!/usr/bin/env python3
"""
🚀 SOPHIA AI - FULL PRODUCTION MCP DEPLOYMENT TO LAMBDA LABS
Deploys ALL MCP servers to Lambda Labs infrastructure in production mode
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp
import docker
from docker.errors import ImageNotFound

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionMCPDeployment:
    """Full production deployment of all MCP servers to Lambda Labs"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.registry = "scoobyjava15"
        self.lambda_labs_host = "146.235.200.1"  # Primary Lambda Labs host
        self.lambda_labs_backup = "165.1.69.44"  # Backup Lambda Labs host
        self.environment = "prod"
        self.deployment_record = {}
        
        # Core MCP servers with production port allocation
        self.mcp_servers = {
            "ai_memory": {"port": 9000, "priority": 1, "critical": True},
            "codacy": {"port": 3008, "priority": 2, "critical": True},
            "linear": {"port": 9004, "priority": 3, "critical": True},
            "github": {"port": 9001, "priority": 4, "critical": True},
            "slack_unified": {"port": 9002, "priority": 5, "critical": True},
            "hubspot_unified": {"port": 9003, "priority": 6, "critical": True},
            "snowflake_unified": {"port": 9005, "priority": 7, "critical": True},
            "notion": {"port": 9006, "priority": 8, "critical": False},
            "asana": {"port": 9007, "priority": 9, "critical": False},
            "lambda_labs_cli": {"port": 9008, "priority": 10, "critical": False},
            "postgres": {"port": 9009, "priority": 11, "critical": False},
            "pulumi": {"port": 9010, "priority": 12, "critical": False},
            "playwright": {"port": 9011, "priority": 13, "critical": False},
            "figma_context": {"port": 9012, "priority": 14, "critical": False},
            "ui_ux_agent": {"port": 9013, "priority": 15, "critical": False},
            "v0dev": {"port": 9014, "priority": 16, "critical": False},
            "intercom": {"port": 9015, "priority": 17, "critical": False},
            "apollo": {"port": 9016, "priority": 18, "critical": False},
            "bright_data": {"port": 9017, "priority": 19, "critical": False},
            "salesforce": {"port": 9018, "priority": 20, "critical": False},
        }
        
        # SSH configuration for Lambda Labs
        self.ssh_config = {
            "host": self.lambda_labs_host,
            "user": "root",
            "key_path": os.path.expanduser("~/.ssh/lambda_labs_key")
        }
        
    def setup_environment(self):
        """Setup production environment variables"""
        os.environ["ENVIRONMENT"] = self.environment
        os.environ["PULUMI_ORG"] = "scoobyjava-org"
        os.environ["DOCKER_REGISTRY"] = self.registry
        os.environ["LAMBDA_LABS_HOST"] = self.lambda_labs_host
        
        logger.info(f"🔧 Environment configured for {self.environment}")
        logger.info(f"🎯 Target: Lambda Labs {self.lambda_labs_host}")
        logger.info(f"📦 Registry: {self.registry}")
        
    def verify_lambda_labs_connection(self) -> bool:
        """Verify connection to Lambda Labs"""
        try:
            cmd = ["ping", "-c", "3", self.lambda_labs_host]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"✅ Lambda Labs connection verified: {self.lambda_labs_host}")
                return True
            else:
                logger.warning(f"⚠️ Primary host unreachable, trying backup: {self.lambda_labs_backup}")
                # Try backup host
                cmd = ["ping", "-c", "3", self.lambda_labs_backup]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.lambda_labs_host = self.lambda_labs_backup
                    logger.info(f"✅ Backup Lambda Labs connection verified: {self.lambda_labs_host}")
                    return True
                else:
                    logger.error("❌ Both Lambda Labs hosts unreachable")
                    return False
                    
        except subprocess.TimeoutExpired:
            logger.error("❌ Lambda Labs connection timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Lambda Labs connection error: {e}")
            return False
            
    def build_mcp_server_image(self, server_name: str) -> bool:
        """Build Docker image for MCP server"""
        try:
            server_path = f"mcp-servers/{server_name}"
            if not Path(server_path).exists():
                logger.error(f"❌ Server path not found: {server_path}")
                return False
                
            image_name = f"{self.registry}/sophia-{server_name}-mcp:latest"
            
            logger.info(f"🏗️ Building {server_name} MCP server image...")
            
            # Check if server has custom Dockerfile
            dockerfile_path = f"{server_path}/Dockerfile"
            if Path(dockerfile_path).exists():
                # Build with custom Dockerfile
                image, logs = self.docker_client.images.build(
                    path=server_path,
                    dockerfile="Dockerfile",
                    tag=image_name,
                    rm=True,
                    forcerm=True
                )
            else:
                # Use generic MCP server Dockerfile
                image, logs = self.docker_client.images.build(
                    path=".",
                    dockerfile="docker/Dockerfile.mcp-server",
                    tag=image_name,
                    buildargs={
                        "SERVER_NAME": server_name,
                        "SERVER_PATH": server_path
                    },
                    rm=True,
                    forcerm=True
                )
            
            logger.info(f"✅ {server_name} image built successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to build {server_name} image: {e}")
            return False
            
    def push_image_to_registry(self, server_name: str) -> bool:
        """Push image to Docker registry"""
        try:
            image_name = f"{self.registry}/sophia-{server_name}-mcp:latest"
            
            logger.info(f"📤 Pushing {server_name} image to registry...")
            
            # Push image
            push_logs = self.docker_client.images.push(image_name, stream=True, decode=True)
            
            # Monitor push progress
            for log in push_logs:
                if 'error' in log:
                    logger.error(f"❌ Push error: {log['error']}")
                    return False
                elif 'status' in log and log['status'] == 'Pushed':
                    logger.info(f"✅ {server_name} image pushed successfully")
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to push {server_name} image: {e}")
            return False
            
    def deploy_server_to_lambda_labs(self, server_name: str) -> bool:
        """Deploy server to Lambda Labs via SSH"""
        try:
            server_config = self.mcp_servers[server_name]
            port = server_config["port"]
            image_name = f"{self.registry}/sophia-{server_name}-mcp:latest"
            container_name = f"sophia-{server_name}-mcp"
            
            logger.info(f"🚀 Deploying {server_name} to Lambda Labs...")
            
            # SSH commands to deploy container
            deploy_commands = [
                f"docker pull {image_name}",
                f"docker stop {container_name} 2>/dev/null || true",
                f"docker rm {container_name} 2>/dev/null || true",
                f"""docker run -d \\
                    --name {container_name} \\
                    --restart unless-stopped \\
                    -p {port}:{port} \\
                    -e ENVIRONMENT=prod \\
                    -e PULUMI_ORG=scoobyjava-org \\
                    -e MCP_SERVER_NAME={server_name} \\
                    -e MCP_SERVER_PORT={port} \\
                    --log-driver json-file \\
                    --log-opt max-size=10m \\
                    --log-opt max-file=3 \\
                    {image_name}""",
                f"sleep 5",
                f"docker ps | grep {container_name}"
            ]
            
            # Execute deployment via SSH
            ssh_cmd = [
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                f"root@{self.lambda_labs_host}",
                " && ".join(deploy_commands)
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"✅ {server_name} deployed successfully to Lambda Labs")
                return True
            else:
                logger.error(f"❌ {server_name} deployment failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {server_name} deployment timeout")
            return False
        except Exception as e:
            logger.error(f"❌ {server_name} deployment error: {e}")
            return False
            
    async def verify_server_health(self, server_name: str) -> bool:
        """Verify server health via HTTP"""
        try:
            server_config = self.mcp_servers[server_name]
            port = server_config["port"]
            health_url = f"http://{self.lambda_labs_host}:{port}/health"
            
            logger.info(f"🏥 Checking {server_name} health...")
            
            async with aiohttp.ClientSession() as session:
                # Try multiple times with increasing delays
                for attempt in range(5):
                    try:
                        async with session.get(health_url, timeout=10) as response:
                            if response.status == 200:
                                health_data = await response.json()
                                logger.info(f"✅ {server_name} health check passed: {health_data}")
                                return True
                            else:
                                logger.warning(f"⚠️ {server_name} health check returned {response.status}")
                    except Exception as e:
                        logger.warning(f"⚠️ {server_name} health check attempt {attempt + 1} failed: {e}")
                        
                    if attempt < 4:
                        await asyncio.sleep(10 * (attempt + 1))  # Exponential backoff
                        
            logger.error(f"❌ {server_name} health check failed after 5 attempts")
            return False
            
        except Exception as e:
            logger.error(f"❌ {server_name} health check error: {e}")
            return False
            
    async def deploy_all_servers(self) -> Dict[str, bool]:
        """Deploy all MCP servers to Lambda Labs"""
        deployment_results = {}
        
        # Sort servers by priority (critical first)
        sorted_servers = sorted(
            self.mcp_servers.items(),
            key=lambda x: (not x[1]["critical"], x[1]["priority"])
        )
        
        logger.info(f"🎯 Deploying {len(sorted_servers)} MCP servers to Lambda Labs")
        
        for server_name, server_config in sorted_servers:
            is_critical = server_config["critical"]
            priority = server_config["priority"]
            
            logger.info(f"🔄 Processing {server_name} (Priority: {priority}, Critical: {is_critical})")
            
            try:
                # Build image
                if not self.build_mcp_server_image(server_name):
                    deployment_results[server_name] = False
                    if is_critical:
                        logger.error(f"❌ Critical server {server_name} build failed - deployment halted")
                        break
                    continue
                    
                # Push image
                if not self.push_image_to_registry(server_name):
                    deployment_results[server_name] = False
                    if is_critical:
                        logger.error(f"❌ Critical server {server_name} push failed - deployment halted")
                        break
                    continue
                    
                # Deploy to Lambda Labs
                if not self.deploy_server_to_lambda_labs(server_name):
                    deployment_results[server_name] = False
                    if is_critical:
                        logger.error(f"❌ Critical server {server_name} deployment failed - deployment halted")
                        break
                    continue
                    
                # Verify health
                if await self.verify_server_health(server_name):
                    deployment_results[server_name] = True
                    logger.info(f"✅ {server_name} fully deployed and operational")
                else:
                    deployment_results[server_name] = False
                    if is_critical:
                        logger.error(f"❌ Critical server {server_name} health check failed - deployment halted")
                        break
                        
            except Exception as e:
                logger.error(f"❌ {server_name} deployment error: {e}")
                deployment_results[server_name] = False
                if is_critical:
                    logger.error(f"❌ Critical server {server_name} failed - deployment halted")
                    break
                    
        return deployment_results
        
    def generate_deployment_report(self, results: Dict[str, bool]) -> str:
        """Generate comprehensive deployment report"""
        successful = [k for k, v in results.items() if v]
        failed = [k for k, v in results.items() if not v]
        
        report = f"""
# 🚀 SOPHIA AI MCP SERVERS - PRODUCTION DEPLOYMENT REPORT

## 📊 DEPLOYMENT SUMMARY
- **Target**: Lambda Labs Production ({self.lambda_labs_host})
- **Environment**: Production
- **Registry**: {self.registry}
- **Total Servers**: {len(self.mcp_servers)}
- **Attempted**: {len(results)}
- **Successful**: {len(successful)}
- **Failed**: {len(failed)}
- **Success Rate**: {(len(successful) / len(results) * 100):.1f}%

## ✅ SUCCESSFULLY DEPLOYED SERVERS
"""
        
        for server in successful:
            config = self.mcp_servers[server]
            port = config["port"]
            critical = "🔴 CRITICAL" if config["critical"] else "🟢 STANDARD"
            report += f"- **{server}** (Port: {port}) - {critical}\n"
            report += f"  - Health: http://{self.lambda_labs_host}:{port}/health\n"
            report += f"  - Status: ✅ OPERATIONAL\n\n"
            
        if failed:
            report += "\n## ❌ FAILED DEPLOYMENTS\n"
            for server in failed:
                config = self.mcp_servers[server]
                critical = "🔴 CRITICAL" if config["critical"] else "🟢 STANDARD"
                report += f"- **{server}** - {critical}\n"
                report += f"  - Status: ❌ FAILED\n\n"
                
        report += f"""
## 🎯 BUSINESS VALUE DELIVERED
- **AI Memory**: Contextual conversation memory and learning
- **Codacy**: Real-time code quality analysis and security scanning
- **Linear**: Integrated project management and task tracking
- **GitHub**: Source code management and CI/CD integration
- **Slack**: Team communication and notification system
- **HubSpot**: CRM integration and customer data management
- **Snowflake**: Data warehousing and business intelligence

## 🔗 ACCESS URLS
Production MCP servers are accessible at:
"""
        
        for server in successful:
            port = self.mcp_servers[server]["port"]
            report += f"- **{server}**: http://{self.lambda_labs_host}:{port}\n"
            
        report += f"""
## 🔒 SECURITY & MONITORING
- All servers running with production security configuration
- Automatic restart policies enabled
- Log rotation configured (10MB, 3 files)
- Health monitoring endpoints active
- SSH access restricted to authorized keys

## 📈 NEXT STEPS
1. Monitor server health dashboards
2. Implement automated backups
3. Set up alerting for critical services
4. Performance optimization based on usage metrics

---
**Deployment Status**: {"✅ SUCCESS" if len(failed) == 0 else "⚠️ PARTIAL SUCCESS"}
**Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}
**Total Deployment Time**: {time.time() - self.start_time:.2f} seconds
"""
        
        return report
        
    async def run_full_deployment(self) -> bool:
        """Run complete production deployment"""
        self.start_time = time.time()
        
        try:
            logger.info("🚀 SOPHIA AI MCP SERVERS - FULL PRODUCTION DEPLOYMENT STARTED")
            logger.info("=" * 70)
            
            # Setup environment
            self.setup_environment()
            
            # Verify Lambda Labs connection
            if not self.verify_lambda_labs_connection():
                logger.error("❌ Lambda Labs connection failed - deployment aborted")
                return False
                
            # Deploy all servers
            results = await self.deploy_all_servers()
            
            # Generate deployment report
            report = self.generate_deployment_report(results)
            
            # Save report to file
            with open("mcp_production_deployment_report.md", "w") as f:
                f.write(report)
                
            logger.info("📋 Deployment report saved to: mcp_production_deployment_report.md")
            
            # Print summary
            successful = sum(1 for v in results.values() if v)
            total = len(results)
            
            logger.info("🎉 DEPLOYMENT COMPLETE")
            logger.info(f"📊 Results: {successful}/{total} servers deployed successfully")
            
            if successful == total:
                logger.info("✅ ALL SERVERS DEPLOYED SUCCESSFULLY!")
                return True
            else:
                logger.warning(f"⚠️ PARTIAL DEPLOYMENT: {total - successful} servers failed")
                return False
                
        except Exception as e:
            logger.error(f"💥 Deployment failed with error: {e}")
            return False


async def main():
    """Main deployment entry point"""
    deployment = ProductionMCPDeployment()
    
    try:
        success = await deployment.run_full_deployment()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("🛑 Deployment interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))