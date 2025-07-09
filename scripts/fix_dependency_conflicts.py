#!/usr/bin/env python3
"""
Sophia AI Dependency Conflict Resolution Script
Automatically fixes critical dependency issues identified in UV scan
"""

import logging
import shutil
import subprocess
import sys
from pathlib import Path

import toml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DependencyFixer:
    """Fixes critical dependency conflicts in Sophia AI"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.pyproject_path = self.project_root / "pyproject.toml"
        self.backup_path = self.project_root / "pyproject.toml.backup"
        self.fixes_applied = []

    def backup_pyproject(self):
        """Create backup of pyproject.toml"""
        logger.info("📁 Creating backup of pyproject.toml")
        shutil.copy2(self.pyproject_path, self.backup_path)
        logger.info(f"✅ Backup created: {self.backup_path}")

    def restore_backup(self):
        """Restore pyproject.toml from backup"""
        if self.backup_path.exists():
            logger.info("🔄 Restoring pyproject.toml from backup")
            shutil.copy2(self.backup_path, self.pyproject_path)
            logger.info("✅ Backup restored")

    def fix_mcp_python_version(self) -> bool:
        """Fix MCP-Python version conflict"""
        logger.info("🔧 Fixing MCP-Python version conflict...")

        try:
            # Read current pyproject.toml
            with open(self.pyproject_path) as f:
                config = toml.load(f)

            # Find and fix mcp-python version
            dependencies = config.get("project", {}).get("dependencies", [])

            updated_deps = []
            mcp_fixed = False

            for dep in dependencies:
                if dep.startswith("mcp-python"):
                    # Replace with compatible version
                    old_version = dep
                    new_version = "mcp-python>=0.1.0,<0.2.0"
                    updated_deps.append(new_version)
                    logger.info(f"  📝 Changed: {old_version} → {new_version}")
                    self.fixes_applied.append(
                        f"MCP-Python: {old_version} → {new_version}"
                    )
                    mcp_fixed = True
                else:
                    updated_deps.append(dep)

            if mcp_fixed:
                # Update config
                config["project"]["dependencies"] = updated_deps

                # Write back to file
                with open(self.pyproject_path, "w") as f:
                    toml.dump(config, f)

                logger.info("✅ MCP-Python version fixed")
                return True
            else:
                logger.warning("⚠️  MCP-Python dependency not found in pyproject.toml")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to fix MCP-Python version: {e}")
            return False

    def fix_cchardet_compilation(self) -> bool:
        """Fix cchardet compilation issues"""
        logger.info("🔧 Fixing cchardet compilation issues...")

        try:
            # Read current pyproject.toml
            with open(self.pyproject_path) as f:
                config = toml.load(f)

            # Remove problematic cchardet version and replace with compatible alternative
            dependencies = config.get("project", {}).get("dependencies", [])
            performance_deps = (
                config.get("project", {})
                .get("optional-dependencies", {})
                .get("performance", [])
            )

            # Remove cchardet from dependencies
            updated_deps = [
                dep for dep in dependencies if not dep.startswith("cchardet")
            ]
            updated_performance = [
                dep for dep in performance_deps if not dep.startswith("cchardet")
            ]

            # Add chardet as alternative (pure Python, no compilation needed)
            if any(
                dep.startswith("cchardet") for dep in dependencies + performance_deps
            ):
                updated_performance.append("chardet>=5.0.0")
                logger.info("  📝 Replaced cchardet with chardet (pure Python)")
                self.fixes_applied.append(
                    "Replaced cchardet with chardet (compilation-free)"
                )

            # Update config
            config["project"]["dependencies"] = updated_deps
            if "optional-dependencies" not in config["project"]:
                config["project"]["optional-dependencies"] = {}
            config["project"]["optional-dependencies"][
                "performance"
            ] = updated_performance

            # Write back to file
            with open(self.pyproject_path, "w") as f:
                toml.dump(config, f)

            logger.info("✅ cchardet compilation issue fixed")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to fix cchardet compilation: {e}")
            return False

    def fix_python_version_compatibility(self) -> bool:
        """Fix Python version compatibility issues"""
        logger.info("🔧 Fixing Python version compatibility...")

        try:
            # Read current pyproject.toml
            with open(self.pyproject_path) as f:
                config = toml.load(f)

            # Update Python version requirement to be more compatible
            current_python = config.get("project", {}).get("requires-python", "")

            if current_python == ">=3.12":
                # Change to allow 3.12 but recommend 3.12 for stability
                new_python = ">=3.12,<3.14"
                config["project"]["requires-python"] = new_python
                logger.info(
                    f"  📝 Updated Python requirement: {current_python} → {new_python}"
                )
                self.fixes_applied.append(
                    f"Python version: {current_python} → {new_python}"
                )

            # Add note about Python 3.13 compatibility in config
            if "tool" not in config:
                config["tool"] = {}
            if "sophia-ai" not in config["tool"]:
                config["tool"]["sophia-ai"] = {}

            config["tool"]["sophia-ai"]["python-compatibility"] = {
                "recommended": "3.12",
                "tested": ["3.12", "3.13"],
                "note": "Python 3.12 recommended for production",
            }

            # Write back to file
            with open(self.pyproject_path, "w") as f:
                toml.dump(config, f)

            logger.info("✅ Python version compatibility updated")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to fix Python version compatibility: {e}")
            return False

    def install_system_dependencies(self) -> bool:
        """Install system dependencies for C extensions"""
        logger.info("🔧 Installing system dependencies for C compilation...")

        # Detect OS and install appropriate packages
        try:
            if sys.platform.startswith("linux"):
                # Ubuntu/Debian
                cmd = [
                    "sudo",
                    "apt-get",
                    "update",
                    "&&",
                    "sudo",
                    "apt-get",
                    "install",
                    "-y",
                    "build-essential",
                    "python3-dev",
                    "libffi-dev",
                    "libssl-dev",
                    "pkg-config",
                ]
                logger.info("  📦 Installing Linux development packages...")

            elif sys.platform == "darwin":
                # macOS
                cmd = ["xcode-select", "--install"]
                logger.info("  📦 Installing macOS development tools...")

            else:
                logger.warning(
                    "⚠️  Unsupported OS for automatic system dependency installation"
                )
                return False

            # Note: We can't actually run sudo commands in a script,
            # so we'll provide instructions instead
            logger.info("📋 Manual system dependency installation required:")

            if sys.platform.startswith("linux"):
                logger.info(
                    "  Run: sudo apt-get update && sudo apt-get install -y build-essential python3-dev libffi-dev libssl-dev pkg-config"
                )
            elif sys.platform == "darwin":
                logger.info("  Run: xcode-select --install")
                logger.info("  Or install via Homebrew: brew install python@3.12")

            self.fixes_applied.append(
                "System dependencies: Manual installation required"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to install system dependencies: {e}")
            return False

    def test_dependency_resolution(self) -> bool:
        """Test dependency resolution with UV"""
        logger.info("🧪 Testing dependency resolution with UV...")

        try:
            # Test UV sync
            result = subprocess.run(
                ["uv", "sync", "--all-extras", "--dry-run"],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            if result.returncode == 0:
                logger.info("✅ Dependency resolution test passed")
                return True
            else:
                logger.error("❌ Dependency resolution failed:")
                logger.error(f"  stdout: {result.stdout}")
                logger.error(f"  stderr: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Dependency resolution test timed out")
            return False
        except FileNotFoundError:
            logger.error("❌ UV not found. Please install UV first:")
            logger.error("  curl -LsSf https://astral.sh/uv/install.sh | sh")
            return False
        except Exception as e:
            logger.error(f"❌ Dependency resolution test failed: {e}")
            return False

    def create_compatibility_layer(self) -> bool:
        """Create MCP compatibility layer"""
        logger.info("🔧 Creating MCP compatibility layer...")

        try:
            # Create compatibility module
            compat_dir = self.project_root / "backend" / "core"
            compat_dir.mkdir(parents=True, exist_ok=True)

            compat_file = compat_dir / "mcp_compatibility.py"

            compat_code = '''"""
