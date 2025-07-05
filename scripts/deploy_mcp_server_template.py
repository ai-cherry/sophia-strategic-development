#!/usr/bin/env python3
"""
Deploy MCP server to Lambda Labs
Replace PLACEHOLDER values with actual credentials
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import requests


class MCPServerDeployer:
    """Deploy MCP servers to Lambda Labs"""

    def __init__(self, server_name: str):
        self.server_name = server_name
        # Get credentials from environment or Pulumi ESC
        self.api_key = os.getenv("LAMBDA_LABS_API_KEY", "PLACEHOLDER")
        self.base_url = "https://cloud.lambda.ai/api/v1"
        self.ssh_key_path = os.getenv("LAMBDA_SSH_KEY_PATH", "/path/to/ssh/key")

    def get_instance(self, instance_name: str):
        """Get instance by name"""
        response = requests.get(
            f"{self.base_url}/instances", auth=(self.api_key, ""), timeout=30
        )

        if response.status_code == 200:
            instances = response.json().get("data", [])
            for instance in instances:
                if instance.get("name") == instance_name:
                    return instance
        return None

    def create_instance(self, instance_name: str):
        """Create a new Lambda Labs instance"""
        print(f"Creating Lambda Labs instance: {instance_name}")

        instance_config = {
            "name": instance_name,
            "instance_type": "gpu_1x_a10",
            "region": "us-west-1",
            "ssh_key": "cherry-ai-collaboration-20250604",
        }

        response = requests.post(
            f"{self.base_url}/instances",
            auth=(self.api_key, ""),
            json=instance_config,
            timeout=30,
        )

        if response.status_code == 200:
            instance = response.json()
            print(f"✅ Instance created: {instance['id']}")
            return instance
        else:
            print(f"❌ Failed to create instance: {response.text}")
            return None

    def deploy_to_instance(self, instance_ip: str):
        """Deploy MCP server to instance"""
        print(f"Deploying {self.server_name} to {instance_ip}")

        # Check if SSH key exists
        if not Path(self.ssh_key_path).exists():
            print(f"❌ SSH key not found at {self.ssh_key_path}")
            print("Please set LAMBDA_SSH_KEY_PATH environment variable")
            return False

        try:
            # Copy MCP server files
            server_path = f"mcp-servers/{self.server_name}"
            subprocess.run(
                [
                    "scp",
                    "-r",
                    "-i",
                    self.ssh_key_path,
                    "-o",
                    "StrictHostKeyChecking=no",
                    server_path,
                    f"ubuntu@{instance_ip}:~/",
                ],
                check=True,
            )

            # Install dependencies and run
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y docker.io docker-compose",
                f"cd ~/{self.server_name} && docker build -t sophia-{self.server_name} .",
                f"docker run -d --name {self.server_name} -p 8000:8000 sophia-{self.server_name}",
            ]

            for cmd in commands:
                subprocess.run(
                    [
                        "ssh",
                        "-i",
                        self.ssh_key_path,
                        "-o",
                        "StrictHostKeyChecking=no",
                        f"ubuntu@{instance_ip}",
                        cmd,
                    ],
                    check=True,
                )

            print(f"✅ {self.server_name} deployed successfully!")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            return False

    def deploy(self):
        """Main deployment process"""
        instance_name = f"sophia-{self.server_name}"

        # Check if instance exists
        instance = self.get_instance(instance_name)

        if not instance:
            # Create new instance
            instance = self.create_instance(instance_name)
            if not instance:
                sys.exit(1)

            # Wait for instance to be ready
            print("Waiting for instance to be ready...")
            import time

            time.sleep(60)  # Give it time to boot

        # Get instance IP
        instance_ip = instance.get("ip")
        if not instance_ip:
            print("❌ No IP address found for instance")
            sys.exit(1)

        # Deploy to instance
        if self.deploy_to_instance(instance_ip):
            # Update MCP configuration
            self.update_mcp_config(instance_ip)

    def update_mcp_config(self, instance_ip: str):
        """Update MCP configuration with new server endpoint"""
        config_file = Path("config/cursor_enhanced_mcp_config.json")

        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
        else:
            config = {"mcpServers": {}}

        # Update server configuration
        config["mcpServers"][self.server_name] = {
            "command": "node",
            "args": ["dist/index.js"],
            "env": {"SERVER_URL": f"http://{instance_ip}:8000"},
        }

        # Save updated configuration
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✅ Updated MCP configuration for {self.server_name}")


def main():
    parser = argparse.ArgumentParser(description="Deploy MCP server to Lambda Labs")
    parser.add_argument("--server", required=True, help="Server name to deploy")

    args = parser.parse_args()

    # Check for required environment variables
    if os.getenv("LAMBDA_LABS_API_KEY") == "PLACEHOLDER" or not os.getenv(
        "LAMBDA_LABS_API_KEY"
    ):
        print("❌ Please set LAMBDA_LABS_API_KEY environment variable")
        print("You can get it from Pulumi ESC or set it directly")
        sys.exit(1)

    if not os.getenv("LAMBDA_SSH_KEY_PATH"):
        print("❌ Please set LAMBDA_SSH_KEY_PATH environment variable")
        print("This should point to your Lambda Labs SSH private key")
        sys.exit(1)

    deployer = MCPServerDeployer(args.server)
    deployer.deploy()


if __name__ == "__main__":
    main()
