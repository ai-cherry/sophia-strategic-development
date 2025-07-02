#!/usr/bin/env python3
"""
Deploy Enhanced MCP Servers for Sophia AI Platform
Consolidates and manages all MCP server deployments
"""

import os
import sys
import json
import time
import signal
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MCPServer:
    """MCP Server configuration"""
    name: str
    port: int
    script_path: str
    priority: int = 2  # 1=critical, 2=standard, 3=optional
    health_endpoint: Optional[str] = None
    dependencies: Optional[List[str]] = None
    environment: Optional[Dict[str, str]] = None


class MCPServerDeployer:
    def __init__(self):
        self.processes = {}
        self.server_configs = self._load_server_configs()
        
    def _load_server_configs(self) -> Dict[str, MCPServer]:
        """Load MCP server configurations"""
        servers = {
            # Critical AI Services (Priority 1)
            "ai_memory": MCPServer(
                name="AI Memory",
                port=9000,
                script_path="mcp-servers/ai_memory/ai_memory_mcp_server.py",
                priority=1,
                health_endpoint="/health"
            ),
            "snowflake_cortex": MCPServer(
                name="Snowflake Cortex",
                port=9021,
                script_path="mcp-servers/snowflake_cortex/production_snowflake_cortex_mcp_server.py",
                priority=1,
                health_endpoint="/health"
            ),
            
            # Business Intelligence (Priority 1)
            "hubspot": MCPServer(
                name="HubSpot",
                port=9005,
                script_path="mcp-servers/hubspot/hubspot_mcp_server.py",
                priority=1,
                health_endpoint="/health"
            ),
            "slack": MCPServer(
                name="Slack",
                port=9008,
                script_path="mcp-servers/slack/slack_mcp_server.py",
                priority=1,
                health_endpoint="/health"
            ),
            
            # Development Tools (Priority 2)
            "github": MCPServer(
                name="GitHub",
                port=9004,
                script_path="mcp-servers/github/github_mcp_server.py",
                priority=2,
                health_endpoint="/health"
            ),
            "codacy": MCPServer(
                name="Codacy",
                port=3008,
                script_path="mcp-servers/codacy/codacy_mcp_server.py",
                priority=2,
                health_endpoint="/health"
            ),
            
            # UI/UX Services (Priority 2)
            "ui_ux_agent": MCPServer(
                name="UI/UX Agent",
                port=9002,
                script_path="mcp-servers/ui_ux_agent/ui_ux_agent_mcp_server.py",
                priority=2,
                health_endpoint="/health"
            ),
            
            # Infrastructure (Priority 2)
            "lambda_labs_cli": MCPServer(
                name="Lambda Labs CLI",
                port=9020,
                script_path="mcp-servers/lambda_labs_cli/lambda_labs_cli_mcp_server.py",
                priority=2,
                health_endpoint="/health"
            ),
            
            # Project Management (Priority 2)
            "linear": MCPServer(
                name="Linear",
                port=9009,
                script_path="mcp-servers/linear/linear_mcp_server.py",
                priority=2,
                health_endpoint="/health"
            ),
            "asana": MCPServer(
                name="Asana",
                port=3006,
                script_path="mcp-servers/asana/asana_mcp_server.py",
                priority=2,
                health_endpoint="/health"
            ),
            "notion": MCPServer(
                name="Notion",
                port=3007,
                script_path="mcp-servers/notion/notion_mcp_server.py",
                priority=2,
                health_endpoint="/health"
            ),
            
            # Optional Services (Priority 3)
            "portkey_admin": MCPServer(
                name="Portkey Admin",
                port=9013,
                script_path="mcp-servers/portkey_admin/portkey_admin_mcp_server.py",
                priority=3,
                health_endpoint="/health"
            ),
        }
        
        return servers

    def check_port_availability(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"],
                capture_output=True,
                text=True
            )
            return result.returncode != 0
        except Exception:
            return True

    def health_check(self, server: MCPServer) -> bool:
        """Check if server is healthy"""
        if not server.health_endpoint:
            return True
            
        try:
            import requests
            response = requests.get(
                f"http://localhost:{server.port}{server.health_endpoint}",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def start_server(self, server_key: str, server: MCPServer) -> Tuple[bool, str]:
        """Start a single MCP server"""
        # Check if already running
        if not self.check_port_availability(server.port):
            if self.health_check(server):
                logger.info(f"✅ {server.name} already running on port {server.port}")
                return True, "Already running"
            else:
                logger.warning(f"⚠️  {server.name} port {server.port} in use but not healthy")
                return False, "Port in use"
        
        # Check if script exists
        script_path = Path(server.script_path)
        if not script_path.exists():
            logger.error(f"❌ {server.name} script not found: {script_path}")
            return False, "Script not found"
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env["ENVIRONMENT"] = "prod"
            env["PULUMI_ORG"] = "scoobyjava-org"
            
            if server.environment:
                env.update(server.environment)
            
            # Start the server
            cmd = [sys.executable, str(script_path)]
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[server_key] = process
            
            # Wait for startup
            time.sleep(3)
            
            # Check if still running
            if process.poll() is None:
                # Check health
                if self.health_check(server):
                    logger.info(f"✅ {server.name} started on port {server.port}")
                    return True, "Started successfully"
                else:
                    logger.warning(f"⚠️  {server.name} started but health check failed")
                    return True, "Started (no health check)"
            else:
                # Get error output
                _, stderr = process.communicate()
                error_msg = stderr.strip() if stderr else "Unknown error"
                logger.error(f"❌ {server.name} failed to start: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            logger.error(f"❌ {server.name} exception: {str(e)}")
            return False, str(e)

    def deploy_by_priority(self, priority: int) -> Dict[str, Tuple[bool, str]]:
        """Deploy all servers of a given priority"""
        servers = {k: v for k, v in self.server_configs.items() if v.priority == priority}
        results = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.start_server, k, v): k 
                for k, v in servers.items()
            }
            
            for future in as_completed(futures):
                server_key = futures[future]
                try:
                    success, message = future.result()
                    results[server_key] = (success, message)
                except Exception as e:
                    results[server_key] = (False, str(e))
        
        return results

    def stop_all(self):
        """Stop all running servers"""
        logger.info("\n🛑 Stopping all MCP servers...")
        
        for name, process in self.processes.items():
            if process.poll() is None:
                process.terminate()
                logger.info(f"  Stopped {name}")
        
        # Give them time to shut down
        time.sleep(2)
        
        # Force kill if needed
        for name, process in self.processes.items():
            if process.poll() is None:
                process.kill()
                logger.warning(f"  Force killed {name}")

    def generate_status_report(self, all_results: Dict[str, Tuple[bool, str]]):
        """Generate deployment status report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_servers": len(self.server_configs),
            "deployment_results": {},
            "summary": {
                "successful": 0,
                "failed": 0,
                "already_running": 0
            }
        }
        
        for server_key, (success, message) in all_results.items():
            server = self.server_configs[server_key]
            report["deployment_results"][server_key] = {
                "name": server.name,
                "port": server.port,
                "priority": server.priority,
                "success": success,
                "message": message
            }
            
            if success:
                if "Already running" in message:
                    report["summary"]["already_running"] += 1
                else:
                    report["summary"]["successful"] += 1
            else:
                report["summary"]["failed"] += 1
        
        # Save report
        with open("mcp_deployment_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("\n📊 Deployment Summary:")
        logger.info(f"Total Servers: {report['total_servers']}")
        logger.info(f"Successful: {report['summary']['successful']}")
        logger.info(f"Already Running: {report['summary']['already_running']}")
        logger.info(f"Failed: {report['summary']['failed']}")
        
        return report

    def run(self):
        """Run the deployment"""
        logger.info("🚀 Sophia AI MCP Server Deployment")
        logger.info("=" * 60)
        
        # Set up signal handler
        def signal_handler(sig, frame):
            logger.info("\n\n⚠️  Deployment interrupted!")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        all_results = {}
        
        # Deploy by priority
        for priority in [1, 2, 3]:
            logger.info(f"\n📦 Deploying Priority {priority} servers...")
            results = self.deploy_by_priority(priority)
            all_results.update(results)
            
            # Check if any critical servers failed
            if priority == 1:
                critical_failures = [k for k, (success, _) in results.items() if not success]
                if critical_failures:
                    logger.error(f"❌ Critical servers failed: {critical_failures}")
                    logger.error("Aborting deployment")
                    self.stop_all()
                    return False
        
        # Generate report
        report = self.generate_status_report(all_results)
        
        # Final status
        if report["summary"]["failed"] == 0:
            logger.info("\n✅ All MCP servers deployed successfully!")
            logger.info("\n🔗 Access URLs:")
            for key, server in self.server_configs.items():
                if all_results.get(key, (False, ""))[0]:
                    logger.info(f"  {server.name}: http://localhost:{server.port}")
            return True
        else:
            logger.warning(f"\n⚠️  {report['summary']['failed']} servers failed to deploy")
            return False


def main():
    deployer = MCPServerDeployer()
    success = deployer.run()
    
    if success:
        logger.info("\n💡 Press Ctrl+C to stop all servers")
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            deployer.stop_all()
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main() 