#!/usr/bin/env python3
"""
Lambda Labs SSH Key Setup Script
Helps manage SSH keys for Lambda Labs instances
"""

import os
import subprocess
from pathlib import Path

import requests

# Your new API key
API_KEY = "secret_sophia-july-25_989f13097e374c779f28629f5a1ac571.iH4OIeM78TWyzDiltkpLAzlPeaTw68HJ"
BASE_URL = "https://cloud.lambda.ai/api/v1"


def list_ssh_keys():
    """List all SSH keys in Lambda Labs"""
    response = requests.get(f"{BASE_URL}/ssh-keys", auth=(API_KEY, ""))
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Error: {response.text}")
        return []


def add_ssh_key(name: str, public_key: str):
    """Add an SSH key to Lambda Labs"""
    response = requests.post(
        f"{BASE_URL}/ssh-keys",
        auth=(API_KEY, ""),
        json={"name": name, "public_key": public_key},
    )
    if response.status_code == 201:
        print(f"✅ Successfully added SSH key: {name}")
        return True
    else:
        print(f"❌ Error adding SSH key: {response.text}")
        return False


def delete_ssh_key(name: str):
    """Delete an SSH key from Lambda Labs"""
    response = requests.delete(f"{BASE_URL}/ssh-keys/{name}", auth=(API_KEY, ""))
    if response.status_code == 204:
        print(f"✅ Successfully deleted SSH key: {name}")
        return True
    else:
        print(f"❌ Error deleting SSH key: {response.text}")
        return False


def create_new_ssh_key(name: str):
    """Create a new SSH key pair"""
    key_path = os.path.expanduser(f"~/.ssh/{name}")

    if os.path.exists(key_path):
        print(f"⚠️  Key already exists at {key_path}")
        return None

    # Generate new key
    cmd = f'ssh-keygen -t rsa -b 4096 -f {key_path} -N "" -C "sophia-ai@lambda-labs"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Created new SSH key: {key_path}")
        with open(f"{key_path}.pub") as f:
            return f.read().strip()
    else:
        print(f"❌ Error creating key: {result.stderr}")
        return None


def main():
    print("🔑 Lambda Labs SSH Key Setup")
    print("=" * 50)

    # Show current Lambda Labs SSH keys
    print("\n📋 Current SSH keys in Lambda Labs:")
    lambda_keys = list_ssh_keys()
    for key in lambda_keys:
        print(f"  - {key['name']}")

    # Show local SSH keys
    print("\n💻 Local SSH keys available:")
    ssh_dir = Path.home() / ".ssh"
    local_keys = {}

    for key_file in ssh_dir.glob("*.pub"):
        if "known_hosts" not in str(key_file):
            key_name = key_file.stem
            with open(key_file) as f:
                local_keys[key_name] = f.read().strip()
            print(f"  - {key_name}")

    # Provide options
    print("\n🎯 Recommended Actions:")
    print("1. Upload your existing 'lambda_labs_key' to Lambda Labs")
    print("2. Create a new 'sophia-ai-key' for the main instance")
    print("3. Upload 'sophia_deployment_key' for deployment")
    print("4. Clean up old/unused keys")

    action = input("\nChoose action (1-4): ")

    if action == "1":
        # Upload lambda_labs_key
        if "lambda_labs_key" in local_keys:
            add_ssh_key("lambda_labs_key", local_keys["lambda_labs_key"])
        else:
            print("❌ lambda_labs_key not found locally")

    elif action == "2":
        # Create new sophia-ai-key
        public_key = create_new_ssh_key("sophia-ai-key")
        if public_key:
            add_ssh_key("sophia-ai-key", public_key)

    elif action == "3":
        # Upload sophia_deployment_key
        if "sophia_deployment_key" in local_keys:
            add_ssh_key("sophia_deployment_key", local_keys["sophia_deployment_key"])
        else:
            print("❌ sophia_deployment_key not found locally")

    elif action == "4":
        # Clean up old keys
        print("\n🧹 Keys to clean up:")
        cleanup_keys = [
            "manus-fresh-key",
            "cherry-ai-key",
            "cherry-ai-collaboration-20250604",
        ]
        for key in cleanup_keys:
            if key in [k["name"] for k in lambda_keys]:
                confirm = input(f"Delete '{key}'? (y/n): ")
                if confirm.lower() == "y":
                    delete_ssh_key(key)

    # Show how to connect
    print("\n📚 To connect to your instances:")
    print("Main instance (104.171.202.64):")
    print("  ssh -i ~/.ssh/sophia-ai-key ubuntu@104.171.202.64")
    print("\nOr with your lambda_labs_key:")
    print("  ssh -i ~/.ssh/lambda_labs_key ubuntu@104.171.202.64")


if __name__ == "__main__":
    main()
