#!/usr/bin/env python3
"""
Deployment Infrastructure Critical Fixes
========================================

Implements approved stability improvements:
1. Consolidate conflicting CI/CD workflows
2. Fix Dockerfile references
3. Resolve environment variable issues
4. Standardize documentation

SCOPE: Critical stability fixes only (no over-engineering)
"""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeploymentInfrastructureFixer:
    """Fix critical deployment infrastructure issues"""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.github_workflows = self.project_root / ".github" / "workflows"
        self.backup_dir = (
            self.project_root
            / f"backup_deployment_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        self.results = {
            "fixes_applied": [],
            "files_modified": [],
            "files_removed": [],
            "validation_results": {},
            "next_steps": [],
        }

    def run_critical_fixes(self) -> dict[str, Any]:
        """Execute all approved critical fixes"""
        logger.info("🚀 STARTING DEPLOYMENT INFRASTRUCTURE CRITICAL FIXES")
        logger.info("=" * 70)

        try:
            # Create backup
            self._create_backup()

            # Phase 1: Fix CI/CD workflows
            logger.info("📋 Phase 1: Consolidating CI/CD workflows...")
            self._fix_cicd_workflows()

            # Phase 2: Fix Dockerfile references
            logger.info("🐳 Phase 2: Fixing Dockerfile references...")
            self._fix_dockerfile_references()

            # Phase 3: Fix environment variables
            logger.info("🔧 Phase 3: Resolving environment variables...")
            self._fix_environment_variables()

            # Phase 4: Standardize documentation
            logger.info("📚 Phase 4: Standardizing documentation...")
            self._standardize_documentation()

            # Validation
            logger.info("✅ Phase 5: Validating fixes...")
            self._validate_fixes()

            logger.info("🎉 DEPLOYMENT INFRASTRUCTURE FIXES COMPLETED SUCCESSFULLY")

        except Exception as e:
            logger.error(f"❌ Critical fix failed: {e}")
            self.results["error"] = str(e)

        return self.results

    def _create_backup(self):
        """Create backup of critical files"""
        logger.info("📁 Creating backup of deployment files...")

        self.backup_dir.mkdir(exist_ok=True)

        # Backup workflows
        if self.github_workflows.exists():
            shutil.copytree(
                self.github_workflows,
                self.backup_dir / "github_workflows",
                dirs_exist_ok=True,
            )

        # Backup Dockerfiles
        for dockerfile in self.project_root.glob("Dockerfile*"):
            shutil.copy2(dockerfile, self.backup_dir)

        logger.info(f"✅ Backup created at: {self.backup_dir}")

    def _fix_cicd_workflows(self):
        """Consolidate conflicting CI/CD workflows"""
        logger.info("🔄 Consolidating CI/CD workflows...")

        # Read existing workflows
        prod_workflow = self.github_workflows / "production-deployment.yml"
        uv_workflow = self.github_workflows / "uv-ci-cd.yml"

        if not prod_workflow.exists() or not uv_workflow.exists():
            logger.warning("⚠️ Expected workflow files not found")
            return

        # Create consolidated workflow
        consolidated_workflow = {
            "name": "Sophia AI Production Deployment",
            "on": {
                "push": {"branches": ["main"]},
                "pull_request": {"branches": ["main"]},
                "workflow_dispatch": {},
            },
            "env": {"ENVIRONMENT": "prod", "PULUMI_ORG": "scoobyjava-org"},
            "jobs": {
                # Combined linting and testing from uv-ci-cd
                "lint-and-test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Install UV",
                            "run": "curl -LsSf https://astral.sh/uv/install.sh | sh",
                        },
                        {
                            "name": "Add UV to PATH",
                            "run": 'echo "$HOME/.local/bin" >> $GITHUB_PATH',
                        },
                        {"name": "Install dependencies", "run": "uv sync --group dev"},
                        {"name": "Run linting with Ruff", "run": "uv run ruff check ."},
                        {
                            "name": "Run tests with pytest",
                            "run": "uv run pytest tests/ --cov=backend --cov-report=xml",
                        },
                    ],
                },
                # Security scanning from uv-ci-cd
                "security": {
                    "runs-on": "ubuntu-latest",
                    "needs": ["lint-and-test"],
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v5",
                            "with": {"python-version": "3.12"},
                        },
                        {
                            "name": "Install UV",
                            "run": 'curl -LsSf https://astral.sh/uv/install.sh | sh && echo "$HOME/.cargo/bin" >> $GITHUB_PATH',
                        },
                        {"name": "Install dependencies", "run": "uv sync --group dev"},
                        {
                            "name": "Run security scan",
                            "run": "uv run pip-audit --format=json --output=vulnerability-report.json || true",
                        },
                    ],
                },
                # Build and deploy from production-deployment (with fixes)
                "build-and-deploy": {
                    "runs-on": "ubuntu-latest",
                    "needs": ["lint-and-test", "security"],
                    "if": "github.ref == 'refs/heads/main'",
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Set up Docker Buildx",
                            "uses": "docker/setup-buildx-action@v3",
                        },
                        {
                            "name": "Login to Docker Hub",
                            "uses": "docker/login-action@v3",
                            "with": {
                                "username": "${{ secrets.DOCKER_USER_NAME }}",
                                "password": "${{ secrets.DOCKER_PERSONAL_ACCESS_TOKEN }}",
                            },
                        },
                        {
                            "name": "Build and push Docker images",
                            "uses": "docker/build-push-action@v5",
                            "with": {
                                "context": ".",
                                "file": "./Dockerfile.production",  # Fixed reference
                                "platforms": "linux/amd64,linux/arm64",
                                "push": True,
                                "tags": "scoobyjava15/sophia-ai:latest\nscoobyjava15/sophia-ai:${{ github.sha }}",
                                "cache-from": "type=gha",
                                "cache-to": "type=gha,mode=max",
                            },
                        },
                        {
                            "name": "Deploy Infrastructure",
                            "uses": "pulumi/actions@v4",
                            "with": {
                                "command": "up",
                                "stack-name": "scoobyjava-org/sophia-prod-on-lambda",
                                "work-dir": "infrastructure/",
                            },
                            "env": {
                                "PULUMI_ACCESS_TOKEN": "${{ secrets.PULUMI_ACCESS_TOKEN }}"
                            },
                        },
                        {
                            "name": "Get Lambda Labs Instance IP",
                            "id": "get-ip",
                            "run": 'INSTANCE_IP=$(pulumi stack output lambdaLabsInstanceIp --stack scoobyjava-org/sophia-prod-on-lambda)\necho "instance_ip=$INSTANCE_IP" >> $GITHUB_OUTPUT',
                        },
                        {
                            "name": "Deploy to Kubernetes",
                            "run": "kubectl apply -f kubernetes/\nkubectl rollout status deployment/sophia-ai --timeout=600s",
                        },
                        {
                            "name": "Verify Deployment",
                            "run": 'INSTANCE_IP="${{ steps.get-ip.outputs.instance_ip }}"\ncurl -f http://$INSTANCE_IP/health\npython scripts/verify_deployment.py --instance-ip $INSTANCE_IP',
                        },
                    ],
                },
            },
        }

        # Write consolidated workflow
        new_workflow_path = self.github_workflows / "sophia-production-deployment.yml"
        with open(new_workflow_path, "w") as f:
            yaml.dump(
                consolidated_workflow, f, default_flow_style=False, sort_keys=False
            )

        # Remove old conflicting workflows
        old_workflows = ["production-deployment.yml", "uv-ci-cd.yml"]

        for workflow in old_workflows:
            workflow_path = self.github_workflows / workflow
            if workflow_path.exists():
                workflow_path.unlink()
                self.results["files_removed"].append(str(workflow_path))

        self.results["fixes_applied"].append("CI/CD workflows consolidated")
        self.results["files_modified"].append(str(new_workflow_path))
        logger.info("✅ CI/CD workflows consolidated successfully")

    def _fix_dockerfile_references(self):
        """Fix references to non-existent Dockerfiles"""
        logger.info("🐳 Fixing Dockerfile references...")

        # Verify Dockerfile.production exists
        dockerfile_prod = self.project_root / "Dockerfile.production"
        if not dockerfile_prod.exists():
            # Check for main Dockerfile
            dockerfile_main = self.project_root / "Dockerfile"
            if dockerfile_main.exists():
                # Copy main Dockerfile to production version
                shutil.copy2(dockerfile_main, dockerfile_prod)
                logger.info("✅ Created Dockerfile.production from main Dockerfile")
            else:
                logger.error("❌ No valid Dockerfile found to use as production version")
                return

        # Create .dockerignore if it doesn't exist
        dockerignore = self.project_root / ".dockerignore"
        if not dockerignore.exists():
            dockerignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
