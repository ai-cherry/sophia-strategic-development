#!/usr/bin/env python3
"""
Add SSH Key to Lambda Labs Instances
Automatically adds your SSH public key to all Lambda Labs instances
"""

import requests
import subprocess
import sys
import time
from pathlib import Path

def get_public_key():
    """Get the SSH public key to add"""
    pub_key_path = Path.home() / ".ssh" / "lambda_labs_private_key.pub"
    
    if pub_key_path.exists():
        with open(pub_key_path, 'r') as f:
            return f.read().strip()
    
    # Fallback to the key we know
    return "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCzGl7DQOjlj2G5iUkCP8mVdIrhRY2WxfweWeWXBn012z9z9gW6Nl6INoMmLNM/bILT6Of/1bOP4Gn+CqVlCiQAhyjWxKpOf6Tkr9RPqQyWj3xxClA9ocRK14OImcYjFGRA4wg1DVoUiUi7EvL4hpP4WzwCVim30wPQ45xOeTEDNR2jhTKTI/pPp4EZoXiD23HzgyaVqUoUnBkJBtHSgVvwSXoV4bor1vIoEGIcYollUUYDZhga/Goa3gxhF8mtuw5nLb3wXivCj2fdkbCJQVzo/sm8z1NlXkce0PpkMVx0mvuFtszB+xEJX4rx3xX8UsrfvNhFNWHv8J/E4tCB/3A9obB6+hTu92sY673LHnlEBsuwepntup5Sm5NMqci+G9mwoFD3BaeWeWJ0tNttjfbS6e8pHmAHcddP+9UdegwTx7wEl3imMBZkhDH/XQZ75sWtCjn8vAse2YpZNO2CJ2aCHKtnrEaPMXqI9DPkqHOEX/ptMTvTWNqQdjYmw/K8e4xAVvx2gFCCnzJ4FFn sophia-ai-deployment"

def add_key_to_instance(ip, description):
    """Add SSH key to a single instance"""
    public_key = get_public_key()
    
    print(f"🔧 Adding SSH key to {description} ({ip})...")
    
    # Try SSH method first
    ssh_command = [
        "ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
        "-i", str(Path.home() / ".ssh" / "lambda_labs_private_key"),
        f"ubuntu@{ip}",
        f"echo '{public_key}' >> ~/.ssh/authorized_keys && echo 'SSH key added successfully'"
    ]
    
    try:
        result = subprocess.run(ssh_command, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print(f"✅ SSH key added to {description}")
            return True
        else:
            print(f"⚠️  SSH failed for {description}: {result.stderr}")
    except Exception as e:
        print(f"⚠️  SSH error for {description}: {e}")
    
    # Provide JupyterLab instructions
    print(f"""
📋 Manual method for {description} ({ip}):
1. Go to: https://cloud.lambdalabs.com/instances
2. Click "Launch" under "Cloud IDE" for {ip}
3. Open Terminal in JupyterLab
4. Run: echo '{public_key}' >> ~/.ssh/authorized_keys
5. Run: cat ~/.ssh/authorized_keys  # to verify
""")
    return False

def main():
    """Main function"""
    print("🚀 Lambda Labs SSH Key Deployment")
    print("=" * 50)
    
    # Lambda Labs server details
    servers = [
        ("192.222.58.232", "Primary Production Server (GH200)"),
        ("104.171.202.117", "MCP Orchestrator Server (A6000)"),
        ("104.171.202.134", "Data Pipeline Server (A100)"),
        ("104.171.202.103", "Production Services Server (RTX6000)"),
        ("155.248.194.183", "Development Server (A10)")
    ]
    
    print(f"📡 Adding SSH key to {len(servers)} Lambda Labs servers...")
    print()
    
    success_count = 0
    
    for ip, description in servers:
        if add_key_to_instance(ip, description):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"✅ SSH key successfully added to {success_count}/{len(servers)} servers")
    
    if success_count < len(servers):
        print("⚠️  Some servers require manual setup via JupyterLab")
        print("📖 See instructions above for manual setup")
    
    print()
    print("🧪 Test SSH access with:")
    for ip, description in servers:
        print(f"   ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@{ip}")
    
    print()
    print("🚀 Once SSH access is working, run deployment:")
    print("   python3 scripts/deploy_to_lambda_labs.py")

if __name__ == "__main__":
    main() 