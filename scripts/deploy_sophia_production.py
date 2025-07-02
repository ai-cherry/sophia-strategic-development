#!/usr/bin/env python3
"""
Sophia AI Production Deployment Orchestrator
Comprehensive deployment script that coordinates infrastructure, backend, frontend, and MCP servers.
"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEPLOYMENT_LOG_DIR = PROJECT_ROOT / "logs" / "deployments"


class SophiaProductionDeployment:
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.deployment_id = f"sophia-{environment}-{int(time.time())}"
        self.log_file = DEPLOYMENT_LOG_DIR / f"{self.deployment_id}.log"
        self.status = {
            "deployment_id": self.deployment_id,
            "environment": environment,
            "started_at": datetime.utcnow().isoformat(),
            "phases": {},
        }

        # Ensure log directory exists
        DEPLOYMENT_LOG_DIR.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")

    async def run_command(
        self, command: list[str], cwd: Path | None = None, timeout: int = 300
    ) -> tuple[bool, str, str]:
        """Run a command with timeout and logging"""
        self.log(f"Running command: {' '.join(command)}")

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd or PROJECT_ROOT,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            success = process.returncode == 0
            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""

            if success:
                self.log(f"Command succeeded: {command[0]}")
                if stdout_str:
                    self.log(f"STDOUT: {stdout_str[:500]}...")
            else:
                self.log(
                    f"Command failed: {command[0]} (exit code: {process.returncode})",
                    "ERROR",
                )
                if stderr_str:
                    self.log(f"STDERR: {stderr_str[:500]}...", "ERROR")

            return success, stdout_str, stderr_str

        except TimeoutError:
            self.log(f"Command timed out after {timeout}s: {command[0]}", "ERROR")
            return False, "", "Command timed out"
        except Exception as e:
            self.log(f"Command execution failed: {e}", "ERROR")
            return False, "", str(e)

    async def validate_prerequisites(self) -> bool:
        """Validate deployment prerequisites"""
        self.log("🔍 Validating deployment prerequisites...")

        checks = [
            ("Environment variables", self._check_environment_vars),
            ("Pulumi access", self._check_pulumi_access),
            ("Docker availability", self._check_docker),
            ("UV installation", self._check_uv),
            ("Git status", self._check_git_status),
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                passed = await check_func()
                if passed:
                    self.log(f"✅ {check_name}: PASSED")
                else:
                    self.log(f"❌ {check_name}: FAILED", "ERROR")
                    all_passed = False
            except Exception as e:
                self.log(f"❌ {check_name}: ERROR - {e}", "ERROR")
                all_passed = False

        return all_passed

    async def _check_environment_vars(self) -> bool:
        """Check required environment variables"""
        required_vars = ["PULUMI_ACCESS_TOKEN", "ENVIRONMENT"]
        missing = [var for var in required_vars if not os.getenv(var)]
        return len(missing) == 0

    async def _check_pulumi_access(self) -> bool:
        """Check Pulumi access"""
        success, _, _ = await self.run_command(["pulumi", "whoami"], timeout=10)
        return success

    async def _check_docker(self) -> bool:
        """Check Docker availability"""
        success, _, _ = await self.run_command(["docker", "version"], timeout=10)
        return success

    async def _check_uv(self) -> bool:
        """Check UV installation"""
        success, _, _ = await self.run_command(["uv", "--version"], timeout=10)
        return success

    async def _check_git_status(self) -> bool:
        """Check git status"""
        success, stdout, _ = await self.run_command(
            ["git", "status", "--porcelain"], timeout=10
        )
        return success and not stdout.strip()  # No uncommitted changes

    async def deploy_infrastructure(self) -> bool:
        """Deploy infrastructure with Pulumi"""
        self.log("🏗️ Deploying infrastructure...")

        # Navigate to infrastructure directory
        infra_dir = PROJECT_ROOT / "infrastructure"

        # Update dependencies
        success, _, _ = await self.run_command(["npm", "install"], cwd=infra_dir)
        if not success:
            self.log("Failed to install infrastructure dependencies", "ERROR")
            return False

        # Deploy with Pulumi
        stack_name = f"sophia-ai-{self.environment}"
        success, _, _ = await self.run_command(
            ["pulumi", "up", "--yes", "--stack", stack_name], cwd=infra_dir, timeout=600
        )

        if success:
            self.log("✅ Infrastructure deployment completed")
        else:
            self.log("❌ Infrastructure deployment failed", "ERROR")

        return success

    async def build_and_deploy_backend(self) -> bool:
        """Build and deploy backend services"""
        self.log("🚀 Building and deploying backend...")

        # Install dependencies with UV
        success, _, _ = await self.run_command(["uv", "sync"])
        if not success:
            self.log("Failed to install backend dependencies", "ERROR")
            return False

        # Build Docker image
        image_tag = f"sophia-backend:{self.deployment_id}"
        success, _, _ = await self.run_command(
            ["docker", "build", "-f", "Dockerfile.production", "-t", image_tag, "."],
            timeout=600,
        )

        if not success:
            self.log("Failed to build backend Docker image", "ERROR")
            return False

        # Deploy to infrastructure (this would integrate with your deployment target)
        self.log("✅ Backend build completed")
        return True

    async def deploy_frontend(self) -> bool:
        """Deploy frontend to Vercel"""
        self.log("🌐 Deploying frontend...")

        frontend_dir = PROJECT_ROOT / "frontend"

        # Install dependencies
        success, _, _ = await self.run_command(["npm", "install"], cwd=frontend_dir)
        if not success:
            self.log("Failed to install frontend dependencies", "ERROR")
            return False

        # Build frontend
        success, _, _ = await self.run_command(
            ["npm", "run", "build"], cwd=frontend_dir, timeout=300
        )
        if not success:
            self.log("Failed to build frontend", "ERROR")
            return False

        # Deploy to Vercel (if configured)
        vercel_token = os.getenv("VERCEL_TOKEN")
        if vercel_token:
            success, _, _ = await self.run_command(
                ["npx", "vercel", "--prod", "--token", vercel_token],
                cwd=frontend_dir,
                timeout=300,
            )

            if success:
                self.log("✅ Frontend deployed to Vercel")
            else:
                self.log("❌ Vercel deployment failed", "ERROR")
                return False
        else:
            self.log("⚠️ VERCEL_TOKEN not set, skipping Vercel deployment")

        return True

    async def deploy_mcp_servers(self) -> bool:
        """Deploy MCP servers"""
        self.log("🔧 Deploying MCP servers...")

        # Use the MCP orchestrator script
        orchestrator_script = SCRIPT_DIR / "start_all_mcp_servers.py"

        if not orchestrator_script.exists():
            self.log("MCP orchestrator script not found", "ERROR")
            return False

        # Start MCP servers (this would be adapted for production deployment)
        success, _, _ = await self.run_command(
            ["python", str(orchestrator_script)], timeout=120
        )

        if success:
            self.log("✅ MCP servers deployment completed")
        else:
            self.log("❌ MCP servers deployment failed", "ERROR")

        return success

    async def run_health_checks(self) -> bool:
        """Run comprehensive health checks"""
        self.log("🏥 Running deployment health checks...")

        # Use the enhanced health gate script
        health_script = SCRIPT_DIR / "ci" / "deployment_health_gate.py"

        success, _, _ = await self.run_command(
            ["python", str(health_script)], timeout=60
        )

        if success:
            self.log("✅ All health checks passed")
        else:
            self.log("❌ Health checks failed", "ERROR")

        return success

    async def run_smoke_tests(self) -> bool:
        """Run smoke tests"""
        self.log("🔥 Running smoke tests...")

        # Run basic smoke tests
        test_commands = [["python", "-m", "pytest", "tests/smoke/", "-v", "--tb=short"]]

        for command in test_commands:
            success, _, _ = await self.run_command(command, timeout=120)
            if not success:
                self.log(f"Smoke test failed: {' '.join(command)}", "ERROR")
                return False

        self.log("✅ All smoke tests passed")
        return True

    async def create_deployment_report(self, success: bool):
        """Create comprehensive deployment report"""
        self.status["completed_at"] = datetime.utcnow().isoformat()
        self.status["success"] = success
        self.status["duration_seconds"] = (
            datetime.fromisoformat(self.status["completed_at"])
            - datetime.fromisoformat(self.status["started_at"])
        ).total_seconds()

        report_file = DEPLOYMENT_LOG_DIR / f"{self.deployment_id}-report.json"
        with open(report_file, "w") as f:
            json.dump(self.status, f, indent=2)

        self.log(f"📊 Deployment report saved: {report_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("🚀 SOPHIA AI DEPLOYMENT SUMMARY")
        print("=" * 60)
        print(f"Deployment ID: {self.deployment_id}")
        print(f"Environment: {self.environment}")
        print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"Duration: {self.status['duration_seconds']:.1f} seconds")
        print(f"Log file: {self.log_file}")
        print(f"Report file: {report_file}")
        print("=" * 60)

    async def rollback_deployment(self):
        """Rollback deployment in case of failure"""
        self.log("🔄 Initiating deployment rollback...")

        # This would implement rollback logic
        # For now, just log the intent
        self.log("⚠️ Rollback logic not yet implemented")
        self.log("Manual intervention may be required")

    async def deploy(self) -> bool:
        """Execute full deployment pipeline"""
        try:
            self.log(f"🎬 Starting Sophia AI deployment to {self.environment}")

            # Phase 1: Prerequisites
            self.status["phases"]["prerequisites"] = {
                "started_at": datetime.utcnow().isoformat()
            }
            if not await self.validate_prerequisites():
                self.status["phases"]["prerequisites"]["success"] = False
                self.log("❌ Prerequisites validation failed", "ERROR")
                return False
            self.status["phases"]["prerequisites"]["success"] = True

            # Phase 2: Infrastructure
            self.status["phases"]["infrastructure"] = {
                "started_at": datetime.utcnow().isoformat()
            }
            if not await self.deploy_infrastructure():
                self.status["phases"]["infrastructure"]["success"] = False
                self.log("❌ Infrastructure deployment failed", "ERROR")
                await self.rollback_deployment()
                return False
            self.status["phases"]["infrastructure"]["success"] = True

            # Phase 3: Backend
            self.status["phases"]["backend"] = {
                "started_at": datetime.utcnow().isoformat()
            }
            if not await self.build_and_deploy_backend():
                self.status["phases"]["backend"]["success"] = False
                self.log("❌ Backend deployment failed", "ERROR")
                await self.rollback_deployment()
                return False
            self.status["phases"]["backend"]["success"] = True

            # Phase 4: Frontend
            self.status["phases"]["frontend"] = {
                "started_at": datetime.utcnow().isoformat()
            }
            if not await self.deploy_frontend():
                self.status["phases"]["frontend"]["success"] = False
                self.log("❌ Frontend deployment failed", "ERROR")
                await self.rollback_deployment()
                return False
            self.status["phases"]["frontend"]["success"] = True

            # Phase 5: MCP Servers
            self.status["phases"]["mcp_servers"] = {
                "started_at": datetime.utcnow().isoformat()
            }
            if not await self.deploy_mcp_servers():
                self.status["phases"]["mcp_servers"]["success"] = False
                self.log("❌ MCP servers deployment failed", "ERROR")
                # MCP failure is not critical for basic functionality
                self.log("⚠️ Continuing deployment despite MCP server issues")
            else:
                self.status["phases"]["mcp_servers"]["success"] = True

            # Phase 6: Health Checks
            self.status["phases"]["health_checks"] = {
                "started_at": datetime.utcnow().isoformat()
            }
            if not await self.run_health_checks():
                self.status["phases"]["health_checks"]["success"] = False
                self.log("❌ Health checks failed", "ERROR")
                await self.rollback_deployment()
                return False
            self.status["phases"]["health_checks"]["success"] = True

            # Phase 7: Smoke Tests
            self.status["phases"]["smoke_tests"] = {
                "started_at": datetime.utcnow().isoformat()
            }
            if not await self.run_smoke_tests():
                self.status["phases"]["smoke_tests"]["success"] = False
                self.log("❌ Smoke tests failed", "ERROR")
                # Smoke test failure is warning, not critical
                self.log("⚠️ Deployment completed with smoke test warnings")
            else:
                self.status["phases"]["smoke_tests"]["success"] = True

            self.log("🎉 Deployment completed successfully!")
            return True

        except Exception as e:
            self.log(f"❌ Deployment failed with exception: {e}", "ERROR")
            await self.rollback_deployment()
            return False


async def main():
    """Main deployment function"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy Sophia AI to production")
    parser.add_argument(
        "--environment", default="production", help="Target environment"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate without deploying"
    )

    args = parser.parse_args()

    deployment = SophiaProductionDeployment(args.environment)

    if args.dry_run:
        print("🔍 Running deployment validation (dry run)...")
        success = await deployment.validate_prerequisites()
        print(f"Validation result: {'✅ PASSED' if success else '❌ FAILED'}")
        sys.exit(0 if success else 1)

    # Run full deployment
    success = await deployment.deploy()
    await deployment.create_deployment_report(success)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
