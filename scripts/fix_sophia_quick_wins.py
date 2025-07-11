#!/usr/bin/env python3
"""
SOPHIA AI QUICK FIXES - Before We Go Full K3s
"Fix the bleeding before the surgery"
"""

import subprocess
import json
from pathlib import Path


class SophiaQuickFixes:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.frontend_dir = self.root_dir / "frontend"
        self.backend_dir = self.root_dir / "backend"

    def print_header(self, text):
        print(f"\n{'='*60}")
        print(f"🔧 {text}")
        print(f"{'='*60}\n")

    def run_command(self, cmd, cwd=None):
        """Run command and return success status"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, cwd=cwd
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def fix_frontend_null_checks(self):
        """Fix the toUpperCase() TypeError"""
        self.print_header("Fixing Frontend Null Checks")

        # Fix UnifiedChatDashboard.tsx
        dashboard_file = (
            self.frontend_dir / "src/components/dashboard/UnifiedChatDashboard.tsx"
        )

        if dashboard_file.exists():
            print(f"Fixing null checks in {dashboard_file}")
            content = dashboard_file.read_text()

            # Fix toUpperCase calls
            content = content.replace(
                "systemStatus.overall_status.toUpperCase()",
                "(systemStatus?.overall_status || 'UNKNOWN').toUpperCase()",
            )
            content = content.replace(
                "status.toUpperCase()", "(status || 'UNKNOWN').toUpperCase()"
            )

            # Add optional chaining for all status accesses
            content = content.replace("systemStatus.backend", "systemStatus?.backend")
            content = content.replace(
                "systemStatus.mcp_servers", "systemStatus?.mcp_servers"
            )

            dashboard_file.write_text(content)
            print("✅ Fixed null checks in UnifiedChatDashboard")
        else:
            print("❌ UnifiedChatDashboard.tsx not found")

    def fix_backend_cors(self):
        """Add proper CORS configuration to backend"""
        self.print_header("Fixing Backend CORS")

        backend_file = self.backend_dir / "app/unified_chat_backend.py"

        if backend_file.exists():
            print(f"Adding CORS to {backend_file}")
            content = backend_file.read_text()

            # Check if CORS is already configured
            if "CORSMiddleware" not in content:
                # Find the app creation line
                app_line_index = content.find("app = FastAPI(")
                if app_line_index != -1:
                    # Find the end of app creation
                    end_index = content.find("\n\n", app_line_index)

                    # Insert CORS configuration
                    cors_config = """
# CORS Configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://sophia-intel.ai",
        "https://www.sophia-intel.ai",
        "https://*.vercel.app"  # Allow Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""
                    content = content[:end_index] + cors_config + content[end_index:]
                    backend_file.write_text(content)
                    print("✅ Added CORS configuration")
            else:
                print("✅ CORS already configured")
        else:
            print("❌ unified_chat_backend.py not found")

    def create_env_files(self):
        """Create proper .env files for local development"""
        self.print_header("Creating Environment Files")

        # Backend .env
        backend_env = self.backend_dir / ".env"
        backend_env_content = """# Sophia AI Backend Configuration
ENVIRONMENT=prod
SNOWFLAKE_ACCOUNT=UHDECNO-CVB64222
SNOWFLAKE_USER=SCOOBYJAVA15
SNOWFLAKE_PASSWORD=your_password_here
SNOWFLAKE_DATABASE=SOPHIA_AI_PRODUCTION
SNOWFLAKE_WAREHOUSE=SOPHIA_AI_COMPUTE_WH_MAIN
SNOWFLAKE_SCHEMA=PAYREADY_SALESIQ
REDIS_HOST=localhost
REDIS_PORT=6379
"""

        if not backend_env.exists():
            backend_env.write_text(backend_env_content)
            print("✅ Created backend/.env (add your Snowflake password)")
        else:
            print("✅ backend/.env already exists")

        # Frontend .env for local development
        frontend_env = self.frontend_dir / ".env"
        frontend_env_content = """# Sophia AI Frontend Configuration
VITE_API_URL=http://localhost:8001
VITE_APP_NAME=Sophia AI
VITE_ENVIRONMENT=development
VITE_DEBUG_MODE=true
"""

        if not frontend_env.exists():
            frontend_env.write_text(frontend_env_content)
            print("✅ Created frontend/.env for local development")
        else:
            print("✅ frontend/.env already exists")

    def create_docker_files(self):
        """Create optimized Dockerfiles"""
        self.print_header("Creating Docker Files")

        # Backend Dockerfile
        backend_dockerfile = self.backend_dir / "Dockerfile"
        backend_dockerfile_content = """FROM python:3.12-slim

# Install build dependencies for snowflake-connector
RUN apt-get update && apt-get install -y \\
    build-essential \\
    g++ \\
    libssl-dev \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "app.unified_chat_backend:app", "--host", "0.0.0.0", "--port", "8001"]
"""

        backend_dockerfile.write_text(backend_dockerfile_content)
        print("✅ Created backend/Dockerfile")

        # MCP Base Dockerfile
        mcp_dockerfile = self.root_dir / "mcp-servers/Dockerfile.base"
        mcp_dockerfile_content = """FROM python:3.12-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    g++ \\
    libssl-dev \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy base requirements
COPY base/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy base classes
COPY base/ ./base/

# This will be extended by each MCP server
"""

        mcp_dockerfile.parent.mkdir(exist_ok=True)
        mcp_dockerfile.write_text(mcp_dockerfile_content)
        print("✅ Created MCP base Dockerfile")

    def create_mcp_manifests(self):
        """Create K8s manifests for MCP servers"""
        self.print_header("Creating MCP K8s Manifests")

        k8s_dir = self.root_dir / "k8s-deployment/mcp-servers"
        k8s_dir.mkdir(parents=True, exist_ok=True)

        mcp_servers = [
            {"name": "ai-memory", "port": 9001},
            {"name": "codacy", "port": 3008},
            {"name": "github", "port": 9003},
            {"name": "linear", "port": 9004},
            {"name": "asana", "port": 9006},
            {"name": "notion", "port": 9102},
            {"name": "slack", "port": 9101},
        ]

        for mcp in mcp_servers:
            manifest = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-{mcp['name']}
  namespace: sophia-ai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mcp-{mcp['name']}
  template:
    metadata:
      labels:
        app: mcp-{mcp['name']}
    spec:
      containers:
      - name: {mcp['name']}
        image: scoobyjava15/mcp-{mcp['name']}:latest
        ports:
        - containerPort: {mcp['port']}
        envFrom:
        - secretRef:
            name: sophia-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: {mcp['port']}
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-{mcp['name']}-service
  namespace: sophia-ai
