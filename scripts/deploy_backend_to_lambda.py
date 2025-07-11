#!/usr/bin/env python3
"""
Deploy Sophia AI backend to Lambda Labs
"""
import os
import subprocess
import sys
import time
from pathlib import Path


def print_status(message: str, status: str = "INFO"):
    """Print colored status messages"""
    colors = {
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m",
        "WARNING": "\033[93m",
        "INFO": "\033[94m",
        "HEADER": "\033[95m",
    }
    reset = "\033[0m"
    color = colors.get(status, "")
    symbol = (
        "✅"
        if status == "SUCCESS"
        else "❌"
        if status == "ERROR"
        else "⚠️"
        if status == "WARNING"
        else "ℹ️"
    )
    print(f"{color}{symbol} {message}{reset}")


# Lambda Labs configuration
SSH_KEY_PATH = os.path.expanduser("~/.ssh/sophia2025.pem")
INSTANCE_IP = "192.222.58.232"
REMOTE_USER = "ubuntu"


def check_ssh_key():
    """Check if SSH key exists"""
    if not Path(SSH_KEY_PATH).exists():
        print_status(f"SSH key not found at {SSH_KEY_PATH}", "ERROR")
        print("\nCreate the key or update SSH_KEY_PATH in this script")
        sys.exit(1)

    # Check permissions
    os.chmod(SSH_KEY_PATH, 0o600)
    print_status("SSH key found and permissions set", "SUCCESS")


