#!/usr/bin/env python3
"""
Use Docker credentials from Pulumi ESC properly.
This assumes the GitHub Actions workflow has synced the secrets.
"""

import os
import subprocess
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.auto_esc_config import get_docker_hub_config


def docker_login():
    """Login to Docker Hub using credentials from Pulumi ESC"""
    print("🔐 Getting Docker credentials from Pulumi ESC...")

    config = get_docker_hub_config()
    username = config.get("username")
    token = config.get("access_token")

    print(f"Username: {username}")
    print(f"Has token: {bool(token)}")

    if not token:
        print("❌ No Docker token found in Pulumi ESC!")
        print("💡 The GitHub Actions workflow should sync it from GitHub secrets")
        print("💡 Check: https://github.com/ai-cherry/sophia-main/actions")
        return False

    print(f"Token length: {len(token)}")
    print(f"Token preview: {token[:10]}..." if len(token) > 10 else "Token too short")

    # Login to Docker
    print("\n🐳 Logging into Docker Hub...")
    cmd = ["docker", "login", "-u", username, "--password-stdin"]

    try:
        result = subprocess.run(
            cmd, check=False, input=token.encode(), capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ Docker login successful!")
            return True
        else:
            print(f"❌ Docker login failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error during Docker login: {e}")
        return False


def push_images():
    """Push images to Docker Hub"""
    images = [
        "scoobyjava15/sophia-backend:latest",
        "scoobyjava15/sophia-frontend:latest",
    ]

    for image in images:
        print(f"\n📤 Pushing {image}...")
        result = subprocess.run(
            ["docker", "push", image], check=False, capture_output=True, text=True
        )

        if result.returncode == 0:
            print(f"✅ Pushed {image}")
        else:
            print(f"❌ Failed to push {image}: {result.stderr}")


def main():
    print("🚀 Docker Hub Integration via Pulumi ESC")
    print("=" * 50)

    # Set required environment variables
    os.environ["PULUMI_ORG"] = "scoobyjava-org"
    os.environ["ENVIRONMENT"] = "prod"

    # Login to Docker
    if docker_login():
        print("\n✅ Ready to push images!")

        # Ask if we should push
        response = input("\nPush images to Docker Hub? (y/n): ")
        if response.lower() == "y":
            push_images()
    else:
        print("\n❌ Cannot proceed without Docker login")
        print("\n📝 Next steps:")
        print(
            "1. Check GitHub Actions: https://github.com/ai-cherry/sophia-main/actions"
        )
        print("2. Verify sync_secrets_comprehensive.yml completed")
        print("3. Check Pulumi ESC has the token")


if __name__ == "__main__":
    main()
