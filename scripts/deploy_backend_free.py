#!/usr/bin/env python3
"""
Deploy Sophia AI Backend to FREE Cloud Services
No Kubernetes, No Complex Setup, Just Works!
"""

import subprocess
import json


def create_simple_backend():
    """Create a simplified backend that works on free tiers"""

    # Create a minimal requirements.txt for free tier limits
    minimal_requirements = """fastapi==0.115.5
uvicorn[standard]==0.32.1
pydantic==2.10.5
redis==5.2.2
snowflake-connector-python==3.16.0
httpx==0.28.1
python-multipart==0.0.12
websockets==14.1
sse-starlette==2.2.0
"""

    with open("backend/requirements.minimal.txt", "w") as f:
        f.write(minimal_requirements)

    # Create Procfile for Railway/Render
    with open("Procfile", "w") as f:
        f.write(
            "web: cd backend && python -m uvicorn app.unified_chat_backend:app --host 0.0.0.0 --port $PORT\n"
        )

    # Create railway.json
    railway_config = {
        "build": {
            "builder": "NIXPACKS",
            "nixpacksPlan": {"phases": {"setup": {"nixPkgs": ["python312", "gcc"]}}},
        },
        "deploy": {
            "runtime": "python",
            "startCommand": "cd backend && python -m uvicorn app.unified_chat_backend:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health",
            "restartPolicyType": "always",
        },
    }

    with open("railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)

    print("✅ Created deployment files")


def deploy_to_railway():
    """Deploy to Railway (free tier available)"""
    print("\n🚂 DEPLOYING TO RAILWAY")
    print("=" * 50)

    # Check if railway CLI is installed
    result = subprocess.run("which railway", shell=True, capture_output=True)
    if result.returncode != 0:
        print("📦 Installing Railway CLI...")
        subprocess.run("curl -fsSL https://railway.app/install.sh | sh", shell=True)

    print(
        """
🔧 MANUAL STEPS REQUIRED:
1. Sign up at https://railway.app (free tier available)
2. Run: railway login
3. Run: railway link (select your project)
4. Run: railway up

Your backend will be deployed with a URL like:
https://your-app.up.railway.app
"""
    )


def deploy_to_render():
    """Deploy to Render (free tier available)"""
    print("\n🎨 DEPLOYING TO RENDER")
    print("=" * 50)

    # Create render.yaml
    render_config = """services:
  - type: web
    name: sophia-ai-backend
    runtime: python
    plan: free
    buildCommand: pip install -r backend/requirements.minimal.txt
    startCommand: cd backend && python -m uvicorn app.unified_chat_backend:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHONPATH
        value: /opt/render/project/src
      - key: ENVIRONMENT
        value: prod
      - key: SNOWFLAKE_ACCOUNT
        value: UHDECNO-CVB64222
      - key: SNOWFLAKE_USER
        value: SCOOBYJAVA15
      - key: SNOWFLAKE_PASSWORD
        value: r=+8^h9EB%A2nBRWaLsT3jD=mN
    healthCheckPath: /health
"""

    with open("render.yaml", "w") as f:
        f.write(render_config)

    print("✅ Created render.yaml")
    print(
        """
🔧 MANUAL STEPS:
1. Push your code to GitHub
2. Go to https://render.com and sign up (free)
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. It will auto-detect render.yaml and deploy!

Your backend will be at:
https://sophia-ai-backend.onrender.com
"""
    )


def deploy_to_fly():
    """Deploy to Fly.io (generous free tier)"""
    print("\n✈️ DEPLOYING TO FLY.IO")
    print("=" * 50)

    # Create fly.toml
    fly_config = """app = "sophia-ai-backend"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile.fly"

[http_service]
  internal_port = 8001
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[env]
  PYTHONPATH = "/app"
  ENVIRONMENT = "prod"
  PORT = "8001"

[[services]]
  protocol = "tcp"
  internal_port = 8001
  
  [[services.ports]]
    port = 80
    handlers = ["http"]
    
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
"""

    with open("fly.toml", "w") as f:
        f.write(fly_config)

    # Create Dockerfile.fly
    dockerfile = """FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.minimal.txt .
RUN pip install --no-cache-dir -r requirements.minimal.txt

COPY backend/ ./backend/
COPY shared/ ./shared/

ENV PYTHONPATH=/app
ENV PORT=8001

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "backend.app.unified_chat_backend:app", "--host", "0.0.0.0", "--port", "8001"]
"""

    with open("Dockerfile.fly", "w") as f:
        f.write(dockerfile)

    print("✅ Created fly.toml and Dockerfile.fly")
    print(
        """
🔧 TO DEPLOY:
1. Install Fly CLI: curl -L https://fly.io/install.sh | sh
2. Run: fly auth signup (or fly auth login)
3. Run: fly launch
4. Run: fly deploy

Your backend will be at:
https://sophia-ai-backend.fly.dev
"""
    )


def main():
    print("🚀 FREE BACKEND DEPLOYMENT OPTIONS")
    print("=" * 50)
    print("\nChoose your deployment platform:")
    print("1. Railway (easiest, good free tier)")
    print("2. Render (GitHub integration, auto-deploy)")
    print("3. Fly.io (best performance, generous free tier)")
    print("4. Create files for all options")

    choice = input("\nEnter your choice (1-4): ").strip()

    create_simple_backend()

    if choice == "1":
        deploy_to_railway()
    elif choice == "2":
        deploy_to_render()
    elif choice == "3":
        deploy_to_fly()
    else:
        deploy_to_railway()
        deploy_to_render()
        deploy_to_fly()
        print("\n✅ Created deployment files for all platforms!")
        print("Choose the one you prefer and follow the manual steps.")

    print("\n💡 AFTER DEPLOYMENT:")
    print("Update your Vercel frontend environment variable:")
    print("VITE_API_URL = https://your-backend-url.com")


if __name__ == "__main__":
    main()
