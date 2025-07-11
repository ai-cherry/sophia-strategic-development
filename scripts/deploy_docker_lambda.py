#!/usr/bin/env python3
"""
Deploy Sophia AI to Lambda Labs using Docker
Simple deployment using Docker on each server
"""

import os
import sys
import subprocess

# Lambda Labs servers
SERVERS = {
    "backend": {"ip": "192.222.58.232", "name": "sophia-ai-core"},
    "mcp": {"ip": "104.171.202.117", "name": "sophia-mcp-orchestrator"},
    "frontend": {"ip": "104.171.202.103", "name": "sophia-production-instance"},
}

SSH_KEY = os.path.expanduser("~/.ssh/sophia2025.pem")


def run_command(cmd, check=True):
    """Run a shell command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)
    return result


def deploy_backend():
    """Deploy backend using Docker"""
    print("\n🚀 Deploying Backend to Lambda Labs...")

    # Create deployment directory on server
    run_command(
        f"ssh -i {SSH_KEY} ubuntu@{SERVERS['backend']['ip']} 'mkdir -p ~/sophia-backend'"
    )

    # Copy necessary files
    print("Copying backend files...")
    run_command(
        f"rsync -avz -e 'ssh -i {SSH_KEY}' backend/ requirements.txt local.env ubuntu@{SERVERS['backend']['ip']}:~/sophia-backend/"
    )

    # Create Dockerfile on server
    dockerfile_content = """FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY local.env .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "backend/app/unified_chat_backend.py"]
"""

    # Create and run deployment script
    deploy_script = f"""
cd ~/sophia-backend

# Create Dockerfile
cat > Dockerfile << 'EOF'
{dockerfile_content}
EOF

# Stop existing container
docker stop sophia-backend || true
docker rm sophia-backend || true

# Build image
docker build -t sophia-backend .

# Run container
docker run -d \\
    --name sophia-backend \\
    --restart always \\
    -p 8001:8001 \\
    -v ~/sophia-backend/local.env:/app/local.env \\
    sophia-backend

# Check status
docker ps | grep sophia-backend
"""

    run_command(f"ssh -i {SSH_KEY} ubuntu@{SERVERS['backend']['ip']} '{deploy_script}'")

    print(f"✅ Backend deployed to {SERVERS['backend']['ip']}:8001")


def deploy_mcp_servers():
    """Deploy MCP servers using Docker"""
    print("\n🤖 Deploying MCP Servers to Lambda Labs...")

    # Create deployment directory
    run_command(
        f"ssh -i {SSH_KEY} ubuntu@{SERVERS['mcp']['ip']} 'mkdir -p ~/sophia-mcp'"
    )

    # Copy necessary files
    print("Copying MCP server files...")
    run_command(
        f"rsync -avz -e 'ssh -i {SSH_KEY}' mcp-servers/ backend/services/ backend/core/ requirements.txt local.env ubuntu@{SERVERS['mcp']['ip']}:~/sophia-mcp/"
    )

    # Create docker-compose file for MCP servers
    compose_content = """version: '3.8'

services:
  ai-memory:
    image: python:3.12-slim
    container_name: mcp-ai-memory
    working_dir: /app
    volumes:
      - ./:/app
    ports:
      - "9001:9001"
    command: python -m mcp-servers.ai_memory.server --port 9001
    restart: always
    
  codacy:
    image: python:3.12-slim
    container_name: mcp-codacy
    working_dir: /app
    volumes:
      - ./:/app
    ports:
      - "3008:3008"
    command: python -m mcp-servers.codacy.server --port 3008
    restart: always
    
  github:
    image: python:3.12-slim
    container_name: mcp-github
    working_dir: /app
    volumes:
      - ./:/app
    ports:
      - "9003:9003"
    command: python -m mcp-servers.github.server --port 9003
    restart: always
"""

    deploy_script = f"""
cd ~/sophia-mcp

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
{compose_content}
EOF

# Install dependencies in a shared image
docker run --rm -v ~/sophia-mcp:/app -w /app python:3.12-slim pip install -r requirements.txt

# Stop existing containers
docker compose down || true

# Start MCP servers
docker compose up -d

