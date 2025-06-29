#!/usr/bin/env python3
"""
Development Environment Validation Script
Ensures we're in the correct virtual environment and all dependencies are available.
"""

import os
import sys
from pathlib import Path


def validate_environment():
    """Validate that we're in the correct development environment."""
    print("🔍 Validating Sophia AI Development Environment...")

    # Check if we're in the project root
    project_root = Path.cwd()
    if not (project_root / ".envrc").exists():
        print("❌ Not in Sophia AI project root directory")
        print(f"Current directory: {project_root}")
        print("💡 Please run from the sophia-main directory")
        return False

    # Check virtual environment
    venv_path = os.environ.get("VIRTUAL_ENV")
    expected_venv = str(project_root / ".venv")

    if not venv_path:
        print("❌ No virtual environment detected")
        print("💡 Run: source .venv/bin/activate")
        return False

    if venv_path != expected_venv:
        print("⚠️  Using different virtual environment:")
        print(f"   Current: {venv_path}")
        print(f"   Expected: {expected_venv}")

    # Check Python version
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    print(f"✅ Python version: {python_version}")
    print(f"✅ Python executable: {sys.executable}")
    print(f"✅ Virtual environment: {venv_path}")

    # Check critical dependencies
    try:
        import aiohttp
        import fastapi
        import pydantic

        print("✅ Core dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

    # Check project structure
    required_dirs = ["backend", "scripts", "tests", "docs"]
    for dir_name in required_dirs:
        if not (project_root / dir_name).exists():
            print(f"⚠️  Missing directory: {dir_name}")

    print("🎉 Development environment is properly configured!")
    return True


if __name__ == "__main__":
    success = validate_environment()
    sys.exit(0 if success else 1)
