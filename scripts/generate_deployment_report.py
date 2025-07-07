#!/usr/bin/env python3
"""
Deployment Report Generator for Sophia AI Platform
Creates comprehensive reports of deployment status and metrics
"""

import argparse
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional


class DeploymentReporter:
    """Generate comprehensive deployment reports"""
    
    def __init__(self, host: str, environment: str):
        self.host = host
        self.environment = environment
        self.report_data = {
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "host": host,
                "environment": environment,
                "report_version": "1.0"
            },
            "infrastructure": {},
            "services": {},
            "mcp_servers": {},
            "performance": {},
            "security": {},
            "summary": {}
        }
    
    def run_ssh_command(self, command: str) -> tuple[bool, str]:
        """Run command on remote host via SSH"""
        try:
            cmd = [
                "ssh", "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=10",
                f"root@{self.host}", command
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)
    
    def collect_infrastructure_info(self):
        """Collect infrastructure information"""
        print("📊 Collecting infrastructure information...")
        
        # Docker Swarm info
        success, output = self.run_ssh_command("docker info --format json")
        if success:
            try:
                docker_info = json.loads(output)
                self.report_data["infrastructure"]["docker"] = {
                    "version": docker_info.get("ServerVersion", "unknown"),
                    "swarm_mode": docker_info.get("Swarm", {}).get("LocalNodeState", "unknown"),
                    "nodes": docker_info.get("Swarm", {}).get("Nodes", 0),
                    "managers": docker_info.get("Swarm", {}).get("Managers", 0)
                }
            except json.JSONDecodeError:
                self.report_data["infrastructure"]["docker"] = {"error": "Failed to parse Docker info"}
        
        # System resources
        success, output = self.run_ssh_command("free -h | grep Mem")
        if success:
            parts = output.split()
            if len(parts) >= 4:
                self.report_data["infrastructure"]["memory"] = {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[3] if len(parts) > 3 else "unknown"
                }
        
        # Disk usage
        success, output = self.run_ssh_command("df -h / | tail -1")
        if success:
            parts = output.split()
            if len(parts) >= 5:
                self.report_data["infrastructure"]["disk"] = {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "usage_percent": parts[4]
                }
        
        # CPU info
        success, output = self.run_ssh_command("nproc")
        if success:
            self.report_data["infrastructure"]["cpu_cores"] = int(output.strip())
    
    def collect_service_info(self):
        """Collect Docker service information"""
        print("📊 Collecting service information...")
        
        success, output = self.run_ssh_command("docker service ls --format json")
        if success:
            services = []
            for line in output.split('\n'):
                if line.strip():
                    try:
                        service = json.loads(line)
                        services.append(service)
                    except json.JSONDecodeError:
                        continue
            
            self.report_data["services"]["total_count"] = len(services)
            self.report_data["services"]["services"] = services
            
            # Count running services
            running_count = 0
            for service in services:
                replicas = service.get("Replicas", "0/0")
                if "/" in replicas:
                    current, desired = replicas.split("/")
                    if current == desired and current != "0":
                        running_count += 1
            
            self.report_data["services"]["running_count"] = running_count
            self.report_data["services"]["health_percentage"] = (
                (running_count / len(services)) * 100 if services else 0
            )
    
    def collect_mcp_server_info(self):
        """Collect MCP server specific information"""
        print("📊 Collecting MCP server information...")
        
        mcp_servers = [
            "ai-memory", "codacy", "anthropic-mcp", "mcp-inspector",
            "github-agent", "pulumi-agent", "docker-agent", "vercel-agent",
            "snowflake-agent", "lambda-labs-agent", "estuary-flow-agent",
            "openai-agent", "anthropic-agent", "slack-agent", "linear-agent",
            "hubspot-agent", "gong-agent", "microsoft-playwright",
            "figma-context", "snowflake-cortex-official", "portkey-admin",
            "openrouter-search", "isaacwasserman-snowflake",
            "davidamom-snowflake", "dynamike-snowflake",
            "mem0-server", "cortex-aisql", "webfetch-server", "v0dev-server"
        ]
        
        mcp_status = {}
        running_mcp = 0
        
        for server in mcp_servers:
            success, output = self.run_ssh_command(
                f"docker service ps sophia-ai_{server} --format json --no-trunc | head -1"
            )
            
            if success and output.strip():
                try:
                    task_info = json.loads(output)
                    status = task_info.get("CurrentState", "unknown")
                    mcp_status[server] = {
                        "status": status,
                        "running": "Running" in status
                    }
                    if "Running" in status:
                        running_mcp += 1
                except json.JSONDecodeError:
                    mcp_status[server] = {"status": "unknown", "running": False}
            else:
                mcp_status[server] = {"status": "not_found", "running": False}
        
        self.report_data["mcp_servers"]["servers"] = mcp_status
        self.report_data["mcp_servers"]["total_count"] = len(mcp_servers)
        self.report_data["mcp_servers"]["running_count"] = running_mcp
        self.report_data["mcp_servers"]["health_percentage"] = (
            (running_mcp / len(mcp_servers)) * 100
        )
    
    def collect_performance_metrics(self):
        """Collect performance metrics"""
        print("📊 Collecting performance metrics...")
        
        # Load average
        success, output = self.run_ssh_command("uptime")
        if success and "load average:" in output:
            load_part = output.split("load average:")[1].strip()
            loads = [float(x.strip()) for x in load_part.split(",")]
            self.report_data["performance"]["load_average"] = {
                "1min": loads[0] if len(loads) > 0 else 0,
                "5min": loads[1] if len(loads) > 1 else 0,
                "15min": loads[2] if len(loads) > 2 else 0
            }
        
        # Container stats
        success, output = self.run_ssh_command("docker stats --no-stream --format json")
        if success:
            container_stats = []
            for line in output.split('\n'):
                if line.strip():
                    try:
                        stats = json.loads(line)
                        container_stats.append({
                            "name": stats.get("Name", "unknown"),
                            "cpu_percent": stats.get("CPUPerc", "0%"),
                            "memory_usage": stats.get("MemUsage", "0B / 0B"),
                            "memory_percent": stats.get("MemPerc", "0%")
                        })
                    except json.JSONDecodeError:
                        continue
            
            self.report_data["performance"]["containers"] = container_stats
    
    def collect_security_info(self):
        """Collect security information"""
        print("📊 Collecting security information...")
        
        # Docker secrets count
        success, output = self.run_ssh_command("docker secret ls --format json")
        if success:
            secrets = []
            for line in output.split('\n'):
                if line.strip():
                    try:
                        secret = json.loads(line)
                        secrets.append(secret.get("Name", "unknown"))
                    except json.JSONDecodeError:
                        continue
            
            self.report_data["security"]["secrets_count"] = len(secrets)
            self.report_data["security"]["secrets_configured"] = len(secrets) > 10
        
        # Network security
        success, output = self.run_ssh_command("docker network ls --format json")
        if success:
            networks = []
            for line in output.split('\n'):
                if line.strip():
                    try:
                        network = json.loads(line)
                        networks.append(network.get("Name", "unknown"))
                    except json.JSONDecodeError:
                        continue
            
            self.report_data["security"]["networks"] = networks
            self.report_data["security"]["isolated_networks"] = any(
                "sophia" in net for net in networks
            )
    
    def generate_summary(self):
        """Generate deployment summary"""
        print("📊 Generating deployment summary...")
        
        # Overall health score
        health_components = []
        
        if "services" in self.report_data and "health_percentage" in self.report_data["services"]:
            health_components.append(self.report_data["services"]["health_percentage"])
        
        if "mcp_servers" in self.report_data and "health_percentage" in self.report_data["mcp_servers"]:
            health_components.append(self.report_data["mcp_servers"]["health_percentage"])
        
        overall_health = sum(health_components) / len(health_components) if health_components else 0
        
        # Deployment status
        if overall_health >= 90:
            status = "excellent"
        elif overall_health >= 75:
            status = "good"
        elif overall_health >= 50:
            status = "degraded"
        else:
            status = "failed"
        
        self.report_data["summary"] = {
            "overall_health_percentage": round(overall_health, 1),
            "deployment_status": status,
            "total_services": self.report_data.get("services", {}).get("total_count", 0),
            "running_services": self.report_data.get("services", {}).get("running_count", 0),
            "total_mcp_servers": self.report_data.get("mcp_servers", {}).get("total_count", 0),
            "running_mcp_servers": self.report_data.get("mcp_servers", {}).get("running_count", 0),
            "secrets_configured": self.report_data.get("security", {}).get("secrets_configured", False),
            "isolated_networks": self.report_data.get("security", {}).get("isolated_networks", False)
        }
        
        # Recommendations
        recommendations = []
        
        if overall_health < 90:
            recommendations.append("Investigate failed services and restart if necessary")
        
        if self.report_data.get("mcp_servers", {}).get("running_count", 0) < 20:
            recommendations.append("Check MCP server deployment and configuration")
        
        if not self.report_data.get("security", {}).get("secrets_configured", False):
            recommendations.append("Verify Docker secrets are properly configured")
        
        self.report_data["summary"]["recommendations"] = recommendations
    
    def generate_report(self, output_file: str):
        """Generate complete deployment report"""
        print("🚀 Generating Sophia AI Deployment Report")
        print(f"🎯 Target: {self.host} ({self.environment})")
        print("=" * 60)
        
        try:
            self.collect_infrastructure_info()
            self.collect_service_info()
            self.collect_mcp_server_info()
            self.collect_performance_metrics()
            self.collect_security_info()
            self.generate_summary()
            
            # Save report
            with open(output_file, 'w') as f:
                json.dump(self.report_data, f, indent=2)
            
            print(f"📊 Report generated: {output_file}")
            
            # Print summary
            summary = self.report_data["summary"]
            print("\n" + "=" * 60)
            print("📊 DEPLOYMENT SUMMARY")
            print("=" * 60)
            print(f"🎯 Overall Health: {summary['overall_health_percentage']}%")
            print(f"📊 Status: {summary['deployment_status'].upper()}")
            print(f"🔧 Services: {summary['running_services']}/{summary['total_services']} running")
            print(f"🤖 MCP Servers: {summary['running_mcp_servers']}/{summary['total_mcp_servers']} running")
            print(f"🔐 Secrets: {'✅' if summary['secrets_configured'] else '❌'} Configured")
            print(f"🌐 Networks: {'✅' if summary['isolated_networks'] else '❌'} Isolated")
            
            if summary.get("recommendations"):
                print("\n🔍 RECOMMENDATIONS:")
                for i, rec in enumerate(summary["recommendations"], 1):
                    print(f"  {i}. {rec}")
            
            return summary["deployment_status"] in ["excellent", "good"]
            
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
            # Create minimal error report
            error_report = {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "host": self.host,
                "environment": self.environment
            }
            with open(output_file, 'w') as f:
                json.dump(error_report, f, indent=2)
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Generate Sophia AI deployment report"
    )
    parser.add_argument(
        "--host", required=True,
        help="Lambda Labs host IP"
    )
    parser.add_argument(
        "--environment", required=True,
        help="Target environment (production/staging)"
    )
    parser.add_argument(
        "--output", default="deployment-report.json",
        help="Output file for report"
    )
    
    args = parser.parse_args()
    
    reporter = DeploymentReporter(args.host, args.environment)
    success = reporter.generate_report(args.output)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main()) 