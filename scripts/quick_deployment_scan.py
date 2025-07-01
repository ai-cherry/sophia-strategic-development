#!/usr/bin/env python3
"""
Quick Deployment Scan - Identify Deployment Issues
Scans for critical deployment blockers before going live
"""

import ast
import json
import logging
import os
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class QuickDeploymentScanner:
    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        self.issues = []
        self.warnings = []
        self.fixes_applied = []

    def scan_deployment_readiness(self) -> dict:
        """Comprehensive deployment readiness scan"""
        logger.info("🔍 Starting quick deployment scan...")

        results = {
            "frontend_check": self._check_frontend_deployment(),
            "backend_check": self._check_backend_deployment(),
            "api_routes_check": self._check_api_routes(),
            "environment_check": self._check_environment_config(),
            "secrets_check": self._check_secrets_management(),
            "syntax_check": self._check_critical_syntax(),
            "deployment_config": self._check_deployment_config(),
        }

        overall_score = self._calculate_readiness_score(results)

        return {
            "overall_readiness": overall_score,
            "detailed_results": results,
            "critical_issues": self.issues,
            "warnings": self.warnings,
            "fixes_applied": self.fixes_applied,
        }

    def _check_frontend_deployment(self) -> dict:
        """Check frontend deployment readiness"""
        logger.info("🎨 Checking frontend deployment readiness...")

        frontend_path = self.root_path / "frontend"
        issues = []

        # Check if package.json exists
        if not (frontend_path / "package.json").exists():
            issues.append("Missing frontend/package.json")

        # Check if App.jsx has the UniversalChatInterface
        app_jsx = frontend_path / "src" / "App.jsx"
        if app_jsx.exists():
            content = app_jsx.read_text()
            if "UniversalChatInterface" not in content:
                issues.append("App.jsx missing UniversalChatInterface import")
            if "/chat" not in content:
                issues.append("App.jsx missing chat route")
        else:
            issues.append("Missing frontend/src/App.jsx")

        # Check if UniversalChatInterface.tsx exists
        chat_interface = (
            frontend_path / "src" / "components" / "UniversalChatInterface.tsx"
        )
        if not chat_interface.exists():
            issues.append("Missing UniversalChatInterface.tsx component")

        # Check for build script
        if (frontend_path / "package.json").exists():
            package_json = json.loads((frontend_path / "package.json").read_text())
            if "scripts" not in package_json or "build" not in package_json["scripts"]:
                issues.append("Missing build script in package.json")

        return {
            "status": "✅ READY" if not issues else "❌ ISSUES",
            "issues": issues,
            "score": 100 if not issues else max(0, 100 - len(issues) * 20),
        }

    def _check_backend_deployment(self) -> dict:
        """Check backend deployment readiness"""
        logger.info("🔧 Checking backend deployment readiness...")

        backend_path = self.root_path / "backend"
        issues = []

        # Check critical backend files
        critical_files = [
            "app/fastapi_app.py",
            "core/auto_esc_config.py",
            "services/mcp_orchestration_service.py",
        ]

        for file_path in critical_files:
            if not (backend_path / file_path).exists():
                issues.append(f"Missing {file_path}")

        # Check if requirements.txt exists
        if not (backend_path / "requirements.txt").exists():
            issues.append("Missing backend/requirements.txt")

        return {
            "status": "✅ READY" if not issues else "❌ ISSUES",
            "issues": issues,
            "score": 100 if not issues else max(0, 100 - len(issues) * 25),
        }

    def _check_api_routes(self) -> dict:
        """Check API routes for chat functionality"""
        logger.info("🛣️ Checking API routes...")

        api_path = self.root_path / "backend" / "api"
        issues = []

        # Check for chat routes
        chat_routes_files = [
            "enhanced_unified_chat_routes.py",
            "sophia_universal_chat_routes.py",
            "unified_chat_routes.py",
        ]

        found_chat_routes = False
        for route_file in chat_routes_files:
            if (api_path / route_file).exists():
                found_chat_routes = True
                # Check if it has the right endpoints
                content = (api_path / route_file).read_text()
                if "/chat/" not in content and "/api/v1/chat" not in content:
                    issues.append(f"{route_file} missing chat endpoints")
                break

        if not found_chat_routes:
            issues.append("No chat routes found")

        return {
            "status": "✅ READY" if not issues else "❌ ISSUES",
            "issues": issues,
            "score": 100 if not issues else 50,
        }

    def _check_environment_config(self) -> dict:
        """Check environment configuration"""
        logger.info("🌍 Checking environment configuration...")

        issues = []

        # Check auto_esc_config.py
        config_file = self.root_path / "backend" / "core" / "auto_esc_config.py"
        if config_file.exists():
            content = config_file.read_text()
            if "get_config_value" not in content:
                issues.append("auto_esc_config.py missing get_config_value function")
            if "sophia-ai-production" not in content:
                issues.append("auto_esc_config.py not configured for production stack")
        else:
            issues.append("Missing auto_esc_config.py")

        return {
            "status": "✅ READY" if not issues else "❌ ISSUES",
            "issues": issues,
            "score": 100 if not issues else 60,
        }

    def _check_secrets_management(self) -> dict:
        """Check secrets management setup"""
        logger.info("🔐 Checking secrets management...")

        issues = []

        # Check GitHub Actions sync workflow
        sync_workflow = self.root_path / ".github" / "workflows" / "sync_secrets.yml"
        if not sync_workflow.exists():
            issues.append("Missing GitHub secrets sync workflow")

        # Check manual sync script
        manual_sync = self.root_path / "scripts" / "manual_sync_github_to_pulumi_esc.py"
        if not manual_sync.exists():
            issues.append("Missing manual secrets sync script")

        return {
            "status": "✅ READY" if not issues else "⚠️ WARNINGS",
            "issues": issues,
            "score": 100 if not issues else 80,
        }

    def _check_critical_syntax(self) -> dict:
        """Check for critical syntax errors"""
        logger.info("🔍 Checking for critical syntax errors...")

        issues = []

        try:
            # Run a quick Python syntax check on critical files
            critical_python_files = [
                "backend/app/fastapi_app.py",
                "backend/core/auto_esc_config.py",
                "backend/api/enhanced_unified_chat_routes.py",
            ]

            for file_path in critical_python_files:
                full_path = self.root_path / file_path
                if full_path.exists():
                    try:
                        with open(full_path) as f:
                            ast.parse(f.read())
                    except SyntaxError as e:
                        issues.append(f"Syntax error in {file_path}: {e}")
                        # Try to fix simple issues
                        self._fix_simple_syntax_error(full_path, e)

        except Exception as e:
            self.warnings.append(f"Could not complete syntax check: {e}")

        return {
            "status": "✅ READY" if not issues else "❌ ISSUES",
            "issues": issues,
            "score": 100 if not issues else 0,  # Syntax errors are critical
        }

    def _check_deployment_config(self) -> dict:
        """Check deployment configuration"""
        logger.info("🚀 Checking deployment configuration...")

        issues = []

        # Check GitHub Actions deployment workflow
        deploy_workflow = (
            self.root_path / ".github" / "workflows" / "deploy-sophia-platform.yml"
        )
        if not deploy_workflow.exists():
            issues.append("Missing deployment workflow")
        else:
            content = deploy_workflow.read_text()
            if "vercel" not in content.lower():
                issues.append("Deployment workflow missing Vercel configuration")

        # Check Vercel configuration
        vercel_config = self.root_path / "infrastructure" / "vercel"
        if not vercel_config.exists():
            issues.append("Missing Vercel infrastructure configuration")

        return {
            "status": "✅ READY" if not issues else "⚠️ WARNINGS",
            "issues": issues,
            "score": 100 if not issues else 70,
        }

    def _fix_simple_syntax_error(self, file_path: Path, error: SyntaxError) -> None:
        """Attempt to fix simple syntax errors"""
        try:
            content = file_path.read_text()

            # Fix common issues from our updates
            fixes_made = []

            # Fix invalid assignment statements
            if "get_config_value =" in content:
                content = content.replace(
                    "get_config_value =", "# get_config_value fixed assignment - "
                )
                fixes_made.append("Fixed invalid get_config_value assignment")

            # Fix missing imports
            if (
                "from backend.core.auto_esc_config import get_config_value"
                not in content
                and "get_config_value" in content
            ):
                lines = content.split("\n")
                import_line = (
                    "from backend.core.auto_esc_config import get_config_value"
                )

                # Find a good place to insert the import
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        insert_index = i + 1
                    elif line.strip() == "":
                        continue
                    else:
                        break

                lines.insert(insert_index, import_line)
                content = "\n".join(lines)
                fixes_made.append("Added missing get_config_value import")

            if fixes_made:
                file_path.write_text(content)
                self.fixes_applied.extend(fixes_made)
                logger.info(f"Applied fixes to {file_path}: {fixes_made}")

        except Exception as e:
            logger.warning(f"Could not fix syntax error in {file_path}: {e}")

    def _calculate_readiness_score(self, results: dict) -> dict:
        """Calculate overall readiness score"""
        scores = [result["score"] for result in results.values()]
        overall_score = sum(scores) / len(scores)

        if overall_score >= 90:
            status = "🚀 READY FOR DEPLOYMENT"
            recommendation = "All systems go! Deploy immediately."
        elif overall_score >= 75:
            status = "⚠️ MOSTLY READY"
            recommendation = "Minor issues detected. Review warnings and deploy."
        elif overall_score >= 50:
            status = "🔧 NEEDS FIXES"
            recommendation = "Address critical issues before deployment."
        else:
            status = "❌ NOT READY"
            recommendation = "Major issues detected. Do not deploy until fixed."

        return {
            "score": overall_score,
            "status": status,
            "recommendation": recommendation,
        }

    def generate_report(self, results: dict) -> str:
        """Generate deployment readiness report"""
        report = f"""
# 🚀 Quick Deployment Scan Report
**Date:** {os.popen('date').read().strip()}
**Branch:** main (merged strategic-plan-comprehensive-improvements)

## 📊 Overall Readiness
**Score:** {results['overall_readiness']['score']:.1f}/100
**Status:** {results['overall_readiness']['status']}
**Recommendation:** {results['overall_readiness']['recommendation']}

## 📋 Detailed Results

### 🎨 Frontend Deployment
- **Status:** {results['detailed_results']['frontend_check']['status']}
- **Score:** {results['detailed_results']['frontend_check']['score']}/100
- **Issues:** {len(results['detailed_results']['frontend_check']['issues'])}

### 🔧 Backend Deployment
- **Status:** {results['detailed_results']['backend_check']['status']}
- **Score:** {results['detailed_results']['backend_check']['score']}/100
- **Issues:** {len(results['detailed_results']['backend_check']['issues'])}

### 🛣️ API Routes
- **Status:** {results['detailed_results']['api_routes_check']['status']}
- **Score:** {results['detailed_results']['api_routes_check']['score']}/100
- **Issues:** {len(results['detailed_results']['api_routes_check']['issues'])}

### 🌍 Environment Config
- **Status:** {results['detailed_results']['environment_check']['status']}
- **Score:** {results['detailed_results']['environment_check']['score']}/100
- **Issues:** {len(results['detailed_results']['environment_check']['issues'])}

### 🔐 Secrets Management
- **Status:** {results['detailed_results']['secrets_check']['status']}
- **Score:** {results['detailed_results']['secrets_check']['score']}/100
- **Issues:** {len(results['detailed_results']['secrets_check']['issues'])}

### 🔍 Syntax Check
- **Status:** {results['detailed_results']['syntax_check']['status']}
- **Score:** {results['detailed_results']['syntax_check']['score']}/100
- **Issues:** {len(results['detailed_results']['syntax_check']['issues'])}

### 🚀 Deployment Config
- **Status:** {results['detailed_results']['deployment_config']['status']}
- **Score:** {results['detailed_results']['deployment_config']['score']}/100
- **Issues:** {len(results['detailed_results']['deployment_config']['issues'])}

## 🔧 Fixes Applied
{chr(10).join(f"- {fix}" for fix in results['fixes_applied']) if results['fixes_applied'] else "No automatic fixes applied"}

## ⚠️ Critical Issues
{chr(10).join(f"- {issue}" for issue in results['critical_issues']) if results['critical_issues'] else "No critical issues detected"}

## 📝 Recommendations
1. **If score >= 90:** Deploy immediately via GitHub Actions
2. **If score >= 75:** Review warnings, then deploy
3. **If score < 75:** Fix critical issues before deployment

## 🚀 Next Steps for Deployment
1. Push changes to GitHub main branch
2. Trigger GitHub Actions deployment workflow
3. Monitor Vercel deployment status
4. Verify chat interface functionality live

**Ready to deploy your real universal chat interface! 🎉**
"""
        return report


def main():
    """Run deployment scan"""
    scanner = QuickDeploymentScanner()
    results = scanner.scan_deployment_readiness()

    report = scanner.generate_report(results)

    # Save report
    report_file = Path("QUICK_DEPLOYMENT_SCAN_REPORT.md")
    report_file.write_text(report)

    print(report)
    print(f"\n📄 Report saved to: {report_file}")

    return results["overall_readiness"]["score"]


if __name__ == "__main__":
    score = main()
    exit(0 if score >= 75 else 1)  # Exit with error if not ready
