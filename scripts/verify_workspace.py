#!/usr/bin/env python3
"""
Sophia AI Workspace Verification Script
Ensures you're always coding in the correct place with proper environment setup
"""

import os
import sys
from pathlib import Path


def verify_workspace():
    """Verify we're in the correct Sophia AI workspace"""

    # Check current directory
    current_dir = Path.cwd()
    expected_dir = Path.home() / "sophia-main"

    if current_dir != expected_dir:
        return False
    else:
        pass

    # Check key project files
    key_files = [
        "pyproject.toml",
        "uv.lock",
        ".cursorrules",
        "backend/app/fastapi_app.py",
        "frontend/package.json",
    ]

    all_files_exist = True
    for file in key_files:
        file_path = current_dir / file
        if file_path.exists():
            pass
        else:
            all_files_exist = False

    # Check virtual environment
    venv_path = current_dir / ".venv"
    python_path = venv_path / "bin" / "python"

    if venv_path.exists() and python_path.exists():
        # Check if we're using the right Python
        current_python = Path(sys.executable)
        if current_python == python_path:
            pass
        else:
            pass
    else:
        all_files_exist = False

    # Check environment variables
    env_vars = {
        "VIRTUAL_ENV": str(venv_path),
        "SOPHIA_PROJECT_ROOT": str(current_dir),
        "ENVIRONMENT": "prod",
        "PULUMI_ORG": "scoobyjava-org",
    }

    env_ok = True
    for var, expected in env_vars.items():
        actual = os.getenv(var)
        if actual == expected:
            pass
        else:
            env_ok = False

    # Final assessment
    return bool(all_files_exist and env_ok and current_dir == expected_dir)


if __name__ == "__main__":
    success = verify_workspace()
    sys.exit(0 if success else 1)