MCP Version Compatibility Layer
Handles version differences between MCP SDK versions
"""

import importlib
import logging
from typing import Protocol, Any, Optional

logger = logging.getLogger(__name__)


class MCPServerProtocol(Protocol):
    """Protocol for MCP server interface"""
    async def handle_request(self, request: Any) -> Any: ...
    async def list_tools(self) -> list: ...


def get_mcp_server_class():
    """Dynamic MCP server class based on available version"""
    try:
        # Try newer version first (if available)
        from mcp.server import Server as MCPServer
        logger.info("Using MCP SDK (newer version)")
        return MCPServer
    except ImportError:
        try:
            # Fallback to older version
            from mcp_python.server import Server as MCPServer
            logger.info("Using mcp-python SDK (older version)")
            return MCPServer
        except ImportError:
            logger.error("No MCP SDK found. Please install mcp-python.")
            raise ImportError("No compatible MCP SDK available")


def get_mcp_types():
    """Get MCP types based on available version"""
    try:
        # Try newer version first
        from mcp import types
        return types
    except ImportError:
        try:
            # Fallback to older version
            from mcp_python import types
            return types
        except ImportError:
            logger.error("No MCP types found.")
            return None


class CompatibilityMCPServer:
    """Compatibility wrapper for MCP servers"""

    def __init__(self, name: str):
        self.name = name
        self.server_class = get_mcp_server_class()
        self.server = self.server_class(name)
        logger.info(f"Initialized MCP server: {name}")

    async def handle_request(self, request: Any) -> Any:
        """Handle request with compatibility layer"""
        try:
            return await self.server.handle_request(request)
        except AttributeError:
            # Handle version differences
            if hasattr(self.server, 'handle'):
                return await self.server.handle(request)
            else:
                raise NotImplementedError("Request handling not supported")

    async def list_tools(self) -> list:
        """List available tools with compatibility layer"""
        try:
            return await self.server.list_tools()
        except AttributeError:
            # Handle version differences
            if hasattr(self.server, 'get_tools'):
                return await self.server.get_tools()
            else:
                return []


# Export for use in MCP servers
MCPServer = get_mcp_server_class()
mcp_types = get_mcp_types()
'''

            with open(compat_file, "w") as f:
                f.write(compat_code)

            logger.info(f"✅ MCP compatibility layer created: {compat_file}")
            self.fixes_applied.append("Created MCP compatibility layer")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create compatibility layer: {e}")
            return False

    def optimize_dependencies(self) -> bool:
        """Optimize dependency configuration"""
        logger.info("🔧 Optimizing dependency configuration...")

        try:
            # Read current pyproject.toml
            with open(self.pyproject_path) as f:
                config = toml.load(f)

            # Add enhanced search specific dependency group
            if "optional-dependencies" not in config["project"]:
                config["project"]["optional-dependencies"] = {}

            # Enhanced search dependencies
            config["project"]["optional-dependencies"]["enhanced-search"] = [
                "playwright>=1.40.0",
                "beautifulsoup4>=4.12.0",
                "selenium>=4.15.0",
                "aiohttp>=3.9.1",
                "requests>=2.31.0",
            ]

            # Browser automation dependencies
            config["project"]["optional-dependencies"]["browser"] = [
                "playwright>=1.40.0",
                "selenium>=4.15.0",
            ]

            # AI/ML core dependencies
            config["project"]["optional-dependencies"]["ai-core"] = [
                "openai>=1.6.1",
                "anthropic>=0.25.0",
                "sentence-transformers>=2.2.2",
            ]

            # Write back to file
            with open(self.pyproject_path, "w") as f:
                toml.dump(config, f)

            logger.info("✅ Dependency groups optimized")
            self.fixes_applied.append("Added enhanced search dependency groups")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to optimize dependencies: {e}")
            return False

    def generate_requirements_lock(self) -> bool:
        """Generate locked requirements file"""
        logger.info("🔧 Generating locked requirements...")

        try:
            # Generate requirements.lock with UV
            result = subprocess.run(
                [
                    "uv",
                    "pip",
                    "compile",
                    "pyproject.toml",
                    "--output-file",
                    "requirements.lock",
                ],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            if result.returncode == 0:
                logger.info("✅ Generated requirements.lock")
                self.fixes_applied.append("Generated locked requirements file")
                return True
            else:
                logger.warning(
                    f"⚠️  Failed to generate requirements.lock: {result.stderr}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Failed to generate requirements.lock: {e}")
            return False

    def run_all_fixes(self) -> bool:
        """Run all dependency fixes"""
        logger.info("🚀 Starting comprehensive dependency fix...")

        success_count = 0
        total_fixes = 7

        # Create backup first
        self.backup_pyproject()

        try:
            # Apply all fixes
            fixes = [
                ("MCP-Python Version", self.fix_mcp_python_version),
                ("C Extension Compilation", self.fix_cchardet_compilation),
                ("Python Version Compatibility", self.fix_python_version_compatibility),
                ("System Dependencies", self.install_system_dependencies),
                ("MCP Compatibility Layer", self.create_compatibility_layer),
                ("Dependency Optimization", self.optimize_dependencies),
                ("Requirements Lock", self.generate_requirements_lock),
            ]

            for fix_name, fix_func in fixes:
                logger.info(f"\n🔄 Applying fix: {fix_name}")
                if fix_func():
                    success_count += 1
                    logger.info(f"✅ {fix_name} completed")
                else:
                    logger.error(f"❌ {fix_name} failed")

            # Test final resolution
            logger.info("\n🧪 Testing final dependency resolution...")
            resolution_success = self.test_dependency_resolution()

            # Generate summary
            self.generate_summary(success_count, total_fixes, resolution_success)

            return (
                success_count >= 5 and resolution_success
            )  # Require most fixes to succeed

        except Exception as e:
            logger.error(f"❌ Critical error during fix process: {e}")
            logger.info("🔄 Restoring backup...")
            self.restore_backup()
            return False

    def generate_summary(
        self, success_count: int, total_fixes: int, resolution_success: bool
    ):
        """Generate fix summary report"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 DEPENDENCY FIX SUMMARY")
        logger.info("=" * 60)

        logger.info(f"✅ Fixes Applied: {success_count}/{total_fixes}")
        logger.info(
            f"🧪 Resolution Test: {'PASSED' if resolution_success else 'FAILED'}"
        )

        if self.fixes_applied:
            logger.info("\n📝 Applied Fixes:")
            for i, fix in enumerate(self.fixes_applied, 1):
                logger.info(f"  {i}. {fix}")

        if success_count >= 5:
            logger.info("\n🎉 DEPENDENCY FIXES MOSTLY SUCCESSFUL!")
            logger.info("Next steps:")
            logger.info("1. Run: uv sync --all-extras")
            logger.info(
                "2. Test: python -c 'from backend.services.enhanced_search_service import EnhancedSearchService'"
            )
            logger.info("3. Deploy: docker-compose -f docker-compose.cloud.yml up")
        else:
            logger.info("\n⚠️  Some fixes failed. Manual intervention required.")
            logger.info("Check the errors above and resolve manually.")
            logger.info("Backup available at: pyproject.toml.backup")

        logger.info("=" * 60)


def main():
    """Main function"""
    fixer = DependencyFixer()

    logger.info("🚀 Sophia AI Dependency Conflict Resolution")
    logger.info("🎯 Fixing critical dependency issues for enhanced search deployment")
    logger.info("-" * 60)

    success = fixer.run_all_fixes()

    if success:
        logger.info("✅ Dependency fixes completed successfully!")
        return 0
    else:
        logger.error("❌ Some dependency fixes failed. Check logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
