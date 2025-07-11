#!/usr/bin/env python3
"""
Quick Lambda Labs Backend Deployment
No complex K8s - just Docker on Lambda Labs GPU instance
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run command and return output"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def main():
    print("🚀 QUICK LAMBDA LABS DEPLOYMENT")
    print("=" * 50)

    # Check SSH key
    ssh_key = Path.home() / ".ssh" / "sophia2025.pem"
    if not ssh_key.exists():
        print(f"❌ SSH key not found: {ssh_key}")
        print("Please ensure your Lambda Labs SSH key is at ~/.ssh/sophia2025.pem")
        sys.exit(1)

    # Lambda Labs instance IP (from your cursor rules)
    LAMBDA_IP = "192.222.58.232"  # K3s cluster IP from cursorrules

    print(f"📍 Deploying to Lambda Labs: {LAMBDA_IP}")

    # 1. Create simple Dockerfile for backend
    dockerfile_content = """FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY shared/ ./shared/

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=prod

# Expose port
EXPOSE 8001

# Run the backend
CMD ["python", "backend/app/unified_chat_backend.py"]
"""

    with open("Dockerfile.lambda", "w") as f:
        f.write(dockerfile_content)

    print("✅ Created Dockerfile")

    # 2. Build Docker image locally
    print("\n📦 Building Docker image...")
    run_command("docker build -f Dockerfile.lambda -t sophia-backend .")

    # 3. Save and compress the image
    print("\n💾 Saving Docker image...")
    run_command("docker save sophia-backend | gzip > sophia-backend.tar.gz")

    # 4. Copy to Lambda Labs
    print("\n📤 Copying to Lambda Labs...")
    run_command(f"scp -i {ssh_key} sophia-backend.tar.gz ubuntu@{LAMBDA_IP}:~/")

    # 5. Deploy on Lambda Labs
    print("\n🚀 Deploying on Lambda Labs...")

    deploy_script = """
# Load the Docker image
docker load < sophia-backend.tar.gz

# Stop any existing container
docker stop sophia-backend 2>/dev/null || true
docker rm sophia-backend 2>/dev/null || true

# Run the new container
docker run -d \\
  --name sophia-backend \\
  -p 8001:8001 \\
  -e SNOWFLAKE_ACCOUNT=UHDECNO-CVB64222 \\
  -e SNOWFLAKE_USER=SCOOBYJAVA15 \\
  -e SNOWFLAKE_PASSWORD='r=+8^h9EB%A2nBRWaLsT3jD=mN' \\
  -e REDIS_URL=redis://localhost:6379 \\
  --restart unless-stopped \\
  sophia-backend

# Check if running
sleep 5
docker ps | grep sophia-backend
curl -s http://localhost:8001/health | jq .
"""

    # Execute on Lambda Labs
    run_command(f"ssh -i {ssh_key} ubuntu@{LAMBDA_IP} '{deploy_script}'")

    # 6. Set up nginx reverse proxy
    print("\n🔧 Setting up public access...")

    nginx_config = """
# Add nginx config for public access
sudo tee /etc/nginx/sites-available/sophia-backend << 'EOF'
server {
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
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/sophia-backend /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
"""

    run_command(f"ssh -i {ssh_key} ubuntu@{LAMBDA_IP} '{nginx_config}'")

    print("\n✅ DEPLOYMENT COMPLETE!")
    print("=" * 50)
    print(f"🌐 Backend URL: http://{LAMBDA_IP}")
    print(f"📚 API Docs: http://{LAMBDA_IP}/docs")
    print(f"🏥 Health Check: http://{LAMBDA_IP}/health")
    print("\n📝 Update your frontend to use this backend URL")
    print(f"   In Vercel, set VITE_API_URL=http://{LAMBDA_IP}")

    # Cleanup
    os.remove("Dockerfile.lambda")
    os.remove("sophia-backend.tar.gz")


if __name__ == "__main__":
    main()
