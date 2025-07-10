#!/usr/bin/env python3
"""
🚨 ONE-TIME SCRIPT - DELETE AFTER USE
Purpose: Deploy MCP servers to K3s cluster on Lambda Labs
Created: July 2025

This script handles the deployment of MCP servers to our K3s cluster.
Once the servers are deployed via CI/CD, this script should be removed.

Unified K3s MCP Server Deployment Script
Orchestrates the deployment of MCP servers to K3s on Lambda Labs

Date: July 10, 2025
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

import click


class K3sMCPDeployer:
    """Orchestrates K3s and MCP server deployment"""

    def __init__(self, instance_ips: list[str], dry_run: bool = False):
        self.instance_ips = instance_ips
        self.dry_run = dry_run
        self.k3s_master = instance_ips[0] if instance_ips else None
        self.k3s_workers = instance_ips[1:] if len(instance_ips) > 1 else []
        self.base_path = Path(__file__).parent.parent
        self.manifests_path = self.base_path / "k3s-manifests"
        self.mcp_config_path = self.base_path / "config" / "mcp_servers_migrated.json"

    def load_mcp_config(self) -> dict[str, Any]:
        """Load MCP server configuration"""
        with open(self.mcp_config_path) as f:
            return json.load(f)

    def run_command(self, cmd: str, host: Optional[str] = None) -> bool:
        """Run a command locally or on a remote host"""
        if host:
            cmd = f"ssh -o StrictHostKeyChecking=no root@{host} '{cmd}'"

        if self.dry_run:
            print(f"[DRY RUN] Would execute: {cmd}")
            return True

        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return True

    def install_k3s(self):
        """Install K3s on all instances"""
        print("\n🚀 Installing K3s...")

        # Install K3s on master
        print(f"\n📦 Installing K3s on master ({self.k3s_master})...")
        install_script = self.base_path / "scripts" / "install_k3s_lambda_labs.sh"

        # Copy and run install script
        self.run_command(f"scp {install_script} root@{self.k3s_master}:/tmp/")
        self.run_command("chmod +x /tmp/install_k3s_lambda_labs.sh", self.k3s_master)
        self.run_command("/tmp/install_k3s_lambda_labs.sh master", self.k3s_master)

        # Get join token
        if not self.dry_run:
            result = subprocess.run(
                f"ssh root@{self.k3s_master} 'cat /var/lib/rancher/k3s/server/node-token'",
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            join_token = result.stdout.strip()
        else:
            join_token = "DRY_RUN_TOKEN"

        # Install K3s on workers
        for worker_ip in self.k3s_workers:
            print(f"\n📦 Installing K3s on worker ({worker_ip})...")
            self.run_command(f"scp {install_script} root@{worker_ip}:/tmp/")
            self.run_command("chmod +x /tmp/install_k3s_lambda_labs.sh", worker_ip)
            self.run_command(
                f"/tmp/install_k3s_lambda_labs.sh worker {self.k3s_master} {join_token}",
                worker_ip,
            )

    def setup_kubeconfig(self):
        """Setup local kubeconfig for accessing the cluster"""
        print("\n🔧 Setting up kubeconfig...")

        # Get kubeconfig from master
        self.run_command(
            f"scp root@{self.k3s_master}:/etc/rancher/k3s/k3s.yaml ~/.kube/config-sophia-k3s"
        )

        # Update server address
        if not self.dry_run and self.k3s_master:
            with open(os.path.expanduser("~/.kube/config-sophia-k3s")) as f:
                config = f.read()

            config = config.replace("127.0.0.1", self.k3s_master)

            with open(os.path.expanduser("~/.kube/config-sophia-k3s"), "w") as f:
                f.write(config)

        # Set KUBECONFIG
        os.environ["KUBECONFIG"] = os.path.expanduser("~/.kube/config-sophia-k3s")
        print(f"✅ KUBECONFIG set to: {os.environ['KUBECONFIG']}")

    def create_namespace(self):
        """Create sophia-mcp namespace"""
        print("\n📁 Creating namespace...")
        self.run_command(
            "kubectl create namespace sophia-mcp --dry-run=client -o yaml | kubectl apply -f -"
        )

    def create_secrets(self):
        """Create K8s secrets from Pulumi ESC"""
        print("\n🔐 Creating secrets...")

        # This would normally pull from Pulumi ESC
        # For now, create a template secret
        secret_yaml = """
apiVersion: v1
kind: Secret
metadata:
  name: mcp-common-secrets
  namespace: sophia-mcp
type: Opaque
stringData:
  PULUMI_ORG: "scoobyjava-org"
  ENVIRONMENT: "prod"
