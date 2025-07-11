#!/usr/bin/env python3
"""
Verify Sophia AI is ready for deployment with no blank screens
"""

import subprocess
from pathlib import Path


def check_mark(condition):
    return "✅" if condition else "❌"


def main():
    root_dir = Path(__file__).parent.parent
    frontend_dir = root_dir / "frontend"

    print("\n🔍 SOPHIA AI DEPLOYMENT READINESS CHECK")
    print("=" * 50)

    issues = []

    # 1. Check backend on Lambda Labs
    print("\n1. Backend Status:")
    try:
        result = subprocess.run(
            ["curl", "-s", "http://192.222.58.232:8001/health"],
            capture_output=True,
            text=True,
        )
        backend_healthy = "healthy" in result.stdout
        print(f"   {check_mark(backend_healthy)} Lambda Labs backend")
        if not backend_healthy:
            issues.append("Backend not running on Lambda Labs")
    except:
        print("   ❌ Lambda Labs backend (unreachable)")
        issues.append("Cannot reach Lambda Labs backend")

    # 2. Check frontend configuration
    print("\n2. Frontend Configuration:")

    # Check package.json
    package_json = frontend_dir / "package.json"
    has_package = package_json.exists()
    print(f"   {check_mark(has_package)} package.json exists")
    if not has_package:
        issues.append("Missing package.json")

    # Check App.tsx
    app_tsx = frontend_dir / "src" / "App.tsx"
    has_app = app_tsx.exists()
    print(f"   {check_mark(has_app)} App.tsx exists")

    if has_app:
        content = app_tsx.read_text()
        correct_import = "components/dashboard/UnifiedDashboard" in content
        print(f"   {check_mark(correct_import)} Correct UnifiedDashboard import")
        if not correct_import:
            issues.append("App.tsx has incorrect import path")

    # Check environment files
    env_prod = frontend_dir / ".env.production"
    has_env = env_prod.exists()
    print(f"   {check_mark(has_env)} .env.production configured")
    if not has_env:
        issues.append("Missing .env.production")

    # Check vercel.json
    vercel_json = frontend_dir / "vercel.json"
    has_vercel = vercel_json.exists()
    print(f"   {check_mark(has_vercel)} vercel.json configured")

    # 3. Check for common blank screen causes
    print("\n3. Blank Screen Prevention:")

    # Check index.html
    index_html = frontend_dir / "index.html"
    has_index = index_html.exists()
    print(f"   {check_mark(has_index)} index.html exists")

    # Check UnifiedDashboard component
    dashboard = (
        frontend_dir / "src" / "components" / "dashboard" / "UnifiedDashboard.tsx"
    )
    has_dashboard = dashboard.exists()
    print(f"   {check_mark(has_dashboard)} UnifiedDashboard component exists")
    if not has_dashboard:
        issues.append("Missing UnifiedDashboard component")

    # 4. Check dependencies
    print("\n4. Dependencies:")
    node_modules = frontend_dir / "node_modules"
    has_deps = node_modules.exists()
    print(f"   {check_mark(has_deps)} node_modules installed")
    if not has_deps:
        issues.append("Dependencies not installed - run 'npm install' in frontend/")

    # Summary
    print("\n" + "=" * 50)
    if issues:
        print("❌ DEPLOYMENT NOT READY - Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n💡 Run these commands to fix:")
        if "Dependencies not installed" in str(issues):
            print("   cd frontend && npm install")
        if "Backend not running" in str(issues):
            print("   ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232")
            print("   python backend/app/unified_chat_backend.py")
    else:
        print("✅ READY FOR DEPLOYMENT!")
        print("\n🚀 To deploy, run:")
        print("   python scripts/deploy_sophia_complete.py")

    print("\n📍 Your site will be available at:")
    print("   https://sophia-intel.ai")
    print("   https://www.sophia-intel.ai")


if __name__ == "__main__":
    main()
