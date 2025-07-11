#!/usr/bin/env python3
"""
Verify Sophia AI deployment and diagnose issues
"""
import os
import requests
import subprocess


def print_status(message: str, status: str):
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


def check_service(name: str, url: str, expected_status=200):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print_status(f"{name} is running at {url}", "SUCCESS")
            return True
        else:
            print_status(f"{name} returned status {response.status_code}", "WARNING")
            return False
    except requests.exceptions.ConnectionError:
        print_status(f"{name} is NOT running at {url}", "ERROR")
        return False
    except Exception as e:
        print_status(f"{name} error: {str(e)}", "ERROR")
        return False


def check_port_listening(port: int, name: str):
    """Check if a port is listening"""
    result = subprocess.run(
        f"lsof -nP -iTCP:{port} -sTCP:LISTEN",
        shell=True,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print_status(f"{name} is listening on port {port}", "SUCCESS")
        return True
    else:
        print_status(f"{name} is NOT listening on port {port}", "ERROR")
        return False


def check_frontend_content():
    """Check frontend is serving the right content"""
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if "root" in response.text and "Sophia AI" in response.text:
            print_status("Frontend HTML content looks correct", "SUCCESS")

            # Check for common issues
            if "Cannot GET /" in response.text:
                print_status("Frontend showing 'Cannot GET /' error", "ERROR")
                return False
            elif response.text.strip() == "":
                print_status("Frontend returning empty response", "ERROR")
                return False

            return True
        else:
            print_status("Frontend HTML content missing expected elements", "WARNING")
            return False
    except Exception as e:
        print_status(f"Frontend content check failed: {str(e)}", "ERROR")
        return False


def test_api_endpoint():
    """Test a real API endpoint"""
    try:
        # Test the orchestrate endpoint
        response = requests.post(
            "http://localhost:8001/api/v4/orchestrate",
            json={
                "query": "Test connection",
                "user_id": "test_user",
                "session_id": "test_session",
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            print_status("API endpoint working correctly", "SUCCESS")
            print_status(
                f"Response: {data.get('response', 'No response field')[:100]}...",
                "INFO",
            )
            return True
        else:
            print_status(f"API returned status {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"API test failed: {str(e)}", "ERROR")
        return False


def check_environment():
    """Check environment variables"""
    env_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PAT",
        "OPENAI_API_KEY",
    ]

    all_good = True
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            masked_value = value[:5] + "..." if len(value) > 5 else value
            print_status(f"{var} is set ({masked_value})", "SUCCESS")
        else:
            print_status(f"{var} is NOT set", "WARNING")
            all_good = False

    return all_good


def check_processes():
    """Check running processes"""
    processes = {
        "Backend": "unified_chat_backend",
        "Frontend": "vite",
        "Redis": "redis-server",
    }

    for name, process in processes.items():
        result = subprocess.run(
            f"ps aux | grep {process} | grep -v grep",
            shell=True,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            print_status(f"{name} process is running", "SUCCESS")
        else:
            print_status(f"{name} process is NOT running", "ERROR")


def main():
    print_status("SOPHIA AI DEPLOYMENT VERIFICATION", "HEADER")
    print("=" * 60)

    # Check services
    print("\n📡 Checking Services:")
    backend_ok = check_service("Backend API", "http://localhost:8001/health")
    frontend_ok = check_service("Frontend", "http://localhost:5173")
    api_docs_ok = check_service("API Docs", "http://localhost:8001/docs")

    # Check ports
    print("\n🔌 Checking Ports:")
    check_port_listening(8001, "Backend")
    check_port_listening(5173, "Frontend")
    check_port_listening(6379, "Redis")

    # Check processes
    print("\n⚙️ Checking Processes:")
    check_processes()

    # Check environment
    print("\n🔐 Checking Environment:")
    env_ok = check_environment()

    # Check frontend content
    print("\n🌐 Checking Frontend Content:")
    content_ok = check_frontend_content()

    # Test API
    print("\n🧪 Testing API:")
    api_ok = test_api_endpoint()

    # Summary
    print("\n" + "=" * 60)
    print_status("DEPLOYMENT SUMMARY", "HEADER")

    if backend_ok and frontend_ok:
        print_status("✅ Core services are running!", "SUCCESS")
        print_status("🌐 Frontend: http://localhost:5173", "INFO")
        print_status("🔧 Backend: http://localhost:8001", "INFO")
        print_status("📚 API Docs: http://localhost:8001/docs", "INFO")

        if not content_ok:
            print("\n⚠️ TROUBLESHOOTING BLANK SCREEN:")
            print("1. Open browser developer tools (F12)")
            print("2. Check Console tab for JavaScript errors")
            print("3. Check Network tab - are all files loading?")
            print("4. Try hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)")
            print("5. Try incognito/private browsing mode")
    else:
        print_status("❌ Some services are not running", "ERROR")
        if not backend_ok:
            print("\nTo start backend:")
            print("python backend/app/unified_chat_backend.py")
        if not frontend_ok:
            print("\nTo start frontend:")
            print("cd frontend && npm run dev")


if __name__ == "__main__":
    main()
