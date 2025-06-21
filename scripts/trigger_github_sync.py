#!/usr/bin/env python3
"""Trigger the GitHub Actions workflow to sync secrets from GitHub org to Pulumi ESC.

This uses the existing workflow without requiring any manual secret entry.
"""

import os
import subprocess

import requests


def get_github_token():
    """Get GitHub token from environment or Pulumi ESC."""

    # Try environment first
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token

    # Try Pulumi ESC
    try:
        result = subprocess.run(
            [
                "pulumi",
                "env",
                "get",
                "ai-cherry/sophia-production",
                "github.github_token",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass

    return None


def trigger_workflow():
    """Trigger the unified-secret-sync workflow."""token = get_github_token().

    if not token:
        print("ERROR: No GitHub token found!")
        print("\nTo fix this:")
        print("1. Set GITHUB_TOKEN environment variable")
        print("2. Or ensure it's in Pulumi ESC")
        return False

    # GitHub API endpoint
    url = "https://api.github.com/repos/Pay-Ready/sophia-ai/actions/workflows/unified-secret-sync.yml/dispatches"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    data = {"ref": "main"}  # or whatever branch you're on

    print("Triggering GitHub Actions workflow to sync secrets...")

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 204:
            print("✅ Workflow triggered successfully!")
            print("\nThe GitHub Actions workflow is now running and will:")
            print("1. Pull all secrets from GitHub organization")
            print("2. Sync them to Pulumi ESC")
            print("3. Update all configuration files")
            print("\nCheck the Actions tab in GitHub to monitor progress.")
            return True
        else:
            print(f"❌ Failed to trigger workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error triggering workflow: {e}")
        return False


def check_workflow_status():
    """Check if the workflow is already running."""
    token = get_github_token()
    if not token:
        return None

    url = "https://api.github.com/repos/Pay-Ready/sophia-ai/actions/workflows/unified-secret-sync.yml/runs"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            runs = response.json()["workflow_runs"]
            if runs:
                latest = runs[0]
                print("\nLatest workflow run:")
                print(f"  Status: {latest['status']}")
                print(f"  Started: {latest['created_at']}")
                print(f"  URL: {latest['html_url']}")
        return True
    except:
        return False


def main():
    print("=" * 60)
    print("GITHUB SECRETS SYNC TRIGGER")
    print("=" * 60)
    print("\nThis will trigger the GitHub Actions workflow that:")
    print("- Pulls secrets from GitHub organization")
    print("- Syncs them to Pulumi ESC")
    print("- No manual secret entry required!")
    print()

    # Check current status
    check_workflow_status()

    # Trigger the workflow
    if trigger_workflow():
        print("\n✅ Success! Secrets are being synced automatically.")
    else:
        print("\n❌ Failed to trigger workflow.")
        print("\nTroubleshooting:")
        print("1. Ensure you have a GitHub token with workflow permissions")
        print("2. Check that the workflow file exists in .github/workflows/")
        print("3. Verify you have permissions to trigger workflows")


if __name__ == "__main__":
    main()
