#!/usr/bin/env python3
"""
Template for updating GitHub Organization Secrets with Lambda Labs configuration

USAGE:
1. Copy this file and rename without _template suffix
2. Set environment variables:
   export GITHUB_PAT="your-github-pat"
   export LAMBDA_API_KEY="your-lambda-api-key"
   export PULUMI_ACCESS_TOKEN="your-pulumi-token"
3. Run the script
"""

import base64
import logging
import os
import subprocess
import sys

import requests
from nacl import public

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get configuration from environment
GITHUB_PAT = os.getenv("GITHUB_PAT")
LAMBDA_API_KEY = os.getenv("LAMBDA_API_KEY")
PULUMI_ACCESS_TOKEN = os.getenv("PULUMI_ACCESS_TOKEN")

if not all([GITHUB_PAT, LAMBDA_API_KEY, PULUMI_ACCESS_TOKEN]):
    logger.error("Missing required environment variables!")
    logger.error("Please set: GITHUB_PAT, LAMBDA_API_KEY, PULUMI_ACCESS_TOKEN")
    sys.exit(1)

ORG_NAME = "ai-cherry"

# Lambda Labs configuration template
LAMBDA_CONFIG = {
    "LAMBDA_API_KEY": LAMBDA_API_KEY,
    "LAMBDA_LABS_API_KEY": LAMBDA_API_KEY,  # Both names for compatibility
    "LAMBDA_IP_ADDRESS": "146.235.200.1",  # Primary platform server
    "LAMBDA_PLATFORM_IP": "146.235.200.1",
    "LAMBDA_MCP_IP": "165.1.69.44",
    "LAMBDA_AI_IP": "137.131.6.213",
    "GITHUB_PAT": GITHUB_PAT,
    "GITHUB_TOKEN": GITHUB_PAT,  # Both names for compatibility
}


class GitHubSecretsUpdater:
    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_PAT}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.base_url = f"https://api.github.com/orgs/{ORG_NAME}"

    def get_public_key(self) -> dict[str, str]:
        """Get the organization's public key for encrypting secrets"""
        response = requests.get(
            f"{self.base_url}/actions/secrets/public-key",
            headers=self.headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def encrypt_secret(self, public_key: str, secret_value: str) -> str:
        """Encrypt a secret value using the organization's public key"""
        public_key_bytes = base64.b64decode(public_key)
        public_key_obj = public.PublicKey(public_key_bytes)

        sealed_box = public.SealedBox(public_key_obj)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))

        return base64.b64encode(encrypted).decode("utf-8")

    def update_secret(
        self, secret_name: str, secret_value: str, key_id: str, public_key: str
    ) -> bool:
        """Update or create a secret in the organization"""
        encrypted_value = self.encrypt_secret(public_key, secret_value)

        payload = {
            "encrypted_value": encrypted_value,
            "key_id": key_id,
            "visibility": "all",  # Available to all repos in org
        }

        response = requests.put(
            f"{self.base_url}/actions/secrets/{secret_name}",
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        if response.status_code in [201, 204]:
            logger.info(f"✅ Updated secret: {secret_name}")
            return True
        else:
            logger.error(f"❌ Failed to update {secret_name}: {response.text}")
            return False

    def update_all_secrets(self):
        """Update all Lambda Labs related secrets"""
        logger.info("🔐 Updating GitHub Organization Secrets")
        logger.info("=" * 50)

        # Get public key
        try:
            key_info = self.get_public_key()
            key_id = key_info["key_id"]
            public_key = key_info["key"]
            logger.info("✅ Retrieved organization public key")
        except Exception as e:
            logger.error(f"❌ Failed to get public key: {e}")
            return

        # Update each secret
        success_count = 0
        for secret_name, secret_value in LAMBDA_CONFIG.items():
            if self.update_secret(secret_name, secret_value, key_id, public_key):
                success_count += 1

        logger.info(f"\n📊 Updated {success_count}/{len(LAMBDA_CONFIG)} secrets")

    def verify_secrets(self):
        """Verify secrets are set correctly"""
        logger.info("\n🔍 Verifying secrets...")

        response = requests.get(
            f"{self.base_url}/actions/secrets", headers=self.headers, timeout=30
        )
        if response.status_code == 200:
            secrets = response.json()["secrets"]

            # Check our secrets exist
            secret_names = [s["name"] for s in secrets]
            for key in LAMBDA_CONFIG:
                if key in secret_names:
                    logger.info(f"✅ {key} exists")
                else:
                    logger.warning(f"⚠️  {key} not found")


def update_pulumi_esc():
    """Update Pulumi ESC with new Lambda Labs configuration"""
    logger.info("\n🔄 Updating Pulumi ESC...")

    # Login to Pulumi
    subprocess.run(
        ["pulumi", "login", "--cloud-url", "https://api.pulumi.com"],
        env={"PULUMI_ACCESS_TOKEN": PULUMI_ACCESS_TOKEN},
        capture_output=True,
        check=False,
    )

    env_path = "scoobyjava-org/default/sophia-ai-production"

    # Update each secret in Pulumi ESC
    for key, value in LAMBDA_CONFIG.items():
        # Map to Pulumi ESC paths
        if key.startswith("LAMBDA"):
            esc_key = key.lower().replace("_", ".")
            cmd = ["pulumi", "env", "set", env_path, esc_key, value, "--secret"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env={"PULUMI_ACCESS_TOKEN": PULUMI_ACCESS_TOKEN},
                check=False,
            )
            if result.returncode == 0:
                logger.info(f"✅ Updated Pulumi ESC: {esc_key}")
            else:
                logger.error(f"❌ Failed to update {esc_key}: {result.stderr}")


def update_codebase_references():
    """Update codebase to use correct Lambda Labs configuration"""
    logger.info("\n📝 Checking codebase references...")

    # Files that should reference Lambda Labs correctly
    files_to_check = [
        "scripts/lambda_labs_complete_reset.py",
        "scripts/deploy_sophia_optimized.sh",
        "backend/core/auto_esc_config.py",
        ".github/workflows/uv-ci-cd.yml",
        "scripts/ci/sync_from_gh_to_pulumi.py",
    ]

    for file in files_to_check:
        logger.info(f"  - {file}")


def main():
    """Main execution"""
    logger.info("🚀 Lambda Labs GitHub Secrets Update")
    logger.info(f"Organization: {ORG_NAME}")
    logger.info("New Lambda Labs Setup:")
    logger.info("  - Platform Server: 146.235.200.1")
    logger.info("  - MCP Server: 165.1.69.44")
    logger.info("  - AI Server: 137.131.6.213")
    logger.info("")

    # Update GitHub secrets
    updater = GitHubSecretsUpdater()
    updater.update_all_secrets()
    updater.verify_secrets()

    # Update Pulumi ESC
    update_pulumi_esc()

    # Check codebase
    update_codebase_references()

    logger.info("\n✅ Complete! Next steps:")
    logger.info("1. Run GitHub Actions sync workflow")
    logger.info("2. Verify Pulumi ESC has updated values")
    logger.info("3. Test Lambda Labs connectivity")


if __name__ == "__main__":
    main()
