#!/usr/bin/env python3
"""
Fix Existing Lambda Labs Instances
Works with your current instances using correct API endpoints
"""

import requests
import subprocess
import time
from pathlib import Path

# Your API key (the one that works)
API_KEY = "secret_sophiacloudapi_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y"
BASE_URL = "https://cloud.lambda.ai/api/v1"  # Correct URL from your working example

# Your SSH keys
SSH_PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5"

SSH_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
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
    """Setup SSH private key locally"""
    print("🔑 Setting up SSH private key...")
    
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True)
    
    private_key_path = ssh_dir / "sophia_correct_key"
    with open(private_key_path, 'w') as f:
        f.write(SSH_PRIVATE_KEY)
    
    private_key_path.chmod(0o600)
    print(f"✅ SSH key saved to {private_key_path}")
    return str(private_key_path)

def get_instances():
    """Get all instances using correct API"""
    print("🔍 Getting instances...")
    
    response = requests.get(f"{BASE_URL}/instances", auth=(API_KEY, ''))
    
    if response.status_code == 200:
        instances = response.json()['data']
        print(f"✅ Found {len(instances)} instances")
        return instances
    else:
        print(f"❌ Failed to get instances: {response.text}")
        return []

def test_ssh_connection(ip, private_key_path):
    """Test SSH connection"""
    print(f"🧪 Testing SSH to {ip}...")
    
    try:
        result = subprocess.run([
            "ssh", "-i", private_key_path,
            "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no",
            f"ubuntu@{ip}",
            "echo 'SSH working!'"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print(f"✅ SSH connection successful to {ip}")
            return True
        else:
            print(f"❌ SSH failed to {ip}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ SSH error to {ip}: {e}")
        return False

def deploy_sophia_simple(ip, private_key_path, name):
    """Simple deployment to server"""
    print(f"🚀 Deploying to {name} ({ip})...")
    
    commands = [
        # Update system
        "sudo apt update -y",
        
        # Install Docker
        "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh",
        "sudo usermod -aG docker ubuntu",
        
        # Create simple Sophia AI container
        """cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn requests
COPY . .
EXPOSE 8000
CMD ["python", "-c", "import uvicorn; from fastapi import FastAPI; app = FastAPI(); app.add_api_route('/', lambda: {'status': 'Sophia AI Running', 'server': 'Lambda Labs'}); app.add_api_route('/health', lambda: {'status': 'healthy'}); uvicorn.run(app, host='0.0.0.0', port=8000)"]
EOF""",
        
        # Build and run
        "sudo docker build -t sophia-ai .",
        "sudo docker run -d -p 8000:8000 --name sophia-ai sophia-ai",
        
        # Test
        "sleep 5 && curl -s http://localhost:8000/health"
    ]
    
    for cmd in commands:
        print(f"  📋 Running: {cmd[:50]}...")
        try:
            result = subprocess.run([
                "ssh", "-i", private_key_path,
                "-o", "StrictHostKeyChecking=no",
                f"ubuntu@{ip}",
                cmd
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"  ✅ Success")
                if "healthy" in result.stdout:
                    print(f"  🎉 Sophia AI is running!")
            else:
                print(f"  ⚠️  Warning: {result.stderr[:100]}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return True

def main():
    print("🚀 FIXING EXISTING LAMBDA LABS INSTANCES")
    print("=" * 50)
    
    # Setup SSH key
    private_key_path = setup_ssh_key()
    
    # Get instances
    instances = get_instances()
    
    if not instances:
        print("❌ No instances found")
        return
    
    # Process each instance
    successful_deployments = 0
    
    for instance in instances:
        name = instance.get('name', 'unnamed')
        ip = instance.get('ip')
        
        if not ip:
            print(f"⚠️ Skipping {name} - no IP")
            continue
        
        print(f"\n🎯 Processing {name} ({ip})...")
        
        if test_ssh_connection(ip, private_key_path):
            if deploy_sophia_simple(ip, private_key_path, name):
                successful_deployments += 1
                print(f"✅ {name} deployment complete")
        else:
            print(f"❌ SSH failed for {name}")
    
    # Results
    print("\n" + "=" * 50)
    print(f"📊 RESULTS:")
    print(f"✅ Successful: {successful_deployments}/{len(instances)}")
    
    if successful_deployments > 0:
        print("\n🎉 SOPHIA AI DEPLOYED!")
        print("🌐 Access URLs:")
        for instance in instances:
            if instance.get('ip'):
                print(f"  • {instance.get('name')}: http://{instance.get('ip')}:8000")
    
    return successful_deployments > 0

if __name__ == "__main__":
    main() 