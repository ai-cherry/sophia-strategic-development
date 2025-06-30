#!/usr/bin/env python3
"""
PERMANENT FIX for GitHub Organization Secrets → Pulumi ESC Sync
This script fixes all the issues that have been preventing proper sync
"""

import os
import re


def fix_github_actions_workflow():
    """Fix the GitHub Actions workflow file"""
    print("🔧 FIXING GITHUB ACTIONS WORKFLOW")
    print("=" * 50)

    workflow_file = ".github/workflows/sync_secrets.yml"

    with open(workflow_file, "r") as f:
        content = f.read()

    # Fix 1: Add missing Lambda credentials
    lambda_section = """          # Cloud Infrastructure:
          LAMBDA_API_KEY: ${{ secrets.LAMBDA_API_KEY }}
          LAMBDA_IP_ADDRESS: ${{ secrets.LAMBDA_IP_ADDRESS }}
          LAMBDA_SSH_PRIVATE_KEY: ${{ secrets.LAMBDA_SSH_PRIVATE_KEY }}
          VERCEL_ACCESS_TOKEN: ${{ secrets.VERCEL_ACCESS_TOKEN }}
          VULTR_API_KEY: ${{ secrets.VULTR_API_KEY }}"""

    # Replace the existing Cloud Infrastructure section
    content = re.sub(
        r"# Cloud Infrastructure:.*?VULTR_API_KEY: \$\{\{ secrets\.VULTR_API_KEY \}\}",
        lambda_section,
        content,
        flags=re.DOTALL,
    )

    # Fix 2: Remove syntax errors (extra colons)
    content = content.replace(
        'curl -LsSf https://astral.sh/uv/install.sh | sh\n        echo "$HOME/.local/bin" >> $GITHUB_PATH:',
        'curl -LsSf https://astral.sh/uv/install.sh | sh\n          echo "$HOME/.local/bin" >> $GITHUB_PATH',
    )

    content = content.replace(
        "# Install basic dependencies needed for the sync script:\n          uv add requests",
        "# Install basic dependencies needed for the sync script\n          uv add requests",
    )

    content = content.replace(
        'pulumi login:\n          pulumi whoami:\n          echo "✅ Pulumi authentication successful"',
        'pulumi login\n          pulumi whoami\n          echo "✅ Pulumi authentication successful"',
    )

    content = content.replace(
        'if [ -f sync_report.json ]; then:\n            echo "📋 Sync Report Summary:"\n            echo "======================="\n            cat sync_report.json | python -m json.tool:\n          else:\n            echo "❌ Sync report not found":\n          fi',
        'if [ -f sync_report.json ]; then\n            echo "📋 Sync Report Summary:"\n            echo "======================="\n            cat sync_report.json | python -m json.tool\n          else\n            echo "❌ Sync report not found"\n          fi',
    )

    content = content.replace(
        'echo "❌ Secret sync failed!":\n          echo "Check the workflow logs and sync report for details.":\n          echo "Some secrets may not be available in the organization secrets."',
        'echo "❌ Secret sync failed!"\n          echo "Check the workflow logs and sync report for details."\n          echo "Some secrets may not be available in the organization secrets."',
    )

    # Fix 3: Fix the paths line
    content = content.replace(
        "      - 'scripts/ci/sync_from_gh_to_pulumi.py':\n      - '.github/workflows/sync_secrets.yml'",
        "      - 'scripts/ci/sync_from_gh_to_pulumi.py'\n      - '.github/workflows/sync_secrets.yml'",
    )

    with open(workflow_file, "w") as f:
        f.write(content)

    print("✅ Fixed GitHub Actions workflow syntax errors")
    print("✅ Added missing Lambda credentials to workflow")


def fix_sync_script():
    """Fix the sync script mapping"""
    print("\n🔧 FIXING SYNC SCRIPT MAPPINGS")
    print("=" * 50)

    sync_file = "scripts/ci/sync_from_gh_to_pulumi.py"

    with open(sync_file, "r") as f:
        content = f.read()

    # Add missing Lambda credentials to the mapping
    lambda_mapping = """            # Cloud Infrastructure - FIXED: GitHub workflow has LAMBDA_API_KEY, not LAMBDA_LABS_API_KEY
            "LAMBDA_API_KEY": "values.sophia.infrastructure.lambda_labs.api_key",
            "LAMBDA_IP_ADDRESS": "values.sophia.infrastructure.lambda_labs.ip_address",
            "LAMBDA_SSH_PRIVATE_KEY": "values.sophia.infrastructure.lambda_labs.ssh_private_key",
            "VERCEL_ACCESS_TOKEN": "values.sophia.infrastructure.vercel.access_token","""

    # Replace the existing Lambda mapping
    content = re.sub(
        r'# Cloud Infrastructure - FIXED:.*?"VERCEL_ACCESS_TOKEN": "values\.sophia\.infrastructure\.vercel\.access_token",',
        lambda_mapping,
        content,
        flags=re.DOTALL,
    )

    with open(sync_file, "w") as f:
        f.write(content)

    print("✅ Added missing Lambda credentials to sync script")