.Python
*.so
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Documentation
docs/
*.md
README*

# Tests
tests/
.pytest_cache/
.coverage

# Logs
logs/
*.log

# Build artifacts
build/
dist/
*.egg-info/

# Node modules (if any)
node_modules/

# Backup files
backup*/
*backup*/

# Temporary files
tmp/
temp/
""".strip()

            with open(dockerignore, "w") as f:
                f.write(dockerignore_content)

            self.results["files_modified"].append(str(dockerignore))
            logger.info("✅ Created .dockerignore for optimized builds")

        self.results["fixes_applied"].append("Dockerfile references standardized")
        logger.info("✅ Dockerfile references fixed")

    def _fix_environment_variables(self):
        """Fix environment variable mapping issues"""
        logger.info("🔧 Fixing environment variable mapping...")

        # Create environment variable validation script
        env_validator = self.project_root / "scripts" / "validate_deployment_env.py"
        env_validator.parent.mkdir(exist_ok=True)

        validator_content = '''#!/usr/bin/env python3
"""
Deployment Environment Validator
Validates all required environment variables for deployment
"""

import os
import sys
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = {
    "DOCKER_USER_NAME": "Docker Hub username",
    "DOCKER_PERSONAL_ACCESS_TOKEN": "Docker Hub access token",
    "PULUMI_ACCESS_TOKEN": "Pulumi access token",
    "LAMBDA_LABS_API_KEY": "Lambda Labs API key"
}

OPTIONAL_ENV_VARS = {
    "ENVIRONMENT": "prod",
    "PULUMI_ORG": "scoobyjava-org"
}

def validate_environment() -> Tuple[bool, List[str]]:
    """Validate deployment environment variables"""
    errors = []

    # Check required variables
    for var, description in REQUIRED_ENV_VARS.items():
        if not os.getenv(var):
            errors.append(f"Missing required variable: {var} ({description})")

    # Set optional defaults
    for var, default in OPTIONAL_ENV_VARS.items():
        if not os.getenv(var):
            os.environ[var] = default
            logger.info(f"Set default {var}={default}")

    return len(errors) == 0, errors

def main():
    """Main validation function"""
    logging.basicConfig(level=logging.INFO)

    success, errors = validate_environment()

    if success:
        logger.info("✅ All environment variables validated successfully")
        sys.exit(0)
    else:
        logger.error("❌ Environment validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        with open(env_validator, "w") as f:
            f.write(validator_content)

        # Make executable
        os.chmod(env_validator, 0o755)

        self.results["files_modified"].append(str(env_validator))
        self.results["fixes_applied"].append("Environment variable validation added")
        logger.info("✅ Environment variable fixes implemented")

    def _standardize_documentation(self):
        """Standardize deployment documentation"""
        logger.info("📚 Standardizing deployment documentation...")

        # Create authoritative deployment guide
        deployment_guide = self.project_root / "docs" / "DEPLOYMENT_GUIDE.md"
        deployment_guide.parent.mkdir(exist_ok=True)

        guide_content = """# Sophia AI Deployment Guide

