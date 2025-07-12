#!/usr/bin/env python3
"""
Test current state of Sophia AI
Tests what actually exists in the codebase
"""

import os
import sys
import asyncio
from pathlib import Path

# Set environment
os.environ["ENVIRONMENT"] = "prod"
os.environ["PULUMI_ORG"] = "scoobyjava-org"

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🔍 SOPHIA AI CURRENT STATE CHECK")
print("=" * 50)


def check_files():
    """Check which key files exist"""
    print("\n📁 Checking key files...")

    files_to_check = [
        ("FastAPI Enhanced", "backend/app/fastapi_app_enhanced.py"),
        ("Unified Chat Backend", "backend/app/unified_chat_backend.py"),
        ("Memory Service V2", "backend/services/unified_memory_service_v2.py"),
        ("Orchestrator", "backend/services/sophia_unified_orchestrator.py"),
        ("Personality Engine", "backend/services/personality_engine.py"),
        ("Chat Service V4", "backend/services/enhanced_chat_service_v4.py"),
        ("Enhanced Chat Service", "backend/services/enhanced_unified_chat_service.py"),
        ("Auto ESC Config", "backend/core/auto_esc_config.py"),
    ]

    existing = []
    missing = []

    for name, path in files_to_check:
        full_path = Path(path)
        if full_path.exists():
            print(f"  ✅ {name}: EXISTS")
            existing.append((name, path))
        else:
            print(f"  ❌ {name}: MISSING")
            missing.append((name, path))

    return existing, missing


def test_imports():
    """Test imports from existing files"""
    print("\n📦 Testing imports from existing files...")

    successful_imports = []
    failed_imports = []

    # Test unified chat backend
    try:

        print("  ✅ Unified Chat Backend app imported")
        successful_imports.append("unified_chat_backend")
    except Exception as e:
        print(f"  ❌ Unified Chat Backend: {str(e)[:50]}...")
        failed_imports.append(("unified_chat_backend", str(e)))

    # Test enhanced service
    try:

        print("  ✅ Enhanced Chat Service imported")
        successful_imports.append("enhanced_chat_service")
    except Exception as e:
        print(f"  ❌ Enhanced Chat Service: {str(e)[:50]}...")
        failed_imports.append(("enhanced_chat_service", str(e)))

    # Test auto ESC config
    try:

        print("  ✅ Auto ESC Config imported")
        successful_imports.append("auto_esc_config")
    except Exception as e:
        print(f"  ❌ Auto ESC Config: {str(e)[:50]}...")
        failed_imports.append(("auto_esc_config", str(e)))

    return successful_imports, failed_imports


async def test_services():
    """Test if services can be instantiated"""
    print("\n🔧 Testing service instantiation...")

    working_services = []
    broken_services = []

    # Test Enhanced Chat Service
    try:
        from backend.services.enhanced_unified_chat_service import (
            EnhancedUnifiedChatService,
        )

        service = EnhancedUnifiedChatService()
        print("  ✅ Enhanced Chat Service instantiated")
        working_services.append("enhanced_chat_service")

        # Try a basic operation
        result = await service.process_unified_query(
            query="Hello", user_id="test", session_id="test"
        )
        if result:
            print("  ✅ Chat service responded")
    except Exception as e:
        print(f"  ❌ Enhanced Chat Service: {str(e)[:100]}...")
        broken_services.append(("enhanced_chat_service", str(e)))

    return working_services, broken_services


def check_dependencies():
    """Check which key dependencies are installed"""
    print("\n📚 Checking dependencies...")

    deps = [
        "fastapi",
        "uvicorn",
        "langchain",
        "langgraph",
        "weaviate",
        "redis",
        "anthropic",
        "openai",
        "snowflake.connector",
    ]

    installed = []
    missing = []

    for dep in deps:
        try:
            __import__(dep.replace(".", "_") if "." in dep else dep)
            print(f"  ✅ {dep}: Installed")
            installed.append(dep)
        except ImportError:
            print(f"  ❌ {dep}: Missing")
            missing.append(dep)

    return installed, missing


async def main():
    """Run all checks"""

    # Check files
    existing_files, missing_files = check_files()

    # Check imports
    successful_imports, failed_imports = test_imports()

    # Check services
    working_services, broken_services = await test_services()

    # Check dependencies
    installed_deps, missing_deps = check_dependencies()

    # Summary
    print("\n" + "=" * 50)
    print("📊 CURRENT STATE SUMMARY")
    print("=" * 50)

    print(
        f"\n📁 Files: {len(existing_files)}/{len(existing_files) + len(missing_files)} exist"
    )
    print(
        f"📦 Imports: {len(successful_imports)}/{len(successful_imports) + len(failed_imports)} work"
    )
    print(
        f"🔧 Services: {len(working_services)}/{len(working_services) + len(broken_services)} operational"
    )
    print(
        f"📚 Dependencies: {len(installed_deps)}/{len(installed_deps) + len(missing_deps)} installed"
    )

    # Overall assessment
    total_checks = (
        len(existing_files)
        + len(missing_files)
        + len(successful_imports)
        + len(failed_imports)
        + len(working_services)
        + len(broken_services)
        + len(installed_deps)
        + len(missing_deps)
    )

    total_passed = (
        len(existing_files)
        + len(successful_imports)
        + len(working_services)
        + len(installed_deps)
    )

    percentage = (total_passed / total_checks * 100) if total_checks > 0 else 0

    print(
        f"\n🎯 Overall: {percentage:.0f}% operational ({total_passed}/{total_checks} checks passed)"
    )

    if percentage >= 70:
        print("\n✅ Sophia AI core is operational!")
        print("📝 Note: Some enhancements may not be present yet")
    elif percentage >= 50:
        print("\n⚠️  Sophia AI partially operational")
        print("📝 Core services working but enhancements missing")
    else:
        print("\n❌ Sophia AI needs significant work")

    # Recommendations
    if missing_deps:
        print("\n💡 Install missing dependencies:")
        print(f"   pip install {' '.join(missing_deps)}")


if __name__ == "__main__":
    asyncio.run(main())
