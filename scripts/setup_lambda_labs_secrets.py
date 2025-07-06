#!/usr/bin/env python3
"""
Set up Lambda Labs GitHub Secrets
This script creates all required Lambda Labs secrets in the GitHub repository
"""

import os
import subprocess
import sys
from datetime import datetime

# Define all required secrets
LAMBDA_LABS_SECRETS = {
    "LAMBDA_LABS_API_KEY": os.environ.get("LAMBDA_LABS_API_KEY", ""),
    "LAMBDA_LABS_SSH_KEY_NAME": "lynn-sophia-h200-key",
    "LAMBDA_LABS_SSH_PRIVATE_KEY": "",  # Will be read from file
    "LAMBDA_LABS_REGION": "us-east-3",  # GH200 region
    "LAMBDA_LABS_INSTANCE_TYPE": "gpu_1x_gh200",  # Updated from H200 to GH200
    "LAMBDA_LABS_CLUSTER_SIZE": "3",
    "LAMBDA_LABS_MAX_CLUSTER_SIZE": "16",
    "LAMBDA_LABS_SHARED_FS_ID": "lynn-sophia-shared-fs",
    "LAMBDA_LABS_SHARED_FS_MOUNT": "/mnt/shared",
    "LAMBDA_LABS_ASG_NAME": "lynn-sophia-h200-asg",
}


def set_github_secret(secret_name, secret_value):
    """Set a GitHub repository secret"""
    if not secret_value:
        print(f"⚠️ Skipping {secret_name} - no value provided")
        return False

    print(f"Setting {secret_name}...")

    # Use gh CLI to set the secret
    result = subprocess.run(
        [
            "gh",
            "secret",
            "set",
            secret_name,
            "--body",
            secret_value,
            "--repo",
            "ai-cherry/sophia-main",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"✅ {secret_name} set successfully")
        return True
    else:
        print(f"❌ Failed to set {secret_name}: {result.stderr}")
        return False


def read_ssh_private_key():
    """Read SSH private key from file"""
    ssh_key_paths = [
        os.path.expanduser("~/.ssh/lynn_sophia_h200_key"),
        os.path.expanduser("~/.ssh/lynn-sophia-h200-key"),
        os.path.expanduser("~/.ssh/lynn_sophia_gh200_key"),
        os.path.expanduser("~/.ssh/lynn-sophia-gh200-key"),
    ]

    for key_path in ssh_key_paths:
        if os.path.exists(key_path):
            print(f"Found SSH key at: {key_path}")
            with open(key_path) as f:
                return f.read().strip()

    print("⚠️ No SSH private key found. Will need to generate one.")
    return ""


def main():
    print("🔧 Lambda Labs GitHub Secrets Setup")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Check if GitHub CLI is authenticated
    auth_result = subprocess.run(
        ["gh", "auth", "status"], capture_output=True, text=True
    )
    if auth_result.returncode != 0:
        print("❌ GitHub CLI not authenticated. Run: gh auth login")
        sys.exit(1)

    print("✅ GitHub CLI authenticated")

    # Read SSH private key
    ssh_private_key = read_ssh_private_key()
    if ssh_private_key:
        LAMBDA_LABS_SECRETS["LAMBDA_LABS_SSH_PRIVATE_KEY"] = ssh_private_key

    # Set each secret
    success_count = 0
    failed_count = 0

    print("\n🚀 Setting GitHub Secrets:")
    print("=" * 60)

    for secret_name, secret_value in LAMBDA_LABS_SECRETS.items():
        if set_github_secret(secret_name, secret_value):
            success_count += 1
        else:
            failed_count += 1

    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"  ✅ Successfully set: {success_count} secrets")
    print(f"  ❌ Failed: {failed_count} secrets")

    if failed_count == 0:
        print("\n✅ All Lambda Labs secrets configured successfully!")
    else:
        print("\n⚠️ Some secrets failed to set. Please check the errors above.")

        if not ssh_private_key:
            print("\n📝 To generate the SSH key:")
            print("   ssh-keygen -t ed25519 -f ~/.ssh/lynn_sophia_h200_key -N ''")
            print("   Then run this script again.")

    # Next steps
    print("\n📋 Next Steps:")
    print("1. If SSH key was missing, generate it and run this script again")
    print(
        "2. Create Pulumi H200 environment: pulumi env init scoobyjava-org/sophia-ai-h200-production"
    )
    print("3. Run the sync workflow to push secrets to Pulumi ESC")
    print("4. Update H200 references to GH200")


if __name__ == "__main__":
    main()
