#!/usr/bin/env python3
"""
Deploy Sophia AI to Lambda Labs K3s Cluster
Uses the existing K3s infrastructure
"""

import os
import sys
import subprocess
import base64

# Lambda Labs K3s cluster
K3S_SERVER = "192.222.58.232"
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


def setup_kubectl():
    """Setup kubectl configuration for Lambda Labs K3s"""
    print("\n🔧 Setting up kubectl configuration...")

    # Get kubeconfig from K3s server
    result = run_command(
        f"ssh -i {SSH_KEY} ubuntu@{K3S_SERVER} 'sudo cat /etc/rancher/k3s/k3s.yaml'",
        check=False,
    )

    if result.returncode != 0:
        print("❌ Failed to get kubeconfig from K3s server")
        return False

    # Save kubeconfig locally
    kubeconfig = result.stdout.replace("127.0.0.1", K3S_SERVER)
    kubeconfig_path = os.path.expanduser("~/.kube/k3s-lambda-labs")

    os.makedirs(os.path.dirname(kubeconfig_path), exist_ok=True)
    with open(kubeconfig_path, "w") as f:
        f.write(kubeconfig)

    # Export KUBECONFIG
    os.environ["KUBECONFIG"] = kubeconfig_path
    print("✅ kubectl configured for Lambda Labs K3s")
    return True


def build_and_push_images():
    """Build and push Docker images"""
    print("\n🐳 Building Docker images...")

    # For now, we'll use public images or skip this step
    # In production, you'd push to a registry accessible by K3s
    print("⚠️  Using pre-built images for now")
    return True


def label_mcp_node():
    """Label the MCP node for proper scheduling"""
    print("\n🏷️  Labeling MCP node...")

    # Get nodes
    result = run_command("kubectl get nodes -o wide", check=False)
    if result.returncode != 0:
        print("❌ Failed to get nodes")
        return False

    # Find node with MCP IP (104.171.202.117)
    for line in result.stdout.split("\n"):
        if "104.171.202.117" in line:
            node_name = line.split()[0]
            run_command(
                f"kubectl label node {node_name} kubernetes.io/hostname=sophia-mcp-orchestrator --overwrite"
            )
            print(f"✅ Labeled node {node_name} as sophia-mcp-orchestrator")
            return True

    print("⚠️  MCP node not found in cluster")
    return False


def deploy_backend():
    """Deploy backend to K3s"""
    print("\n🚀 Deploying Backend...")

    # Create backend deployment YAML
    backend_yaml = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: sophia-env
  namespace: sophia-ai-prod
data:
  ENVIRONMENT: "prod"
  SNOWFLAKE_ACCOUNT: "{os.getenv('SNOWFLAKE_ACCOUNT', 'UHDECNO-CVB64222')}"
  SNOWFLAKE_USER: "{os.getenv('SNOWFLAKE_USER', 'SCOOBYJAVA15')}"
  SNOWFLAKE_WAREHOUSE: "{os.getenv('SNOWFLAKE_WAREHOUSE', 'SOPHIA_AI_COMPUTE_WH')}"
  SNOWFLAKE_DATABASE: "{os.getenv('SNOWFLAKE_DATABASE', 'AI_MEMORY')}"
  SNOWFLAKE_SCHEMA: "{os.getenv('SNOWFLAKE_SCHEMA', 'VECTORS')}"
  SNOWFLAKE_ROLE: "{os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')}"
---
apiVersion: v1
kind: Secret
metadata:
  name: sophia-secrets
  namespace: sophia-ai-prod
type: Opaque
data:
  SNOWFLAKE_PASSWORD: {base64.b64encode(os.getenv('SNOWFLAKE_PASSWORD', '').encode()).decode()}
  SNOWFLAKE_PAT: {base64.b64encode(os.getenv('SNOWFLAKE_PAT', '').encode()).decode()}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sophia-backend
  namespace: sophia-ai-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sophia-backend
  template:
    metadata:
      labels:
        app: sophia-backend
    spec:
      containers:
      - name: backend
        image: python:3.12-slim
        command: ["/bin/bash", "-c"]
        args:
        - |
          apt-get update && apt-get install -y git
          git clone https://github.com/ai-cherry/sophia-main.git /app
          cd /app
          pip install -r requirements.txt
          python backend/app/unified_chat_backend.py
        ports:
        - containerPort: 8001
        envFrom:
        - configMapRef:
            name: sophia-env
        - secretRef:
            name: sophia-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
