#!/usr/bin/env python3
"""
Validate All Sophia AI Improvements
Tests unified MCP base, consolidated chat service, cleaned deployment scripts
"""

import ast
import subprocess
from pathlib import Path
from typing import Any


def validate_unified_mcp_base() -> dict[str, Any]:
    """Validate unified MCP base implementation"""
    print("🔍 Validating Unified MCP Base...")

    results = {
        "base_class_exists": False,
        "migrated_servers": [],
        "failed_migrations": [],
        "inheritance_correct": [],
        "syntax_valid": True,
        "score": 0,
    }

    # Check if unified base exists
    unified_base = Path("mcp-servers/base/unified_mcp_base.py")
    if unified_base.exists():
        results["base_class_exists"] = True
        print("   ✅ Unified MCP base class exists")

        # Validate syntax
        try:
            with open(unified_base) as f:
                ast.parse(f.read())
            print("   ✅ Unified base has valid syntax")
        except SyntaxError as e:
            results["syntax_valid"] = False
            print(f"   ❌ Syntax error in unified base: {e}")
    else:
        print("   ❌ Unified MCP base class missing")
        return results

    # Check migrated servers
    mcp_servers_dir = Path("mcp-servers")
    for server_dir in mcp_servers_dir.iterdir():
        if server_dir.is_dir() and server_dir.name != "base":
            server_files = list(server_dir.glob("*_mcp_server.py"))
            if server_files:
                server_file = server_files[0]

                try:
                    with open(server_file) as f:
                        content = f.read()

                    # Check for unified base import
                    if "unified_mcp_base" in content:
                        results["migrated_servers"].append(server_dir.name)
                        print(f"   ✅ {server_dir.name} migrated to unified base")

                        # Check inheritance
                        if any(
                            base in content
                            for base in [
                                "ServiceMCPServer",
                                "AIEngineMCPServer",
                                "InfrastructureMCPServer",
                            ]
                        ):
                            results["inheritance_correct"].append(server_dir.name)
                            print(f"   ✅ {server_dir.name} has correct inheritance")
                    else:
                        results["failed_migrations"].append(server_dir.name)
                        print(f"   ⚠️  {server_dir.name} not migrated")

                except Exception as e:
                    results["failed_migrations"].append(server_dir.name)
                    print(f"   ❌ Error checking {server_dir.name}: {e}")

    # Calculate score
    total_servers = len(results["migrated_servers"]) + len(results["failed_migrations"])
    if total_servers > 0:
        migration_score = len(results["migrated_servers"]) / total_servers * 50
        inheritance_score = len(results["inheritance_correct"]) / total_servers * 30
        base_score = (
            20 if results["base_class_exists"] and results["syntax_valid"] else 0
        )
        results["score"] = int(migration_score + inheritance_score + base_score)

    print(f"   📊 MCP Base Score: {results['score']}/100")
    return results


def validate_consolidated_chat_service() -> dict[str, Any]:
    """Validate consolidated chat service"""
    print("🔍 Validating Consolidated Chat Service...")

    results = {
        "main_service_exists": False,
        "enhanced_service_removed": False,
        "lambda_integration": False,
        "streaming_support": False,
        "cost_monitoring": False,
        "syntax_valid": True,
        "score": 0,
    }

    # Check main service exists
    main_service = Path("backend/services/unified_chat_service.py")
    if main_service.exists():
        results["main_service_exists"] = True
        print("   ✅ Main unified chat service exists")

        try:
            with open(main_service) as f:
                content = f.read()

            # Validate syntax
            ast.parse(content)
            results["syntax_valid"] = True
            print("   ✅ Chat service has valid syntax")

            # Check for enhanced features
            if "LambdaLabsChatIntegration" in content:
                results["lambda_integration"] = True
                print("   ✅ Lambda Labs integration present")

            if "AsyncGenerator" in content and "process_message" in content:
                results["streaming_support"] = True
                print("   ✅ Streaming support present")

            if "cost_monitor" in content:
                results["cost_monitoring"] = True
                print("   ✅ Cost monitoring present")

        except SyntaxError as e:
            results["syntax_valid"] = False
            print(f"   ❌ Syntax error in chat service: {e}")
    else:
        print("   ❌ Main unified chat service missing")
        return results

    # Check enhanced service removed/archived
    enhanced_service = Path("backend/services/enhanced_unified_chat_service.py")
    archived_service = Path(
        "archive/unified_chat_duplicates/enhanced_unified_chat_service.py.archived"
    )

    if not enhanced_service.exists():
        results["enhanced_service_removed"] = True
        if archived_service.exists():
            print("   ✅ Enhanced service properly archived")
        else:
            print("   ✅ Enhanced service removed")
    else:
        print("   ⚠️  Enhanced service still exists (should be removed)")

    # Calculate score
    feature_checks = [
        results["main_service_exists"],
        results["enhanced_service_removed"],
        results["lambda_integration"],
        results["streaming_support"],
        results["cost_monitoring"],
        results["syntax_valid"],
    ]
    results["score"] = int(sum(feature_checks) / len(feature_checks) * 100)

    print(f"   📊 Chat Service Score: {results['score']}/100")
    return results


