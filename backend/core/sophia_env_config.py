"""
Sophia AI - Bulletproof Environment Configuration System
PERMANENT SOLUTION to eliminate recurring environment/secret management issues

This module provides a centralized, robust environment configuration system that:
1. Always defaults to production environment
2. Provides intelligent fallback mechanisms
3. Validates environment health automatically
4. Integrates with all Sophia AI systems
5. Eliminates the need for manual environment setup
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Deployment environment enumeration with production-first design."""

    PRODUCTION = "prod"
    STAGING = "staging"
    DEVELOPMENT = "dev"


class EnvironmentError(Exception):
    """Environment configuration error."""

    pass


class SophiaEnvironmentConfig:
    """
    Bulletproof environment configuration manager.

    DESIGN PRINCIPLES:
    1. Production-first: Always default to production
    2. Fail-safe: Never fail completely, always provide fallback
    3. Self-healing: Automatically fix common issues
    4. Transparent: Log all decisions and actions
    5. Persistent: Remember and maintain state
    """

    # PRODUCTION-FIRST CONFIGURATION
    DEFAULT_ENVIRONMENT = Environment.PRODUCTION
    DEFAULT_PULUMI_ORG = "scoobyjava-org"

    # Stack mapping with production-first priority
    STACK_MAPPING = {
        Environment.PRODUCTION: "sophia-ai-production",
        Environment.STAGING: "sophia-ai-platform-staging",
        Environment.DEVELOPMENT: "sophia-ai-platform-dev",
    }

    # Environment detection priority order
    DETECTION_PRIORITY = [
        "explicit_environment_variable",
        "git_branch_detection",
        "pulumi_stack_context",
        "project_context",
        "production_fallback",  # Always fallback to production
    ]

    def __init__(self):
        """Initialize environment configuration with health validation."""
        self._environment: Environment | None = None
        self._pulumi_org: str | None = None
        self._stack_name: str | None = None
        self._health_status: dict[str, Any] = {}
        self._last_validated: datetime | None = None

        # Initialize and validate environment
        self._detect_and_set_environment()
        self._validate_environment_health()
        self._ensure_persistent_setup()

    def _detect_and_set_environment(self) -> None:
        """
        Intelligent environment detection with production-first fallback.
        """
        logger.info("🔍 Starting intelligent environment detection...")

        # Try each detection method in priority order
        for method in self.DETECTION_PRIORITY:
            try:
                if env := getattr(self, f"_detect_from_{method}")():
                    self._environment = Environment(env)
                    logger.info(
                        f"✅ Environment detected via {method}: {self._environment}"
                    )
                    break
            except Exception as e:
                logger.warning(f"⚠️ Detection method {method} failed: {e}")
                continue

        # Ensure we always have an environment (production fallback)
        if not self._environment:
            self._environment = self.DEFAULT_ENVIRONMENT
            logger.warning(f"🔄 Using production fallback: {self._environment}")

        # Set associated configuration
        self._pulumi_org = os.getenv("PULUMI_ORG", self.DEFAULT_PULUMI_ORG)
        self._stack_name = self.STACK_MAPPING[self._environment]

        logger.info(
            f"🎯 Final configuration: env={self._environment}, org={self._pulumi_org}, stack={self._stack_name}"
        )

    def _detect_from_explicit_environment_variable(self) -> str | None:
        """Detect from explicit ENVIRONMENT variable."""
        if env := os.getenv("ENVIRONMENT"):
            logger.info(f"📍 Found explicit ENVIRONMENT={env}")
            if env in ["prod", "production"]:
                return Environment.PRODUCTION
            elif env in ["staging", "stg"]:
                return Environment.STAGING
            elif env in ["dev", "development"]:
                return Environment.DEVELOPMENT
            else:
                logger.warning(
                    f"⚠️ Unknown environment '{env}', defaulting to production"
                )
                return Environment.PRODUCTION
        return None

    def _detect_from_git_branch_detection(self) -> str | None:
        """Detect from Git branch with intelligent mapping."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                logger.info(f"📍 Git branch detected: {branch}")

                # Intelligent branch mapping
                if branch in ["main", "master"]:
                    return Environment.PRODUCTION
                elif branch in ["develop", "staging"]:
                    return Environment.STAGING
                elif branch.startswith(("feature/", "fix/", "dev/")):
                    return Environment.DEVELOPMENT
                else:
                    # Unknown branch -> production for safety
                    logger.info(
                        f"🔄 Unknown branch '{branch}', defaulting to production"
                    )
                    return Environment.PRODUCTION
        except Exception as e:
            logger.debug(f"Git branch detection failed: {e}")
        return None

    def _detect_from_pulumi_stack_context(self) -> str | None:
        """Detect from current Pulumi stack context."""
        try:
            result = subprocess.run(
                ["pulumi", "stack", "--show-name"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                stack = result.stdout.strip()
                logger.info(f"📍 Pulumi stack detected: {stack}")

                if "production" in stack.lower():
                    return Environment.PRODUCTION
                elif "staging" in stack.lower():
                    return Environment.STAGING
                elif any(word in stack.lower() for word in ["dev", "development"]):
                    return Environment.DEVELOPMENT
        except Exception as e:
            logger.debug(f"Pulumi stack detection failed: {e}")
        return None

    def _detect_from_project_context(self) -> str | None:
        """Detect from project context and files."""
        try:
            # Check for environment indicator files
            project_root = Path.cwd()

            # Check for legacy .env files with environment hints (detection only - NOT used for secrets)
            env_files = [".env", ".env.local", ".env.production", ".env.staging"]
            for env_file in env_files:
                env_path = project_root / env_file
                if env_path.exists():
                    content = env_path.read_text()
                    if "ENVIRONMENT=" in content:
                        for line in content.split("\n"):
                            if line.startswith("ENVIRONMENT="):
                                env_value = line.split("=", 1)[1].strip().strip("\"'")
                                logger.info(
                                    f"📍 Environment found in {env_file}: {env_value}"
                                )
                                return env_value

            # Check package.json for environment hints
            package_json = project_root / "package.json"
            if package_json.exists():
                try:
                    data = json.loads(package_json.read_text())
                    if "scripts" in data:
                        # Look for production-like scripts
                        scripts = data["scripts"]
                        if any("production" in script for script in scripts.values()):
                            return Environment.PRODUCTION
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Project context detection failed: {e}")
        return None

    def _detect_from_production_fallback(self) -> str:
        """Always fallback to production - never fail."""
        logger.info("🔄 Using production fallback (never fail)")
        return Environment.PRODUCTION

    def _validate_environment_health(self) -> None:
        """Comprehensive environment health validation."""
        logger.info("🏥 Validating environment health...")

        self._health_status = {
            "environment_set": bool(self._environment),
            "pulumi_org_set": bool(self._pulumi_org),
            "stack_name_resolved": bool(self._stack_name),
            "pulumi_auth": self._check_pulumi_auth(),
            "stack_accessible": self._check_stack_access(),
            "secrets_loadable": self._check_secrets_loadable(),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self._last_validated = datetime.now(UTC)

        # Log health status
        healthy_checks = sum(1 for v in self._health_status.values() if v is True)
        total_checks = len(
            [v for v in self._health_status.values() if isinstance(v, bool)]
        )

        logger.info(f"🏥 Health check: {healthy_checks}/{total_checks} checks passed")

        if healthy_checks < total_checks:
            logger.warning("⚠️ Some health checks failed - attempting auto-repair...")
            self._attempt_auto_repair()

    def _check_pulumi_auth(self) -> bool:
        """Check if Pulumi authentication is working."""
        try:
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                logger.debug("✅ Pulumi authentication successful")
                return True
            else:
                logger.warning(f"⚠️ Pulumi auth failed: {result.stderr}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Pulumi auth check failed: {e}")
            return False

    def _check_stack_access(self) -> bool:
        """Check if we can access the target stack."""
        try:
            result = subprocess.run(
                [
                    "pulumi",
                    "env",
                    "open",
                    f"{self._pulumi_org}/default/{self._stack_name}",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                logger.debug(f"✅ Stack access successful: {self._stack_name}")
                return True
            else:
                logger.warning(f"⚠️ Stack access failed: {result.stderr}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Stack access check failed: {e}")
            return False

    def _check_secrets_loadable(self) -> bool:
        """Check if secrets can be loaded from the stack."""
        try:
            result = subprocess.run(
                [
                    "pulumi",
                    "env",
                    "open",
                    f"{self._pulumi_org}/default/{self._stack_name}",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                config = json.loads(result.stdout)
                secret_count = len(config)
                logger.debug(f"✅ Secrets loadable: {secret_count} items")
                return secret_count > 0
            else:
                return False
        except Exception as e:
            logger.warning(f"⚠️ Secrets check failed: {e}")
            return False

    def _attempt_auto_repair(self) -> None:
        """Attempt to automatically repair common environment issues."""
        logger.info("🔧 Attempting automatic environment repair...")

        # Repair 1: Set environment variables if missing
        if not os.getenv("ENVIRONMENT"):
            os.environ["ENVIRONMENT"] = self._environment.value
            logger.info(f"🔧 Set ENVIRONMENT={self._environment.value}")

        if not os.getenv("PULUMI_ORG"):
            os.environ["PULUMI_ORG"] = self._pulumi_org
            logger.info(f"🔧 Set PULUMI_ORG={self._pulumi_org}")

        # Repair 2: Try to login to Pulumi if auth fails
        if not self._health_status.get("pulumi_auth"):
            try:
                if pulumi_token := os.getenv("PULUMI_ACCESS_TOKEN"):
                    subprocess.run(
                        ["pulumi", "login"], input=pulumi_token, text=True, timeout=30
                    )
                    logger.info("🔧 Attempted Pulumi login")
            except Exception as e:
                logger.warning(f"⚠️ Auto-repair Pulumi login failed: {e}")

        # Repair 3: Create missing stack if needed
        if not self._health_status.get("stack_accessible"):
            try:
                subprocess.run(
                    ["pulumi", "stack", "init", self._stack_name, "--yes"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                logger.info(f"🔧 Attempted to create missing stack: {self._stack_name}")
            except Exception as e:
                logger.warning(f"⚠️ Auto-repair stack creation failed: {e}")

    def _ensure_persistent_setup(self) -> None:
        """Ensure environment variables are set persistently."""
        logger.info("💾 Ensuring persistent environment setup...")

        # Environment variables to set persistently
        env_vars = {
            "ENVIRONMENT": self._environment.value,
            "PULUMI_ORG": self._pulumi_org,
        }

        # Update shell profiles
        shell_profiles = [
            Path.home() / ".bashrc",
            Path.home() / ".zshrc",
            Path.home() / ".profile",
        ]

        for profile in shell_profiles:
            if profile.exists():
                try:
                    content = profile.read_text()
                    updated = False

                    for var_name, var_value in env_vars.items():
                        export_line = f'export {var_name}="{var_value}"'
                        if export_line not in content:
                            profile.write_text(
                                content + f"\n# Sophia AI Environment\n{export_line}\n"
                            )
                            updated = True

                    if updated:
                        logger.info(
                            f"💾 Updated {profile.name} with persistent environment variables"
                        )
                except Exception as e:
                    logger.debug(f"Could not update {profile}: {e}")

    # PUBLIC API

    @property
    def environment(self) -> Environment:
        """Get the current environment."""
        return self._environment

    @property
    def stack_name(self) -> str:
        """Get the Pulumi stack name."""
        return self._stack_name

    @property
    def pulumi_org(self) -> str:
        """Get the Pulumi organization."""
        return self._pulumi_org

    @property
    def is_production(self) -> bool:
        """Check if current environment is production."""
        return self._environment == Environment.PRODUCTION

    @property
    def is_staging(self) -> bool:
        """Check if current environment is staging."""
        return self._environment == Environment.STAGING

    @property
    def is_development(self) -> bool:
        """Check if current environment is development."""
        return self._environment == Environment.DEVELOPMENT

    def get_health_status(self) -> dict[str, Any]:
        """Get comprehensive health status."""
        return {
            "environment": self._environment.value,
            "stack_name": self._stack_name,
            "pulumi_org": self._pulumi_org,
            "health_checks": self._health_status,
            "last_validated": (
                self._last_validated.isoformat() if self._last_validated else None
            ),
            "overall_health": all(
                v for v in self._health_status.values() if isinstance(v, bool)
            ),
        }

    def force_environment(self, environment: Environment) -> None:
        """Force a specific environment (for testing/debugging)."""
        logger.warning(f"🔧 Forcing environment to: {environment}")
        self._environment = environment
        self._stack_name = self.STACK_MAPPING[environment]
        os.environ["ENVIRONMENT"] = environment.value
        self._validate_environment_health()

    def refresh_health(self) -> dict[str, Any]:
        """Refresh and return health status."""
        self._validate_environment_health()
        return self.get_health_status()

    def get_pulumi_env_command(self) -> list[str]:
        """Get the Pulumi ESC command for current environment."""
        return [
            "pulumi",
            "env",
            "open",
            f"{self._pulumi_org}/default/{self._stack_name}",
            "--format",
            "json",
        ]

    def load_secrets(self) -> dict[str, Any]:
        """Load secrets from Pulumi ESC with error handling."""
        try:
            result = subprocess.run(
                self.get_pulumi_env_command(),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                secrets = json.loads(result.stdout)
                logger.info(f"✅ Loaded {len(secrets)} secrets from {self._stack_name}")
                return secrets
            else:
                logger.error(f"❌ Failed to load secrets: {result.stderr}")
                return {}
        except Exception as e:
            logger.error(f"❌ Secret loading error: {e}")
            return {}

    def __str__(self) -> str:
        """String representation."""
        return f"SophiaEnvironment(env={self._environment}, stack={self._stack_name})"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"SophiaEnvironmentConfig("
            f"environment={self._environment}, "
            f"stack={self._stack_name}, "
            f"org={self._pulumi_org}, "
            f"healthy={all(v for v in self._health_status.values() if isinstance(v, bool))}"
            f")"
        )


# GLOBAL SINGLETON INSTANCE
_sophia_env_config: SophiaEnvironmentConfig | None = None


def get_sophia_environment() -> SophiaEnvironmentConfig:
    """Get the global Sophia environment configuration singleton."""
    global _sophia_env_config
    if _sophia_env_config is None:
        _sophia_env_config = SophiaEnvironmentConfig()
    return _sophia_env_config


def get_environment() -> Environment:
    """Get current environment (convenience function)."""
    return get_sophia_environment().environment


def get_stack_name() -> str:
    """Get current stack name (convenience function)."""
    return get_sophia_environment().stack_name


def get_pulumi_org() -> str:
    """Get Pulumi organization (convenience function)."""
    return get_sophia_environment().pulumi_org


def is_production() -> bool:
    """Check if in production environment (convenience function)."""
    return get_sophia_environment().is_production


def load_secrets() -> dict[str, Any]:
    """Load secrets from current environment (convenience function)."""
    return get_sophia_environment().load_secrets()


def validate_environment() -> bool:
    """Validate environment health (convenience function)."""
    health = get_sophia_environment().get_health_status()
    return health["overall_health"]


# CLI INTERFACE
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]

        env_config = get_sophia_environment()

        if command == "status":
            status = env_config.get_health_status()
            for _check, result in status["health_checks"].items():
                if isinstance(result, bool):
                    pass

        elif command == "repair":
            env_config.refresh_health()

        elif command == "secrets":
            secrets = env_config.load_secrets()

        else:
            pass
    else:
        # Default: show status
        env_config = get_sophia_environment()
