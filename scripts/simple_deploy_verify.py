#!/usr/bin/env python3
"""
Simple Sophia AI deployment with basic verification
"""
import os
import sys
import time
import subprocess
import requests
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"


def print_status(message: str, level: str = "INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "HEADER": "\033[95m",
    }
    print(f"{colors.get(level, '')}[{level}] {message}\033[0m")


def run_command(cmd, cwd=None, check=False):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if check and result.returncode != 0:
            print_status(f"Command failed: {' '.join(cmd)}", "ERROR")
            print_status(f"Error: {result.stderr}", "ERROR")
            return False
        return True
    except Exception as e:
        print_status(f"Failed to run command: {e}", "ERROR")
        return False


def check_url(url, timeout=30):
    """Check if a URL is accessible"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False


def kill_port(port):
    """Kill process on port"""
    run_command(["lsof", "-ti", f":{port}"], check=False)
    result = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
    if result.stdout.strip():
        subprocess.run(["kill", "-9", result.stdout.strip()], capture_output=True)
        time.sleep(1)


def main():
    print_status("🚀 Starting Sophia AI Deployment", "HEADER")

    # Change to project directory
    os.chdir(BASE_DIR)

    # Kill existing processes
    print_status("Cleaning up existing processes...", "INFO")
    kill_port(8001)  # Backend
    kill_port(5173)  # Frontend

    # Check Redis
    print_status("Checking Redis...", "INFO")
    redis_check = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True)
    if redis_check.returncode == 0 and redis_check.stdout.strip() == "PONG":
        print_status("Redis is running", "SUCCESS")
    else:
        print_status("Redis is not running - please start Redis first", "ERROR")
        sys.exit(1)

    # Load environment
    print_status("Loading environment variables...", "INFO")
    if (BASE_DIR / "local.env").exists():
        # Source the environment file
        env_cmd = f"source {BASE_DIR}/local.env && env"
        result = subprocess.run(["bash", "-c", env_cmd], capture_output=True, text=True)
        if result.returncode == 0:
            print_status("Environment loaded", "SUCCESS")

    # Start backend
    print_status("Starting backend API...", "INFO")
    backend_process = subprocess.Popen(
        ["python", "backend/app/unified_chat_backend.py"],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait and check backend
    print_status("Waiting for backend to start...", "INFO")
    if check_url("http://localhost:8001/health", timeout=20):
        print_status("✅ Backend is running at http://localhost:8001", "SUCCESS")
        print_status("   API Docs: http://localhost:8001/docs", "INFO")
    else:
        print_status("❌ Backend failed to start", "ERROR")
        # Get error output
        backend_process.terminate()
        stdout, stderr = backend_process.communicate()
        print_status(f"Backend output: {stderr[:500]}", "ERROR")
        sys.exit(1)

    # Check if npm is installed in frontend
    print_status("Checking frontend setup...", "INFO")
    if not (FRONTEND_DIR / "node_modules").exists():
        print_status("Installing frontend dependencies...", "INFO")
        if run_command(["npm", "install"], cwd=FRONTEND_DIR, check=True):
            print_status("Frontend dependencies installed", "SUCCESS")
        else:
            print_status("Failed to install frontend dependencies", "ERROR")
            backend_process.terminate()
            sys.exit(1)

    # Start frontend
    print_status("Starting frontend...", "INFO")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait for frontend
    print_status("Waiting for frontend to start...", "INFO")
    time.sleep(10)  # Give it more time

    # Check if frontend is accessible
    if check_url("http://localhost:5173", timeout=20):
        print_status("✅ Frontend is running at http://localhost:5173", "SUCCESS")
    else:
        print_status(
            "⚠️  Frontend may still be starting or running on a different port",
            "WARNING",
        )
        # Check common alternative ports
        for port in [3000, 5174, 5175]:
            if check_url(f"http://localhost:{port}", timeout=5):
                print_status(f"✅ Frontend found at http://localhost:{port}", "SUCCESS")
                break

    # Summary
    print_status("\n=== DEPLOYMENT SUMMARY ===", "HEADER")
    print_status("Backend API: http://localhost:8001", "INFO")
    print_status("API Docs: http://localhost:8001/docs", "INFO")
    print_status("Frontend: http://localhost:5173 (or check console output)", "INFO")

    # Test backend endpoints
    print_status("\nTesting backend endpoints...", "INFO")
    test_endpoints = [
        ("Health", "http://localhost:8001/health"),
        ("System Status", "http://localhost:8001/api/v3/system/status"),
        ("API Docs", "http://localhost:8001/docs"),
    ]

    for name, url in test_endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_status(f"✅ {name}: {response.status_code} OK", "SUCCESS")
            else:
                print_status(f"⚠️  {name}: {response.status_code}", "WARNING")
        except Exception as e:
            print_status(f"❌ {name}: Failed - {str(e)}", "ERROR")

    print_status("\nPress Ctrl+C to stop all services", "INFO")

    try:
        # Keep processes running
        while True:
            # Check if processes are still alive
            if backend_process.poll() is not None:
                print_status("Backend process died!", "ERROR")
                break
            if frontend_process.poll() is not None:
                print_status("Frontend process died!", "WARNING")
            time.sleep(5)
    except KeyboardInterrupt:
        print_status("\nShutting down...", "WARNING")
        backend_process.terminate()
        frontend_process.terminate()
        print_status("Services stopped", "INFO")


if __name__ == "__main__":
    main()