---
apiVersion: v1
kind: Service
metadata:
  name: sophia-backend
  namespace: sophia-ai-prod
spec:
  selector:
    app: sophia-backend
  ports:
  - port: 8001
    targetPort: 8001
  type: LoadBalancer
"""

    # Apply the deployment
    with open("/tmp/backend-deploy.yaml", "w") as f:
        f.write(backend_yaml)

    run_command(
        "kubectl create namespace sophia-ai-prod --dry-run=client -o yaml | kubectl apply -f -"
    )
    run_command("kubectl apply -f /tmp/backend-deploy.yaml")

    print("✅ Backend deployment applied")


def deploy_mcp_servers():
    """Deploy MCP servers to K3s"""
    print("\n🤖 Deploying MCP Servers...")

    # Apply existing MCP deployments with updated images
    run_command("kubectl apply -f kubernetes/production/mcp-*.yaml")

    print("✅ MCP server deployments applied")


def deploy_frontend():
    """Deploy frontend using nginx on K3s"""
    print("\n🌐 Deploying Frontend...")

    # Build frontend
    print("Building frontend...")
    os.chdir("frontend")
    run_command("npm install")
    run_command("npm run build")
    os.chdir("..")

    # Create nginx deployment for frontend
    frontend_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sophia-frontend
  namespace: sophia-ai-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sophia-frontend
  template:
    metadata:
      labels:
        app: sophia-frontend
    spec:
      containers:
      - name: frontend
        image: nginx:alpine
        ports:
        - containerPort: 80
        volumeMounts:
        - name: frontend-dist
          mountPath: /usr/share/nginx/html
      volumes:
      - name: frontend-dist
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: sophia-frontend
  namespace: sophia-ai-prod
spec:
  selector:
    app: sophia-frontend
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
"""

    with open("/tmp/frontend-deploy.yaml", "w") as f:
        f.write(frontend_yaml)

    run_command("kubectl apply -f /tmp/frontend-deploy.yaml")

    # Copy frontend files to the pod (this is a simplified approach)
    print("⚠️  Frontend deployment created - manual file copy needed")

    print("✅ Frontend deployment applied")


def check_deployment_status():
    """Check deployment status"""
    print("\n📊 Checking Deployment Status...")

    # Get all pods
    run_command("kubectl get pods -n sophia-ai-prod -o wide")

    # Get services
    run_command("kubectl get svc -n sophia-ai-prod")

    # Get external IPs
    result = run_command(
        'kubectl get svc -n sophia-ai-prod -o json | jq -r \'.items[] | select(.spec.type=="LoadBalancer") | "\\(.metadata.name): \\(.status.loadBalancer.ingress[0].ip // "pending")"\'',
        check=False,
    )


def main():
    print("🚀 DEPLOYING TO LAMBDA LABS K3S CLUSTER")
    print("=" * 50)

    # Check SSH key
    if not os.path.exists(SSH_KEY):
        print(f"❌ SSH key not found: {SSH_KEY}")
        sys.exit(1)

    # Setup kubectl
    if not setup_kubectl():
        print("❌ Failed to setup kubectl")
        sys.exit(1)

    # Label MCP node
    label_mcp_node()

    # Deploy components
    deploy_backend()
    deploy_mcp_servers()
    deploy_frontend()

    # Check status
    check_deployment_status()

    print("\n✅ DEPLOYMENT INITIATED!")
    print("Monitor with: kubectl get pods -n sophia-ai-prod -w")
    print("Logs: kubectl logs -n sophia-ai-prod <pod-name>")


if __name__ == "__main__":
    main()
