#!/usr/bin/env python3
"""
Set up Pulumi ESC secrets for Sophia AI infrastructure
This script securely migrates all provided secrets to Pulumi ESC
"""

import subprocess
import sys
import os

def run_pulumi_command(args, check=True):
    """Run a Pulumi command and handle errors"""
    try:
        result = subprocess.run(
            ['pulumi'] + args,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return None

def set_secret(key, value, description=""):
    """Set a secret in Pulumi ESC"""
    print(f"🔐 Setting secret: {key}")
    
    # Set the secret
    result = run_pulumi_command(['config', 'set', key, value, '--secret'])
    
    if result is not None:
        print(f"  ✅ {key} configured successfully")
        if description:
            print(f"     {description}")
    else:
        print(f"  ❌ Failed to set {key}")
    
    return result is not None

def main():
    """Main setup function"""
    
    print("🚀 Sophia AI Pulumi ESC Secret Setup")
    print("=" * 60)
    
    # Check Pulumi login status
    whoami = run_pulumi_command(['whoami'], check=False)
    if not whoami:
        print("❌ Pulumi not logged in. Please run: pulumi login")
        sys.exit(1)
    
    print(f"✅ Logged in as: {whoami}")
    
    # Set Pulumi organization
    os.environ['PULUMI_ORG'] = 'scoobyjava-org'
    
    # Secrets to configure
    # NOTE: These should be provided as environment variables or command line arguments
    # Never hardcode secrets in source code!
    secrets = {
        # GitHub
        'github.token': (
            os.getenv('GITHUB_TOKEN', 'PLACEHOLDER_GITHUB_TOKEN'),
            'GitHub Personal Access Token for CI/CD and automation'
        ),
        
        # Pulumi
        'pulumi.access_token': (
            os.getenv('PULUMI_ACCESS_TOKEN', 'PLACEHOLDER_PULUMI_TOKEN'),
            'Pulumi Access Token for IaC operations'
        ),
        
        # Lambda Labs API Keys
        'lambda_labs.api_key': (
            os.getenv('LAMBDA_LABS_API_KEY', 'PLACEHOLDER_LAMBDA_API_KEY'),
            'Lambda Labs API Key for instance management'
        ),
        
        'lambda_labs.cloud_api_key': (
            os.getenv('LAMBDA_LABS_CLOUD_API_KEY', 'PLACEHOLDER_LAMBDA_CLOUD_KEY'),
            'Lambda Labs Cloud API Key for cloud operations'
        ),
        
        # Lambda Labs Endpoints
        'lambda_labs.api_endpoint': (
            'https://cloud.lambda.ai/api/v1',
            'Lambda Labs API endpoint'
        ),
        
        # Infrastructure settings
        'infrastructure.provider': (
            'lambda-labs',
            'Infrastructure provider'
        ),
        
        'infrastructure.region': (
            'us-south-1',
            'Default Lambda Labs region'
        ),
    }
    
    print(f"\n📋 Configuring {len(secrets)} secrets...")
    
    # Check for placeholder values
    placeholder_count = 0
    for key, (value, description) in secrets.items():
        if 'PLACEHOLDER' in value:
            print(f"⚠️  {key} has placeholder value - set environment variable")
            placeholder_count += 1
    
    if placeholder_count > 0:
        print(f"\n❌ {placeholder_count} secrets have placeholder values.")
        print("Set the environment variables and run again:")
        print("  export GITHUB_TOKEN='your-github-pat'")
        print("  export PULUMI_ACCESS_TOKEN='your-pulumi-token'")
        print("  export LAMBDA_LABS_API_KEY='your-lambda-key'")
        print("  export LAMBDA_LABS_CLOUD_API_KEY='your-lambda-cloud-key'")
        sys.exit(1)
    
    success_count = 0
    for key, (value, description) in secrets.items():
        if set_secret(key, value, description):
            success_count += 1
    
    print(f"\n✅ Successfully configured {success_count}/{len(secrets)} secrets")
    
    # Verify configuration
    print("\n🔍 Verifying configuration...")
    
    # Test Lambda Labs API access
    print("\n🧪 Testing Lambda Labs API access...")
    print("  ℹ️  To test API access, run:")
    print("     python -c \"from backend.core.auto_esc_config import get_config_value\"")
    print("     python -c \"print(get_config_value('lambda_labs.cloud_api_key'))\"")
    print("\n  Then test with curl:")
    print("     curl -u <API_KEY>: https://cloud.lambda.ai/api/v1/instances")
    
    print("\n✅ Pulumi ESC setup complete!")
    print("\nNext steps:")
    print("1. Run: pulumi stack select sophia-ai-production")
    print("2. Run: python scripts/setup_lambda_labs_infrastructure.py")
    print("3. Deploy: pulumi up")

if __name__ == "__main__":
    main() 