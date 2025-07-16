#!/usr/bin/env python3
"""
🔍 GitHub Organization Secrets Validation Script

This script validates that all required GitHub Organization Secrets 
are available for Sophia AI deployment.

Usage:
    python scripts/validate_github_secrets.py
    python scripts/validate_github_secrets.py --check-values
"""

import os
import sys
import subprocess
import argparse
from typing import Dict, List, Optional, Tuple

# Required secrets for Sophia AI deployment
REQUIRED_SECRETS = {
    # Core Infrastructure
    "PULUMI_ACCESS_TOKEN": {
        "description": "Pulumi Cloud access token",
        "required": True,
        "min_length": 40,
        "prefix": "pul-"
    },
    
    # Container Registry
    "DOCKER_HUB_USERNAME": {
        "description": "Docker Hub username (should be 'scoobyjava15')",
        "required": True,
        "expected_value": "scoobyjava15"
    },
    "DOCKER_HUB_ACCESS_TOKEN": {
        "description": "Docker Hub personal access token",
        "required": True,
        "min_length": 30
    },
    
    # Lambda Labs Infrastructure
    "LAMBDA_API_KEY": {
        "description": "Lambda Labs API key for GPU instances",
        "required": True,
        "min_length": 20
    },
    "LAMBDA_LABS_KUBECONFIG": {
        "description": "Base64-encoded kubeconfig for K3s cluster",
        "required": True,
        "min_length": 100
    },
    "LAMBDA_SSH_PRIVATE_KEY": {
        "description": "SSH private key for Lambda Labs instances",
        "required": True,
        "contains": "-----BEGIN"
    },
    
    # Vector Database
    "QDRANT_API_KEY": {
        "description": "Qdrant Cloud API key",
        "required": True,
        "min_length": 20
    },
    "QDRANT_URL": {
        "description": "Qdrant Cloud cluster URL",
        "required": True,
        "expected_value": "https://cloud.qdrant.io"
    },
    
    # AI Services
    "OPENAI_API_KEY": {
        "description": "OpenAI API key",
        "required": True,
        "prefix": "sk-",
        "min_length": 40
    },
    "ANTHROPIC_API_KEY": {
        "description": "Anthropic API key for Claude",
        "required": True,
        "prefix": "sk-ant-",
        "min_length": 40
    },
    
    # Business Intelligence
    "GONG_ACCESS_KEY": {
        "description": "Gong.io API access key",
        "required": False,
        "min_length": 20
    },
    "GONG_ACCESS_KEY_SECRET": {
        "description": "Gong.io API secret",
        "required": False,
        "min_length": 20
    },
    "HUBSPOT_ACCESS_TOKEN": {
        "description": "HubSpot API access token",
        "required": False,
        "min_length": 20
    },
    
    # Development Tools
    "LINEAR_API_KEY": {
        "description": "Linear API key for project management",
        "required": False,
        "min_length": 20
    },
    "SLACK_BOT_TOKEN": {
        "description": "Slack bot token for notifications",
        "required": False,
        "prefix": "xoxb-"
    },
}