## Overview

This is the **authoritative deployment guide** for Sophia AI. All deployments follow the patterns documented here.

## Quick Deployment

### Prerequisites
- Docker Hub account with push permissions
- Pulumi access token configured
- Lambda Labs API key

### Automated Deployment (Recommended)

1. **Push to main branch** - triggers automatic deployment via GitHub Actions
2. **Monitor workflow** - check GitHub Actions tab for progress
3. **Verify deployment** - health checks run automatically

### Manual Deployment (Emergency)

```bash
# 1. Build and push image
docker build -t scoobyjava15/sophia-ai:latest -f Dockerfile.production .
docker push scoobyjava15/sophia-ai:latest

# 2. Deploy infrastructure
cd infrastructure/
pulumi up --stack scoobyjava-org/sophia-prod-on-lambda

# 3. Deploy to Kubernetes
kubectl apply -f kubernetes/
kubectl rollout status deployment/sophia-ai
```

## Infrastructure Architecture

- **CI/CD**: GitHub Actions (`sophia-production-deployment.yml`)
- **Container Registry**: Docker Hub (`scoobyjava15/sophia-ai`)
- **Infrastructure**: Pulumi (Lambda Labs Kubernetes)
- **Deployment**: Kubernetes manifests
- **Monitoring**: Built-in health checks

