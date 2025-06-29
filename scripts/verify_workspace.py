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

    print("🔍 Sophia AI Workspace Verification")
    print("=" * 50)

    # Check current directory
    current_dir = Path.cwd()
    expected_dir = Path.home() / "sophia-main"

    print(f"📍 Current Directory: {current_dir}")
    print(f"📍 Expected Directory: {expected_dir}")

    if current_dir != expected_dir:
        print("❌ WRONG DIRECTORY!")
        print(f"💡 Please run: cd {expected_dir}")
        return False
    else:
        print("✅ Correct directory")

    # Check key project files
    key_files = [
        "pyproject.toml",
        "uv.lock",
        ".cursorrules",
        "backend/app/fastapi_app.py",
        "frontend/package.json"
    ]

    print("\n📁 Project Files Check:")
    all_files_exist = True
    for file in key_files:
        file_path = current_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING!")
            all_files_exist = False

    # Check virtual environment
    print("\n🐍 Virtual Environment Check:")
    venv_path = current_dir / ".venv"
    python_path = venv_path / "bin" / "python"

    if venv_path.exists() and python_path.exists():
        print(f"✅ Virtual environment: {venv_path}")

        # Check if we're using the right Python
        current_python = Path(sys.executable)
        if current_python == python_path:
            print("✅ Using correct Python from .venv")
        else:
            print(f"⚠️  Using: {current_python}")
            print(f"⚠️  Expected: {python_path}")
            print("💡 Run: source .venv/bin/activate")
    else:
        print("❌ Virtual environment not found!")
        print("💡 Run: python -m venv .venv && source .venv/bin/activate")
        all_files_exist = False

    # Check environment variables
    print("\n🌍 Environment Variables Check:")
    env_vars = {
        "VIRTUAL_ENV": str(venv_path),
        "SOPHIA_PROJECT_ROOT": str(current_dir),
        "ENVIRONMENT": "prod",
        "PULUMI_ORG": "scoobyjava-org"
    }

    env_ok = True
    for var, expected in env_vars.items():
        actual = os.getenv(var)
        if actual == expected:
            print(f"✅ {var}: {actual}")
        else:
            print(f"❌ {var}: {actual} (expected: {expected})")
            env_ok = False

    # Final assessment
    print("\n" + "=" * 50)
    if all_files_exist and env_ok and current_dir == expected_dir:
        print("🎉 WORKSPACE VERIFICATION: ✅ PERFECT!")
        print("🚀 Ready for Sophia AI development!")
        return True
    else:
        print("⚠️  WORKSPACE VERIFICATION: ❌ ISSUES FOUND")
        print("🔧 Please fix the issues above before continuing")
        return False


if __name__ == "__main__":
    success = verify_workspace()
    sys.exit(0 if success else 1)
