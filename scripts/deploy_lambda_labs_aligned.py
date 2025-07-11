#!/usr/bin/env python3
"""
Aligned Lambda Labs Deployment Script
Deploys all components to Lambda Labs infrastructure as requested
"""

import os
import sys
import subprocess
import requests

# Lambda Labs Instance IPs
LAMBDA_LABS_IPS = {
    "backend": "192.222.58.232",  # sophia-ai-core
    "mcp_servers": "104.171.202.117",  # sophia-mcp-orchestrator
    "frontend": "104.171.202.103",  # sophia-production-instance
}

# SSH Configuration
SSH_KEY_PATH = os.path.expanduser("~/.ssh/sophia2025.pem")
SSH_USER = "ubuntu"


def run_command(cmd, check=True):
    """Run a shell command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def ssh_command(host, command):
    """Run command on remote host"""
    ssh_cmd = f"ssh -i {SSH_KEY_PATH} -o StrictHostKeyChecking=no {SSH_USER}@{host} '{command}'"
    return run_command(ssh_cmd)


def deploy_frontend_to_lambda():
    """Deploy frontend to Lambda Labs instead of Vercel"""
    print("\n🌐 Deploying Frontend to Lambda Labs...")

    # Build frontend
    print("Building frontend...")
    os.chdir("frontend")
    run_command("npm install")
    run_command("npm run build")

    # Create deployment package
    print("Creating deployment package...")
    run_command("tar -czf frontend-dist.tar.gz dist/")

    # Copy to Lambda Labs frontend server
    frontend_ip = LAMBDA_LABS_IPS["frontend"]
    print(f"Copying to Lambda Labs frontend server ({frontend_ip})...")
    run_command(
        f"scp -i {SSH_KEY_PATH} frontend-dist.tar.gz {SSH_USER}@{frontend_ip}:/tmp/"
    )

    # Deploy on server
    print("Deploying on server...")
    ssh_command(
        frontend_ip,
        """
        cd /var/www
        sudo rm -rf html.bak
        sudo mv html html.bak || true
        sudo mkdir -p html
        cd html
        sudo tar -xzf /tmp/frontend-dist.tar.gz --strip-components=1
        sudo chown -R www-data:www-data .
        sudo systemctl restart nginx
    """,
    )

    print(f"✅ Frontend deployed to https://{frontend_ip}")
    os.chdir("..")


def deploy_backend_to_lambda():
    """Deploy backend to Lambda Labs K3s cluster"""
    print("\n🚀 Deploying Backend to Lambda Labs...")

    # Build backend image
    print("Building backend Docker image...")
    run_command("docker build -t sophia-backend:latest -f Dockerfile.production .")

    # Tag for Lambda Labs registry
    backend_ip = LAMBDA_LABS_IPS["backend"]
    run_command(
        f"docker tag sophia-backend:latest {backend_ip}:5000/sophia-backend:latest"
    )

    # Push to Lambda Labs registry
    print("Pushing to Lambda Labs registry...")
    run_command(f"docker push {backend_ip}:5000/sophia-backend:latest")

    # Update K3s deployment
    print("Updating K3s deployment...")
    kube_cmd = f"KUBECONFIG=$HOME/.kube/k3s-lambda-labs kubectl set image deployment/sophia-api sophia-api={backend_ip}:5000/sophia-backend:latest -n sophia-ai-prod"
    run_command(kube_cmd)

    print(f"✅ Backend deployed to {backend_ip}")


def deploy_mcp_servers():
    """Deploy MCP servers to dedicated Lambda Labs instance"""
    print("\n🤖 Deploying MCP Servers to Lambda Labs...")

    mcp_ip = LAMBDA_LABS_IPS["mcp_servers"]

    # Update K3s manifests to target specific node
    print("Updating MCP server manifests...")

    mcp_servers = [
        "mcp-ai-memory",
        "mcp-codacy",
        "mcp-github",
        "mcp-linear",
        "mcp-asana",
        "mcp-notion",
        "mcp-slack",
        "mcp-snowflake",
        "mcp-gong",
        "mcp-hubspot",
    ]

    for server in mcp_servers:
        manifest_path = f"kubernetes/production/{server}-deployment.yaml"
        if os.path.exists(manifest_path):
            print(f"Updating {server}...")

            # Read manifest
            with open(manifest_path, "r") as f:
                content = f.read()

            # Add nodeSelector to target specific IP
            if "nodeSelector:" not in content:
                # Add nodeSelector before containers
                content = content.replace(
                    "    spec:\n      containers:",
                    "    spec:\n      nodeSelector:\n        kubernetes.io/hostname: mcp-node\n      containers:",
                )

                with open(manifest_path, "w") as f:
                    f.write(content)

    # Label the MCP node
    print(f"Labeling MCP node ({mcp_ip})...")
    ssh_command(
        LAMBDA_LABS_IPS["backend"],
        f"""
        kubectl label node $(kubectl get nodes -o name | grep {mcp_ip} | cut -d/ -f2) kubernetes.io/hostname=mcp-node --overwrite
    """,
    )

    # Apply all MCP deployments
    print("Deploying MCP servers...")
    kube_cmd = (
        "KUBECONFIG=$HOME/.kube/k3s-lambda-labs kubectl apply -k kubernetes/production/"
    )
    run_command(kube_cmd)

    print(f"✅ MCP servers deployed to {mcp_ip}")


def setup_lambda_labs_ingress():
    """Setup ingress rules for Lambda Labs"""
    print("\n🔗 Setting up Lambda Labs ingress...")

    # Create ingress manifest
    ingress_manifest = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sophia-ingress
  namespace: sophia-ai-prod
  annotations:
    kubernetes.io/ingress.class: traefik
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  rules:
  - host: api.sophia-lambda.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-api
            port:
              number: 8000
  - host: mcp.sophia-lambda.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mcp-gateway
            port:
              number: 8080
  tls:
  - hosts:
    - api.sophia-lambda.ai
    - mcp.sophia-lambda.ai
    secretName: sophia-tls
"""

    with open("kubernetes/production/sophia-ingress.yaml", "w") as f:
        f.write(ingress_manifest)

    run_command(
        "KUBECONFIG=$HOME/.kube/k3s-lambda-labs kubectl apply -f kubernetes/production/sophia-ingress.yaml"
    )
    print("✅ Ingress configured")