# Check status
docker compose ps
"""

    run_command(f"ssh -i {SSH_KEY} ubuntu@{SERVERS['mcp']['ip']} '{deploy_script}'")

    print(f"✅ MCP Servers deployed to {SERVERS['mcp']['ip']}")


def deploy_frontend_nginx():
    """Deploy frontend to nginx server"""
    print("\n🌐 Deploying Frontend to Lambda Labs...")

    # Build frontend locally first
    print("Building frontend...")
    os.chdir("frontend")

    # Create production env file
    with open(".env.production", "w") as f:
        f.write(f"VITE_API_URL=http://{SERVERS['backend']['ip']}:8001\n")
        f.write("VITE_SNOWFLAKE_ENABLED=true\n")

    run_command("npm install")
    run_command("npm run build")
    os.chdir("..")

    # Create tar of dist
    run_command("cd frontend && tar -czf ../frontend-dist.tar.gz dist/")

    # Copy to server
    run_command(
        f"scp -i {SSH_KEY} frontend-dist.tar.gz ubuntu@{SERVERS['frontend']['ip']}:/tmp/"
    )

    # Deploy script
    deploy_script = """
# Install nginx if not present
if ! command -v nginx &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y nginx
fi

# Extract frontend
sudo rm -rf /var/www/html/*
cd /var/www/html
sudo tar -xzf /tmp/frontend-dist.tar.gz --strip-components=1
sudo chown -R www-data:www-data .

# Configure nginx
sudo tee /etc/nginx/sites-available/default > /dev/null << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    root /var/www/html;
    index index.html;
    
    server_name _;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://192.222.58.232:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Restart nginx
sudo nginx -t && sudo systemctl restart nginx
sudo systemctl enable nginx
"""

    run_command(
        f"ssh -i {SSH_KEY} ubuntu@{SERVERS['frontend']['ip']} '{deploy_script}'"
    )

    print(f"✅ Frontend deployed to http://{SERVERS['frontend']['ip']}")


def verify_deployment():
    """Verify all services are running"""
    print("\n🔍 Verifying Deployment...")

    # Check backend
    result = run_command(
        f"curl -s http://{SERVERS['backend']['ip']}:8001/health", check=False
    )
    if "healthy" in result.stdout:
        print(f"✅ Backend: http://{SERVERS['backend']['ip']}:8001")
    else:
        print("❌ Backend not responding")

    # Check frontend
    result = run_command(
        f"curl -s -o /dev/null -w '%{{http_code}}' http://{SERVERS['frontend']['ip']}",
        check=False,
    )
    if result.stdout.strip() == "200":
        print(f"✅ Frontend: http://{SERVERS['frontend']['ip']}")
    else:
        print("❌ Frontend not responding")

    # Check MCP servers
    for name, port in [("AI Memory", 9001), ("Codacy", 3008), ("GitHub", 9003)]:
        result = run_command(
            f"curl -s http://{SERVERS['mcp']['ip']}:{port}/health", check=False
        )
        if result.returncode == 0:
            print(f"✅ {name} MCP: {SERVERS['mcp']['ip']}:{port}")
        else:
            print(f"⚠️  {name} MCP not responding on port {port}")


def main():
    print("🚀 LAMBDA LABS DOCKER DEPLOYMENT")
    print("=" * 50)
    print(f"Backend: {SERVERS['backend']['ip']} ({SERVERS['backend']['name']})")
    print(f"MCP: {SERVERS['mcp']['ip']} ({SERVERS['mcp']['name']})")
    print(f"Frontend: {SERVERS['frontend']['ip']} ({SERVERS['frontend']['name']})")
    print("=" * 50)

    # Check SSH key
    if not os.path.exists(SSH_KEY):
        print(f"❌ SSH key not found: {SSH_KEY}")
        sys.exit(1)

    # Deploy components
    deploy_backend()
    deploy_mcp_servers()
    deploy_frontend_nginx()

    # Verify
    verify_deployment()

    print("\n✅ DEPLOYMENT COMPLETE!")
    print(f"Frontend: http://{SERVERS['frontend']['ip']}")
    print(f"Backend API: http://{SERVERS['backend']['ip']}:8001")
    print(f"API Docs: http://{SERVERS['backend']['ip']}:8001/docs")
    print(f"MCP Servers: http://{SERVERS['mcp']['ip']}:9001 (and other ports)")


if __name__ == "__main__":
    main()
