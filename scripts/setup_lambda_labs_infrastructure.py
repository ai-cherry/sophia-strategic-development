#!/usr/bin/env python3
"""
Set up Lambda Labs infrastructure for Sophia AI
This script manages Lambda Labs instances and K3s cluster configuration
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

import requests


class LambdaLabsManager:
    """Manages Lambda Labs infrastructure"""

    def __init__(self):
        self.api_key = self.get_api_key()
        self.base_url = "https://cloud.lambdalabs.com/api/v1"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def get_api_key(self):
        """Get Lambda Labs API key from environment"""
        # Try local.env first
        env_file = Path("local.env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        if key.strip() == "LAMBDA_API_KEY":
                            return value.strip()

        # Fallback to environment variable
        api_key = os.getenv("LAMBDA_API_KEY")
        if not api_key:
            print("❌ Lambda Labs API key not found")
            print("Please set LAMBDA_API_KEY in local.env or environment")
            sys.exit(1)

        return api_key

    def list_instances(self) -> list[dict[str, Any]]:
        """List all Lambda Labs instances"""
        try:
            response = requests.get(f"{self.base_url}/instances", headers=self.headers)
            response.raise_for_status()

            data = response.json()
            return data.get("data", [])

        except Exception as e:
            print(f"❌ Failed to list instances: {e}")
            return []

    def get_instance_types(self) -> dict[str, Any]:
        """Get available instance types"""
        try:
            response = requests.get(
                f"{self.base_url}/instance-types", headers=self.headers
            )
            response.raise_for_status()

            data = response.json()
            return data.get("data", {})

        except Exception as e:
            print(f"❌ Failed to get instance types: {e}")
            return {}

    def launch_instance(
        self, instance_type: str, region: str, name: str, ssh_key_names: list[str]
    ) -> Optional[str]:
        """Launch a new Lambda Labs instance"""
        try:
            payload = {
                "region_name": region,
                "instance_type_name": instance_type,
                "name": name,
                "ssh_key_names": ssh_key_names,
                "quantity": 1,
            }

            response = requests.post(
                f"{self.base_url}/instance-operations/launch",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            instance_ids = data.get("data", {}).get("instance_ids", [])

            if instance_ids:
                return instance_ids[0]

            return None

        except Exception as e:
            print(f"❌ Failed to launch instance: {e}")
            return None

    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate a Lambda Labs instance"""
        try:
            payload = {"instance_ids": [instance_id]}

            response = requests.post(
                f"{self.base_url}/instance-operations/terminate",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()

            return True

        except Exception as e:
            print(f"❌ Failed to terminate instance: {e}")
            return False

    def restart_instance(self, instance_id: str) -> bool:
        """Restart a Lambda Labs instance"""
        try:
            payload = {"instance_ids": [instance_id]}

            response = requests.post(
                f"{self.base_url}/instance-operations/restart",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()

            return True

        except Exception as e:
            print(f"❌ Failed to restart instance: {e}")
            return False

    def setup_k3s_cluster(self):
        """Set up K3s cluster on Lambda Labs instances"""
        print("\n🐋 Setting up K3s cluster...")

        instances = self.list_instances()

        if not instances:
            print("⚠️ No Lambda Labs instances found")
            print("Would you like to launch a new instance? (Manual action required)")
            return False

        # Find the primary instance (usually the first one)
        primary_instance = instances[0]
        instance_ip = primary_instance.get("ip_address")
        instance_name = primary_instance.get("name", "unnamed")
        instance_status = primary_instance.get("status", "unknown")

        print("\n📊 Primary instance:")
        print(f"  Name: {instance_name}")
        print(f"  IP: {instance_ip}")
        print(f"  Status: {instance_status}")

        if instance_status != "active":
            print(f"⚠️ Instance is not active (status: {instance_status})")
            return False

        if not instance_ip:
            print("❌ Instance IP not available")
            return False

        # Save K3s cluster configuration
        k3s_config = {
            "cluster_name": "sophia-ai-k3s",
            "control_plane_ip": instance_ip,
            "control_plane_port": 6443,
            "instance_id": primary_instance.get("id"),
            "instance_name": instance_name,
            "namespaces": ["sophia-ai-prod", "mcp-servers", "monitoring", "ingress"],
            "storage_class": "local-path",
            "registry": "scoobyjava15",
        }

        config_file = Path("k3s_cluster_config.json")
        with open(config_file, "w") as f:
            json.dump(k3s_config, f, indent=2)

        print(f"\n✅ K3s cluster configuration saved to {config_file}")

        # Generate kubectl config
        self.generate_kubectl_config(instance_ip)

        return True

    def generate_kubectl_config(self, control_plane_ip: str):
        """Generate kubectl configuration"""
        kubeconfig = f"""apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: # Will be populated after K3s installation
    server: https://{control_plane_ip}:6443
  name: lambda-labs-k3s
contexts:
- context:
    cluster: lambda-labs-k3s
    user: lambda-labs-k3s-admin
  name: lambda-labs-k3s
current-context: lambda-labs-k3s
kind: Config
preferences: {{}}
users:
- name: lambda-labs-k3s-admin
  user:
    client-certificate-data: # Will be populated after K3s installation
    client-key-data: # Will be populated after K3s installation
"""

        kubeconfig_file = Path("kubeconfig-lambda-labs.yaml")
        with open(kubeconfig_file, "w") as f:
            f.write(kubeconfig)

        print(f"✅ Kubectl config template saved to {kubeconfig_file}")
        print("   Note: Certificate data will be populated after K3s installation")

    def check_infrastructure_health(self):
        """Check health of Lambda Labs infrastructure"""
        print("\n🏥 Checking infrastructure health...")

        instances = self.list_instances()

        if not instances:
            print("❌ No instances found")
            return False

        healthy_count = 0

        for instance in instances:
            name = instance.get("name", "unnamed")
            status = instance.get("status", "unknown")
            ip = instance.get("ip_address", "no-ip")
            instance_type = instance.get("instance_type", {}).get("name", "unknown")

            if status == "active":
                healthy_count += 1
                print(f"✅ {name}: {status} ({instance_type}) - {ip}")
            else:
                print(f"⚠️ {name}: {status} ({instance_type})")

        print(
            f"\n📊 Health Summary: {healthy_count}/{len(instances)} instances healthy"
        )

        return healthy_count == len(instances)

    def optimize_costs(self):
        """Analyze and optimize Lambda Labs costs"""
        print("\n💰 Analyzing Lambda Labs costs...")

        instances = self.list_instances()
        instance_types = self.get_instance_types()

        if not instances:
            print("No instances to analyze")
            return

        total_hourly_cost = 0

        print("\n📊 Current instances:")
        for instance in instances:
            instance_type_name = instance.get("instance_type", {}).get(
                "name", "unknown"
            )

            # Find pricing info
            hourly_price = 0
            for region, types in instance_types.items():
                for type_info in types:
                    if (
                        type_info.get("instance_type", {}).get("name")
                        == instance_type_name
                    ):
                        hourly_price = type_info.get("price_cents_per_hour", 0) / 100
                        break

            total_hourly_cost += hourly_price

            print(
                f"  - {instance.get('name', 'unnamed')}: {instance_type_name} (${hourly_price:.2f}/hour)"
            )

        daily_cost = total_hourly_cost * 24
        monthly_cost = daily_cost * 30

        print("\n💸 Cost Summary:")
        print(f"  Hourly: ${total_hourly_cost:.2f}")
        print(f"  Daily: ${daily_cost:.2f}")
        print(f"  Monthly: ${monthly_cost:.2f}")

        # Cost optimization suggestions
        print("\n💡 Cost Optimization Tips:")
        print("  1. Use spot instances when available")
        print("  2. Schedule instances to stop during off-hours")
        print("  3. Right-size instances based on actual usage")
        print("  4. Use auto-scaling for variable workloads")

    def generate_deployment_scripts(self):
        """Generate deployment scripts for Lambda Labs"""
        print("\n📝 Generating deployment scripts...")

        # K3s installation script
        k3s_install_script = """#!/bin/bash
# K3s installation script for Lambda Labs

echo "🚀 Installing K3s on Lambda Labs..."

# Install K3s
curl -sfL https://get.k3s.io | sh -s - \
  --write-kubeconfig-mode 644 \
  --disable traefik \
  --node-label sophia-ai=true

# Wait for K3s to be ready
echo "⏳ Waiting for K3s to be ready..."
sleep 30

# Create namespaces
kubectl create namespace sophia-ai-prod
kubectl create namespace mcp-servers
kubectl create namespace monitoring
kubectl create namespace ingress

# Install GPU operator for Lambda Labs GPUs
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/gpu-operator/master/deployments/gpu-operator/gpu-operator.yaml

# Label nodes for GPU workloads
kubectl label nodes --all sophia-ai/gpu=true

echo "✅ K3s installation complete!"

# Export kubeconfig
echo ""
echo "To access the cluster, run:"
echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml"
"""

        with open("deploy_k3s_lambda_labs.sh", "w") as f:
            f.write(k3s_install_script)
        os.chmod("deploy_k3s_lambda_labs.sh", 0o755)

        # MCP deployment script
        mcp_deploy_script = """#!/bin/bash
# Deploy MCP servers to Lambda Labs K3s

echo "🚀 Deploying MCP servers to Lambda Labs K3s..."

# Apply Kubernetes manifests
kubectl apply -k k8s/overlays/production

# Wait for deployments
kubectl -n mcp-servers wait --for=condition=available --timeout=300s deployment --all

# Check status
kubectl -n mcp-servers get all

echo "✅ MCP deployment complete!"
"""

        with open("deploy_mcp_lambda_labs.sh", "w") as f:
            f.write(mcp_deploy_script)
        os.chmod("deploy_mcp_lambda_labs.sh", 0o755)

        print("✅ Deployment scripts generated:")
        print("  - deploy_k3s_lambda_labs.sh")
        print("  - deploy_mcp_lambda_labs.sh")


def main():
    """Main function"""
    manager = LambdaLabsManager()

    print("🚀 Lambda Labs Infrastructure Manager")
    print("=" * 50)

    # List current instances
    instances = manager.list_instances()
    print(f"\n📊 Found {len(instances)} Lambda Labs instances")

    for instance in instances:
        print(f"\n🖥️ Instance: {instance.get('name', 'unnamed')}")
        print(f"  ID: {instance.get('id')}")
        print(f"  Type: {instance.get('instance_type', {}).get('name', 'unknown')}")
        print(f"  Status: {instance.get('status', 'unknown')}")
        print(f"  IP: {instance.get('ip_address', 'no-ip')}")
        print(f"  Region: {instance.get('region', {}).get('name', 'unknown')}")

    # Set up K3s cluster
    manager.setup_k3s_cluster()

    # Check health
    manager.check_infrastructure_health()

    # Analyze costs
    manager.optimize_costs()

    # Generate deployment scripts
    manager.generate_deployment_scripts()

    print("\n✅ Lambda Labs infrastructure setup complete!")


if __name__ == "__main__":
    main()