def verify_deployments():
    """Verify all deployments are running"""
    print("\n🔍 Verifying deployments...")

    # Check backend
    backend_ip = LAMBDA_LABS_IPS["backend"]
    try:
        resp = requests.get(f"http://{backend_ip}:8000/health", timeout=5)
        if resp.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print("❌ Backend health check failed")
    except:
        print("❌ Cannot reach backend")

    # Check frontend
    frontend_ip = LAMBDA_LABS_IPS["frontend"]
    try:
        resp = requests.get(f"http://{frontend_ip}", timeout=5)
        if resp.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print("❌ Frontend not accessible")
    except:
        print("❌ Cannot reach frontend")

    # Check MCP servers
    print("\nChecking MCP servers...")
    result = run_command(
        "KUBECONFIG=$HOME/.kube/k3s-lambda-labs kubectl get pods -n sophia-ai-prod -o wide | grep mcp",
        check=False,
    )
    print(result.stdout)


def main():
    print("🚀 ALIGNED LAMBDA LABS DEPLOYMENT")
    print("=" * 50)
    print("This script deploys all components to Lambda Labs")
    print(f"Frontend: {LAMBDA_LABS_IPS['frontend']}")
    print(f"Backend: {LAMBDA_LABS_IPS['backend']}")
    print(f"MCP Servers: {LAMBDA_LABS_IPS['mcp_servers']}")
    print("=" * 50)

    # Check prerequisites
    if not os.path.exists(SSH_KEY_PATH):
        print(f"❌ SSH key not found at {SSH_KEY_PATH}")
        print("Please ensure your Lambda Labs SSH key is installed")
        sys.exit(1)

    # Deploy components
    deploy_frontend_to_lambda()
    deploy_backend_to_lambda()
    deploy_mcp_servers()
    setup_lambda_labs_ingress()
    verify_deployments()

    print("\n✅ DEPLOYMENT COMPLETE!")
    print("\nAccess your services at:")
    print(f"Frontend: http://{LAMBDA_LABS_IPS['frontend']}")
    print(f"Backend API: http://{LAMBDA_LABS_IPS['backend']}:8000")
    print(f"MCP Gateway: http://{LAMBDA_LABS_IPS['mcp_servers']}:8080")


if __name__ == "__main__":
    main()