def check_gh_cli() -> bool:
    """Check if GitHub CLI is installed and authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def get_github_secret(secret_name: str, org: str = "ai-cherry") -> Optional[str]:
    """Get a GitHub organization secret using GitHub CLI."""
    try:
        result = subprocess.run(
            ["gh", "secret", "get", secret_name, "--org", org],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

def validate_secret_value(secret_name: str, value: str, config: Dict) -> List[str]:
    """Validate a secret value against its configuration."""
    errors = []
    
    # Check minimum length
    if "min_length" in config and len(value) < config["min_length"]:
        errors.append(f"Value too short (minimum {config['min_length']} characters)")
    
    # Check prefix
    if "prefix" in config and not value.startswith(config["prefix"]):
        errors.append(f"Should start with '{config['prefix']}'")
    
    # Check expected value
    if "expected_value" in config and value != config["expected_value"]:
        errors.append(f"Expected '{config['expected_value']}', got '{value[:20]}...'")
    
    # Check contains
    if "contains" in config and config["contains"] not in value:
        errors.append(f"Should contain '{config['contains']}'")
    
    return errors

def validate_github_secrets(check_values: bool = False, org: str = "ai-cherry") -> Tuple[int, int, List[str]]:
    """
    Validate GitHub organization secrets.
    
    Returns:
        Tuple of (total_secrets, available_secrets, error_messages)
    """
    print(f"🔍 Validating GitHub Organization Secrets for {org}...")
    print("=" * 60)
    
    if not check_gh_cli():
        return 0, 0, ["❌ GitHub CLI not installed or not authenticated"]
    
    total_secrets = len(REQUIRED_SECRETS)
    available_secrets = 0
    error_messages = []
    
    for secret_name, config in REQUIRED_SECRETS.items():
        print(f"\n🔑 Checking {secret_name}...")
        print(f"   📝 {config['description']}")
        
        # Check if secret exists
        value = get_github_secret(secret_name, org)
        
        if value is None:
            if config["required"]:
                print(f"   ❌ MISSING (Required)")
                error_messages.append(f"Missing required secret: {secret_name}")
            else:
                print(f"   ⚠️  Missing (Optional)")
        else:
            available_secrets += 1
            print(f"   ✅ Available ({len(value)} characters)")
            
            # Validate value if requested
            if check_values:
                validation_errors = validate_secret_value(secret_name, value, config)
                if validation_errors:
                    print(f"   ⚠️  Validation issues:")
                    for error in validation_errors:
                        print(f"      - {error}")
                    error_messages.extend([f"{secret_name}: {error}" for error in validation_errors])
                else:
                    print(f"   ✅ Validation passed")
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY:")
    print(f"   Total secrets: {total_secrets}")
    print(f"   Available: {available_secrets}")
    print(f"   Missing: {total_secrets - available_secrets}")
    
    # Calculate required vs available
    required_secrets = sum(1 for config in REQUIRED_SECRETS.values() if config["required"])
    available_required = sum(
        1 for secret_name, config in REQUIRED_SECRETS.items() 
        if config["required"] and get_github_secret(secret_name, org) is not None
    )
    
    print(f"   Required available: {available_required}/{required_secrets}")
    
    if error_messages:
        print(f"\n❌ ERRORS FOUND:")
        for error in error_messages:
            print(f"   - {error}")
    
    if available_required == required_secrets:
        print(f"\n✅ ALL REQUIRED SECRETS AVAILABLE - DEPLOYMENT READY!")
        return total_secrets, available_secrets, error_messages
    else:
        print(f"\n⚠️  MISSING REQUIRED SECRETS - DEPLOYMENT WILL FAIL")
        return total_secrets, available_secrets, error_messages

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate GitHub Organization Secrets")
    parser.add_argument(
        "--check-values", 
        action="store_true", 
        help="Also validate secret values (requires read access)"
    )
    parser.add_argument(
        "--org", 
        default="ai-cherry", 
        help="GitHub organization name (default: ai-cherry)"
    )
    
    args = parser.parse_args()
    
    total, available, errors = validate_github_secrets(args.check_values, args.org)
    
    # Exit with appropriate code
    required_count = sum(1 for config in REQUIRED_SECRETS.values() if config["required"])
    available_required = sum(
        1 for secret_name, config in REQUIRED_SECRETS.items() 
        if config["required"] and get_github_secret(secret_name, args.org) is not None
    )
    
    if available_required == required_count:
        print(f"\n🎉 SUCCESS: Ready for deployment!")
        sys.exit(0)
    else:
        print(f"\n💥 FAILURE: Missing required secrets for deployment")
        sys.exit(1)

if __name__ == "__main__":
    main() 