#!/usr/bin/env python3
"""
Configure GitHub Personal Access Token for Sophia AI
This script helps set up GitHub authentication for deployment

PERMANENT SCRIPT - DO NOT DELETE
Usage: GITHUB_PAT=your_token_here python scripts/configure_github_pat.py
"""

import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def configure_github_pat():
    """Configure GitHub PAT for authentication"""
    print("🔐 Configuring GitHub Personal Access Token")
    print("=" * 50)

    # Check if PAT is already set
    existing_pat = os.environ.get("GITHUB_TOKEN")
    if existing_pat:
        print("✅ GitHub token already configured in environment")
        return True

    # Example PAT format (DO NOT COMMIT REAL TOKENS)
    example_pat = "ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

    print("\n📋 To configure GitHub PAT:")
    print("1. Go to GitHub Settings > Developer settings > Personal access tokens")
    print("2. Generate a new token with 'repo' and 'workflow' scopes")
    print("3. Set the token as an environment variable:")
    print(f"   export GITHUB_TOKEN={example_pat}")
    print("\n⚠️  Never commit real tokens to the repository!")

    # Try to get from GitHub CLI
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, check=True
        )
        if result.stdout.strip():
            print("\n✅ Found GitHub token from GitHub CLI")
            os.environ["GITHUB_TOKEN"] = result.stdout.strip()
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check if user wants to input token
    response = input("\nDo you have a GitHub PAT to configure now? (y/n): ")
    if response.lower() == "y":
        pat = input("Enter your GitHub PAT: ").strip()
        if pat and pat.startswith("ghp_"):
            os.environ["GITHUB_TOKEN"] = pat
            print("✅ GitHub PAT configured for this session")
            print("💡 To make it permanent, add to your shell profile:")
            print(f"   echo 'export GITHUB_TOKEN={example_pat}' >> ~/.zshrc")
            return True

    print("\n❌ GitHub PAT not configured")
    print("You'll need to configure it before pushing to GitHub")
    return False


if __name__ == "__main__":
    success = configure_github_pat()
    sys.exit(0 if success else 1)