def test_ssh_connection():
    """Test SSH connection to Lambda Labs"""
    cmd = [
        "ssh",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "StrictHostKeyChecking=no",
        "-i",
        SSH_KEY_PATH,
        f"{REMOTE_USER}@{INSTANCE_IP}",
        "echo 'SSH connection successful'",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print_status("SSH connection test passed", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"SSH connection failed: {e.stderr}", "ERROR")
        return False


def create_deployment_files():
    """Create necessary deployment files"""
    # Create Dockerfile for backend
    dockerfile = """FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Expose port
EXPOSE 8001

# Start the application
CMD ["python", "backend/app/unified_chat_backend.py"]
"""

    with open("Dockerfile.backend", "w") as f:
        f.write(dockerfile)
    print_status("Created Dockerfile.backend", "SUCCESS")

    # Create docker-compose for Lambda Labs
    docker_compose = """version: '3.8'

services:
  backend:
    image: sophia-ai-backend:latest
    ports:
      - "8001:8001"
    environment:
      - PORT=8001
      - ENVIRONMENT=production
      - SNOWFLAKE_ACCOUNT=${SNOWFLAKE_ACCOUNT}
      - SNOWFLAKE_USER=${SNOWFLAKE_USER}
      - SNOWFLAKE_PAT=${SNOWFLAKE_PAT}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
    command: redis-server --save 60 1 --loglevel warning
"""

    with open("docker-compose.lambda.yml", "w") as f:
        f.write(docker_compose)
    print_status("Created docker-compose.lambda.yml", "SUCCESS")


def deploy_to_lambda():
    """Deploy backend to Lambda Labs"""
    print_status("Building Docker image...", "INFO")

    # Build the Docker image
    build_cmd = [
        "docker",
        "build",
        "-f",
        "Dockerfile.backend",
        "-t",
        "sophia-ai-backend:latest",
        ".",
    ]
    try:
        subprocess.run(build_cmd, check=True)
        print_status("Docker image built successfully", "SUCCESS")
    except subprocess.CalledProcessError as e:
        print_status(f"Docker build failed: {e}", "ERROR")
        return False

    # Save Docker image
    print_status("Saving Docker image...", "INFO")
    save_cmd = [
        "docker",
        "save",
        "-o",
        "sophia-backend.tar",
        "sophia-ai-backend:latest",
    ]
    try:
        subprocess.run(save_cmd, check=True)
        print_status("Docker image saved", "SUCCESS")
    except subprocess.CalledProcessError as e:
        print_status(f"Docker save failed: {e}", "ERROR")
        return False

    # Copy files to Lambda Labs
    print_status("Copying files to Lambda Labs...", "INFO")
    files_to_copy = ["sophia-backend.tar", "docker-compose.lambda.yml", "local.env"]

    for file in files_to_copy:
        scp_cmd = ["scp", "-i", SSH_KEY_PATH, file, f"{REMOTE_USER}@{INSTANCE_IP}:~/"]
        try:
            subprocess.run(scp_cmd, check=True)
            print_status(f"Copied {file}", "SUCCESS")
        except subprocess.CalledProcessError as e:
            print_status(f"Failed to copy {file}: {e}", "ERROR")
            return False

    # Load and run on Lambda Labs
    print_status("Deploying on Lambda Labs...", "INFO")

    remote_commands = [
        "docker load -i sophia-backend.tar",
        "docker-compose -f docker-compose.lambda.yml down",
        "docker-compose -f docker-compose.lambda.yml up -d",
    ]

    for cmd in remote_commands:
        ssh_cmd = ["ssh", "-i", SSH_KEY_PATH, f"{REMOTE_USER}@{INSTANCE_IP}", cmd]
        try:
            subprocess.run(ssh_cmd, check=True)
            print_status(f"Executed: {cmd}", "SUCCESS")
        except subprocess.CalledProcessError as e:
            print_status(f"Failed to execute {cmd}: {e}", "ERROR")
            return False

    # Clean up local tar file
    os.remove("sophia-backend.tar")

    return True


def setup_nginx_proxy():
    """Set up nginx reverse proxy on Lambda Labs"""
    nginx_config = """server {
    listen 80;
    server_name api.sophia-intel.ai;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}"""

    # Write nginx config
    with open("sophia-api.conf", "w") as f:
        f.write(nginx_config)

    # Copy and set up nginx
    commands = [
        f"scp -i {SSH_KEY_PATH} sophia-api.conf {REMOTE_USER}@{INSTANCE_IP}:~/",
        f"ssh -i {SSH_KEY_PATH} {REMOTE_USER}@{INSTANCE_IP} 'sudo cp sophia-api.conf /etc/nginx/sites-available/'",
        f"ssh -i {SSH_KEY_PATH} {REMOTE_USER}@{INSTANCE_IP} 'sudo ln -sf /etc/nginx/sites-available/sophia-api.conf /etc/nginx/sites-enabled/'",
        f"ssh -i {SSH_KEY_PATH} {REMOTE_USER}@{INSTANCE_IP} 'sudo nginx -t && sudo systemctl reload nginx'",
    ]

    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
        except:
            print_status(
                "Nginx setup failed - may need manual configuration", "WARNING"
            )

    os.remove("sophia-api.conf")


def main():
    print_status("DEPLOYING SOPHIA AI BACKEND TO LAMBDA LABS", "HEADER")
    print("=" * 60)

    # Check prerequisites
    check_ssh_key()

    if not test_ssh_connection():
        print_status("Cannot connect to Lambda Labs instance", "ERROR")
        print(f"\nInstance IP: {INSTANCE_IP}")
        print("Check if the instance is running in Lambda Labs dashboard")
        sys.exit(1)

    # Create deployment files
    create_deployment_files()

    # Deploy to Lambda Labs
    if deploy_to_lambda():
        print_status("Backend deployed successfully!", "SUCCESS")

        # Set up nginx
        setup_nginx_proxy()

        # Wait for services to start
        print_status("Waiting for services to start...", "INFO")
        time.sleep(10)

        # Test deployment
        print_status("Testing deployment...", "INFO")
        test_cmd = f"ssh -i {SSH_KEY_PATH} {REMOTE_USER}@{INSTANCE_IP} 'curl -s http://localhost:8001/health'"
        try:
            result = subprocess.run(
                test_cmd, shell=True, capture_output=True, text=True, check=True
            )
            if "healthy" in result.stdout:
                print_status("Backend is healthy!", "SUCCESS")
            else:
                print_status("Backend health check failed", "WARNING")
        except:
            print_status("Could not verify backend health", "WARNING")

        print("\n" + "=" * 60)
        print_status("DEPLOYMENT COMPLETE", "HEADER")
        print("\n🚀 Backend deployed to Lambda Labs!")
        print(f"📍 Instance IP: {INSTANCE_IP}")
        print(f"🔗 API URL: http://{INSTANCE_IP}:8001")
        print(f"📚 API Docs: http://{INSTANCE_IP}:8001/docs")
        print(
            f"\n⚠️ Note: For api.sophia-intel.ai to work, DNS must point to {INSTANCE_IP}"
        )

        # Clean up
        os.remove("Dockerfile.backend")
        os.remove("docker-compose.lambda.yml")
    else:
        print_status("Deployment failed", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