spec:
  selector:
    app: mcp-{mcp['name']}
  ports:
  - port: {mcp['port']}
    targetPort: {mcp['port']}
"""

            manifest_file = k8s_dir / f"{mcp['name']}.yaml"
            manifest_file.write_text(manifest)

        print(f"✅ Created {len(mcp_servers)} MCP manifests in {k8s_dir}")

    def create_vercel_config(self):
        """Create Vercel configuration"""
        self.print_header("Creating Vercel Configuration")

        vercel_json = self.frontend_dir / "vercel.json"
        vercel_config = {
            "buildCommand": "npm run build",
            "outputDirectory": "dist",
            "framework": "vite",
            "rewrites": [{"source": "/(.*)", "destination": "/index.html"}],
            "env": {"VITE_API_URL": "https://api.sophia-intel.ai"},
        }

        vercel_json.write_text(json.dumps(vercel_config, indent=2))
        print("✅ Created vercel.json")

    def create_github_actions(self):
        """Create GitHub Actions deployment workflow"""
        self.print_header("Creating GitHub Actions Workflow")

        workflow_dir = self.root_dir / ".github/workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)

        workflow = workflow_dir / "deploy-sophia.yaml"
        workflow_content = """name: Deploy Sophia AI

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_HUB_USERNAME }}
        password: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}
    
    - name: Build and Push Backend
      run: |
        cd backend
        docker build -t scoobyjava15/sophia-backend:latest .
        docker push scoobyjava15/sophia-backend:latest
    
    - name: Deploy to K3s
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: 104.171.202.117
        username: ubuntu
        key: ${{ secrets.LAMBDA_SSH_KEY }}
        script: |
          export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
          kubectl rollout restart deployment/sophia-backend -n sophia-ai
  
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Vercel
      run: |
        npm i -g vercel
        cd frontend
        vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
"""

        workflow.write_text(workflow_content)
        print("✅ Created GitHub Actions workflow")

    def run_all_fixes(self):
        """Run all quick fixes"""
        print("\n🚀 SOPHIA AI QUICK FIXES - NO BS EDITION")
        print("=" * 60)

        self.fix_frontend_null_checks()
        self.fix_backend_cors()
        self.create_env_files()
        self.create_docker_files()
        self.create_mcp_manifests()
        self.create_vercel_config()
        self.create_github_actions()

        print("\n✅ ALL QUICK FIXES APPLIED!")
        print("\n📋 Next Steps:")
        print("1. Add your Snowflake password to backend/.env")
        print("2. Run the backend: cd backend && python app/unified_chat_backend.py")
        print("3. Run the frontend: cd frontend && npm run dev")
        print("4. Test locally before deploying to K3s")
        print("\n🚀 Then run: bash scripts/deploy_sophia_k3s_battle_plan.sh")
        print("\n💀 Remember: If it breaks, blame the MCP servers!")


if __name__ == "__main__":
    fixer = SophiaQuickFixes()
    fixer.run_all_fixes()
