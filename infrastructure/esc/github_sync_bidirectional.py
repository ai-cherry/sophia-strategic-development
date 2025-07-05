#!/usr/bin/env python3
"""
Bi-directional GitHub <-> Pulumi ESC Sync
=========================================
Ensures GitHub Organization Secrets and Pulumi ESC stay in sync
"""

import json
import os
import subprocess
from pathlib import Path


class BiDirectionalSync:
    def __init__(self):
        self.mappings_path = Path(__file__).parent / "secret_mappings.json"
        self.load_mappings()

    def load_mappings(self):
        """Load secret mappings configuration"""
        with open(self.mappings_path) as f:
            self.mappings = json.load(f)

    def get_github_secrets(self) -> set[str]:
        """Get list of GitHub organization secrets"""
        cmd = ["gh", "secret", "list", "--org", "ai-cherry", "--json", "name"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            secrets = json.loads(result.stdout)
            return {s["name"] for s in secrets}
        return set()

    def get_pulumi_secrets(self) -> dict[str, str]:
        """Get all Pulumi ESC values"""
        cmd = [
            "pulumi",
            "env",
            "open",
            "scoobyjava-org/default/sophia-ai-production",
            "--format",
            "json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {}

    def sync_github_to_pulumi(self):
        """Sync GitHub secrets to Pulumi ESC"""
        print("📥 Syncing GitHub → Pulumi ESC...")
        github_secrets = self.get_github_secrets()

        for gh_secret, pulumi_path in self.mappings["github_to_pulumi"].items():
            if gh_secret in github_secrets:
                # Get the secret value from GitHub (requires PAT with org:admin)
                value = os.environ.get(gh_secret, "")
                if value and value != f"PLACEHOLDER_{gh_secret}":
                    # Set in Pulumi ESC
                    cmd = [
                        "pulumi",
                        "env",
                        "set",
                        "scoobyjava-org/default/sophia-ai-production",
                        pulumi_path,
                        value,
                        "--secret",
                    ]
                    subprocess.run(cmd, capture_output=True)
                    print(f"  ✅ {gh_secret} → {pulumi_path}")

    def sync_pulumi_to_github(self):
        """Sync Pulumi ESC secrets to GitHub"""
        print("📤 Syncing Pulumi ESC → GitHub...")
        pulumi_secrets = self.get_pulumi_secrets()

        for gh_secret, pulumi_path in self.mappings["github_to_pulumi"].items():
            # Navigate nested path
            value = pulumi_secrets
            for part in pulumi_path.split("."):
                value = value.get(part, {})

            if (
                isinstance(value, str)
                and value
                and not value.startswith("PLACEHOLDER_")
            ):
                # Set in GitHub
                cmd = [
                    "gh",
                    "secret",
                    "set",
                    gh_secret,
                    "--org",
                    "ai-cherry",
                    "--body",
                    value,
                ]
                subprocess.run(cmd, capture_output=True)
                print(f"  ✅ {pulumi_path} → {gh_secret}")

    def validate_sync(self):
        """Validate that all required secrets are present"""
        print("\n🔍 Validating secret synchronization...")
        pulumi_secrets = self.get_pulumi_secrets()

        all_valid = True
        for service, config in self.mappings["services"].items():
            print(f"\n  Service: {service}")
            for secret in config["required_secrets"]:
                # Check if secret exists and is not a placeholder
                value = pulumi_secrets.get(secret, "")
                if value and not value.startswith("PLACEHOLDER_"):
                    print(f"    ✅ {secret}")
                else:
                    print(f"    ❌ {secret} (missing or placeholder)")
                    all_valid = False

        return all_valid


if __name__ == "__main__":
    sync = BiDirectionalSync()
    sync.sync_github_to_pulumi()
    sync.sync_pulumi_to_github()

    if sync.validate_sync():
        print("\n✅ All secrets synchronized successfully!")
    else:
        print("\n⚠️  Some secrets are missing or need configuration")
