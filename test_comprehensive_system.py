#!/usr/bin/env python3
"""
Comprehensive System Test for Sophia AI Platform
Tests all major components and generates health report
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

async def test_system_health():
    """Test all system components and generate health report"""
    print("🔍 COMPREHENSIVE SOPHIA AI SYSTEM TEST")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "summary": {"passed": 0, "failed": 0, "warnings": 0}
    }
    
    # Test 1: CEO Dashboard Health
    print("\n1️⃣  Testing CEO Dashboard...")
    try:
        import subprocess
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8000/health"], 
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and "healthy" in result.stdout:
            results["tests"].append({
                "test": "CEO Dashboard Health",
                "status": "✅ PASS",
                "details": result.stdout.strip()
            })
            results["summary"]["passed"] += 1
            print("   ✅ CEO Dashboard is healthy")
        else:
            results["tests"].append({
                "test": "CEO Dashboard Health", 
                "status": "❌ FAIL",
                "details": result.stdout or result.stderr
            })
            results["summary"]["failed"] += 1
            print(f"   ❌ CEO Dashboard failed")
    except Exception as e:
        results["tests"].append({
            "test": "CEO Dashboard Health",
            "status": "❌ FAIL", 
            "details": str(e)
        })
        results["summary"]["failed"] += 1
        print(f"   ❌ CEO Dashboard error: {e}")
    
    # Test 2: File System Structure
    print("\n2️⃣  Testing File System Structure...")
    critical_files = [
        "backend/app/ceo_dashboard_app.py",
        "frontend/src/components/dashboard/CEODashboard.tsx",
        "docker-compose.yml",
        "n8n-integration/docker-compose.yml",
        "SOPHIA_AI_UNIFIED_DASHBOARD_ENHANCEMENT_PLAN.md"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} - MISSING")
    
    if not missing_files:
        results["tests"].append({
            "test": "Critical Files",
            "status": "✅ PASS",
            "details": "All critical files present"
        })
        results["summary"]["passed"] += 1
    else:
        results["tests"].append({
            "test": "Critical Files",
            "status": "❌ FAIL",
            "details": {"missing": missing_files}
        })
        results["summary"]["failed"] += 1
    
    # Test 3: Documentation Coverage
    print("\n3️⃣  Testing Documentation Coverage...")
    doc_files = list(Path("docs").glob("**/*.md")) if Path("docs").exists() else []
    root_docs = list(Path(".").glob("*.md"))
    
    total_docs = len(doc_files) + len(root_docs)
    print(f"   📚 Found {total_docs} documentation files")
    
    if total_docs > 50:
        results["tests"].append({
            "test": "Documentation Coverage",
            "status": "✅ PASS",
            "details": {"total_files": total_docs}
        })
        results["summary"]["passed"] += 1
        print("   ✅ Documentation coverage is comprehensive")
    else:
        results["tests"].append({
            "test": "Documentation Coverage",
            "status": "⚠️  WARN",
            "details": {"total_files": total_docs}
        })
        results["summary"]["warnings"] += 1
        print("   ⚠️  Documentation coverage could be improved")
    
    # Generate Summary
    print("\n" + "=" * 50)
    print("📊 SYSTEM HEALTH SUMMARY")
    print("=" * 50)
    
    total_tests = results["summary"]["passed"] + results["summary"]["failed"] + results["summary"]["warnings"]
    health_percentage = (results["summary"]["passed"] / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"✅ Passed: {results['summary']['passed']}")
    print(f"❌ Failed: {results['summary']['failed']}")
    print(f"⚠️  Warnings: {results['summary']['warnings']}")
    print(f"📈 Overall Health: {health_percentage:.1f}%")
    
    # System Status
    if health_percentage >= 90:
        status = "🟢 EXCELLENT"
    elif health_percentage >= 70:
        status = "🟡 GOOD"
    elif health_percentage >= 50:
        status = "🟠 FAIR"
    else:
        status = "🔴 NEEDS ATTENTION"
    
    print(f"🎯 System Status: {status}")
    
    # Save results
    with open("system_health_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: system_health_report.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_system_health())
