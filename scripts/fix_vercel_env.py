#!/usr/bin/env python3
"""
Fix Vercel environment variables and redeploy
"""

import subprocess
import os
import time


def main():
    print("🔧 FIXING SOPHIA AI DEPLOYMENT")
    print("=" * 50)

    # Get current ngrok URL
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:4040/api/tunnels"],
            capture_output=True,
            text=True,
        )
        import json

        data = json.loads(result.stdout)
        ngrok_url = data["tunnels"][0]["public_url"]
        print(f"✅ Ngrok URL: {ngrok_url}")
    except:
        print("❌ Ngrok not running!")
        print("   Starting ngrok...")
        subprocess.Popen(["ngrok", "http", "8001"])
        time.sleep(3)
        # Try again
        result = subprocess.run(
            ["curl", "-s", "http://localhost:4040/api/tunnels"],
            capture_output=True,
            text=True,
        )
        import json

        data = json.loads(result.stdout)
        ngrok_url = data["tunnels"][0]["public_url"]
        print(f"✅ Ngrok URL: {ngrok_url}")

    # Update .env.production
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    env_file = os.path.join(frontend_dir, ".env.production")

    env_content = f"""# Sophia AI Production Configuration
VITE_API_URL={ngrok_url}
VITE_APP_NAME=Sophia AI
VITE_APP_VERSION=4.0.0
VITE_ENVIRONMENT=production
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_CHAT=true
VITE_ENABLE_DASHBOARD=true
VITE_WS_URL={ngrok_url.replace('https', 'wss')}/ws
"""

    with open(env_file, "w") as f:
        f.write(env_content)

    print("✅ Updated .env.production")

    # Change to frontend directory
    os.chdir(frontend_dir)

    # Build the project
    print("\n📦 Building frontend...")
    subprocess.run(["npm", "run", "build"], check=True)

    # Deploy to Vercel with environment variable
    print("\n🚀 Deploying to Vercel...")
    subprocess.run(
        ["vercel", "--prod", "--yes", "--env", f"VITE_API_URL={ngrok_url}"], check=True
    )

    print("\n" + "=" * 50)
    print("✅ DEPLOYMENT FIXED!")
    print(f"🌐 Backend API: {ngrok_url}")
    print("\n🎯 Your Sophia AI should now work without errors!")
    print("\n📝 To set up sophia-intel.ai domain:")
    print("1. Go to Vercel dashboard")
    print("2. Add domain sophia-intel.ai")
    print("3. Update Namecheap DNS as instructed")


if __name__ == "__main__":
    main()
