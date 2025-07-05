#!/usr/bin/env python3
"""
Lambda Labs Cleanup and Deployment Script for Sophia AI
Automates instance management, SSH key cleanup, and deployment
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Optional

import requests


class LambdaLabsManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://cloud.lambdalabs.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def list_instances(self) -> list[dict]:
        """List all Lambda Labs instances"""
        response = requests.get(f"{self.base_url}/instances", headers=self.headers)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            print(f"Error listing instances: {response.text}")
            return []

    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate a specific instance"""
        response = requests.delete(
            f"{self.base_url}/instances/{instance_id}", headers=self.headers
        )
        return response.status_code == 200

    def list_ssh_keys(self) -> list[dict]:
        """List all SSH keys"""
        response = requests.get(f"{self.base_url}/ssh-keys", headers=self.headers)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            print(f"Error listing SSH keys: {response.text}")
            return []

    def delete_ssh_key(self, key_name: str) -> bool:
        """Delete an SSH key"""
        response = requests.delete(
            f"{self.base_url}/ssh-keys/{key_name}", headers=self.headers
        )
        return response.status_code == 200

    def create_api_key(self, name: str) -> Optional[str]:
        """Create a new API key"""
        response = requests.post(
            f"{self.base_url}/api-keys", headers=self.headers, json={"name": name}
        )
        if response.status_code == 201:
            return response.json()["data"]["api_key"]
        else:
            print(f"Error creating API key: {response.text}")
            return None


def cleanup_instances(manager: LambdaLabsManager, dry_run: bool = True):
    """Clean up unnecessary instances"""
    print("🔍 Analyzing Lambda Labs instances...")

    instances = manager.list_instances()

    # Instances to keep
    keep_ips = {
        "104.171.202.64",  # sophia-ai-production (8x V100)
        "150.230.47.71",  # orchestra-sophia-prod
        "129.153.123.54",  # sophia-ai-production-gpu (A100)
    }

    instances_to_remove = []
    instances_to_keep = []

    for instance in instances:
        if instance["ip_address"] in keep_ips:
            instances_to_keep.append(instance)
        else:
            instances_to_remove.append(instance)

    print(f"\n✅ Instances to KEEP ({len(instances_to_keep)}):")
    for inst in instances_to_keep:
        print(f"  - {inst['name']} ({inst['instance_type']}) - {inst['ip_address']}")

    print(f"\n❌ Instances to REMOVE ({len(instances_to_remove)}):")
    for inst in instances_to_remove:
        print(f"  - {inst['name']} ({inst['instance_type']}) - {inst['ip_address']}")

    if not dry_run and instances_to_remove:
        confirm = input("\nProceed with termination? (yes/no): ")
        if confirm.lower() == "yes":
            for inst in instances_to_remove:
                print(f"Terminating {inst['name']}...")
                if manager.terminate_instance(inst["id"]):
                    print("  ✅ Terminated successfully")
                else:
                    print("  ❌ Failed to terminate")
                time.sleep(1)  # Rate limiting


def cleanup_ssh_keys(manager: LambdaLabsManager, dry_run: bool = True):
    """Clean up unnecessary SSH keys"""
    print("\n🔑 Analyzing SSH keys...")

    keys = manager.list_ssh_keys()

    # Keys to keep
    keep_keys = {
        "sophia-ai-key",
        "cherry-ai-collaboration-20250604",
        "sophia-deployment-key-20250621",
        "sophia-prod-key-2025",
    }

    keys_to_remove = []
    keys_to_keep = []

    for key in keys:
        if key["name"] in keep_keys:
            keys_to_keep.append(key)
        else:
            keys_to_remove.append(key)

    print(f"\n✅ SSH Keys to KEEP ({len(keys_to_keep)}):")
    for key in keys_to_keep:
        print(f"  - {key['name']}")

    print(f"\n❌ SSH Keys to REMOVE ({len(keys_to_remove)}):")
    for key in keys_to_remove:
        print(f"  - {key['name']}")

    if not dry_run and keys_to_remove:
        confirm = input("\nProceed with SSH key deletion? (yes/no): ")
        if confirm.lower() == "yes":
            for key in keys_to_remove:
                print(f"Deleting {key['name']}...")
                if manager.delete_ssh_key(key["name"]):
                    print("  ✅ Deleted successfully")
                else:
                    print("  ❌ Failed to delete")