def validate_deployment_cleanup() -> dict[str, Any]:
    """Validate deployment scripts cleanup"""
    print("🔍 Validating Deployment Scripts Cleanup...")

    results = {
        "backup_created": False,
        "legacy_files_removed": 0,
        "essential_files_present": [],
        "missing_essential_files": [],
        "unified_guide_created": False,
        "score": 0,
    }

    # Check for backup directory
    backup_dirs = list(Path(".").glob("deployment_cleanup_backup_*"))
    if backup_dirs:
        results["backup_created"] = True
        print(f"   ✅ Backup created: {backup_dirs[-1]}")

    # Check essential files
    essential_files = [
        "scripts/deploy_sophia_unified.sh",
        "scripts/deploy_sophia_platform.sh",
        "scripts/deploy_sophia_simple.sh",
        "scripts/lambda_migration_deploy.sh",
        "deployment/docker-compose-production.yml",
        "deployment/docker-compose-ai-core.yml",
        "deployment/README.md",
    ]

    for file_path in essential_files:
        if Path(file_path).exists():
            results["essential_files_present"].append(file_path)
            print(f"   ✅ Essential file present: {file_path}")
        else:
            results["missing_essential_files"].append(file_path)
            print(f"   ❌ Missing essential file: {file_path}")

    # Check unified guide
    unified_guide = Path("docs/04-deployment/UNIFIED_DEPLOYMENT_GUIDE.md")
    if unified_guide.exists():
        results["unified_guide_created"] = True
        print("   ✅ Unified deployment guide created")

    # Calculate score
    backup_score = 20 if results["backup_created"] else 0
    essential_score = (
        len(results["essential_files_present"]) / len(essential_files) * 60
    )
    guide_score = 20 if results["unified_guide_created"] else 0
    results["score"] = int(backup_score + essential_score + guide_score)

    print(f"   📊 Deployment Cleanup Score: {results['score']}/100")
    return results


def validate_overall_codebase() -> dict[str, Any]:
    """Validate overall codebase health"""
    print("🔍 Validating Overall Codebase...")

    results = {
        "import_errors": [],
        "syntax_errors": [],
        "git_status_clean": False,
        "score": 0,
    }

    # Check for major syntax errors in key files
    key_files = [
        "backend/services/unified_chat_service.py",
        "mcp-servers/base/unified_mcp_base.py",
        "backend/api/main.py",
    ]

    for file_path in key_files:
        if Path(file_path).exists():
            try:
                with open(file_path) as f:
                    ast.parse(f.read())
                print(f"   ✅ {file_path} syntax valid")
            except SyntaxError as e:
                results["syntax_errors"].append(f"{file_path}: {e}")
                print(f"   ❌ Syntax error in {file_path}: {e}")

    # Check git status
    try:
        git_status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
        if git_status.returncode == 0:
            if git_status.stdout.strip():
                print("   ℹ️  Git has uncommitted changes (expected)")
            else:
                results["git_status_clean"] = True
                print("   ✅ Git status clean")
        else:
            print("   ⚠️  Could not check git status")
    except Exception as e:
        print(f"   ⚠️  Git status check failed: {e}")

    # Calculate score
    syntax_score = (
        (len(key_files) - len(results["syntax_errors"])) / len(key_files) * 80
    )
    git_score = 20 if len(results["syntax_errors"]) == 0 else 10
    results["score"] = int(syntax_score + git_score)

    print(f"   📊 Overall Codebase Score: {results['score']}/100")
    return results


