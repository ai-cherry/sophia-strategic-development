#!/usr/bin/env python3
"""
Use Existing Lambda Labs SSH Key
Extracts and sets up the SSH key that's already embedded in the configuration
"""

import os
import subprocess
import sys
from pathlib import Path

def setup_lambda_ssh_key():
    """Setup the existing Lambda Labs SSH key from configuration"""
    
    # The SSH private key from your configuration
    private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAsctiuxhwWHR6Vw2MCEKFQTo0fDd0cDE4G2S7AexGvQZvTyqy
Vl/bBqVE8k3ToTO1VzVynbX4UIv4jmtZ+f85uAkCfkW9xIhfrdMGLVIoMs7UN0rS
iuFdyUD7pf41RDGah35+FfpxQWq+gL0ac9LCFwhE66YyeB2MzG6hrabsKVAAK7Tv
GSYH2ApULQdSowZP0niIshBEy9Sq3px1Vylyon7RsY3UWwEgcrEpQens4s3aJDMe
o/du4cUhbtMJf3RqcDrva9aL3ub0n1Xq5o57lju7umtqlfsJXP776Vyg2oobviaf
LeLg3ZkRHNFgkUz6nWXSZkEyeeM0nSaKIbBoawIDAQABAoIBABvsIbbZeTdjH52R
Wpcnf08FqZ2Chg5ipHmk4bvFFDz2iD+qKHTpO/g4t3HIaD6uZMHr+nKrU/KucNxJ
Hsnk2/c7rwEOyeVWN5SQii1O9FI6ali+rv8xsq17P6pLmKj7k1XJN1sTSHsqHP4R
9NgQ1vuQCGbr5Iw5s9WdYFXp27gG/cwCPcRmtbDwxWypNqBJXCuzryTcj12mXWxx
KXyR1D2i64kYJvfX4XpdO2fHqCwy9OQe6XXCgfO8EmY16GEBA9OYFz7TWD05g/ag
e4C3PhO/OJ8wdd6EUA8/DS8ycN8iAxrqJJ4O8ZRKhPWVTIWG++2b9AJlc+vy+lCo
4PbAWKECgYEA4SZhKQnDAHzt6xuHkVZCxcFGDQPtEhdPc3B23SIFgRtCCss4h5NC
20WoxjsULv+CWG6rlTxNojUS3dKwS/xZs7RZRVleV6Rd3nWikuRDTZTDXQBsxRfr
mgrfdnRKhCkqBfvxEsiRz/dewUL4owkZYyr3B8T6NRDXuCNeWKHHlgsCgYEAyifp
VmQ9aCS3PrZTVo9CwCz7vh0NHjrZ1LQpJzGWld/BKzwmqZeOe3EKlNI0BaYH43sb
38uTq5A0TnjfD16hqeWhy7oIgAabnKUU894PkMZNt4xjk9iRFKvsJiCZxv4vN5MY
MraJRj61jH/9BtXnLAhqsnH7tJYN2uAzufjB0yECgYAyalipStFKg672zWRO7ATp
qTyZX36vZV7aF53WKG8ZGNRx/E19NkFrPi7rrID5gSdby/RJ54Xuw3mlCC+H5Erl
zYWL3NYeQ+TtEmREBi736U7RvW2duJx+Et809BdXfqw1SNQTg6v66IZkOi3YvAne
Rdmo+LeaOFpFlk3jBN7fPwKBgAhMLxWus56Ms0DNtwn8g17j+clJ4/nzrHFAm9fR
/z5TmtgtdeDMKbsDXs3Q+vWoZPZ/XRuIfZ0zJBJ8f5tf5P7WQBfeoO6wVr7NP9jq
qnTkztfT2Vp+LyZMEDtYZzd1w3ZigUHDoErT1BvaPQaEzSJPjiGY8B3vcs4jGbxu
a3ZBAoGARVeKJRgiPHQTxguouBYLSpKr5kuF+sYp0TB3XvOPlMPjKMLIryOajRpd
3ot+NheIx7IOO8nbRBjcdr1CsxvKVrC6K1iEyV1cOwrGo2JednJr5cY92oE3Q3BZ
Si02dEz1jsNZT5IObnR+EZU3x3tUPVwobDfLiVIhf5iOHg48b/w=
-----END RSA PRIVATE KEY-----"""

    # The SSH public key from your configuration
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5"

    print("🔑 Setting up existing Lambda Labs SSH key...")
    
    # Create .ssh directory
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    
    # Write private key
    private_key_path = ssh_dir / "lambda_labs_private_key"
    with open(private_key_path, 'w') as f:
        f.write(private_key)
    private_key_path.chmod(0o600)
    
    # Write public key
    public_key_path = ssh_dir / "lambda_labs_private_key.pub"
    with open(public_key_path, 'w') as f:
        f.write(public_key)
    public_key_path.chmod(0o644)
    
    print(f"✅ SSH keys written to:")
    print(f"   Private: {private_key_path}")
    print(f"   Public: {public_key_path}")

def update_ssh_config():
    """Update SSH config to use Lambda Labs key"""
    ssh_config = """
