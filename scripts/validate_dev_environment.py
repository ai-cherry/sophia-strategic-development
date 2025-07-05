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

    # Check if we're in the project root
    project_root = Path.cwd()
    if not (project_root / ".envrc").exists():
        return False

    # Check virtual environment
    venv_path = os.environ.get("VIRTUAL_ENV")
    expected_venv = str(project_root / ".venv")

    if not venv_path:
        return False

    if venv_path != expected_venv:
        pass

    # Check Python version

    # Check critical dependencies
    try:
        import aiohttp
        import fastapi
        import pydantic

    except ImportError:
        return False

    # Check project structure
    required_dirs = ["backend", "scripts", "tests", "docs"]
    for dir_name in required_dirs:
        if not (project_root / dir_name).exists():
            pass

    return True


if __name__ == "__main__":
    success = validate_environment()
    sys.exit(0 if success else 1)
