#!/usr/bin/env python3
"""
Setup SSH Access to Lambda Labs Servers
Configures SSH keys and access for deployment
"""

import os
import subprocess
import sys
from pathlib import Path

def check_ssh_key():
    """Check if SSH key exists, create if needed"""
    ssh_dir = Path.home() / ".ssh"
    ssh_key = ssh_dir / "id_rsa"
    ssh_pub = ssh_dir / "id_rsa.pub"
    
    if not ssh_key.exists():
        print("🔑 Creating SSH key pair...")
        try:
            subprocess.run([
                "ssh-keygen", "-t", "rsa", "-b", "4096", 
                "-f", str(ssh_key), "-N", "", "-C", "sophia-ai-deployment"
            ], check=True)
            print("✅ SSH key pair created")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create SSH key: {e}")
            return False
    else:
        print("✅ SSH key already exists")
    
    # Display public key
    if ssh_pub.exists():
        with open(ssh_pub, 'r') as f:
            public_key = f.read().strip()
        
        print("\n🔑 Your SSH Public Key:")
        print("=" * 80)
        print(public_key)
        print("=" * 80)
        
        return public_key
    
    return False

def create_ssh_config():
    """Create SSH config for Lambda Labs servers"""
    ssh_config = """
# Lambda Labs Sophia AI Infrastructure
Host sophia-primary
    HostName 192.222.58.232
    User root
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host sophia-mcp
    HostName 104.171.202.117
    User root
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host sophia-data
    HostName 104.171.202.134
    User root
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host sophia-dev
    HostName 155.248.194.183
    User root
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
"""
    
    ssh_dir = Path.home() / ".ssh"
    config_file = ssh_dir / "config"
    
    # Backup existing config
    if config_file.exists():
        backup_file = ssh_dir / "config.backup"
        subprocess.run(["cp", str(config_file), str(backup_file)])
        print("✅ Backed up existing SSH config")
    
    # Append or create config
    with open(config_file, 'a') as f:
        f.write(ssh_config)
    
    # Set proper permissions
    os.chmod(config_file, 0o600)
    print("✅ SSH config updated")

def test_ssh_connections():
    """Test SSH connections to all servers"""
    servers = {
        "sophia-primary": "192.222.58.232",
        "sophia-mcp": "104.171.202.117", 
        "sophia-data": "104.171.202.134",
        "sophia-dev": "155.248.194.183"
    }
    
    print("\n🧪 Testing SSH connections...")
    
    working_servers = []
    failed_servers = []
    
    for alias, ip in servers.items():
        try:
            result = subprocess.run([
                "ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
                alias, "echo 'SSH connection successful'"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print(f"✅ {alias} ({ip}): Connected")
                working_servers.append(alias)
            else:
                print(f"❌ {alias} ({ip}): Failed - {result.stderr.strip()}")
                failed_servers.append(alias)
                
        except subprocess.TimeoutExpired:
            print(f"❌ {alias} ({ip}): Timeout")
            failed_servers.append(alias)
        except Exception as e:
            print(f"❌ {alias} ({ip}): Error - {e}")
            failed_servers.append(alias)
    
    return working_servers, failed_servers

def create_manual_deployment_guide():
    """Create manual deployment instructions"""
    guide = """
# 🚀 Manual Lambda Labs Deployment Guide

## SSH Key Setup Required

Your SSH public key needs to be added to each Lambda Labs server.

### Step 1: Add SSH Key to Lambda Labs Console
1. Go to Lambda Labs console: https://cloud.lambdalabs.com/
2. Navigate to each instance
3. Add your SSH public key to authorized_keys

### Step 2: Alternative - Use Lambda Labs SSH Key
If you have the Lambda Labs private key, use it:

```bash
# Copy your Lambda Labs private key to ~/.ssh/
cp /path/to/lambda-labs-key ~/.ssh/lambda_labs_key
chmod 600 ~/.ssh/lambda_labs_key

# Update SSH config to use Lambda Labs key
ssh-add ~/.ssh/lambda_labs_key
```

### Step 3: Manual Deployment Commands

Once SSH access is working, run these commands:

```bash
# Deploy primary server
ssh root@192.222.58.232 'bash -s' < scripts/deploy_primary_server.sh

# Deploy MCP orchestrator  
ssh root@104.171.202.117 'bash -s' < scripts/deploy_mcp_server.sh

# Setup SSL certificates
ssh root@192.222.58.232 'bash -s' < scripts/setup_ssl.sh

# Setup monitoring
ssh root@192.222.58.232 'bash -s' < scripts/setup_monitoring.sh
```

### Step 4: Test Deployment

```bash
# Test endpoints
curl -s https://sophia-intel.ai/health
curl -s https://api.sophia-intel.ai/health
curl -s https://app.sophia-intel.ai/health
```

## Alternative: Direct Server Access

If SSH keys are complex, you can also:

1. SSH directly to each server
2. Clone the repository: `git clone https://github.com/ai-cherry/sophia-main.git`
3. Run deployment scripts locally on each server

### Primary Server (192.222.58.232):
```bash
ssh root@192.222.58.232
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main
bash scripts/deploy_primary_server.sh
```

### MCP Server (104.171.202.117):
```bash
ssh root@104.171.202.117
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main
bash scripts/deploy_mcp_server.sh
```
"""
    
    with open("MANUAL_DEPLOYMENT_GUIDE.md", "w") as f:
        f.write(guide.strip())
    
    print("✅ Created MANUAL_DEPLOYMENT_GUIDE.md")

def main():
    """Main setup function"""
    print("🔑 Setting up SSH access to Lambda Labs servers...")
    
    # Check/create SSH key
    public_key = check_ssh_key()
    if not public_key:
        print("❌ Failed to setup SSH key")
        sys.exit(1)
    
    # Create SSH config
    create_ssh_config()
    
    # Test connections
    working, failed = test_ssh_connections()
    
    # Create manual guide
    create_manual_deployment_guide()
    
    print("\n" + "="*80)
    print("🎯 SSH SETUP SUMMARY")
    print("="*80)
    
    if working:
        print(f"✅ Working servers: {', '.join(working)}")
        print("🚀 You can now run: python3 scripts/master_deploy.py")
    
    if failed:
        print(f"❌ Failed servers: {', '.join(failed)}")
        print("📋 Manual setup required - see instructions below")
        
        print("\n🔑 NEXT STEPS:")
        print("1. Add this SSH public key to your Lambda Labs servers:")
        print("   " + public_key)
        print("\n2. Or use your existing Lambda Labs SSH key")
        print("\n3. Run deployment again: python3 scripts/master_deploy.py")
        print("\n4. Or follow manual deployment guide: MANUAL_DEPLOYMENT_GUIDE.md")
    
    print("\n💡 TIP: You can also deploy directly on each server by SSH'ing in and running scripts locally")

if __name__ == "__main__":
    main() 