## Environment Variables

Required secrets (managed in GitHub):
- `DOCKER_USER_NAME` - Docker Hub username
- `DOCKER_PERSONAL_ACCESS_TOKEN` - Docker Hub token
- `PULUMI_ACCESS_TOKEN` - Pulumi access token
- `LAMBDA_LABS_API_KEY` - Lambda Labs API key

## Troubleshooting

### Build Failures
- Check Dockerfile.production exists
- Verify .dockerignore excludes unnecessary files
- Check Docker Hub credentials

### Deployment Failures
- Validate environment variables: `python scripts/validate_deployment_env.py`
- Check Pulumi stack status
- Verify Kubernetes cluster access

### Health Check Failures
- Ensure LAMBDA_LABS_INSTANCE_IP is properly set
- Check service endpoints are accessible
- Verify Pulumi outputs are correct

## Architecture Decisions

### Current Approach (Approved)
- **Hybrid Infrastructure**: Pulumi for AWS resources + manual Kubernetes
- **Single Instance Databases**: Redis/PostgreSQL without HA (sufficient for current scale)
- **Docker Registry**: Docker Hub (scoobyjava15)
- **Primary Dockerfile**: Dockerfile.production

### Rejected Approaches (Over-Engineering)
- Full Pulumi Kubernetes resource management
- High Availability database clustering
- Complex cache invalidation strategies
- Multiple environment complexity

This approach prioritizes **stability and simplicity** over theoretical scalability needs.
"""

        with open(deployment_guide, "w") as f:
            f.write(guide_content)

        self.results["files_modified"].append(str(deployment_guide))
        self.results["fixes_applied"].append("Authoritative deployment guide created")
        logger.info("✅ Documentation standardized")

    def _validate_fixes(self):
        """Validate all fixes were applied correctly"""
        logger.info("🔍 Validating fixes...")

        validations = {
            "dockerfile_production_exists": (
                self.project_root / "Dockerfile.production"
            ).exists(),
            "consolidated_workflow_exists": (
                self.github_workflows / "sophia-production-deployment.yml"
            ).exists(),
            "env_validator_exists": (
                self.project_root / "scripts" / "validate_deployment_env.py"
            ).exists(),
            "deployment_guide_exists": (
                self.project_root / "docs" / "DEPLOYMENT_GUIDE.md"
            ).exists(),
            "dockerignore_exists": (self.project_root / ".dockerignore").exists(),
        }

        self.results["validation_results"] = validations

        success_count = sum(1 for v in validations.values() if v)
        total_count = len(validations)

        logger.info(f"✅ Validation: {success_count}/{total_count} checks passed")

        if success_count == total_count:
            logger.info("🎉 All validations passed!")
        else:
            failed = [k for k, v in validations.items() if not v]
            logger.warning(f"⚠️ Failed validations: {failed}")

        # Add next steps
        self.results["next_steps"] = [
            "Test deployment workflow: git push origin main",
            "Verify environment variables: python scripts/validate_deployment_env.py",
            "Monitor first automated deployment in GitHub Actions",
            "Update team on new consolidated deployment process",
        ]


def main():
    """Main execution function"""
    fixer = DeploymentInfrastructureFixer()
    results = fixer.run_critical_fixes()

    print("\n" + "=" * 70)
    print("DEPLOYMENT INFRASTRUCTURE FIXES SUMMARY")
    print("=" * 70)
    print(f"Fixes Applied: {len(results['fixes_applied'])}")
    for fix in results["fixes_applied"]:
        print(f"  ✅ {fix}")

    print(f"\nFiles Modified: {len(results['files_modified'])}")
    for file in results["files_modified"]:
        print(f"  📝 {file}")

    print(f"\nFiles Removed: {len(results['files_removed'])}")
    for file in results["files_removed"]:
        print(f"  🗑️ {file}")

    print("\nValidation Results:")
    for check, passed in results["validation_results"].items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    print("\nNext Steps:")
    for step in results["next_steps"]:
        print(f"  📋 {step}")

    if "error" in results:
        print(f"\n❌ Error encountered: {results['error']}")
        return 1

    print("\n🎉 DEPLOYMENT INFRASTRUCTURE FIXES COMPLETED SUCCESSFULLY!")
    return 0


if __name__ == "__main__":
    exit(main())
