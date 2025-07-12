#!/usr/bin/env python3
"""
Sophia AI Deployment Health Check - July 2025
Tests all critical components and provides actionable fixes
"""

import subprocess
import sys
import os
import json
from pathlib import Path


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def run_command(cmd, check=False):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_python_import(module):
    """Check if a Python module can be imported"""
    cmd = f"python -c 'import {module}'"
    success, _, _ = run_command(cmd)
    return success


def check_port_listening(port):
    """Check if a port is listening"""
    cmd = f"lsof -i :{port} | grep LISTEN"
    success, output, _ = run_command(cmd)
    return success and output.strip() != ""


def check_health_endpoint(url):
    """Check if health endpoint responds"""
    cmd = f"curl -s -f {url}/health"
    success, output, _ = run_command(cmd)
    try:
        if success and output:
            data = json.loads(output)
            return True, data
    except:
        pass
    return False, {}


def print_status(name, status, details=""):
    """Print colored status"""
    icon = "✅" if status else "❌"
    color = Colors.GREEN if status else Colors.RED
    print(f"{color}{icon} {name}{Colors.ENDC}")
    if details:
        print(f"   {details}")


def main():
    print(f"{Colors.BOLD}🚀 Sophia AI Deployment Health Check - July 2025{Colors.ENDC}")
    print("=" * 60)

    issues = []
    fixes = []

    # Check 1: Python Environment
    print(f"\n{Colors.BLUE}1. Python Environment{Colors.ENDC}")

    python_version = sys.version.split()[0]
    print_status(
        "Python Version",
        python_version.startswith("3.12"),
        f"Version: {python_version}",
    )

    venv_active = os.environ.get("VIRTUAL_ENV") is not None
    print_status(
        "Virtual Environment",
        venv_active,
        f"Path: {os.environ.get('VIRTUAL_ENV', 'Not activated')}",
    )
    if not venv_active:
        issues.append("Virtual environment not activated")
        fixes.append("source .venv/bin/activate")

    # Check 2: Critical Imports
    print(f"\n{Colors.BLUE}2. Critical Python Imports{Colors.ENDC}")

    critical_modules = [
        ("backend", "Core backend module"),
        ("fastapi", "Web framework"),
        ("uvicorn", "ASGI server"),
        ("redis", "Cache client"),
        ("asyncpg", "PostgreSQL async client"),
        ("weaviate", "Vector database client"),
        ("langchain", "LLM orchestration"),
        ("langgraph", "Graph-based workflows"),
    ]

    for module, desc in critical_modules:
        status = check_python_import(module)
        print_status(f"{module}", status, desc)
        if not status:
            issues.append(f"Missing module: {module}")
            if module == "backend":
                fixes.append("export PYTHONPATH=$(pwd):$PYTHONPATH")
            else:
                fixes.append(f"pip install {module}")

    # Check 3: Environment Variables
    print(f"\n{Colors.BLUE}3. Environment Variables{Colors.ENDC}")

    env_vars = {
        "ENVIRONMENT": "prod",
        "PYTHONPATH": os.getcwd(),
        "WEAVIATE_URL": "http://localhost:8080",
        "REDIS_URL": "redis://localhost:6379",
        "POSTGRESQL_URL": "postgresql://sophia:sophia@localhost:5432/sophia",
    }

    for var, expected in env_vars.items():
        actual = os.environ.get(var, "")
        status = var in os.environ
        if var == "PYTHONPATH":
            status = os.getcwd() in actual
        print_status(var, status, f"Value: {actual[:50]}...")
        if not status:
            issues.append(f"Missing or incorrect {var}")
            fixes.append(f"export {var}={expected}")

    # Check 4: Service Ports
    print(f"\n{Colors.BLUE}4. Service Ports{Colors.ENDC}")

    ports = {
        8000: "Backend API",
        8080: "Weaviate",
        6379: "Redis",
        5432: "PostgreSQL",
    }

    for port, service in ports.items():
        status = check_port_listening(port)
        print_status(f"Port {port}", status, service)
        if not status and port == 8000:
            issues.append(f"{service} not running on port {port}")

    # Check 5: Health Endpoints
    print(f"\n{Colors.BLUE}5. Health Endpoints{Colors.ENDC}")

    if check_port_listening(8000):
        success, data = check_health_endpoint("http://localhost:8000")
        print_status("Backend Health", success, f"Response: {data}")
        if not success:
            issues.append("Backend health check failed")

    # Check 6: File Structure
    print(f"\n{Colors.BLUE}6. File Structure{Colors.ENDC}")

    critical_files = [
        ("backend/app/unified_chat_backend.py", "Main backend app"),
        ("backend/services/unified_memory_service_v2.py", "Memory service v2"),
        ("backend/services/personality_engine.py", "Personality engine"),
        ("backend/services/enhanced_chat_service_v4.py", "Chat service v4"),
    ]

    for file_path, desc in critical_files:
        exists = Path(file_path).exists()
        print_status(file_path, exists, desc)
        if not exists:
            issues.append(f"Missing file: {file_path}")
            if "personality" in file_path or "v4" in file_path:
                fixes.append(f"# Create placeholder: touch {file_path}")

    # Check 7: Dependency Versions
    print(f"\n{Colors.BLUE}7. Dependency Versions{Colors.ENDC}")

    version_checks = [
        ("weaviate", "4.6.1", "weaviate.__version__"),
        ("langchain", "0.2.0", "langchain.__version__"),
        ("langgraph", "0.5.1", "langgraph.__version__"),
    ]

    for module, expected, attr_path in version_checks:
        try:
            mod = __import__(module)
            version = eval(f"mod.{attr_path.split('.', 1)[1]}")
            status = version >= expected
            print_status(
                f"{module} version",
                status,
                f"Current: {version}, Expected: >={expected}",
            )
            if not status:
                issues.append(f"{module} version outdated")
                fixes.append(f"pip install {module}>={expected}")
        except:
            pass

    # Summary
    print(f"\n{Colors.BOLD}📊 Summary{Colors.ENDC}")
    print("=" * 60)

    operational_percentage = max(0, 100 - (len(issues) * 10))
    color = (
        Colors.GREEN
        if operational_percentage >= 80
        else Colors.YELLOW
        if operational_percentage >= 50
        else Colors.RED
    )
    print(f"{color}Operational Status: {operational_percentage}%{Colors.ENDC}")

    if issues:
        print(f"\n{Colors.RED}Issues Found ({len(issues)}):{Colors.ENDC}")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")

        print(f"\n{Colors.YELLOW}Recommended Fixes:{Colors.ENDC}")
        for fix in fixes:
            print(f"  {fix}")

        print(f"\n{Colors.BLUE}Quick Fix Script:{Colors.ENDC}")
        print("  bash -c '" + " && ".join(fixes) + "'")
    else:
        print(f"\n{Colors.GREEN}🎉 All systems operational!{Colors.ENDC}")

    # Docker test
    print(f"\n{Colors.BLUE}8. Docker Build Test{Colors.ENDC}")
    print("Testing Docker build (this may take a moment)...")

    success, output, error = run_command(
        "docker build -f backend/Dockerfile -t sophia-test:latest . 2>&1 | tail -5"
    )
    print_status("Docker Build", "successfully built" in output.lower() or success)
    if not success:
        print(f"   Last lines: {output}")


if __name__ == "__main__":
    main()
