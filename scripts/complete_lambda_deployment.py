#!/usr/bin/env python3
"""
Complete Lambda Labs Deployment Script
Handles all setup and deployment to Lambda Labs infrastructure
"""

import os
import sys
import subprocess

# Lambda Labs Instance IPs
LAMBDA_LABS = {
    "frontend": {"ip": "104.171.202.103", "name": "sophia-production-instance"},
    "backend": {"ip": "192.222.58.232", "name": "sophia-ai-core"},
    "mcp": {"ip": "104.171.202.117", "name": "sophia-mcp-orchestrator"},
}

SSH_KEY = os.path.expanduser("~/.ssh/sophia2025.pem")


def run_command(cmd, check=True):
    """Run a shell command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result


def setup_frontend_server():
    """Setup nginx and deploy frontend"""
    print("\n🌐 Setting up Frontend Server...")

    # First, setup nginx on the server
    setup_cmds = """
    sudo apt-get update
    sudo apt-get install -y nginx
    sudo systemctl enable nginx
    sudo mkdir -p /var/www/html
    sudo chown -R ubuntu:ubuntu /var/www/html
    """

    result = run_command(
        f"ssh -i {SSH_KEY} -o StrictHostKeyChecking=no ubuntu@{LAMBDA_LABS['frontend']['ip']} '{setup_cmds}'",
        check=False,
    )

    # Build frontend
    print("Building frontend...")
    os.chdir("frontend")
    run_command("npm install")

    # Create .env with Lambda Labs backend
    with open(".env", "w") as f:
        f.write(f"VITE_API_URL=http://{LAMBDA_LABS['backend']['ip']}:8001\n")
        f.write("VITE_SNOWFLAKE_ENABLED=true\n")

    run_command("npm run build")
    os.chdir("..")

    # Deploy to server
    print("Deploying frontend to Lambda Labs...")
    run_command("cd frontend && tar -czf ../frontend-dist.tar.gz dist/")
    run_command(
        f"scp -i {SSH_KEY} frontend-dist.tar.gz ubuntu@{LAMBDA_LABS['frontend']['ip']}:/tmp/"
    )

    deploy_cmds = (
        """
    cd /var/www/html
    sudo rm -rf *
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
        proxy_pass http://BACKEND_IP:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF
    
    sudo sed -i 's/BACKEND_IP/"""
        + LAMBDA_LABS["backend"]["ip"]
        + """/' /etc/nginx/sites-available/default
    sudo nginx -t && sudo systemctl restart nginx
    """
    )

    run_command(
        f"ssh -i {SSH_KEY} ubuntu@{LAMBDA_LABS['frontend']['ip']} '{deploy_cmds}'"
    )

    print(f"✅ Frontend deployed to http://{LAMBDA_LABS['frontend']['ip']}")


def deploy_backend():
    """Deploy backend to Lambda Labs"""
    print("\n🔧 Deploying Backend...")

    # Create deployment package
    print("Creating backend deployment package...")
    run_command("tar -czf backend-deploy.tar.gz backend/ requirements.txt local.env")

    # Copy to server
    print("Copying to Lambda Labs backend server...")
    run_command(
        f"scp -i {SSH_KEY} backend-deploy.tar.gz ubuntu@{LAMBDA_LABS['backend']['ip']}:/tmp/"
    )

    # Deploy on server
    deploy_cmds = """
    # Setup Python environment
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv redis-server
    
    # Create app directory
    mkdir -p ~/sophia-backend
    cd ~/sophia-backend
    
    # Extract files
    tar -xzf /tmp/backend-deploy.tar.gz
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create systemd service
    sudo tee /etc/systemd/system/sophia-backend.service > /dev/null << 'EOF'
[Unit]
Description=Sophia AI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sophia-backend
Environment="PATH=/home/ubuntu/sophia-backend/venv/bin"
ExecStart=/home/ubuntu/sophia-backend/venv/bin/python backend/app/unified_chat_backend.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    
    # Start service
    sudo systemctl daemon-reload
    sudo systemctl enable sophia-backend
    sudo systemctl restart sophia-backend
    """

    run_command(
        f"ssh -i {SSH_KEY} ubuntu@{LAMBDA_LABS['backend']['ip']} '{deploy_cmds}'"
    )

    print(f"✅ Backend deployed to http://{LAMBDA_LABS['backend']['ip']}:8001")