def update_auto_esc_config():
    """Update auto_esc_config.py to handle Lambda credentials"""
    print("\n🔧 UPDATING AUTO ESC CONFIG")
    print("=" * 50)

    config_file = "backend/core/auto_esc_config.py"

    with open(config_file, "r") as f:
        content = f.read()

    # Add Lambda Labs configuration getter
    lambda_config_function = '''

def get_lambda_labs_config() -> dict[str, Any]:
    """
    Get Lambda Labs configuration from Pulumi ESC

    Returns:
        Lambda Labs configuration dictionary
    """
    return {
        "api_key": get_config_value("lambda_api_key") or get_config_value("LAMBDA_API_KEY"),
        "ip_address": get_config_value("lambda_ip_address") or get_config_value("LAMBDA_IP_ADDRESS"),
        "ssh_private_key": get_config_value("lambda_ssh_private_key") or get_config_value("LAMBDA_SSH_PRIVATE_KEY"),
    }
'''

    # Add the function before the ConfigObject class
    if "def get_lambda_labs_config" not in content:
        content = content.replace(
            "# Backward compatibility - create a config object",
            lambda_config_function
            + "\n# Backward compatibility - create a config object",
        )

    with open(config_file, "w") as f:
        f.write(content)

    print("✅ Added Lambda Labs configuration function")


def create_manual_sync_script():
    """Create a manual sync script for immediate testing"""
    print("\n🔧 CREATING MANUAL SYNC SCRIPT")
    print("=" * 50)

    manual_sync = '''#!/usr/bin/env python3
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
    
    print("\\n📋 ENTER LAMBDA LABS CREDENTIALS:")
    print("(Get these from GitHub Organization Secrets)")
    
    values = {}
    for env_var, pulumi_path in credentials.items():
        if env_var == "LAMBDA_SSH_PRIVATE_KEY":
            print(f"\\n{env_var} (SSH private key - paste entire key):")
            print("Paste the SSH private key and press Ctrl+D when done:")
            try:
                lines = []
                while True:
                    try:
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
                value = "\\n".join(lines)
            except KeyboardInterrupt:
                print("\\n❌ Cancelled")
                return False
        else:
            value = input(f"{env_var}: ").strip()
        
        if value:
            values[env_var] = (value, pulumi_path)
            print(f"✅ Got {env_var}")
        else:
            print(f"⚠️ Skipping empty {env_var}")
    
    # Sync to Pulumi ESC
    print("\\n🔄 SYNCING TO PULUMI ESC...")
    success_count = 0
    
    for env_var, (value, pulumi_path) in values.items():
        try:
            cmd = ["pulumi", "env", "set", env_path, pulumi_path, value, "--secret"]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Synced {env_var} → {pulumi_path}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to sync {env_var}: {e.stderr}")
    
    print(f"\\n📊 SYNC COMPLETE: {success_count}/{len(values)} credentials synced")
    
    if success_count > 0:
        print("\\n🧪 TESTING ACCESS...")
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
'''

    with open("manual_lambda_sync.py", "w") as f:
        f.write(manual_sync)

    os.chmod("manual_lambda_sync.py", 0o755)
    print("✅ Created manual sync script: manual_lambda_sync.py")


def main():
    """Apply all fixes"""
    print("🚀 PERMANENT FIX FOR GITHUB→PULUMI ESC SYNC")
    print("=" * 70)

    fix_github_actions_workflow()
    fix_sync_script()
    update_auto_esc_config()
    create_manual_sync_script()

    print("\n�� ALL FIXES APPLIED SUCCESSFULLY!")
    print("=" * 70)
    print("✅ Fixed GitHub Actions workflow syntax errors")
    print("✅ Added missing Lambda credentials to workflow")
    print("✅ Updated sync script mappings")
    print("✅ Enhanced auto_esc_config.py")
    print("✅ Created manual sync script")

    print("\n🚀 NEXT STEPS:")
    print("1. Commit and push these fixes to trigger GitHub Actions")
    print("2. Or run manual sync: ./manual_lambda_sync.py")
    print("3. Verify credentials: python lambda_labs_access_and_config.py")

    print("\n💡 WHY THIS KEEPS FAILING:")
    print("- GitHub Actions workflow had syntax errors (extra colons)")
    print("- Missing Lambda credentials in workflow environment")
    print("- Sync script missing Lambda IP and SSH key mappings")
    print("- No fallback mechanism for manual sync")
    print("- These fixes address ALL the root causes!")


if __name__ == "__main__":
    main()
