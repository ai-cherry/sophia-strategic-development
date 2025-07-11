#!/usr/bin/env python3
"""
Deploy Sophia AI Backend to Vercel Serverless Functions
Easier than AWS Lambda - uses your existing Vercel account!
"""

import json
import shutil
from pathlib import Path


def create_vercel_api_structure():
    """Create Vercel API structure"""
    # Create api directory
    api_dir = Path("api")
    api_dir.mkdir(exist_ok=True)

    # Create main API handler
    api_handler = '''"""
Vercel Serverless Function for Sophia AI Backend
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.app.unified_chat_backend import app as fastapi_app

# Export the FastAPI app for Vercel
app = fastapi_app

# Health check endpoint
async def handler(request: Request):
    """Vercel serverless handler"""
    # For Vercel, we need to handle the request differently
    return JSONResponse({"message": "Use specific endpoints like /api/health"})
'''

    with open("api/index.py", "w") as f:
        f.write(api_handler)

    # Create specific endpoint handlers
    endpoints = {
        "health.py": """from backend.app.unified_chat_backend import app
from fastapi.responses import JSONResponse

async def handler(request, response):
    return JSONResponse({"status": "healthy", "service": "sophia-ai-backend", "version": "4.0.0"})
""",
        "chat.py": """import json
from backend.app.unified_chat_backend import app
from backend.services.sophia_unified_orchestrator import get_unified_orchestrator

async def handler(request, response):
    if request.method != "POST":
        return JSONResponse({"error": "Method not allowed"}, status_code=405)
    
    try:
        body = json.loads(request.body)
        orchestrator = get_unified_orchestrator()
        result = await orchestrator.process_request(
            query=body.get("query", ""),
            user_id=body.get("user_id", "user_default"),
            conversation_id=body.get("conversation_id"),
            context=body.get("context", {})
        )
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
""",
        "docs.py": '''from fastapi.responses import HTMLResponse

async def handler(request, response):
    return HTMLResponse("""
    <html>
    <head><title>Sophia AI API</title></head>
    <body>
        <h1>Sophia AI Backend API</h1>
        <h2>Available Endpoints:</h2>
        <ul>
            <li>GET /api/health - Health check</li>
            <li>POST /api/chat - Chat with AI</li>
            <li>GET /api/status - System status</li>
        </ul>
    </body>
    </html>
    """)
''',
    }

    for filename, content in endpoints.items():
        with open(f"api/{filename}", "w") as f:
            f.write(content)

    print("✅ Created Vercel API structure")


def create_vercel_json():
    """Create vercel.json configuration"""
    vercel_config = {
        "version": 2,
        "builds": [{"src": "api/*.py", "use": "@vercel/python"}],
        "routes": [{"src": "/api/(.*)", "dest": "/api/$1"}],
        "env": {
            "ENVIRONMENT": "prod",
            "SNOWFLAKE_ACCOUNT": "@snowflake-account",
            "SNOWFLAKE_USER": "@snowflake-user",
            "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE": "@snowflake-passphrase",
            "REDIS_URL": "@redis-url",
            "OPENAI_API_KEY": "@openai-api-key",
            "ANTHROPIC_API_KEY": "@anthropic-api-key",
        },
        "functions": {"api/*.py": {"maxDuration": 30, "memory": 1024}},
    }

    with open("vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)

    print("✅ Created vercel.json")


def create_requirements():
    """Create minimal requirements for Vercel"""
    requirements = """fastapi==0.115.5
uvicorn[standard]==0.32.1
pydantic==2.10.5
redis==5.2.2
snowflake-connector-python==3.16.0
httpx==0.28.1
python-multipart==0.0.12
openai==1.30.5
anthropic==0.45.0
"""

    with open("requirements.txt", "w") as f:
        f.write(requirements)

    print("✅ Created requirements.txt")


def main():
    print("🚀 DEPLOYING SOPHIA AI BACKEND TO VERCEL SERVERLESS")
    print("=" * 50)
    print("This is MUCH easier than AWS Lambda!")
    print()

    # Create structure
    create_vercel_api_structure()
    create_vercel_json()
    create_requirements()

    # Copy backend directory
    if not Path("backend").exists() and Path("../backend").exists():
        print("📦 Copying backend directory...")
        shutil.copytree("../backend", "backend")

    print("\n✅ READY TO DEPLOY!")
    print("=" * 50)
    print("\n1️⃣ First, add secrets to Vercel:")
    print("   vercel secrets add snowflake-account UHDECNO-CVB64222")
    print("   vercel secrets add snowflake-user SCOOBYJAVA15")
    print("   vercel secrets add snowflake-passphrase <your-passphrase>")
    print("   vercel secrets add redis-url <your-redis-url>")
    print("   vercel secrets add openai-api-key <your-key>")
    print("   vercel secrets add anthropic-api-key <your-key>")
    print("\n2️⃣ Deploy:")
    print("   vercel --prod")
    print("\n3️⃣ Your API will be at:")
    print("   https://your-project.vercel.app/api/health")
    print("   https://your-project.vercel.app/api/chat")
    print("   https://your-project.vercel.app/api/docs")
    print("\n✨ Benefits:")
    print("   - Zero configuration")
    print("   - Automatic HTTPS")
    print("   - Global CDN")
    print("   - Generous free tier")
    print("   - Easy secret management")


if __name__ == "__main__":
    main()
