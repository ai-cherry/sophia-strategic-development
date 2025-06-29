#!/usr/bin/env python3
"""
Manual GitHub Secrets → Pulumi ESC Sync for Lambda Labs
Use this to manually sync Lambda Labs credentials
"""

import os
import subprocess
import sys

def manual_sync_lambda_credentials():
    """Manually sync Lambda Labs credentials to Pulumi ESC"""
    print("🔧 MANUAL LAMBDA LABS CREDENTIALS SYNC")
    print("=" * 60)
    
    # Check if we have Pulumi access
    try:
        subprocess.run(["pulumi", "whoami"], capture_output=True, text=True, check=True)
        print("✅ Pulumi access verified")
    except subprocess.CalledProcessError:
        print("❌ Pulumi access failed - check PULUMI_ACCESS_TOKEN")
        return False
    
    env_path = "scoobyjava-org/default/sophia-ai-production"
    
    # Lambda Labs credentials to sync
    credentials = {
        "LAMBDA_API_KEY": "values.sophia.infrastructure.lambda_labs.api_key",
        "LAMBDA_IP_ADDRESS": "values.sophia.infrastructure.lambda_labs.ip_address", 
        "LAMBDA_SSH_PRIVATE_KEY": "values.sophia.infrastructure.lambda_labs.ssh_private_key"
    }
    
    print("\n📋 ENTER LAMBDA LABS CREDENTIALS:")
    print("(Get these from GitHub Organization Secrets)")
    
    values = {}
    for env_var, pulumi_path in credentials.items():
        if env_var == "LAMBDA_SSH_PRIVATE_KEY":
            print(f"\n{env_var} (SSH private key - paste entire key):")
            print("Paste the SSH private key and press Ctrl+D when done:")
            try:
                lines = []
                while True:
                    try:
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
                value = "\n".join(lines)
            except KeyboardInterrupt:
                print("\n❌ Cancelled")
                return False
        else:
            value = input(f"{env_var}: ").strip()
        
        if value:
            values[env_var] = (value, pulumi_path)
            print(f"✅ Got {env_var}")
        else:
            print(f"⚠️ Skipping empty {env_var}")
    
    # Sync to Pulumi ESC
    print("\n🔄 SYNCING TO PULUMI ESC...")
    success_count = 0
    
    for env_var, (value, pulumi_path) in values.items():
        try:
            cmd = ["pulumi", "env", "set", env_path, pulumi_path, value, "--secret"]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Synced {env_var} → {pulumi_path}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to sync {env_var}: {e.stderr}")
    
    print(f"\n📊 SYNC COMPLETE: {success_count}/{len(values)} credentials synced")
    
    if success_count > 0:
        print("\n🧪 TESTING ACCESS...")
        # Test the synced credentials
        try:
            result = subprocess.run(
                ["pulumi", "env", "get", env_path, "--show-secrets"],
                capture_output=True, text=True, check=True
            )
            
            if "lambda_labs" in result.stdout:
                print("✅ Lambda Labs credentials found in Pulumi ESC")
            else:
                print("⚠️ Lambda Labs credentials not visible in Pulumi ESC")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to verify sync: {e.stderr}")
    
    return success_count > 0

if __name__ == "__main__":
    success = manual_sync_lambda_credentials()
    sys.exit(0 if success else 1)