def deploy_mcp_servers():
    """Deploy MCP servers to Lambda Labs"""
    print("\n🤖 Deploying MCP Servers...")

    # Create MCP deployment package
    print("Creating MCP deployment package...")
    run_command(
        "tar -czf mcp-deploy.tar.gz mcp-servers/ backend/services/ backend/core/ requirements.txt local.env"
    )

    # Copy to server
    print("Copying to Lambda Labs MCP server...")
    run_command(
        f"scp -i {SSH_KEY} mcp-deploy.tar.gz ubuntu@{LAMBDA_LABS['mcp']['ip']}:/tmp/"
    )

    # Deploy on server
    deploy_cmds = """
    # Setup Python environment
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv
    
    # Create app directory
    mkdir -p ~/sophia-mcp
    cd ~/sophia-mcp
    
    # Extract files
    tar -xzf /tmp/mcp-deploy.tar.gz
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create start script
    cat > start_mcp_servers.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
source local.env

# Start each MCP server
python -m mcp-servers.ai_memory.server --port 9001 &
python -m mcp-servers.codacy.server --port 3008 &
python -m mcp-servers.github.server --port 9003 &
python -m mcp-servers.linear.server --port 9004 &
python -m mcp-servers.asana.server --port 9006 &
python -m mcp-servers.notion.server --port 9102 &
python -m mcp-servers.slack.server --port 9101 &

wait
EOF
    
    chmod +x start_mcp_servers.sh
    
    # Create systemd service
    sudo tee /etc/systemd/system/sophia-mcp.service > /dev/null << 'EOF'
[Unit]
Description=Sophia MCP Servers
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sophia-mcp
ExecStart=/home/ubuntu/sophia-mcp/start_mcp_servers.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    
    # Start service
    sudo systemctl daemon-reload
    sudo systemctl enable sophia-mcp
    sudo systemctl restart sophia-mcp
    """

    run_command(f"ssh -i {SSH_KEY} ubuntu@{LAMBDA_LABS['mcp']['ip']} '{deploy_cmds}'")

    print(f"✅ MCP Servers deployed to {LAMBDA_LABS['mcp']['ip']}")


def verify_deployment():
    """Verify all services are running"""
    print("\n🔍 Verifying Deployment...")

    # Check frontend
    result = run_command(
        f"curl -s -o /dev/null -w '%{{http_code}}' http://{LAMBDA_LABS['frontend']['ip']}",
        check=False,
    )
    if result.stdout.strip() == "200":
        print(f"✅ Frontend: http://{LAMBDA_LABS['frontend']['ip']}")
    else:
        print("❌ Frontend not responding")

    # Check backend
    result = run_command(
        f"curl -s http://{LAMBDA_LABS['backend']['ip']}:8001/health", check=False
    )
    if "healthy" in result.stdout:
        print(f"✅ Backend: http://{LAMBDA_LABS['backend']['ip']}:8001")
    else:
        print("❌ Backend not responding")

    # Check MCP servers
    for port in [9001, 3008, 9003, 9004, 9006, 9102, 9101]:
        result = run_command(
            f"curl -s http://{LAMBDA_LABS['mcp']['ip']}:{port}/health", check=False
        )
        if result.returncode == 0:
            print(f"✅ MCP Server on port {port}")
        else:
            print(f"⚠️  MCP Server on port {port} not responding")


def main():
    print("🚀 COMPLETE LAMBDA LABS DEPLOYMENT")
    print("=" * 50)
    print(
        f"Frontend: {LAMBDA_LABS['frontend']['ip']} ({LAMBDA_LABS['frontend']['name']})"
    )
    print(f"Backend: {LAMBDA_LABS['backend']['ip']} ({LAMBDA_LABS['backend']['name']})")
    print(f"MCP Servers: {LAMBDA_LABS['mcp']['ip']} ({LAMBDA_LABS['mcp']['name']})")
    print("=" * 50)

    # Check SSH key
    if not os.path.exists(SSH_KEY):
        print(f"❌ SSH key not found: {SSH_KEY}")
        sys.exit(1)

    # Deploy components
    setup_frontend_server()
    deploy_backend()
    deploy_mcp_servers()

    # Verify
    verify_deployment()

    print("\n✅ DEPLOYMENT COMPLETE!")
    print(f"Frontend: http://{LAMBDA_LABS['frontend']['ip']}")
    print(f"Backend API: http://{LAMBDA_LABS['backend']['ip']}:8001")
    print(f"API Docs: http://{LAMBDA_LABS['backend']['ip']}:8001/docs")


if __name__ == "__main__":
    main()
