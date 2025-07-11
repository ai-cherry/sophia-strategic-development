#!/usr/bin/env python3
"""
Fix Backend Deployment on Lambda Labs
Uses a pre-built Python image with all dependencies
"""

import os
import subprocess

SSH_KEY = os.path.expanduser("~/.ssh/sophia2025.pem")
BACKEND_IP = "192.222.58.232"


def run_command(cmd, check=True):
    """Run a shell command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)
    return result


def main():
    print("🔧 Fixing Backend Deployment...")

    # Create simplified deployment directory
    run_command(
        f"ssh -i {SSH_KEY} ubuntu@{BACKEND_IP} 'mkdir -p ~/sophia-backend-simple'"
    )

    # Copy only essential files
    print("Copying backend files...")
    run_command(
        f"rsync -avz -e 'ssh -i {SSH_KEY}' --exclude='__pycache__' --exclude='*.pyc' backend/ ubuntu@{BACKEND_IP}:~/sophia-backend-simple/backend/"
    )
    run_command(
        f"scp -i {SSH_KEY} requirements.txt local.env ubuntu@{BACKEND_IP}:~/sophia-backend-simple/"
    )

    # Create a startup script
    startup_script = """#!/bin/bash
cd /app

# Source environment variables
if [ -f local.env ]; then
    set -a
    source local.env
    set +a
fi

# Install dependencies
pip install --no-cache-dir -r requirements.txt

# Start the backend
python backend/app/unified_chat_backend.py
"""

    # Deploy using direct Python image
    deploy_script = f"""
cd ~/sophia-backend-simple

# Create startup script
cat > start.sh << 'EOF'
{startup_script}
EOF
chmod +x start.sh

# Stop existing container
docker stop sophia-backend || true
docker rm sophia-backend || true

# Run with Python image that has necessary build tools
docker run -d \\
    --name sophia-backend \\
    --restart always \\
    -p 8001:8001 \\
    -v ~/sophia-backend-simple:/app \\
    -w /app \\
    python:3.12 \\
    bash start.sh

# Wait a moment
sleep 5

# Check logs
docker logs sophia-backend --tail 50
"""

    run_command(f"ssh -i {SSH_KEY} ubuntu@{BACKEND_IP} '{deploy_script}'")

    # Check if it's running
    print("\n🔍 Checking backend status...")
    result = run_command(f"curl -s http://{BACKEND_IP}:8001/health", check=False)
    if "healthy" in result.stdout or result.returncode == 0:
        print(f"✅ Backend is now running at http://{BACKEND_IP}:8001")
    else:
        print("⚠️  Backend may still be starting up...")
        print(
            "Check logs with: ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232 'docker logs sophia-backend'"
        )


if __name__ == "__main__":
    main()
