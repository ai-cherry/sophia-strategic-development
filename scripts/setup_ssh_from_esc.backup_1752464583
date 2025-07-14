#!/usr/bin/env python3
"""
Setup SSH key from Pulumi ESC for Lambda Labs deployment
This script retrieves the SSH private key from Pulumi ESC and sets it up locally
"""

import os
import sys
import stat
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from backend.core.auto_esc_config import get_config_value

def setup_ssh_key():
    """Retrieve SSH key from Pulumi ESC and set it up locally"""
    
    print("🔐 Setting up SSH key from Pulumi ESC...")
    
    # Get SSH key from ESC
    ssh_key = get_config_value("lambda_private_ssh_key")
    
    if not ssh_key:
        print("❌ ERROR: Could not retrieve SSH key from Pulumi ESC")
        print("Please ensure:")
        print("  1. PULUMI_ACCESS_TOKEN is set")
        print("  2. You have access to the sophia-ai-production stack")
        print("  3. The lambda_private_ssh_key is configured in ESC")
        return False
    
    # Create .ssh directory if it doesn't exist
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    
    # Write SSH key
    ssh_key_path = ssh_dir / "sophia2025.pem"
    
    # Check if file already exists
    if ssh_key_path.exists():
        print(f"⚠️  SSH key already exists at {ssh_key_path}")
        response = input("Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing key")
            return True
    
    # Write the key
    ssh_key_path.write_text(ssh_key.strip() + '\n')
    
    # Set proper permissions (read-only for owner)
    ssh_key_path.chmod(0o600)
    
    print(f"✅ SSH key written to {ssh_key_path}")
    print(f"✅ Permissions set to 600 (read-only for owner)")
    
    # Test the key format
    key_content = ssh_key_path.read_text()
    if "BEGIN RSA PRIVATE KEY" in key_content or "BEGIN OPENSSH PRIVATE KEY" in key_content:
        print("✅ SSH key format looks valid")
    else:
        print("⚠️  WARNING: SSH key format might be invalid")
    
    # Show how to test the connection
    print("\n📋 Next steps:")
    print("1. Test connection:")
    print("   ssh -i ~/.ssh/sophia2025.pem ubuntu@104.171.202.103 'echo OK'")
    print("\n2. Run deployment:")
    print("   ./scripts/deploy_sophia_production_real.sh")
    print("   OR")
    print("   ./scripts/deploy_sophia_production_fixed.sh")
    
    return True

if __name__ == "__main__":
    success = setup_ssh_key()
    sys.exit(0 if success else 1) 