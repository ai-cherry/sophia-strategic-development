#!/usr/bin/env python3
"""
Setup Lambda Labs SSH key for deployment
"""

import os
import stat
from pathlib import Path

def setup_lambda_labs_ssh():
    """Setup Lambda Labs SSH key for deployment"""
    
    # Lambda Labs SSH private key (provided by user)
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
    
    # Lambda Labs SSH public key (provided by user)
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5"
    
    # Create .ssh directory if it doesn't exist
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    
    # Write private key
    private_key_path = ssh_dir / "lambda_labs_private_key"
    with open(private_key_path, 'w') as f:
        f.write(private_key)
    
    # Set correct permissions for private key
    private_key_path.chmod(0o600)
    
    # Write public key
    public_key_path = ssh_dir / "lambda_labs_private_key.pub"
    with open(public_key_path, 'w') as f:
        f.write(public_key)
    
    # Set correct permissions for public key
    public_key_path.chmod(0o644)
    
    print("✅ Lambda Labs SSH keys set up successfully!")
    print(f"   Private key: {private_key_path}")
    print(f"   Public key: {public_key_path}")
    
    # Test SSH connection to Lambda Labs instances
    instances = [
        ("master", "192.222.58.232", "GH200"),
        ("mcp", "104.171.202.117", "A6000"),
        ("data", "104.171.202.134", "A100"),
        ("prod", "104.171.202.103", "RTX6000")
    ]
    
    print("\n🔍 Testing SSH connections...")
    for name, ip, gpu in instances:
        try:
            import subprocess
            result = subprocess.run([
                "ssh", "-i", str(private_key_path), 
                "-o", "ConnectTimeout=5",
                "-o", "StrictHostKeyChecking=no", 
                "-o", "UserKnownHostsFile=/dev/null",
                f"ubuntu@{ip}", "echo 'OK'"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"   ✅ {name} ({ip}) - {gpu} - Connected")
            else:
                print(f"   ❌ {name} ({ip}) - {gpu} - Failed: {result.stderr.strip()}")
                
        except Exception as e:
            print(f"   ❌ {name} ({ip}) - {gpu} - Error: {e}")
    
    # Set environment variables
    print("\n🔧 Setting environment variables...")
    os.environ["LAMBDA_API_KEY"] = "secret_sophia5apikey_a404a99d985d41828d7020f0b9a122a2.PjbWZb0lLubKu1nmyWYLy9Ycl3vyL18o"
    os.environ["LAMBDA_PRIVATE_SSH_KEY"] = private_key
    os.environ["LAMBDA_SSH_KEY"] = public_key
    
    print("   ✅ Environment variables set")
    print("   ✅ LAMBDA_API_KEY configured")
    print("   ✅ LAMBDA_PRIVATE_SSH_KEY configured")
    print("   ✅ LAMBDA_SSH_KEY configured")
    
    print("\n🚀 Lambda Labs SSH setup complete!")
    print("   Ready for deployment with unified_deployment_orchestrator.py")

if __name__ == "__main__":
    setup_lambda_labs_ssh() 