# Lambda Labs Sophia AI Infrastructure (Using Existing Key)
Host sophia-primary
    HostName 192.222.58.232
    User ubuntu
    IdentityFile ~/.ssh/lambda_labs_private_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host sophia-mcp
    HostName 104.171.202.117
    User ubuntu
    IdentityFile ~/.ssh/lambda_labs_private_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host sophia-data
    HostName 104.171.202.134
    User ubuntu
    IdentityFile ~/.ssh/lambda_labs_private_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host sophia-prod
    HostName 104.171.202.103
    User ubuntu
    IdentityFile ~/.ssh/lambda_labs_private_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host sophia-dev
    HostName 155.248.194.183
    User ubuntu
    IdentityFile ~/.ssh/lambda_labs_private_key
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
    
    # Append Lambda Labs config
    with open(config_file, 'a') as f:
        f.write(ssh_config)
    
    config_file.chmod(0o600)
    print("✅ SSH config updated with Lambda Labs hosts")

def test_connections():
    """Test SSH connections using existing key"""
    servers = {
        "sophia-primary": "192.222.58.232",
        "sophia-mcp": "104.171.202.117", 
        "sophia-data": "104.171.202.134",
        "sophia-prod": "104.171.202.103",
        "sophia-dev": "155.248.194.183"
    }
    
    print("\n🧪 Testing SSH connections with existing Lambda Labs key...")
    
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

def main():
    """Main function"""
    print("🚀 Setting up existing Lambda Labs SSH access...")
    
    # Setup SSH key
    setup_lambda_ssh_key()
    
    # Update SSH config
    update_ssh_config()
    
    # Test connections
    working, failed = test_connections()
    
    print("\n" + "="*80)
    print("🎯 SSH SETUP SUMMARY (Using Existing Lambda Labs Key)")
    print("="*80)
    
    if working:
        print(f"✅ Working servers: {', '.join(working)}")
        print("🚀 You can now run: python3 scripts/master_deploy.py")
    
    if failed:
        print(f"❌ Failed servers: {', '.join(failed)}")
        print("\n📋 NEXT STEPS:")
        print("1. The SSH key is now configured, but servers may need the public key added")
        print("2. Check Lambda Labs console to ensure public key is added to instances")
        print("3. Public key to add:")
        print("   ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5")
        print("\n4. Or try manual deployment on each server")
    
    print("\n💡 ALTERNATIVE: You can also deploy directly on each server:")
    print("   1. SSH to each server using Lambda Labs console")
    print("   2. Clone repo: git clone https://github.com/ai-cherry/sophia-main.git")
    print("   3. Run deployment scripts locally")

if __name__ == "__main__":
    main() 