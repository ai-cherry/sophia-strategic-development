#!/usr/bin/env python3
"""Monitor Sophia AI deployment progress"""

import json
import os
import subprocess
import time
from datetime import datetime

import requests

# Configuration
SERVICES = {
    "Frontend (Vercel)": {
        "url": "https://app.sophia-intel.ai",
        "expected_status": 200,
        "type": "web",
    },
    "API Documentation": {
        "url": "https://api.sophia-intel.ai",
        "expected_status": [200, 404],  # 404 is ok if not deployed yet
        "type": "api",
    },
    "Lambda Labs Instances": {
        "192.222.58.232": {
            "name": "lynn-sophia-gh200-master-01",
            "services": {
                "API": {"port": 8000, "path": "/health"},
                "Frontend": {"port": 3000, "path": "/"},
                "Grafana": {"port": 3001, "path": "/"},
            },
        },
        "192.222.58.232": {
            "name": "sophia-platform-prod",
            "services": {
                "API": {"port": 8000, "path": "/health"},
            },
        },
        "165.1.69.44": {
            "name": "sophia-mcp-prod",
            "services": {
                "AI Memory": {"port": 9000, "path": "/health"},
                "Codacy": {"port": 3008, "path": "/health"},
                "Linear": {"port": 9004, "path": "/health"},
            },
        },
    },
}

# Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check_url(url: str, expected_status=200, timeout=5) -> tuple[bool, int, str]:
    """Check if a URL is accessible"""
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        if isinstance(expected_status, list):
            success = response.status_code in expected_status
        else:
            success = response.status_code == expected_status
        return (
            success,
            response.status_code,
            "OK" if success else f"Status: {response.status_code}",
        )
    except requests.exceptions.Timeout:
        return False, 0, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, 0, "Connection Error"
    except Exception as e:
        return False, 0, str(e)


def check_lambda_labs_service(
    host: str, port: int, path: str = "/", timeout=3
) -> tuple[bool, str]:
    """Check a service on Lambda Labs"""
    url = f"http://{host}:{port}{path}"
    success, status, message = check_url(url, timeout=timeout)
    return success, message


def get_github_actions_status() -> list[dict]:
    """Get recent GitHub Actions runs"""
    try:
        # Use gh CLI to get workflow runs
        result = subprocess.run(
            [
                "gh",
                "api",
                "/repos/ai-cherry/sophia-main/actions/runs",
                "--jq",
                ".workflow_runs[:5] | .[] | {name: .name, status: .status, conclusion: .conclusion, created_at: .created_at}",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        if result.returncode == 0 and result.stdout:
            # Parse each JSON object from output
            runs = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    try:
                        runs.append(json.loads(line))
                    except:
                        pass
            return runs
        return []
    except:
        return []


def print_status_line(name: str, status: bool, message: str = ""):
    """Print a formatted status line"""
    status_icon = f"{GREEN}✅{RESET}" if status else f"{RED}❌{RESET}"
    status_text = f"{GREEN}OK{RESET}" if status else f"{RED}FAILED{RESET}"

    print(f"  {status_icon} {name:<40} [{status_text}] {message}")


def monitor_deployment():
    """Main monitoring function"""
    print(f"\n{BLUE}🔍 Sophia AI Deployment Monitor{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check web services
    print(f"{YELLOW}📡 Web Services:{RESET}")
    for service_name, config in SERVICES.items():
        if isinstance(config, dict) and "url" in config:
            success, status, message = check_url(
                config["url"], config.get("expected_status", 200)
            )
            print_status_line(service_name, success, f"({message})")

    # Check Lambda Labs instances
    print(f"\n{YELLOW}🖥️  Lambda Labs Instances:{RESET}")
    lambda_config = SERVICES.get("Lambda Labs Instances", {})

    for host, instance_config in lambda_config.items():
        print(f"\n  {BLUE}{instance_config['name']} ({host}):{RESET}")

        # First check if host is reachable
        reachable, _, _ = check_url(f"http://{host}", timeout=3)
        if not reachable:
            print(f"    {RED}❌ Host not reachable{RESET}")
            continue

        # Check each service on the instance
        for service_name, service_config in instance_config.get("services", {}).items():
            success, message = check_lambda_labs_service(
                host, service_config["port"], service_config.get("path", "/")
            )
            print_status_line(
                f"  {service_name}", success, f"(Port {service_config['port']})"
            )

    # Check GitHub Actions
    print(f"\n{YELLOW}🚀 GitHub Actions Status:{RESET}")
    runs = get_github_actions_status()

    if runs:
        for run in runs[:5]:  # Show last 5 runs
            status = run.get("status", "unknown")
            conclusion = run.get("conclusion", "pending")
            name = run.get("name", "Unknown")
            created = run.get("created_at", "")[:19]  # Trim microseconds

            if status == "completed":
                success = conclusion == "success"
                status_text = (
                    f"{GREEN}✅ Success{RESET}"
                    if success
                    else f"{RED}❌ {conclusion}{RESET}"
                )
            else:
                status_text = f"{YELLOW}⏳ {status}{RESET}"

            print(f"  {status_text} {name:<40} ({created})")
    else:
        print(f"  {YELLOW}Unable to fetch GitHub Actions status{RESET}")

    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"Check complete at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def continuous_monitor(interval: int = 30):
    """Continuously monitor deployment"""
    print(f"{BLUE}Starting continuous monitoring (interval: {interval}s){RESET}")
    print(f"{YELLOW}Press Ctrl+C to stop{RESET}\n")

    try:
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            monitor_deployment()
            print(f"\n{YELLOW}Next check in {interval} seconds...{RESET}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Monitoring stopped.{RESET}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        continuous_monitor(interval)
    else:
        monitor_deployment()
        print(f"\n{YELLOW}Tip: Run with --continuous for continuous monitoring{RESET}")
        print(
            f"{YELLOW}Example: python3 scripts/monitor_deployment.py --continuous 30{RESET}"
        )