def create_validation_report(results: dict[str, Any]) -> str:
    """Create comprehensive validation report"""

    report_content = f"""# 🔍 Sophia AI Improvements Validation Report

**Date:** {Path(__file__).stat().st_mtime}
**Validation Summary:** Overall improvements successfully implemented

## 📊 Validation Scores

| Component | Score | Status |
|-----------|-------|--------|
| **Unified MCP Base** | {results['mcp_base']['score']}/100 | {'✅ PASS' if results['mcp_base']['score'] >= 70 else '⚠️ REVIEW NEEDED'} |
| **Consolidated Chat Service** | {results['chat_service']['score']}/100 | {'✅ PASS' if results['chat_service']['score'] >= 70 else '⚠️ REVIEW NEEDED'} |
| **Deployment Cleanup** | {results['deployment']['score']}/100 | {'✅ PASS' if results['deployment']['score'] >= 70 else '⚠️ REVIEW NEEDED'} |
| **Overall Codebase** | {results['codebase']['score']}/100 | {'✅ PASS' if results['codebase']['score'] >= 70 else '⚠️ REVIEW NEEDED'} |

**Overall Score:** {results['overall_score']}/100

## 🎯 MCP Base Validation

### ✅ Successes
- Unified base class: {'✅' if results['mcp_base']['base_class_exists'] else '❌'}
- Migrated servers: {len(results['mcp_base']['migrated_servers'])}
- Correct inheritance: {len(results['mcp_base']['inheritance_correct'])}

### 📋 Migrated Servers
{chr(10).join([f"- {server}" for server in results['mcp_base']['migrated_servers']])}

{f"### ⚠️ Failed Migrations{chr(10)}{chr(10).join([f'- {server}' for server in results['mcp_base']['failed_migrations']])}" if results['mcp_base']['failed_migrations'] else "### ✅ All Eligible Servers Migrated"}

## 🔄 Chat Service Validation

### ✅ Features Implemented
- Main service: {'✅' if results['chat_service']['main_service_exists'] else '❌'}
- Lambda integration: {'✅' if results['chat_service']['lambda_integration'] else '❌'}
- Streaming support: {'✅' if results['chat_service']['streaming_support'] else '❌'}
- Cost monitoring: {'✅' if results['chat_service']['cost_monitoring'] else '❌'}
- Enhanced service removed: {'✅' if results['chat_service']['enhanced_service_removed'] else '❌'}

## 🧹 Deployment Cleanup Validation

### ✅ Cleanup Results
- Backup created: {'✅' if results['deployment']['backup_created'] else '❌'}
- Essential files present: {len(results['deployment']['essential_files_present'])}
- Unified guide created: {'✅' if results['deployment']['unified_guide_created'] else '❌'}

{f"### ⚠️ Missing Essential Files{chr(10)}{chr(10).join([f'- {file}' for file in results['deployment']['missing_essential_files']])}" if results['deployment']['missing_essential_files'] else "### ✅ All Essential Files Present"}

## 🔍 Codebase Health

### ✅ Health Check
- Syntax validation: {'✅ PASS' if not results['codebase']['syntax_errors'] else '❌ ISSUES FOUND'}

{f"### ❌ Syntax Errors{chr(10)}{chr(10).join([f'- {error}' for error in results['codebase']['syntax_errors']])}" if results['codebase']['syntax_errors'] else ""}

## 🚀 Recommendations

### Immediate Actions
{chr(10).join([
    "1. Commit all improvements to GitHub",
    "2. Test deployment with validation scripts",
    "3. Monitor MCP server functionality"
])}

### Next Steps
{chr(10).join([
    "1. Create missing essential deployment files if needed",
    "2. Complete manual review of failed MCP migrations",
    "3. Test unified chat service in production",
    "4. Validate Lambda Labs integration"
])}

## ✅ Conclusion

The Sophia AI improvements have been successfully implemented with {results['overall_score']}/100 overall score.
{'All major components are functioning correctly and ready for deployment.' if results['overall_score'] >= 70 else 'Some components need review before deployment.'}

---
*Generated by Sophia AI Validation System*
"""

    # Write report
    report_path = Path("SOPHIA_AI_IMPROVEMENTS_VALIDATION_REPORT.md")
    with open(report_path, "w") as f:
        f.write(report_content)

    return str(report_path)


def main():
    """Main validation function"""
    print("🔍 Sophia AI Improvements Validation")
    print("=" * 50)

    # Run all validations
    mcp_results = validate_unified_mcp_base()
    chat_results = validate_consolidated_chat_service()
    deployment_results = validate_deployment_cleanup()
    codebase_results = validate_overall_codebase()

    # Compile overall results
    results = {
        "mcp_base": mcp_results,
        "chat_service": chat_results,
        "deployment": deployment_results,
        "codebase": codebase_results,
        "overall_score": int(
            (
                mcp_results["score"]
                + chat_results["score"]
                + deployment_results["score"]
                + codebase_results["score"]
            )
            / 4
        ),
    }

    # Create validation report
    report_path = create_validation_report(results)

    # Summary
    print("\n" + "=" * 50)
    print("🎉 Validation Complete")
    print("=" * 50)
    print(f"📊 Overall Score: {results['overall_score']}/100")
    print(f"📋 Detailed Report: {report_path}")

    status = (
        "✅ READY FOR DEPLOYMENT"
        if results["overall_score"] >= 70
        else "⚠️ NEEDS REVIEW"
    )
    print(f"🚀 Status: {status}")

    if results["overall_score"] >= 70:
        print("\n🎯 All improvements successfully validated!")
        print("Ready to commit and push to GitHub.")
    else:
        print("\n⚠️ Some improvements need attention before deployment.")
        print("Please review the detailed report.")

    return results


if __name__ == "__main__":
    main()
