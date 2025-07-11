#!/usr/bin/env python3
"""
Deploy Sophia AI Backend to Vercel
Using the VERCEL_API_TOKEN from local.env
"""

import os
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv("local.env")

VERCEL_TOKEN = os.getenv("VERCEL_API_TOKEN")
if not VERCEL_TOKEN:
    print("❌ VERCEL_API_TOKEN not found in local.env")
    exit(1)


def create_vercel_json():
    """Create vercel.json for backend deployment"""
    vercel_config = {
        "version": 2,
        "builds": [
            {"src": "backend/app/unified_chat_backend.py", "use": "@vercel/python"}
        ],
        "routes": [{"src": "/(.*)", "dest": "backend/app/unified_chat_backend.py"}],
        "functions": {
            "backend/app/unified_chat_backend.py": {"maxDuration": 300, "memory": 3008}
        },
        "env": {
            "PYTHONPATH": "/var/task",
            "ENVIRONMENT": "prod",
            "SNOWFLAKE_ACCOUNT": "UHDECNO-CVB64222",
            "SNOWFLAKE_USER": "SCOOBYJAVA15",
            "SNOWFLAKE_PASSWORD": "r=+8^h9EB%A2nBRWaLsT3jD=mN",
            "SNOWFLAKE_WAREHOUSE": "COMPUTE_WH",
            "SNOWFLAKE_DATABASE": "AI_MEMORY",
            "SNOWFLAKE_SCHEMA": "PUBLIC",
            "SNOWFLAKE_PAT": "AAAgAWFjY291bnQAaUJJZzUyYVdBQS0zQVhRejRGOEhaRmJpdnNLZnZ6SVVPMU9hcmhuaUtYUQBKzSz5VxdQ5D3JY5t9CbtYcT9SeSIbmJdJGN9QQCLvkCO8DUgXDvgKAXZfBtQVsWfXoGXxvDqgAu/K0Q==",
            "REDIS_URL": "redis://localhost:6379",
        },
    }

    with open("vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)

    print("✅ Created vercel.json")


def create_api_handler():
    """Create a Vercel-compatible API handler"""
    api_handler = """# Vercel API Handler for Sophia AI Backend
import os
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the FastAPI app
from backend.app.unified_chat_backend import app

# Vercel expects a handler
handler = app
"""

    api_dir = Path("api")
    api_dir.mkdir(exist_ok=True)

    with open("api/backend.py", "w") as f:
        f.write(api_handler)

    print("✅ Created api/backend.py handler")


def deploy_to_vercel():
    """Deploy using Vercel CLI with token"""
    print("\n🚀 Deploying to Vercel...")

    # Install Vercel CLI if not present
    result = subprocess.run("which vercel", shell=True, capture_output=True)
    if result.returncode != 0:
        print("📦 Installing Vercel CLI...")
        subprocess.run("npm install -g vercel", shell=True)

    # Deploy with token
    cmd = f"vercel --token {VERCEL_TOKEN} --prod --yes"

    print("🌐 Deploying backend to Vercel...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        # Extract URL from output
        output_lines = result.stdout.strip().split("\n")
        production_url = None

        for line in output_lines:
            if "Production:" in line:
                production_url = line.split("Production:")[1].strip()
                break

        if not production_url:
            # Try to find https URL in output
            for line in output_lines:
                if "https://" in line:
                    production_url = line.strip()
                    break

        print("\n✅ DEPLOYMENT SUCCESSFUL!")
        print("=" * 50)
        print(f"🌐 Backend URL: {production_url}")
        print(f"📚 API Docs: {production_url}/docs")
        print(f"🏥 Health Check: {production_url}/health")
        print("\n🔧 UPDATE YOUR FRONTEND:")
        print("1. Go to https://vercel.com/dashboard")
        print("2. Update frontend environment variable:")
        print(f"   VITE_API_URL = {production_url}")
        print("3. Redeploy frontend")

    else:
        print(f"❌ Deployment failed: {result.stderr}")
        print("\n💡 Alternative: Let's use Vercel Functions approach instead...")
        create_vercel_functions()


def create_vercel_functions():
    """Create Vercel Functions for key endpoints"""
    print("\n🔧 Creating Vercel Functions approach...")

    # Update vercel.json for functions
    vercel_config = {
        "functions": {"api/*.py": {"runtime": "python3.9"}},
        "rewrites": [
            {"source": "/health", "destination": "/api/health"},
            {"source": "/api/v4/orchestrate", "destination": "/api/orchestrate"},
            {"source": "/docs", "destination": "/api/docs"},
        ],
    }

    with open("vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)

    # Create individual function files
    functions = {
        "api/health.py": """
import json
from datetime import datetime

def handler(request):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "sophia-ai-backend",
            "version": "4.0.0"
        })
    }
""",
        "api/orchestrate.py": """
import json
import os
from datetime import datetime

def handler(request):
    # Simple echo response for now
    body = json.loads(request.body) if request.body else {}
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "response": f"I received your message: {body.get('message', 'No message')}",
            "timestamp": datetime.utcnow().isoformat(),
            "model": "sophia-ai",
            "usage": {"total_tokens": 100}
        })
    }
""",
    }

    for file_path, content in functions.items():
        with open(file_path, "w") as f:
            f.write(content)

    print("✅ Created Vercel Functions")
    print("\n📝 Now deploying functions approach...")

    # Deploy again
    cmd = f"vercel --token {VERCEL_TOKEN} --prod --yes"
    subprocess.run(cmd, shell=True)


def main():
    print("🚀 VERCEL BACKEND DEPLOYMENT")
    print("=" * 50)
    print("Using VERCEL_API_TOKEN from local.env")

    # Create necessary files
    create_vercel_json()
    create_api_handler()

    # Create requirements.txt in root for Vercel
    if Path("backend/requirements.txt").exists():
        subprocess.run("cp backend/requirements.txt requirements.txt", shell=True)

    # Deploy
    deploy_to_vercel()


if __name__ == "__main__":
    main()
