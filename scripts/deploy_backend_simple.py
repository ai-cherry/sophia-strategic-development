#!/usr/bin/env python3
"""
Deploy Sophia AI backend using ngrok for immediate access
"""
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


def check_ngrok():
    """Check if ngrok is installed"""
    try:
        subprocess.run(["ngrok", "version"], capture_output=True, check=True)
        return True
    except:
        return False


def install_ngrok():
    """Install ngrok if not present"""
    print_status("Installing ngrok...", "INFO")
    try:
        subprocess.run(["brew", "install", "ngrok"], check=True)
        print_status("ngrok installed successfully", "SUCCESS")
    except:
        print_status("Failed to install ngrok with brew", "ERROR")
        print("\nManual installation:")
        print("1. Visit https://ngrok.com/download")
        print("2. Download and install ngrok")
        print("3. Run: ngrok config add-authtoken <your-token>")
        sys.exit(1)


def update_frontend_api_url(ngrok_url: str):
    """Update frontend to use ngrok URL"""
    env_file = Path("frontend/.env.production")
    content = f"""VITE_API_URL={ngrok_url}
VITE_WS_URL={ngrok_url.replace('https://', 'wss://')}
"""
    env_file.write_text(content)
    print_status(f"Updated frontend API URL to {ngrok_url}", "SUCCESS")


def main():
    print_status("EXPOSING SOPHIA AI BACKEND", "HEADER")
    print("=" * 60)

    # Check dependencies
    if not check_ngrok():
        install_ngrok()

    # Check if backend is running
    try:
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code != 200:
            print_status("Backend not running on port 8001", "ERROR")
            print("\nStart the backend first:")
            print("python backend/app/unified_chat_backend.py")
            sys.exit(1)
    except:
        print_status("Backend not accessible on port 8001", "ERROR")
        print("\nStart the backend first:")
        print("python backend/app/unified_chat_backend.py")
        sys.exit(1)

    print_status("Backend is running on port 8001", "SUCCESS")

    # Start ngrok
    print_status("Starting ngrok tunnel...", "INFO")
    ngrok_process = subprocess.Popen(
        ["ngrok", "http", "8001", "--log=stdout"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait for ngrok to start and get URL
    time.sleep(3)

    try:
        # Get ngrok URL from API
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()

        for tunnel in tunnels["tunnels"]:
            if tunnel["proto"] == "https":
                ngrok_url = tunnel["public_url"]
                print_status(f"ngrok tunnel created: {ngrok_url}", "SUCCESS")

                # Update frontend configuration
                update_frontend_api_url(ngrok_url)

                print("\n" + "=" * 60)
                print_status("BACKEND EXPOSED", "HEADER")
                print(f"\n🌐 Backend API URL: {ngrok_url}")
                print(f"📚 API Documentation: {ngrok_url}/docs")
                print(f"❤️ Health Check: {ngrok_url}/health")

                print("\n⚠️ IMPORTANT:")
                print("1. This URL is temporary and will change when ngrok restarts")
                print("2. Redeploy frontend to use new backend URL:")
                print("   cd frontend && vercel --prod")

                print("\n✅ Keep this terminal open to maintain the tunnel")
                print("Press Ctrl+C to stop")

                # Keep running
                try:
                    ngrok_process.wait()
                except KeyboardInterrupt:
                    print("\n\nStopping ngrok tunnel...")
                    ngrok_process.terminate()

                return

    except Exception as e:
        print_status(f"Failed to get ngrok URL: {e}", "ERROR")
        print("\nManual steps:")
        print("1. Run: ngrok http 8001")
        print("2. Copy the HTTPS URL")
        print("3. Update frontend/.env.production with VITE_API_URL=<ngrok-url>")
        print("4. Redeploy frontend: cd frontend && vercel --prod")


if __name__ == "__main__":
    main()
