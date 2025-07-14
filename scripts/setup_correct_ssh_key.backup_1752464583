#!/usr/bin/env python3
"""
Setup the correct Lambda Labs SSH key
"""

import os
import sys
import stat
from pathlib import Path

def setup_ssh_key():
    """Set up the correct SSH private key for Lambda Labs"""
    
    # The private key from Lambda Labs
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
    
    print("🔐 Setting up correct Lambda Labs SSH key...")
    
    # Create .ssh directory if it doesn't exist
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    
    # Backup existing key if it exists
    ssh_key_path = ssh_dir / "sophia2025.pem"
    if ssh_key_path.exists():
        backup_path = ssh_dir / "sophia2025.pem.backup"
        print(f"📦 Backing up existing key to {backup_path}")
        ssh_key_path.rename(backup_path)
    
    # Write the correct private key
    ssh_key_path.write_text(private_key + '\n')
    
    # Set proper permissions (read-only for owner)
    ssh_key_path.chmod(0o600)
    
    print(f"✅ SSH key written to {ssh_key_path}")
    print(f"✅ Permissions set to 600 (read-only for owner)")
    
    # Also save the Lambda API keys to environment
    print("\n📝 Lambda API Keys (add these to your environment):")
    print("export LAMBDA_API_KEY='secret_sophia5apikey_a404a99d985d41828d7020f0b9a122a2.PjbWZb0lLubKu1nmyWYLy9Ycl3vyL18o'")
    print("export LAMBDA_CLOUD_API_KEY='secret_sophiacloudapi_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y'")
    
    print("\n🧪 Testing SSH connectivity...")
    
    # Test each server
    servers = {
        "sophia-production-instance": "104.171.202.103",
        "sophia-ai-core": "192.222.58.232",
        "sophia-mcp-orchestrator": "104.171.202.117",
        "sophia-data-pipeline": "104.171.202.134",
        "sophia-development": "155.248.194.183"
    }
    
    working_servers = []
    for name, ip in servers.items():
        cmd = f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no -o ConnectTimeout=5 ubuntu@{ip} 'echo OK' 2>&1"
        result = os.popen(cmd).read()
        if "OK" in result:
            print(f"✅ {name} ({ip}) - Connection successful!")
            working_servers.append((name, ip))
        else:
            print(f"❌ {name} ({ip}) - Connection failed")
    
    if working_servers:
        print(f"\n🎉 Success! {len(working_servers)} server(s) are now accessible:")
        for name, ip in working_servers:
            print(f"   - {name}: {ip}")
        print("\n📋 Next steps:")
        print("1. Deploy to a working server:")
        print(f"   ./scripts/deploy_sophia_production_real.sh")
        print("2. Or check server status:")
        print(f"   ssh -i ~/.ssh/sophia2025.pem ubuntu@{working_servers[0][1]} 'docker ps'")
    else:
        print("\n⚠️  No servers are accessible. Check Lambda Labs dashboard.")
    
    return len(working_servers) > 0

if __name__ == "__main__":
    success = setup_ssh_key()
    sys.exit(0 if success else 1) 