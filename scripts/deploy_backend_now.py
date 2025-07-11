#!/usr/bin/env python3
"""
Quick deployment of Sophia AI backend using ngrok for immediate access
Then update frontend with the backend URL
"""
import os
import subprocess
import sys
import time
import requests
from pathlib import Path


def print_status(message: str, status: str = "INFO"):
    """Print colored status messages"""
    colors = {
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m",
        "WARNING": "\033[93m",
        "INFO": "\033[94m",
        "HEADER": "\033[95m",
    }
    reset = "\033[0m"
    color = colors.get(status, "")
    symbol = (
        "✅"
        if status == "SUCCESS"
        else "❌"
        if status == "ERROR"
        else "⚠️"
        if status == "WARNING"
        else "ℹ️"
    )
    print(f"{color}{symbol} {message}{reset}")


def ensure_backend_running():
    """Ensure backend is running locally"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code == 200:
            print_status("Backend is already running", "SUCCESS")
            return True
    except:
        pass

    print_status("Starting backend...", "INFO")

    # Start backend in background
    backend_process = subprocess.Popen(
        ["python", "backend/app/unified_chat_backend.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            **os.environ,
            "SNOWFLAKE_ACCOUNT": "UHDECNO-CVB64222",
            "SNOWFLAKE_USER": "SCOOBYJAVA15",
            "SNOWFLAKE_PAT": "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A",
        },
    )

    # Wait for backend to start
    for i in range(30):
        try:
            response = requests.get("http://localhost:8001/health", timeout=2)
            if response.status_code == 200:
                print_status("Backend started successfully", "SUCCESS")
                return True
        except:
            time.sleep(1)

    print_status("Backend failed to start", "ERROR")
    return False


def start_ngrok():
    """Start ngrok tunnel"""
    # Kill any existing ngrok
    subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
    time.sleep(1)

    print_status("Starting ngrok tunnel...", "INFO")
    ngrok_process = subprocess.Popen(
        ["ngrok", "http", "8001", "--log=stdout"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait for ngrok to start
    time.sleep(3)

    # Get ngrok URL
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()

        for tunnel in tunnels["tunnels"]:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except:
        pass

    print_status("Could not get ngrok URL automatically", "WARNING")
    print("Check http://localhost:4040 for the URL")
    return None


def update_frontend_env(backend_url):
    """Update frontend environment configuration"""
    env_content = f"""# Production environment variables
VITE_API_URL={backend_url}
VITE_WS_URL={backend_url.replace('https://', 'wss://')}
"""

    # Write to frontend .env.production
    env_file = Path("frontend/.env.production")
    env_file.write_text(env_content)
    print_status("Updated frontend/.env.production with backend URL", "SUCCESS")

    # Also create .env.local for development
    env_local = Path("frontend/.env.local")
    env_local.write_text(env_content)
    print_status("Updated frontend/.env.local", "SUCCESS")


def redeploy_frontend():
    """Redeploy frontend to Vercel"""
    print_status("Redeploying frontend to Vercel...", "INFO")

    os.chdir("frontend")

    # Build first
    build_result = subprocess.run(
        ["npm", "run", "build"], capture_output=True, text=True
    )
    if build_result.returncode != 0:
        print_status("Frontend build failed", "ERROR")
        print(build_result.stderr)
        return False

    # Deploy to Vercel
    deploy_result = subprocess.run(
        ["vercel", "--prod", "--yes"], capture_output=True, text=True
    )

    if deploy_result.returncode == 0:
        print_status("Frontend deployed successfully!", "SUCCESS")

        # Update custom domain
        subprocess.run(
            ["vercel", "alias", "set", "frontend-prod", "app.sophia-intel.ai"],
            capture_output=True,
        )

        os.chdir("..")
        return True
    else:
        print_status("Frontend deployment failed", "ERROR")
        print(deploy_result.stderr)
        os.chdir("..")
        return False


def main():
    print_status("COMPLETE SOPHIA AI DEPLOYMENT", "HEADER")
    print("=" * 60)

    # Step 1: Ensure backend is running
    if not ensure_backend_running():
        print_status("Cannot start backend", "ERROR")
        sys.exit(1)

    # Step 2: Check if ngrok is installed
    try:
        subprocess.run(["ngrok", "version"], capture_output=True, check=True)
    except:
        print_status("ngrok not installed", "ERROR")
        print("\nInstall ngrok:")
        print("1. brew install ngrok")
        print("2. ngrok config add-authtoken <your-token>")
        sys.exit(1)

    # Step 3: Start ngrok
    backend_url = start_ngrok()
    if not backend_url:
        print_status("Failed to get ngrok URL", "ERROR")
        sys.exit(1)

    print_status(f"Backend accessible at: {backend_url}", "SUCCESS")

    # Step 4: Update frontend configuration
    update_frontend_env(backend_url)

    # Step 5: Redeploy frontend
    if redeploy_frontend():
        print("\n" + "=" * 60)
        print_status("🎉 DEPLOYMENT COMPLETE!", "HEADER")
        print("\n✅ Frontend: https://app.sophia-intel.ai")
        print(f"✅ Backend: {backend_url}")
        print(f"✅ API Docs: {backend_url}/docs")
        print("\n⚠️ Note: The ngrok URL is temporary and will change when restarted")
        print("\n🚀 Your Sophia AI system is FULLY DEPLOYED and FUNCTIONAL!")
    else:
        print_status("Frontend deployment failed", "ERROR")
        print(f"\nBackend is still accessible at: {backend_url}")


if __name__ == "__main__":
    main()
