#!/usr/bin/env python3
"""
Test script to verify Sophia AI startup with fixed virtual environment
"""

import asyncio
import os
import sys
from pathlib import Path


def check_environment():
    """Check if we're in the correct virtual environment and have required packages"""
    print("🔍 Environment Check:")
    print(f"   Python executable: {sys.executable}")
    print(f"   Python version: {sys.version}")
    print(f"   Virtual env: {os.getenv('VIRTUAL_ENV', 'Not set')}")
    print(f"   PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
    print(f"   ENVIRONMENT: {os.getenv('ENVIRONMENT', 'Not set')}")
    print(f"   PULUMI_ORG: {os.getenv('PULUMI_ORG', 'Not set')}")

    # Check if we're in the correct virtual environment
    expected_venv = str(Path.cwd() / ".venv")
    current_venv = os.getenv("VIRTUAL_ENV", "")

    if expected_venv in current_venv:
        print("✅ Virtual environment: CORRECT")
    else:
        print("❌ Virtual environment: INCORRECT")
        print(f"   Expected: {expected_venv}")
        print(f"   Current:  {current_venv}")
        return False

    return True


def check_imports():
    """Check if critical imports work"""
    print("\n🔍 Import Check:")

    try:
        import fastapi

        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

    try:
        import uvicorn

        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False

    try:
        # Test our patched snowflake import
        sys.path.insert(0, str(Path.cwd() / "patches"))
        import snowflake_test_util_fix

        print("✅ Snowflake test_util patch loaded")
    except ImportError as e:
        print(f"❌ Snowflake patch failed: {e}")
        return False

    try:
        from backend.core.auto_esc_config import get_config_value

        print("✅ Sophia AI config imported successfully")
    except ImportError as e:
        print(f"❌ Sophia AI config import failed: {e}")
        return False

    return True


async def test_config_loading():
    """Test if Pulumi ESC configuration loads properly"""
    print("\n🔍 Configuration Loading Test:")

    try:
        from backend.core.auto_esc_config import get_config_value

        # Test loading a basic config value
        environment = get_config_value("environment", default="unknown")
        print(f"✅ Environment config: {environment}")

        # Test if we can access Pulumi ESC (this might fail if secrets aren't synced yet)
        try:
            openai_key = get_config_value("openai_api_key", default=None)
            if openai_key and len(openai_key) > 10:
                print(f"✅ OpenAI key loaded: {openai_key[:10]}...")
            else:
                print("⚠️  OpenAI key not found (secrets may not be synced yet)")
        except Exception as e:
            print(f"⚠️  Secret loading failed: {e}")

        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False


def test_simple_startup():
    """Test if we can create a simple FastAPI app"""
    print("\n🔍 Simple FastAPI Startup Test:")

    try:
        from fastapi import FastAPI

        app = FastAPI(title="Sophia AI Test")

        @app.get("/health")
        async def health():
            return {"status": "healthy", "service": "sophia-ai-test"}

        print("✅ FastAPI app created successfully")
        print("✅ Health endpoint defined")
        return True
    except Exception as e:
        print(f"❌ FastAPI startup failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 Sophia AI Startup Test")
    print("=" * 50)

    # Run all tests
    env_ok = check_environment()
    imports_ok = check_imports()
    config_ok = await test_config_loading()
    startup_ok = test_simple_startup()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Environment: {'✅' if env_ok else '❌'}")
    print(f"   Imports:     {'✅' if imports_ok else '❌'}")
    print(f"   Config:      {'✅' if config_ok else '❌'}")
    print(f"   Startup:     {'✅' if startup_ok else '❌'}")

    if all([env_ok, imports_ok, config_ok, startup_ok]):
        print("\n🎉 ALL TESTS PASSED! Sophia AI is ready to start.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
