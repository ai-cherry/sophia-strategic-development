#!/usr/bin/env python3
"""
Comprehensive Deployment Validation for Sophia AI Platform
Validates all services, MCP servers, and infrastructure components
"""

import argparse
import json
import subprocess
import sys
import time
from typing import Dict, List, Tuple


class DeploymentValidator:
    """Validate complete Sophia AI deployment"""
    
    def __init__(self, host: str, environment: str):
        self.host = host
        self.environment = environment
        self.validation_results = []
        
    def run_ssh_command(self, command: str) -> Tuple[bool, str]:
        """Run command on remote host via SSH"""
        try:
            cmd = [
                "ssh", "-o", "StrictHostKeyChecking=no",
                f"root@{self.host}", command
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)
    
    def validate_docker_swarm(self) -> bool:
        """Validate Docker Swarm cluster"""
        print("🔍 Validating Docker Swarm cluster...")
        
        success, output = self.run_ssh_command("docker node ls")
        if success and "Ready" in output:
            print("✅ Docker Swarm cluster is healthy")
            self.validation_results.append({
                "component": "docker_swarm",
                "status": "healthy",
                "details": "Cluster operational"
            })
            return True
        else:
            print("❌ Docker Swarm cluster issues detected")
            self.validation_results.append({
                "component": "docker_swarm",
                "status": "unhealthy",
                "details": output
            })
            return False
    
    def validate_services(self) -> bool:
        """Validate all Docker services"""
        print("🔍 Validating Docker services...")
        
        success, output = self.run_ssh_command("docker service ls")
        if not success:
            print("❌ Failed to list Docker services")
            return False
        
        services = []
        healthy_count = 0
        total_count = 0
        
        for line in output.split('\n')[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[1]
                    replicas = parts[3]
                    services.append({"name": name, "replicas": replicas})
                    total_count += 1
                    
                    # Check if service is healthy (replicas match)
                    if "/" in replicas:
                        current, desired = replicas.split("/")
                        if current == desired and current != "0":
                            healthy_count += 1
                            print(f"✅ {name}: {replicas}")
                        else:
                            print(f"❌ {name}: {replicas}")
                    else:
                        print(f"⚠️ {name}: {replicas}")
        
        self.validation_results.append({
            "component": "docker_services",
            "status": "healthy" if healthy_count == total_count else "degraded",
            "details": f"{healthy_count}/{total_count} services healthy",
            "services": services
        })
        
        return healthy_count > 0
    
    def validate_mcp_servers(self) -> bool:
        """Validate MCP servers specifically"""
        print("🔍 Validating MCP servers...")
        
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
        
        healthy_mcp = 0
        
        for server in mcp_servers:
            success, output = self.run_ssh_command(
                f"docker service ps sophia-ai_{server} --format 'table {{.CurrentState}}' | grep Running | wc -l"
            )
            
            if success and output.strip() != "0":
                print(f"✅ {server}: Running")
                healthy_mcp += 1
            else:
                print(f"❌ {server}: Not running")
        
        self.validation_results.append({
            "component": "mcp_servers",
            "status": "healthy" if healthy_mcp > 20 else "degraded",
            "details": f"{healthy_mcp}/{len(mcp_servers)} MCP servers running",
            "healthy_count": healthy_mcp,
            "total_count": len(mcp_servers)
        })
        
        return healthy_mcp > 0
    
    def validate_networking(self) -> bool:
        """Validate Docker networking"""
        print("🔍 Validating Docker networking...")
        
        success, output = self.run_ssh_command("docker network ls | grep sophia")
        if success and "sophia" in output:
            print("✅ Sophia AI networks created")
            self.validation_results.append({
                "component": "networking",
                "status": "healthy",
                "details": "Networks operational"
            })
            return True
        else:
            print("❌ Sophia AI networks missing")
            self.validation_results.append({
                "component": "networking",
                "status": "unhealthy",
                "details": "Networks not found"
            })
            return False
    
    def validate_secrets(self) -> bool:
        """Validate Docker secrets"""
        print("🔍 Validating Docker secrets...")
        
        success, output = self.run_ssh_command("docker secret ls | wc -l")
        if success:
            secret_count = int(output.strip()) - 1  # Subtract header
            if secret_count > 10:  # Should have many secrets
                print(f"✅ {secret_count} Docker secrets configured")
                self.validation_results.append({
                    "component": "secrets",
                    "status": "healthy",
                    "details": f"{secret_count} secrets available"
                })
                return True
            else:
                print(f"⚠️ Only {secret_count} Docker secrets found")
                self.validation_results.append({
                    "component": "secrets",
                    "status": "degraded",
                    "details": f"Only {secret_count} secrets"
                })
                return False
        else:
            print("❌ Failed to check Docker secrets")
            return False
    
    def validate_monitoring(self) -> bool:
        """Validate monitoring stack"""
        print("🔍 Validating monitoring stack...")
        
        monitoring_services = ["prometheus", "grafana", "alertmanager"]
        healthy_monitoring = 0
        
        for service in monitoring_services:
            success, output = self.run_ssh_command(
                f"docker service ps sophia-ai_{service} --format 'table {{.CurrentState}}' | grep Running | wc -l"
            )
            
            if success and output.strip() != "0":
                print(f"✅ {service}: Running")
                healthy_monitoring += 1
            else:
                print(f"❌ {service}: Not running")
        
        self.validation_results.append({
            "component": "monitoring",
            "status": "healthy" if healthy_monitoring == len(monitoring_services) else "degraded",
            "details": f"{healthy_monitoring}/{len(monitoring_services)} monitoring services running"
        })
        
        return healthy_monitoring > 0
    
    def run_validation(self) -> bool:
        """Run complete validation suite"""
        print("🚀 Starting Sophia AI Deployment Validation")
        print(f"🎯 Target: {self.host} ({self.environment})")
        print("=" * 60)
        
        validation_checks = [
            ("Docker Swarm", self.validate_docker_swarm),
            ("Docker Services", self.validate_services),
            ("MCP Servers", self.validate_mcp_servers),
            ("Networking", self.validate_networking),
            ("Secrets", self.validate_secrets),
            ("Monitoring", self.validate_monitoring)
        ]
        
        passed_checks = 0
        total_checks = len(validation_checks)
        
        for check_name, check_func in validation_checks:
            print(f"\n🔍 {check_name} Validation:")
            try:
                if check_func():
                    passed_checks += 1
                    print(f"✅ {check_name}: PASSED")
                else:
                    print(f"❌ {check_name}: FAILED")
            except Exception as e:
                print(f"❌ {check_name}: ERROR - {e}")
                self.validation_results.append({
                    "component": check_name.lower().replace(" ", "_"),
                    "status": "error",
                    "details": str(e)
                })
        
        print("\n" + "=" * 60)
        print("🎯 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed_checks}/{total_checks}")
        print(f"❌ Failed: {total_checks - passed_checks}/{total_checks}")
        
        success_rate = (passed_checks / total_checks) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 DEPLOYMENT VALIDATION: SUCCESS")
            return True
        elif success_rate >= 50:
            print("⚠️ DEPLOYMENT VALIDATION: DEGRADED")
            return False
        else:
            print("❌ DEPLOYMENT VALIDATION: FAILED")
            return False
    
    def save_results(self, output_file: str = "validation-results.json"):
        """Save validation results to file"""
        results = {
            "timestamp": time.time(),
            "host": self.host,
            "environment": self.environment,
            "validation_results": self.validation_results
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📊 Validation results saved to {output_file}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Validate Sophia AI deployment"
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
        "--output", default="validation-results.json",
        help="Output file for results"
    )
    
    args = parser.parse_args()
    
    validator = DeploymentValidator(args.host, args.environment)
    success = validator.run_validation()
    validator.save_results(args.output)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 