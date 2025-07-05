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
    return bool(venv_path)


def check_environment_vars():
    """Check required environment variables"""
    required_vars = {"ENVIRONMENT": "prod", "PULUMI_ORG": "scoobyjava-org"}

    all_good = True
    for var, expected in required_vars.items():
        actual = os.environ.get(var)
        if actual == expected:
            pass
        else:
            all_good = False

    return all_good


def check_python_path():
    """Check if PYTHONPATH includes current directory"""
    pythonpath = os.environ.get("PYTHONPATH", "")
    current_dir = str(Path.cwd())

    return current_dir in pythonpath


def check_backend_import():
    """Check if backend module can be imported"""
    try:
        import backend

        return True
    except ImportError:
        return False


def check_git_branch():
    """Check current git branch"""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )
        if result.returncode == 0:
            result.stdout.strip()
            return True
        else:
            return False
    except Exception:
        return False


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    return bool(version.major == 3 and version.minor >= 11)


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
            pass
        else:
            all_good = False

    return all_good


def main():
    """Run all environment checks"""

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
    for _name, check_func in checks:
        results.append(check_func())

    passed = sum(results)
    total = len(results)

    if passed == total:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
