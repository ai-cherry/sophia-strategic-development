#!/usr/bin/env python3
"""AI Memory MCP Deployment Test Suite.

Comprehensive testing to ensure AI Memory MCP is deployed, working, and discoverable.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AIMemoryDeploymentTester:
    """Comprehensive testing suite for AI Memory MCP deployment."""

    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "pending",
            "errors": [],
            "warnings": [],
        }

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all deployment tests."""
        print("🧪 AI Memory MCP Deployment Test Suite").

        print("=" * 60)

        # Test sequence
        tests = [
            ("config_validation", self.test_config_validation),
            ("server_startup", self.test_server_startup),
            ("dependencies", self.test_dependencies),
            ("cursor_integration", self.test_cursor_integration),
        ]

        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            try:
                result = await test_func()
                self.test_results["tests"][test_name] = result
                status = "✅" if result.get("passed", False) else "❌"
                print(f"   {status} {test_name}: {result.get('message', 'No message')}")

                if result.get("warnings"):
                    for warning in result["warnings"]:
                        print(f"   ⚠️  {warning}")
                        self.test_results["warnings"].append(f"{test_name}: {warning}")

            except Exception as e:
                self.test_results["tests"][test_name] = {
                    "passed": False,
                    "error": str(e),
                    "message": f"Test failed with exception: {e}",
                }
                print(f"   ❌ {test_name}: Exception - {e}")
                self.test_results["errors"].append(f"{test_name}: {e}")

        # Determine overall status
        passed_tests = sum(
            1
            for test in self.test_results["tests"].values()
            if test.get("passed", False)
        )
        total_tests = len(self.test_results["tests"])

        if passed_tests == total_tests:
            self.test_results["overall_status"] = "passed"
        elif passed_tests > total_tests * 0.7:
            self.test_results["overall_status"] = "warning"
        else:
            self.test_results["overall_status"] = "failed"

        # Print summary
        print("\n📊 Test Summary:")
        print(f"   Passed: {passed_tests}/{total_tests}")
        print(f"   Status: {self.test_results['overall_status'].upper()}")

        return self.test_results

    async def test_config_validation(self) -> Dict[str, Any]:
        """Test MCP configuration includes AI Memory server."""
        try:.

            config_path = "mcp_config.json"
            if not os.path.exists(config_path):
                return {"passed": False, "message": "MCP config file not found"}

            with open(config_path, "r") as f:
                config = json.load(f)

            servers = config.get("mcpServers", {})
            if "ai_memory" not in servers:
                return {
                    "passed": False,
                    "message": "AI Memory server not found in MCP config",
                    "available_servers": list(servers.keys()),
                }

            return {"passed": True, "message": "AI Memory server properly configured"}

        except Exception as e:
            return {
                "passed": False,
                "message": "Config validation failed",
                "error": str(e),
            }

    async def test_server_startup(self) -> Dict[str, Any]:
        """Test that AI Memory MCP server can start."""
        try:.

            server_path = "backend/mcp/ai_memory_mcp_server.py"
            if not os.path.exists(server_path):
                return {
                    "passed": False,
                    "message": "AI Memory MCP server file not found",
                }

            # Try to import the server
            try:
                from backend.mcp.ai_memory_mcp_server import AIMemoryMCPServer

                server = AIMemoryMCPServer()

                return {
                    "passed": True,
                    "message": "AI Memory MCP server can be instantiated",
                    "server_name": server.server_name,
                }
            except ImportError as e:
                return {
                    "passed": False,
                    "message": "Failed to import AI Memory MCP server",
                    "error": str(e),
                }

        except Exception as e:
            return {
                "passed": False,
                "message": "Server startup test failed",
                "error": str(e),
            }

    async def test_dependencies(self) -> Dict[str, Any]:
        """Test required dependencies are available."""
        try:.

            missing_deps = []
            warnings = []

            # Test core dependencies
            try:
                import pinecone
            except ImportError:
                missing_deps.append("pinecone-client")

            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                missing_deps.append("sentence-transformers")

            try:
                from mcp.types import TextContent, Tool
            except ImportError:
                missing_deps.append("mcp")

            # Test environment variables
            if not os.getenv("PINECONE_API_KEY"):
                warnings.append("PINECONE_API_KEY environment variable not set")

            if missing_deps:
                return {
                    "passed": False,
                    "message": f"Missing dependencies: {missing_deps}",
                    "missing_dependencies": missing_deps,
                    "warnings": warnings,
                }

            return {
                "passed": True,
                "message": "All dependencies available",
                "warnings": warnings,
            }

        except Exception as e:
            return {
                "passed": False,
                "message": "Dependency test failed",
                "error": str(e),
            }

    async def test_cursor_integration(self) -> Dict[str, Any]:
        """Test Cursor AI integration readiness."""
        try:.

            warnings = []

            # Check .cursorrules file
            cursorrules_path = ".cursorrules"
            if os.path.exists(cursorrules_path):
                with open(cursorrules_path, "r") as f:
                    content = f.read()

                if "AI Memory MCP Integration" in content:
                    cursorrules_ok = True
                else:
                    cursorrules_ok = False
                    warnings.append(
                        ".cursorrules missing AI Memory integration section"
                    )
            else:
                cursorrules_ok = False
                warnings.append(".cursorrules file not found")

            # Check MCP config
            mcp_config_ok = os.path.exists("mcp_config.json")

            # Check auto-discovery file
            auto_discovery_ok = os.path.exists(
                "backend/mcp/ai_memory_auto_discovery.py"
            )

            all_checks = [cursorrules_ok, mcp_config_ok, auto_discovery_ok]
            passed_checks = sum(all_checks)

            return {
                "passed": passed_checks >= 2,
                "message": f"Cursor integration readiness: {passed_checks}/3 checks passed",
                "cursorrules_updated": cursorrules_ok,
                "mcp_config_exists": mcp_config_ok,
                "auto_discovery_exists": auto_discovery_ok,
                "warnings": warnings,
            }

        except Exception as e:
            return {
                "passed": False,
                "message": "Cursor integration test failed",
                "error": str(e),
            }

    def save_test_results(self, filename: str = "ai_memory_test_results.json"):
        """Save test results to file."""
        try:.

            with open(filename, "w") as f:
                json.dump(self.test_results, f, indent=2)
            print(f"\n💾 Test results saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save test results: {e}")


async def main():
    """Run the deployment test suite."""
    tester = AIMemoryDeploymentTester()

    try:
        # Run all tests
        results = await tester.run_all_tests()

        # Save results
        tester.save_test_results()

        # Print final status
        print(f"\n🎯 Final Status: {results['overall_status'].upper()}")

        if results["overall_status"] == "passed":
            print("✅ AI Memory MCP system is ready for use!")
            print("\n📋 Next Steps:")
            print("   1. Start MCP gateway: docker-compose up mcp-gateway")
            print("   2. AI coders will automatically discover the memory system")
            print("   3. Conversations will be stored and recalled automatically")
        elif results["overall_status"] == "warning":
            print("⚠️  AI Memory MCP system is mostly working but has some issues.")
        else:
            print(
                "❌ AI Memory MCP system has significant issues that need to be addressed."
            )

        # Exit with appropriate code
        if results["overall_status"] == "failed":
            sys.exit(1)
        elif results["overall_status"] == "warning":
            sys.exit(2)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⏹️  Test suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test suite failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