"""
        if not self.dry_run:
            with open("/tmp/mcp-secrets.yaml", "w") as f:
                f.write(secret_yaml)
            self.run_command("kubectl apply -f /tmp/mcp-secrets.yaml")

    def convert_compose_files(self):
        """Convert Docker Compose files to K3s manifests"""
        print("\n🔄 Converting Docker Compose to K3s manifests...")

        compose_files = [
            "deployment/docker-compose-mcp-orchestrator.yml",
            "deployment/docker-compose-ai-core.yml",
        ]

        convert_script = self.base_path / "scripts" / "convert_compose_to_k3s.py"

        for compose_file in compose_files:
            if (self.base_path / compose_file).exists():
                print(f"Converting {compose_file}...")
                self.run_command(
                    f"python {convert_script} {self.base_path / compose_file} "
                    f"-o {self.manifests_path}"
                )

    def deploy_mcp_servers(self):
        """Deploy MCP servers to K3s"""
        print("\n🚀 Deploying MCP servers...")

        # Load MCP configuration
        config = self.load_mcp_config()

        # Deploy only implemented servers
        for server_name, server_info in config["servers"].items():
            if server_info["status"] == "implemented":
                manifest_path = (
                    self.manifests_path / f"mcp-{server_name.replace('_', '-')}.yaml"
                )

                if manifest_path.exists():
                    print(
                        f"\n📦 Deploying {server_info['name']} (port {server_info['port']})..."
                    )
                    self.run_command(f"kubectl apply -f {manifest_path}")
                else:
                    print(f"⚠️  No manifest found for {server_name}")

    def verify_deployment(self):
        """Verify all deployments are running"""
        print("\n✅ Verifying deployments...")

        if not self.dry_run:
            # Wait a bit for pods to start
            print("Waiting for pods to start...")
            import time

            time.sleep(10)

        # Check pod status
        self.run_command("kubectl get pods -n sophia-mcp")
        self.run_command("kubectl get svc -n sophia-mcp")
        self.run_command("kubectl get hpa -n sophia-mcp")

    def setup_ingress(self):
        """Setup ingress for MCP servers"""
        print("\n🌐 Setting up ingress...")

        ingress_yaml = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-servers-ingress
  namespace: sophia-mcp
  annotations:
    kubernetes.io/ingress.class: traefik
spec:
  rules:
  - host: mcp.sophia-ai.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mcp-gateway
            port:
              number: 8080
"""
        if not self.dry_run:
            with open("/tmp/mcp-ingress.yaml", "w") as f:
                f.write(ingress_yaml)
            self.run_command("kubectl apply -f /tmp/mcp-ingress.yaml")

    def display_summary(self):
        """Display deployment summary"""
        config = self.load_mcp_config()

        print("\n" + "=" * 80)
        print("🎉 K3s MCP Deployment Summary")
        print("=" * 80)
        print(f"K3s Master: {self.k3s_master}")
        print(
            f"K3s Workers: {', '.join(self.k3s_workers) if self.k3s_workers else 'None'}"
        )
        print(
            f"\nMCP Servers Deployed: {config['statistics']['implemented']}/{config['statistics']['total_servers']}"
        )
        print(f"Progress: {config['statistics']['progress_percentage']}%")
        print(f"Total Tools Available: {config['statistics']['total_tools']}")

        print("\n📊 Deployed Servers:")
        for server_name, server_info in config["servers"].items():
            if server_info["status"] == "implemented":
                print(
                    f"  - {server_info['name']} (port {server_info['port']}): {server_info['description']}"
                )

        print("\n🚀 Next Steps:")
        print("1. Access K3s dashboard: kubectl proxy")
        print("2. Monitor pods: kubectl get pods -n sophia-mcp -w")
        print("3. Check logs: kubectl logs -n sophia-mcp <pod-name>")
        print("4. Access MCP Gateway: http://mcp.sophia-ai.local")

    async def run(self):
        """Run the complete deployment process"""
        print("🚀 Starting K3s MCP Server Deployment")
        print(f"Target instances: {', '.join(self.instance_ips)}")
        print(f"Dry run: {self.dry_run}")

        # Step 1: Install K3s
        self.install_k3s()

        # Step 2: Setup kubeconfig
        self.setup_kubeconfig()

        # Step 3: Create namespace
        self.create_namespace()

        # Step 4: Create secrets
        self.create_secrets()

        # Step 5: Convert compose files
        self.convert_compose_files()

        # Step 6: Deploy MCP servers
        self.deploy_mcp_servers()

        # Step 7: Setup ingress
        self.setup_ingress()

        # Step 8: Verify deployment
        self.verify_deployment()

        # Step 9: Display summary
        self.display_summary()


@click.command()
@click.option(
    "--instances",
    "-i",
    help="Comma-separated list of Lambda Labs instance IPs",
    required=True,
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without executing",
)
def main(instances: str, dry_run: bool):
    """Deploy K3s and MCP servers to Lambda Labs"""
    instance_ips = [ip.strip() for ip in instances.split(",")]

    if not instance_ips:
        print("❌ No instance IPs provided")
        sys.exit(1)

    deployer = K3sMCPDeployer(instance_ips, dry_run)
    asyncio.run(deployer.run())


if __name__ == "__main__":
    main()
