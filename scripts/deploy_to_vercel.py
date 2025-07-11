#!/usr/bin/env python3
"""
Deploy Sophia AI frontend to Vercel
"""
import os
import subprocess
import sys
from pathlib import Path


def print_status(message: str, status: str = "INFO"):
    """Print colored status messages"""
    colors = {
        "SUCCESS": "\033[92m",  # Green
        "ERROR": "\033[91m",  # Red
        "WARNING": "\033[93m",  # Yellow
        "INFO": "\033[94m",  # Blue
        "HEADER": "\033[95m",  # Purple
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


def main():
    print_status("DEPLOYING SOPHIA AI TO VERCEL", "HEADER")
    print("=" * 60)

    # Change to frontend directory
    frontend_dir = Path(__file__).parent.parent / "frontend"
    os.chdir(frontend_dir)

    print_status(f"Working directory: {frontend_dir}")

    # Set environment variables for the build
    env = os.environ.copy()
    env["VITE_API_URL"] = "https://api.sophia-intel.ai"
    env["VITE_WS_URL"] = "wss://api.sophia-intel.ai"

    # Deploy to Vercel
    print_status("Deploying to Vercel...")
    try:
        result = subprocess.run(
            ["vercel", "--prod", "--yes"], env=env, capture_output=True, text=True
        )

        if result.returncode == 0:
            print_status("Deployment successful!", "SUCCESS")
            print("\nDeployment output:")
            print(result.stdout)

            # Extract the URL from output
            for line in result.stdout.splitlines():
                if "https://" in line and "vercel.app" in line:
                    print_status(f"Preview URL: {line.strip()}", "INFO")

            print_status("\n🌐 PRODUCTION URL: https://app.sophia-intel.ai", "SUCCESS")
            print_status("Your app is live and ready to use!", "SUCCESS")

        else:
            print_status("Deployment failed", "ERROR")
            print(result.stderr)
            sys.exit(1)

    except FileNotFoundError:
        print_status("Vercel CLI not found", "ERROR")
        print("Install it with: npm install -g vercel")
        sys.exit(1)
    except Exception as e:
        print_status(f"Error during deployment: {e}", "ERROR")
        sys.exit(1)

    print("\n" + "=" * 60)
    print_status("DEPLOYMENT COMPLETE", "HEADER")
    print("\n📱 Access your app at:")
    print("   Production: https://app.sophia-intel.ai")
    print("   Vercel URL: Check output above")
    print("\n💡 Note: DNS may take a few minutes to propagate")


if __name__ == "__main__":
    main()
