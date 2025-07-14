#!/usr/bin/env python3
"""
Fix Lambda Labs SSH Access and Deploy NOW
Uses the API credentials provided to fix this immediately
"""

import requests
import subprocess
import json
import time
from pathlib import Path

# Your API credentials
API_KEY = "secret_sophiacloudapi_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y"
BASE_URL = "https://cloud.lambda.ai/api/v1"

# Your SSH keys
PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5"

PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
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

def setup_ssh_key():
    """Set up the correct SSH key locally"""
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True)
    
    # Write the private key
    private_key_path = ssh_dir / "sophia_working_key"
    with open(private_key_path, 'w') as f:
        f.write(PRIVATE_KEY)
    private_key_path.chmod(0o600)
    
    # Write the public key
    public_key_path = ssh_dir / "sophia_working_key.pub"
    with open(public_key_path, 'w') as f:
        f.write(PUBLIC_KEY)
    
    print(f"✅ SSH keys written to {private_key_path}")
    return str(private_key_path)

def test_ssh_access(private_key_path):
    """Test SSH access to all servers"""
    servers = [
        ("192.222.58.232", "Primary GH200"),
        ("104.171.202.117", "MCP A6000"),
        ("104.171.202.134", "Data A100"),
        ("104.171.202.103", "Prod RTX6000"),
        ("155.248.194.183", "Dev A10")
    ]
    
    working_servers = []
    
    for ip, name in servers:
        print(f"🧪 Testing {name} ({ip})...")
        try:
            result = subprocess.run([
                "ssh", "-i", private_key_path, "-o", "ConnectTimeout=10", 
                "-o", "StrictHostKeyChecking=no", f"ubuntu@{ip}", 
                "echo 'SSH working'"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print(f"✅ {name} - SSH working")
                working_servers.append((ip, name))
            else:
                print(f"❌ {name} - SSH failed: {result.stderr}")
        except Exception as e:
            print(f"❌ {name} - Error: {e}")
    
    return working_servers

def deploy_to_servers(private_key_path, working_servers):
    """Deploy Sophia AI to working servers"""
    if not working_servers:
        print("❌ No working servers found!")
        return False
    
    print(f"\n🚀 Deploying to {len(working_servers)} servers...")
    
    for ip, name in working_servers:
        print(f"\n📦 Deploying to {name} ({ip})...")
        
        # Copy deployment files
        try:
            subprocess.run([
                "scp", "-i", private_key_path, "-o", "StrictHostKeyChecking=no",
                "-r", ".", f"ubuntu@{ip}:~/sophia-ai/"
            ], check=True)
            print(f"✅ Files copied to {name}")
            
            # Run deployment
            subprocess.run([
                "ssh", "-i", private_key_path, "-o", "StrictHostKeyChecking=no",
                f"ubuntu@{ip}", 
                "cd ~/sophia-ai && chmod +x scripts/*.sh && ./scripts/deploy_on_server.sh"
            ], check=True)
            print(f"✅ Deployment completed on {name}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed on {name}: {e}")
            continue
    
    return True

def main():
    """Main deployment function"""
    print("🚀 SOPHIA AI LAMBDA LABS DEPLOYMENT - FIXING NOW")
    print("=" * 60)
    
    # Setup SSH keys
    private_key_path = setup_ssh_key()
    
    # Test SSH access
    print("\n🔑 Testing SSH access...")
    working_servers = test_ssh_access(private_key_path)
    
    if not working_servers:
        print("\n❌ SSH access failed on all servers!")
        print("💡 The servers are configured with 'sophia2025' SSH key")
        print("💡 Using the private key you provided...")
        return False
    
    # Deploy to working servers
    success = deploy_to_servers(private_key_path, working_servers)
    
    if success:
        print("\n✅ DEPLOYMENT COMPLETE!")
        print("🌐 Your Sophia AI platform should now be running")
        for ip, name in working_servers:
            print(f"   - {name}: https://{ip}")
    else:
        print("\n❌ DEPLOYMENT FAILED!")
    
    return success

if __name__ == "__main__":
    main() 