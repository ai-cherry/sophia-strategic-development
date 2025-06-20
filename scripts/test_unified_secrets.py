#!/usr/bin/env python3
"""Test script to verify unified secret management is working
"""

import json
import os
import subprocess


def test_env_file():
    """Test if .env file exists and has secrets"""
    print("=== Testing .env file ===")
    if os.path.exists(".env"):
        print("✓ .env file exists")
        with open(".env", "r") as f:
            content = f.read()
            if "LINEAR_API_KEY" in content:
                print("✓ Found LINEAR_API_KEY in .env")
            else:
                print("✗ LINEAR_API_KEY not found in .env")
    else:
        print("✗ .env file not found")
        print("  Create one from .env.template and add your secrets")
    print()


def test_mcp_config():
    """Test if MCP config has proper env references"""
    print("=== Testing MCP Configuration ===")
    try:
        with open("mcp_config.json", "r") as f:
            config = json.load(f)

        # Check Linear config
        if "linear" in config.get("mcpServers", {}):
            linear_config = config["mcpServers"]["linear"]
            if "env" in linear_config and "LINEAR_API_KEY" in linear_config["env"]:
                if linear_config["env"]["LINEAR_API_KEY"] == "${LINEAR_API_KEY}":
                    print("✓ Linear MCP config uses environment variable reference")
                else:
                    print("✗ Linear MCP config has hardcoded value!")
            else:
                print("✗ Linear MCP config missing env configuration")
        else:
            print("✗ Linear not found in MCP config")
    except Exception as e:
        print(f"✗ Error reading MCP config: {e}")
    print()


def test_pulumi_esc():
    """Test if Pulumi ESC has secrets"""
    print("=== Testing Pulumi ESC ===")

    # Check if Pulumi is installed
    try:
        result = subprocess.run(["pulumi", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Pulumi is installed")
        else:
            print("✗ Pulumi not installed")
            return
    except:
        print("✗ Pulumi not found in PATH")
        return

    # Check if logged in
    try:
        result = subprocess.run(["pulumi", "whoami"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Logged in as: {result.stdout.strip()}")
        else:
            print("✗ Not logged into Pulumi")
            print("  Run: pulumi login")
            return
    except:
        print("✗ Could not check Pulumi login status")
        return

    # Try to get a secret
    try:
        cmd = [
            "pulumi",
            "env",
            "get",
            "ai-cherry/sophia-production",
            "linear.linear_api_key",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Successfully retrieved Linear API key from Pulumi ESC")
        else:
            print("✗ Could not retrieve Linear API key from Pulumi ESC")
            print("  Run: python scripts/setup_all_secrets_once.py")
    except Exception as e:
        print(f"✗ Error checking Pulumi ESC: {e}")
    print()


def test_github_workflow():
    """Test if GitHub workflow exists"""
    print("=== Testing GitHub Workflow ===")
    workflow_path = ".github/workflows/unified-secret-sync.yml"
    if os.path.exists(workflow_path):
        print("✓ Unified secret sync workflow exists")
        with open(workflow_path, "r") as f:
            content = f.read()
            if "LINEAR_API_KEY" in content:
                print("✓ Workflow includes LINEAR_API_KEY")
            else:
                print("✗ Workflow missing LINEAR_API_KEY")
    else:
        print("✗ Unified secret sync workflow not found")
    print()


def main():
    print("=" * 60)
    print("UNIFIED SECRET MANAGEMENT TEST")
    print("=" * 60)
    print()

    test_env_file()
    test_mcp_config()
    test_pulumi_esc()
    test_github_workflow()

    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("\nTo set up unified secret management:")
    print("1. Create .env file with your secrets")
    print("2. Run: python scripts/setup_all_secrets_once.py")
    print("3. Commit changes to mcp_config.json")
    print("4. Push to trigger GitHub Actions sync")


if __name__ == "__main__":
    main()
