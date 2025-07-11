#!/usr/bin/env python3
"""
Deploy Sophia AI Backend to Vercel Serverless - INSTANT!
"""

import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv("local.env")


def set_vercel_env_vars():
    """Set environment variables in Vercel"""
    env_vars = {
        "ENVIRONMENT": "prod",
        "SNOWFLAKE_ACCOUNT": "UHDECNO-CVB64222",
        "SNOWFLAKE_USER": "SCOOBYJAVA15",
        "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE": os.getenv(
            "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", ""
        ),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "REDIS_URL": "redis://localhost:6379",  # For now, will need proper Redis later
    }

    print("🔐 Setting environment variables in Vercel...")
    for key, value in env_vars.items():
        if value:
            cmd = f'vercel env add {key} production --force < <(echo "{value}")'
            subprocess.run(cmd, shell=True, executable="/bin/bash")
            print(f"   ✅ Set {key}")
        else:
            print(f"   ⚠️  Skipped {key} (no value)")


def deploy():
    """Deploy to Vercel"""
    print("\n🚀 Deploying to Vercel...")

    # First, let's make sure we're in the right directory
    os.chdir(Path(__file__).parent.parent)

    # Deploy with Vercel
    result = subprocess.run(
        "vercel --prod --yes", shell=True, capture_output=True, text=True
    )

    if result.returncode == 0:
        # Extract the URL from output
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if "https://" in line and ".vercel.app" in line:
                url = line.strip()
                if "Production:" in line:
                    url = line.split("Production:")[1].strip()
                    url = url.split()[0]  # Get first URL

                print("\n✅ DEPLOYMENT SUCCESSFUL!")
                print(f"🌐 Your backend is live at: {url}")
                print("📚 API Endpoints:")
                print(f"   - Health: {url}/api/health")
                print(f"   - Chat: {url}/api/chat")
                print(f"   - Docs: {url}/api/docs")
                print("\n🔧 Update your frontend:")
                print(f"   VITE_API_URL={url}")
                return url
    else:
        print(f"❌ Deployment failed: {result.stderr}")
        return None


def main():
    print("🚀 INSTANT VERCEL SERVERLESS DEPLOYMENT")
    print("=" * 50)

    # Check if api directory exists
    if not Path("api").exists():
        print("❌ API directory not found!")
        print("   Run: python scripts/deploy_backend_serverless_vercel.py first")
        return

    # Set environment variables
    set_vercel_env_vars()

    # Deploy
    url = deploy()

    if url:
        print("\n🎉 Your Sophia AI backend is now serverless!")
        print("   - Auto-scaling ✅")
        print("   - Global CDN ✅")
        print("   - HTTPS ✅")
        print("   - Zero maintenance ✅")


if __name__ == "__main__":
    main()
