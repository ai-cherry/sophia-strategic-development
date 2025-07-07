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
            return []

    def delete_ssh_key(self, key_name: str) -> bool:
        """Delete an SSH key"""
        response = requests.delete(
            f"{self.base_url}/ssh-keys/{key_name}", headers=self.headers
        )
        return response.status_code == 200

    def create_api_key(self, name: str) -> str | None:
        """Create a new API key"""
        response = requests.post(
            f"{self.base_url}/api-keys", headers=self.headers, json={"name": name}
        )
        if response.status_code == 201:
            return response.json()["data"]["api_key"]
        else:
            return None


def cleanup_instances(manager: LambdaLabsManager, dry_run: bool = True):
    """Clean up unnecessary instances"""

    instances = manager.list_instances()

    # Instances to keep
    keep_ips = {
        "146.235.200.1",  # sophia-ai-production (8x V100)
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

    for inst in instances_to_keep:
        pass

    for inst in instances_to_remove:
        pass

    if not dry_run and instances_to_remove:
        confirm = input("\nProceed with termination? (yes/no): ")
        if confirm.lower() == "yes":
            for inst in instances_to_remove:
                if manager.terminate_instance(inst["id"]):
                    pass
                else:
                    pass
                time.sleep(1)  # Rate limiting


def cleanup_ssh_keys(manager: LambdaLabsManager, dry_run: bool = True):
    """Clean up unnecessary SSH keys"""

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

    for key in keys_to_keep:
        pass

    for key in keys_to_remove:
        pass

    if not dry_run and keys_to_remove:
        confirm = input("\nProceed with SSH key deletion? (yes/no): ")
        if confirm.lower() == "yes":
            for key in keys_to_remove:
                if manager.delete_ssh_key(key["name"]):
                    pass
                else:
                    pass


def create_new_api_keys(manager: LambdaLabsManager, dry_run: bool = True):
    """Create properly named API keys"""

    new_keys = ["sophia-ai-prod", "sophia-ai-dev", "sophia-ai-pulumi"]

    if dry_run:
        for key_name in new_keys:
            pass
    else:
        confirm = input("\nCreate new API keys? (yes/no): ")
        if confirm.lower() == "yes":
            created_keys = {}
            for key_name in new_keys:
                api_key = manager.create_api_key(key_name)
                if api_key:
                    created_keys[key_name] = api_key
                else:
                    pass

            # Save keys securely
            if created_keys:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"lambda_labs_api_keys_{timestamp}.json"
                with open(filename, "w") as f:
                    json.dump(created_keys, f, indent=2)


def deploy_to_instances(ssh_key_path: str, github_token: str):
    """Deploy Sophia AI to Lambda Labs instances"""

    instances = {
        "main": {"ip": "146.235.200.1", "role": "Main Platform (8x V100)"},
        "mcp": {"ip": "150.230.47.71", "role": "MCP Servers"},
        "ai": {"ip": "129.153.123.54", "role": "AI Services (A100)"},
    }

    for name, config in instances.items():
        # Test SSH connectivity
        test_cmd = f"ssh -i {ssh_key_path} -o ConnectTimeout=10 ubuntu@{config['ip']} 'echo Connected'"
        result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            continue

        # Run deployment script
        deploy_cmd = f"./scripts/lambda_labs_deployment.sh {config['ip']} {name}"
        subprocess.run(deploy_cmd, shell=True)


def main():
    # Check for required environment variables
    api_key = os.getenv("LAMBDA_LABS_API_KEY")
    if not api_key:
        sys.exit(1)

    ssh_key_path = os.getenv("LAMBDA_SSH_KEY_PATH", "~/.ssh/sophia-ai-key")
    ssh_key_path = os.path.expanduser(ssh_key_path)

    if not os.path.exists(ssh_key_path):
        sys.exit(1)

    github_token = os.getenv("GITHUB_TOKEN", "")
    if not github_token:
        pass

    # Initialize manager
    manager = LambdaLabsManager(api_key)

    # Run in dry-run mode first

    cleanup_instances(manager, dry_run=True)
    cleanup_ssh_keys(manager, dry_run=True)
    create_new_api_keys(manager, dry_run=True)

    # Ask to proceed
    proceed = input("\nProceed with actual changes? (yes/no): ")

    if proceed.lower() == "yes":
        cleanup_instances(manager, dry_run=False)
        cleanup_ssh_keys(manager, dry_run=False)
        create_new_api_keys(manager, dry_run=False)

        # Deploy to instances
        deploy = input("\nDeploy Sophia AI to instances? (yes/no): ")
        if deploy.lower() == "yes":
            deploy_to_instances(ssh_key_path, github_token)


if __name__ == "__main__":
    main()
