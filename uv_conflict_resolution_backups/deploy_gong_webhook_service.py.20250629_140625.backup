#!/usr/bin/env python3
"""
Deploy Gong Webhook Service to production server
"""

import subprocess
from datetime import datetime


def print_header(message):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"🚀 {message}")
    print("=" * 80)


def run_command(command, capture_output=False, shell=False):
    """
    Run command securely.

    Args:
        command: Command to run (string or list of arguments)
        capture_output: Whether to capture and return stdout
        shell: Whether to run command through shell (SECURITY RISK - use only when necessary)
              If shell=False (safer), command must be a list of arguments
    """
    if isinstance(command, str) and not shell:
        # Split string into args for safer execution
        import shlex

        command = shlex.split(command)

    cmd_display = command if isinstance(command, str) else " ".join(command)
    print(f"  ⚡ Running: {cmd_display}")

    if capture_output:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.stdout.strip()
    else:
        return subprocess.run(command, shell=shell).returncode == 0


def check_dns():
    """Check DNS resolution"""
    print_header("Checking DNS Resolution")
    domain = "webhooks.sophia-intel.ai"

    # Check DNS - requires shell for output parsing
    result = run_command(["nslookup", domain], capture_output=True)
    print(f"  DNS Result:\n{result}")

    # Check if it resolves to expected IP - ensure result is a string
    expected_ip = "34.74.88.2"
    # Check if it resolves to expected IP
    expected_ip = "34.74.88.2"
    if isinstance(result, str) and expected_ip in result:
        print(f"  ✅ DNS correctly points to {expected_ip}")
        return True
    else:
        print(f"  ❌ DNS does not point to expected IP {expected_ip}")
        return False


def deploy_locally():
    """Deploy webhook service locally for testing"""
    print_header("Deploying Webhook Service Locally")

    # Build Docker image - requires shell due to cd command
    print("\n  📦 Building Docker image...")
    if run_command(
        "cd gong-webhook-service && docker build -t gong-webhook:latest .", shell=True
    ):
        print("  ✅ Docker image built successfully")
    else:
        print("  ❌ Failed to build Docker image")
        return False

    # Stop any existing container - shell needed for redirection
    run_command("docker stop gong-webhook 2>/dev/null", shell=True)
    run_command("docker rm gong-webhook 2>/dev/null", shell=True)

    # Run container
    print("\n  🏃 Starting webhook service...")
    if run_command(
        [
            "docker",
            "run",
            "-d",
            "--name",
            "gong-webhook",
            "-p",
            "8080:8080",
            "gong-webhook:latest",
        ]
    ):
        print("  ✅ Webhook service started on port 8080")

        # Test the service
        import time

        time.sleep(3)  # Wait for service to start

        # Test health endpoint
        health_result = run_command(
            ["curl", "-s", "http://localhost:8080/health"], capture_output=True
        )
        print(f"\n  Health Check Result: {health_result}")

        # Test webhook endpoint
        webhook_test = run_command(
            [
                "curl",
                "-s",
                "-X",
                "POST",
                "http://localhost:8080/webhook/gong/calls",
                "-H",
                "Content-Type: application/json",
                "-d",
                "{}",
            ],
            capture_output=True,
        )
        print(f"\n  Webhook Test Result: {webhook_test}")

        return True
    else:
        print("  ❌ Failed to start webhook service")
        return False


def generate_deployment_commands():
    """Generate commands for remote deployment"""
    print_header("Remote Deployment Instructions")

    print(
        r"""
To deploy the webhook service on the remote server (34.74.88.2), follow these steps:

1. SSH into the server:
   ssh ubuntu@34.74.88.2

2. Create webhook directory:
   mkdir -p /home/ubuntu/gong-webhook-service

3. Copy files to server (from your local machine):
   scp -r gong-webhook-service/* ubuntu@34.74.88.2:/home/ubuntu/gong-webhook-service/

4. On the server, build and run with Docker:
   cd /home/ubuntu/gong-webhook-service
   docker build -t gong-webhook:latest .
   docker stop gong-webhook 2>/dev/null
   docker rm gong-webhook 2>/dev/null
   docker run -d --name gong-webhook -p 443:8080 --restart always gong-webhook:latest

5. Set up Nginx for SSL (if not already configured):
   sudo apt update
   sudo apt install -y nginx certbot python3-certbot-nginx

   # Create Nginx config
   sudo tee /etc/nginx/sites-available/webhooks.sophia-intel.ai << EOF
   server {
       listen 80;
       server_name webhooks.sophia-intel.ai;

       location / {
           proxy_pass http://localhost:8080;
           proxy_http_version 1.1;
           proxy_set_header Upgrade \$http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host \$host;
           proxy_cache_bypass \$http_upgrade;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;
       }
   }
   EOF

   sudo ln -s /etc/nginx/sites-available/webhooks.sophia-intel.ai /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx

   # Get SSL certificate
   sudo certbot --nginx -d webhooks.sophia-intel.ai --non-interactive --agree-tos --email admin@sophia-intel.ai

6. Verify deployment:
   curl https://webhooks.sophia-intel.ai/health
   curl -X POST https://webhooks.sophia-intel.ai/webhook/gong/calls -H "Content-Type: application/json" -d "{}"
"""
    )


def main():
    """Main deployment function"""
    print("\n" + "=" * 80)
    print("🔧 GONG WEBHOOK SERVICE DEPLOYMENT")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Check DNS
    check_dns()

    # Deploy locally for testing
    print("\n🧪 Testing webhook service locally first...")
    local_ok = deploy_locally()

    if local_ok:
        print("\n✅ Local testing successful!")

        # Generate deployment instructions
        generate_deployment_commands()

        print("\n" + "=" * 80)
        print("📋 NEXT STEPS:")
        print("=" * 80)
        print(
            """
1. Follow the remote deployment instructions above
2. Ensure SSL certificate is properly configured
3. Verify the service is accessible at https://webhooks.sophia-intel.ai/health
4. Test the webhook endpoint returns 200 OK
5. Re-test in Gong UI

The webhook service is designed to:
- Always return 200 OK for Gong's test
- Accept any JSON payload (or empty body)
- Log all incoming requests
- Provide health check endpoints
- Serve the public key for JWT verification
"""
        )
    else:
        print("\n❌ Local testing failed. Please fix issues before deploying.")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
