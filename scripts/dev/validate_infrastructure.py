#!/usr/bin/env python3
"""Sophia AI Infrastructure Validation Script.

Tests all critical components for deployment readiness.
"""import logging

import os
import sys
from typing import Any, Dict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class InfrastructureValidator:
    """Validate Sophia AI infrastructure components."""

    def __init__(self):
        self.results = {}

    def test_python_imports(self) -> bool:
        """Test critical Python imports."""logger.info("Testing Python imports...").

        critical_imports = [
            "fastapi",
            "uvicorn",
            "aiohttp",
            "requests",
            "sqlalchemy",
            "psycopg2",
            "redis",
            "openai",
            "anthropic",
            "pydantic",
        ]

        failed_imports = []
        for module in critical_imports:
            try:
                __import__(module)
                logger.info(f"✅ {module}")
            except ImportError as e:
                logger.error(f"❌ {module}: {e}")
                failed_imports.append(module)

        success = len(failed_imports) == 0
        self.results["python_imports"] = {
            "success": success,
            "failed": failed_imports,
            "total": len(critical_imports),
        }
        return success

    def test_backend_structure(self) -> bool:
        """Test backend module structure."""logger.info("Testing backend structure...").

        required_modules = [
            "backend.core.secure_credential_manager",
            "backend.agents.core.orchestrator",
            "backend.integrations.kong_ai_gateway",
            "backend.integrations.natural_language_processor",
        ]

        failed_modules = []
        for module in required_modules:
            try:
                __import__(module)
                logger.info(f"✅ {module}")
            except ImportError as e:
                logger.error(f"❌ {module}: {e}")
                failed_modules.append(module)

        success = len(failed_modules) == 0
        self.results["backend_structure"] = {
            "success": success,
            "failed": failed_modules,
            "total": len(required_modules),
        }
        return success

    def test_credential_manager(self) -> bool:
        """Test secure credential manager."""logger.info("Testing credential manager...").

        try:
            from backend.core.secure_credential_manager import credential_manager

            # Test credential status
            status = credential_manager.get_credential_status()
            missing = credential_manager.get_missing_credentials()

            logger.info("✅ Credential manager loaded")
            logger.info(f"📊 Total credentials: {len(status)}")
            logger.info(f"⚠️  Missing credentials: {len(missing)}")

            self.results["credential_manager"] = {
                "success": True,
                "total_credentials": len(status),
                "missing_credentials": len(missing),
                "missing_list": missing,
            }
            return True

        except Exception as e:
            logger.error(f"❌ Credential manager error: {e}")
            self.results["credential_manager"] = {"success": False, "error": str(e)}
            return False

    def test_fastapi_app_creation(self) -> bool:
        """Test FastAPI app creation without running event loop."""logger.info("Testing FastAPI app creation...").

        try:
            # Import without triggering async initialization
            import backend.main

            # Check if app variable exists
            if hasattr(backend.main, "app"):
                logger.info("✅ FastAPI app variable exists")
                app = backend.main.app
                logger.info(f"✅ App type: {type(app)}")

                # Get routes without triggering async operations
                try:
                    routes = [route.path for route in app.routes]
                    logger.info(f"✅ App has {len(routes)} routes")
                    logger.info(f"✅ Sample routes: {routes[:3]}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not get routes: {e}")

                self.results["fastapi_app"] = {
                    "success": True,
                    "app_type": str(type(app)),
                    "routes_count": len(routes) if "routes" in locals() else 0,
                }
                return True
            else:
                logger.error("❌ FastAPI app variable not found")
                self.results["fastapi_app"] = {
                    "success": False,
                    "error": "App variable not found",
                }
                return False

        except Exception as e:
            logger.error(f"❌ FastAPI app creation error: {e}")
            self.results["fastapi_app"] = {"success": False, "error": str(e)}
            return False

    def test_deployment_scripts(self) -> bool:
        """Test deployment script syntax."""logger.info("Testing deployment scripts...").

        scripts = [
            "scripts/deploy_production_mcp.py",
            "quick_setup.sh",
            "scripts/start_ceo_dashboard.sh",
        ]

        failed_scripts = []
        for script in scripts:
            if os.path.exists(script):
                if script.endswith(".sh"):
                    result = os.system(f"bash -n {script} 2>/dev/null")  # nosec B605
                elif script.endswith(".py"):
                    result = os.system(f"python -m py_compile {script} 2>/dev/null")  # nosec B605
                else:
                    logger.warning(f"Unknown script type for {script}")
                    result = 1
                if result == 0:
                    logger.info(f"✅ {script}")
                else:
                    logger.error(f"❌ {script}: syntax error")
                    failed_scripts.append(script)
            else:
                logger.warning(f"⚠️  {script}: not found")
                failed_scripts.append(script)

        success = len(failed_scripts) == 0
        self.results["deployment_scripts"] = {
            "success": success,
            "failed": failed_scripts,
            "total": len(scripts),
        }
        return success

    def run_validation(self) -> Dict[str, Any]:
        """Run complete infrastructure validation."""
        logger.info("🚀 Starting Sophia AI Infrastructure Validation")
        logger.info("=" * 60)

        tests = [
            ("Python Imports", self.test_python_imports),
            ("Backend Structure", self.test_backend_structure),
            ("Credential Manager", self.test_credential_manager),
            ("FastAPI App", self.test_fastapi_app_creation),
            ("Deployment Scripts", self.test_deployment_scripts),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            logger.info(f"\n📋 {test_name}")
            logger.info("-" * 40)

            try:
                success = test_func()
                if success:
                    passed += 1
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("🎯 VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Tests Passed: {passed}/{total}")
        logger.info(f"Success Rate: {(passed / total) * 100:.1f}%")

        if passed == total:
            logger.info("🎉 ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT!")
        else:
            logger.warning(f"⚠️  {total - passed} TESTS FAILED - SYSTEM NEEDS FIXES")

        self.results["summary"] = {
            "passed": passed,
            "total": total,
            "success_rate": (passed / total) * 100,
            "ready_for_deployment": passed == total,
        }

        return self.results


if __name__ == "__main__":
    validator = InfrastructureValidator()
    results = validator.run_validation()

    # Exit with appropriate code
    if results["summary"]["ready_for_deployment"]:
        sys.exit(0)
    else:
        sys.exit(1)
