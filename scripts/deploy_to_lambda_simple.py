#!/usr/bin/env python3
"""
SIMPLE Lambda Labs Deployment - No BS, Just Works
"""

import subprocess
import time
from pathlib import Path

# Lambda Labs instance (from your cursor rules)
LAMBDA_IP = "192.222.58.232"
SSH_KEY = Path.home() / ".ssh" / "sophia2025.pem"


def run_ssh(cmd):
    """Run command on Lambda Labs"""
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no -i {SSH_KEY} ubuntu@{LAMBDA_IP} '{cmd}'"
    print(f"Running: {cmd}")
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result


def main():
    print("🚀 DEPLOYING TO LAMBDA LABS - SIMPLE & FAST")
    print("=" * 50)

    # 1. Check SSH key
    if not SSH_KEY.exists():
        print(f"❌ SSH key not found: {SSH_KEY}")
        return

    print(f"✅ Using SSH key: {SSH_KEY}")
    print(f"📍 Deploying to: {LAMBDA_IP}")

    # 2. Kill any existing backend
    print("\n🔪 Killing existing backend...")
    run_ssh("pkill -f 'python.*unified_chat_backend' || true")
    run_ssh("docker stop sophia-backend 2>/dev/null || true")
    run_ssh("docker rm sophia-backend 2>/dev/null || true")

    # 3. Create deployment directory
    print("\n📁 Setting up deployment directory...")
    run_ssh("mkdir -p ~/sophia-deployment")

    # 4. Copy files
    print("\n📤 Copying files to Lambda Labs...")
    subprocess.run(
        f"scp -r -i {SSH_KEY} backend ubuntu@{LAMBDA_IP}:~/sophia-deployment/",
        shell=True,
    )
    subprocess.run(
        f"scp -r -i {SSH_KEY} shared ubuntu@{LAMBDA_IP}:~/sophia-deployment/",
        shell=True,
    )
    subprocess.run(
        f"scp -i {SSH_KEY} local.env ubuntu@{LAMBDA_IP}:~/sophia-deployment/",
        shell=True,
    )

    # 5. Create simple run script
    run_script = """#!/bin/bash
cd ~/sophia-deployment
export PYTHONPATH=/home/ubuntu/sophia-deployment

# Load environment
source local.env

# Install Python if needed
if ! command -v python3.12 &> /dev/null; then
    sudo apt update
    sudo apt install -y python3.12 python3.12-venv python3-pip
fi

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install fastapi uvicorn redis snowflake-connector-python httpx websockets sse-starlette python-multipart

# Run the backend
nohup python backend/app/unified_chat_backend.py > backend.log 2>&1 &
echo $! > backend.pid

echo "Backend started with PID: $(cat backend.pid)"
"""

    # Save and run the script
    with open("/tmp/run_backend.sh", "w") as f:
        f.write(run_script)

    subprocess.run(
        f"scp -i {SSH_KEY} /tmp/run_backend.sh ubuntu@{LAMBDA_IP}:~/sophia-deployment/",
        shell=True,
    )

    print("\n🚀 Starting backend...")
    run_ssh("chmod +x ~/sophia-deployment/run_backend.sh")
    run_ssh("cd ~/sophia-deployment && ./run_backend.sh")

    # 6. Wait for backend to start
    print("\n⏳ Waiting for backend to start...")
    time.sleep(10)

    # 7. Set up nginx for public access
    print("\n🌐 Setting up public access...")
    nginx_config = """server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range' always;
    }
}"""

    # Write nginx config
    run_ssh(
        f"echo '{nginx_config}' | sudo tee /etc/nginx/sites-available/sophia-backend"
    )
    run_ssh(
        "sudo ln -sf /etc/nginx/sites-available/sophia-backend /etc/nginx/sites-enabled/"
    )
    run_ssh("sudo rm -f /etc/nginx/sites-enabled/default")
    run_ssh("sudo nginx -t && sudo systemctl reload nginx")

    # 8. Check if it's working
    print("\n🔍 Checking deployment...")
    result = run_ssh("curl -s http://localhost:8001/health | head -20")

    print("\n✅ DEPLOYMENT COMPLETE!")
    print("=" * 50)
    print(f"🌐 Backend URL: http://{LAMBDA_IP}")
    print(f"📚 API Docs: http://{LAMBDA_IP}/docs")
    print(f"🏥 Health Check: http://{LAMBDA_IP}/health")
    print("\n🔧 UPDATE YOUR VERCEL FRONTEND:")
    print("1. Go to https://vercel.com/dashboard")
    print("2. Set environment variable:")
    print(f"   VITE_API_URL = http://{LAMBDA_IP}")
    print("3. Redeploy frontend")
    print("\n💡 This is a PERMANENT URL that won't change!")
    print("   Unlike ngrok, this stays up 24/7")

    # Test the public endpoint
    print("\n🧪 Testing public access...")
    test_result = subprocess.run(
        f"curl -s http://{LAMBDA_IP}/health", shell=True, capture_output=True, text=True
    )
    if "healthy" in test_result.stdout:
        print("✅ Public access confirmed!")
    else:
        print("⚠️ Public access may take a moment to propagate")


if __name__ == "__main__":
    main()
