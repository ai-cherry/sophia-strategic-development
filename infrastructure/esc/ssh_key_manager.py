#!/usr/bin/env python3
"""
Lambda Labs SSH Key Manager
===========================
Automates SSH key provisioning for Lambda Labs instances
"""

import base64
import subprocess
from pathlib import Path


class LambdaLabsSSHManager:
    def __init__(self):
        self.ssh_dir = Path.home() / ".ssh"
        self.key_name = "pulumi_lambda_key"

    def generate_ssh_key_if_needed(self):
        """Generate SSH key pair if it doesn't exist"""
        private_key_path = self.ssh_dir / self.key_name
        public_key_path = self.ssh_dir / f"{self.key_name}.pub"

        if not private_key_path.exists():
            print(f"🔑 Generating new SSH key pair: {self.key_name}")
            subprocess.run(
                [
                    "ssh-keygen",
                    "-t",
                    "ed25519",
                    "-f",
                    str(private_key_path),
                    "-N",
                    "",  # No passphrase
                    "-C",
                    "pulumi@sophia-ai",
                ],
                check=True,
            )

            # Set proper permissions
            private_key_path.chmod(0o600)
            public_key_path.chmod(0o644)

        return private_key_path, public_key_path

    def get_public_key_content(self):
        """Get the public key content"""
        _, public_key_path = self.generate_ssh_key_if_needed()
        return public_key_path.read_text().strip()

    def encode_for_pulumi_esc(self, content: str) -> str:
        """Encode multi-line content for Pulumi ESC"""
        # Base64 encode to handle multi-line content
        encoded = base64.b64encode(content.encode()).decode()
        return encoded

    def store_in_pulumi_esc(self):
        """Store SSH public key in Pulumi ESC"""
        public_key = self.get_public_key_content()
        encoded_key = self.encode_for_pulumi_esc(public_key)

        # Store as base64 encoded value
        cmd = [
            "pulumi",
            "env",
            "set",
            "scoobyjava-org/default/sophia-ai-production",
            "lambda_labs_ssh_public_key_base64",
            encoded_key,
        ]

        print("📤 Storing SSH public key in Pulumi ESC (base64 encoded)")
        subprocess.run(cmd, check=True)

        # Also store the key name
        subprocess.run(
            [
                "pulumi",
                "env",
                "set",
                "scoobyjava-org/default/sophia-ai-production",
                "lambda_labs_ssh_key_name",
                self.key_name,
            ],
            check=True,
        )

        print("✅ SSH key stored in Pulumi ESC successfully")

    def inject_key_via_lambda_api(self, instance_id: str):
        """Inject SSH key into Lambda Labs instance via API"""
        # This would use the Lambda Labs API to inject the key
        # For now, we'll use user-data approach in Pulumi
        print(f"🚀 Would inject SSH key into instance: {instance_id}")


if __name__ == "__main__":
    manager = LambdaLabsSSHManager()
    manager.store_in_pulumi_esc()
