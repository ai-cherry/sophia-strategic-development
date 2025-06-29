#!/usr/bin/env python3
"""
Sophia AI Environment Validation Script
Validates that the development environment is properly configured
"""

import os
import subprocess
import sys
from pathlib import Path


def check_virtual_env():
    """Check if virtual environment is activated"""
    venv_path = os.environ.get("VIRTUAL_ENV")
    if venv_path:
        print(f"✅ Virtual environment active: {venv_path}")
        return True
    else:
        print("❌ Virtual environment not active")
        print("   Run: source .venv/bin/activate")
        return False


def check_environment_vars():
    """Check required environment variables"""
    required_vars = {"ENVIRONMENT": "prod", "PULUMI_ORG": "scoobyjava-org"}

    all_good = True
    for var, expected in required_vars.items():
        actual = os.environ.get(var)
        if actual == expected:
            print(f"✅ {var}={actual}")
        else:
            print(f"❌ {var}={actual} (expected: {expected})")
            all_good = False

    return all_good


def check_python_path():
    """Check if PYTHONPATH includes current directory"""
    pythonpath = os.environ.get("PYTHONPATH", "")
    current_dir = str(Path.cwd())

    if current_dir in pythonpath:
        print("✅ PYTHONPATH includes current directory")
        return True
    else:
        print("❌ PYTHONPATH missing current directory")
        print(f"   Current PYTHONPATH: {pythonpath}")
        return False


def check_backend_import():
    """Check if backend module can be imported"""
    try:
        import backend

        print("✅ Backend module imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import backend module: {e}")
        return False


def check_git_branch():
    """Check current git branch"""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            print(f"✅ Git branch: {branch}")
            return True
        else:
            print("❌ Failed to get git branch")
            return False
    except Exception as e:
        print(f"❌ Git error: {e}")
        return False


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(
            f"❌ Python version: {version.major}.{version.minor}.{version.micro} (requires 3.11+)"
        )
        return False


def check_key_files():
    """Check for key configuration files"""
    key_files = [
        ".venv/bin/activate",
        "backend/__init__.py",
        "requirements.txt",
        ".cursorrules",
        "cursor_mcp_config.json",
    ]

    all_good = True
    for file in key_files:
        if Path(file).exists():
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            all_good = False

    return all_good


def main():
    """Run all environment checks"""
    print("=== Sophia AI Environment Validation ===")
    print(f"Current directory: {Path.cwd()}")
    print("")

    checks = [
        ("Virtual Environment", check_virtual_env),
        ("Environment Variables", check_environment_vars),
        ("Python Path", check_python_path),
        ("Python Version", check_python_version),
        ("Backend Import", check_backend_import),
        ("Git Status", check_git_branch),
        ("Key Files", check_key_files),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        results.append(check_func())

    print("\n=== Summary ===")
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ All {total} checks passed! Environment is ready.")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
