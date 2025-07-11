#!/usr/bin/env python3
"""
INSTANT Backend Deployment - Works in 30 seconds!
No accounts needed, no complex setup
"""

import subprocess
import os
import time
import requests


def install_ngrok():
    """Install ngrok if not present"""
    result = subprocess.run("which ngrok", shell=True, capture_output=True)
    if result.returncode != 0:
        print("📦 Installing ngrok...")
        if os.path.exists("/opt/homebrew/bin/brew"):
            subprocess.run("brew install ngrok", shell=True)
        else:
            subprocess.run(
                "curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok",
                shell=True,
            )


def main():
    print("🚀 INSTANT SOPHIA AI DEPLOYMENT")
    print("=" * 50)
    print("✨ This will make your backend globally accessible in 30 seconds!")
    print()

    # 1. Check if backend is running
    try:
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code == 200:
            print("✅ Backend is already running on port 8001")
        else:
            raise Exception("Backend not healthy")
    except:
        print("🔄 Starting backend...")
        # Start backend in background
        subprocess.Popen(
            ["python", "backend/app/unified_chat_backend.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        for i in range(30):
            try:
                response = requests.get("http://localhost:8001/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Backend started successfully!")
                    break
            except:
                time.sleep(1)
                continue

    # 2. Install ngrok if needed
    install_ngrok()

    # 3. Start ngrok
    print("\n🌐 Creating public tunnel...")
    ngrok_process = subprocess.Popen(
        ["ngrok", "http", "8001", "--log=stdout"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait for ngrok to start
    time.sleep(3)

    # 4. Get public URL
    try:
        api_response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = api_response.json()
        public_url = tunnels["tunnels"][0]["public_url"]

        # Use HTTPS version
        if public_url.startswith("http://"):
            public_url = public_url.replace("http://", "https://")
    except:
        print("⚠️ Could not get ngrok URL automatically.")
        print("Check http://localhost:4040 for your public URL")
        public_url = "https://YOUR-NGROK-URL.ngrok-free.app"

    print("\n✅ DEPLOYMENT COMPLETE!")
    print("=" * 50)
    print("🌐 Your backend is now LIVE at:")
    print(f"   {public_url}")
    print(f"📚 API Docs: {public_url}/docs")
    print(f"🏥 Health Check: {public_url}/health")
    print()
    print("🔧 UPDATE YOUR FRONTEND:")
    print("1. Go to Vercel Dashboard")
    print("2. Add environment variable:")
    print(f"   VITE_API_URL = {public_url}")
    print("3. Redeploy frontend")
    print()
    print("📝 Or update frontend/.env:")
    print(f"   VITE_API_URL={public_url}")
    print()
    print("⚠️ NOTE: This URL changes when you restart ngrok")
    print("   For permanent URL, use one of these:")
    print("   - Railway (railway.app)")
    print("   - Render (render.com)")
    print("   - Fly.io (fly.io)")
    print()
    print("Press Ctrl+C to stop the tunnel")

    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping tunnel...")
        ngrok_process.terminate()


if __name__ == "__main__":
    main()