def create_new_api_keys(manager: LambdaLabsManager, dry_run: bool = True):
    """Create properly named API keys"""
    print("\n🔐 Creating new API keys...")

    new_keys = ["sophia-ai-prod", "sophia-ai-dev", "sophia-ai-pulumi"]

    if dry_run:
        print("Would create the following API keys:")
        for key_name in new_keys:
            print(f"  - {key_name}")
    else:
        confirm = input("\nCreate new API keys? (yes/no): ")
        if confirm.lower() == "yes":
            created_keys = {}
            for key_name in new_keys:
                print(f"Creating {key_name}...")
                api_key = manager.create_api_key(key_name)
                if api_key:
                    created_keys[key_name] = api_key
                    print("  ✅ Created successfully")
                else:
                    print("  ❌ Failed to create")

            # Save keys securely
            if created_keys:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"lambda_labs_api_keys_{timestamp}.json"
                with open(filename, "w") as f:
                    json.dump(created_keys, f, indent=2)
                print(f"\n📄 API keys saved to: {filename}")
                print(
                    "⚠️  Store this file securely and delete after saving to Pulumi ESC!"
                )


def deploy_to_instances(ssh_key_path: str, github_token: str):
    """Deploy Sophia AI to Lambda Labs instances"""
    print("\n🚀 Deploying to Lambda Labs instances...")

    instances = {
        "main": {"ip": "104.171.202.64", "role": "Main Platform (8x V100)"},
        "mcp": {"ip": "150.230.47.71", "role": "MCP Servers"},
        "ai": {"ip": "129.153.123.54", "role": "AI Services (A100)"},
    }

    for name, config in instances.items():
        print(f"\n📦 Deploying to {config['role']} ({config['ip']})...")

        # Test SSH connectivity
        test_cmd = f"ssh -i {ssh_key_path} -o ConnectTimeout=10 ubuntu@{config['ip']} 'echo Connected'"
        result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"  ❌ Cannot connect to {config['ip']}")
            print(f"  Error: {result.stderr}")
            continue

        print("  ✅ Connected successfully")

        # Run deployment script
        deploy_cmd = f"./scripts/lambda_labs_deployment.sh {config['ip']} {name}"
        subprocess.run(deploy_cmd, shell=True)


def main():
    print("🛠️  Lambda Labs Cleanup and Deployment Tool")
    print("=" * 50)

    # Check for required environment variables
    api_key = os.getenv("LAMBDA_LABS_API_KEY")
    if not api_key:
        print("❌ Please set LAMBDA_LABS_API_KEY environment variable")
        print("   export LAMBDA_LABS_API_KEY='your-api-key-here'")
        sys.exit(1)

    ssh_key_path = os.getenv("LAMBDA_SSH_KEY_PATH", "~/.ssh/sophia-ai-key")
    ssh_key_path = os.path.expanduser(ssh_key_path)

    if not os.path.exists(ssh_key_path):
        print(f"❌ SSH key not found at: {ssh_key_path}")
        print("   Set LAMBDA_SSH_KEY_PATH environment variable if using different path")
        sys.exit(1)

    github_token = os.getenv("GITHUB_TOKEN", "")
    if not github_token:
        print("⚠️  Warning: GITHUB_TOKEN not set, repository cloning may fail")

    # Initialize manager
    manager = LambdaLabsManager(api_key)

    # Run in dry-run mode first
    print("\n🔍 Running in DRY-RUN mode (no changes will be made)")

    cleanup_instances(manager, dry_run=True)
    cleanup_ssh_keys(manager, dry_run=True)
    create_new_api_keys(manager, dry_run=True)

    # Ask to proceed
    print("\n" + "=" * 50)
    proceed = input("\nProceed with actual changes? (yes/no): ")

    if proceed.lower() == "yes":
        cleanup_instances(manager, dry_run=False)
        cleanup_ssh_keys(manager, dry_run=False)
        create_new_api_keys(manager, dry_run=False)

        # Deploy to instances
        deploy = input("\nDeploy Sophia AI to instances? (yes/no): ")
        if deploy.lower() == "yes":
            deploy_to_instances(ssh_key_path, github_token)

    print("\n✅ Lambda Labs setup complete!")


if __name__ == "__main__":
    main()
