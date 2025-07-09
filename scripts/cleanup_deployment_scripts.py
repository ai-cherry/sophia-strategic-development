#!/usr/bin/env python3
"""
Cleanup Redundant Deployment Scripts and Configurations
Removes outdated, duplicate, and legacy deployment files while preserving essential ones.
Based on current 5 Lambda Labs instances architecture.
"""

import shutil
from pathlib import Path

# CURRENT 5 LAMBDA LABS INSTANCES (KEEP REFERENCES TO THESE)
CURRENT_INFRASTRUCTURE = {
    "sophia-production-instance": "104.171.202.103",  # RTX6000
    "sophia-ai-core": "192.222.58.232",  # GH200
    "sophia-mcp-orchestrator": "104.171.202.117",  # A6000
    "sophia-data-pipeline": "104.171.202.134",  # A100
    "sophia-development": "155.248.194.183",  # A10
}

# LEGACY/REDUNDANT DEPLOYMENT FILES TO REMOVE
LEGACY_DEPLOYMENT_FILES = [
    # Outdated deployment scripts
    "scripts/deploy_to_lambda.sh",
    "scripts/deploy_to_lambda_labs.sh",
    "scripts/deploy-mcp-v2-lambda.sh",
    "scripts/docker-cloud-deploy-v2.sh",
    "scripts/deploy_unified_platform.sh",
    "scripts/deploy_production_complete.py",
    "scripts/deploy_complete_sophia_platform.py",
    "scripts/deploy_k8s_lambda_2025.sh",
    "scripts/setup_k8s_automation.sh",
    "scripts/deploy_sophia_unified.py",
    "scripts/deploy_lambda_labs_comprehensive.py",
    "scripts/ultimate_lambda_deployment.py",
    "scripts/comprehensive_lambda_migration_cleanup.py",
    "scripts/deploy_with_automation.sh",
    "scripts/quick_deploy_lambda_k8s.sh",
    # Redundant build scripts
    "scripts/unified_build_images.sh",
    "scripts/unified_docker_hub_push.sh",
    "scripts/unified_push_images.sh",
    "scripts/prepare_production_deployment.sh",
    "scripts/prepare_deployment_package.sh",
    # Legacy Docker configurations
    "docker-compose.cloud.enhanced.yml",
    "docker-compose.cloud.unified.yml",
    "docker-compose.cloud.optimized.yml",
    "docker-compose.mcp-essential.yml",
    "docker-compose.mcp-v2.yml",
    "docker-compose.cloud.yml.backup",
    # Outdated documentation
    "docs/04-deployment/DOCKER_CLOUD_LAMBDA_LABS.md",
    "docs/04-deployment/LAMBDA_LABS_MCP_DEPLOYMENT_GUIDE.md",
    "docs/deployment/LAMBDA_LABS_DEPLOYMENT_GUIDE.md",
    "docs/deployment/LAMBDA_LABS_GUIDE.md",
    "lambda_labs_mcp_deployment.md",
    "LAMBDA_LABS_DEPLOYMENT_GUIDE.md",
    "SOPHIA_INTEL_AI_DEPLOYMENT_ENHANCEMENT_PLAN.md",
    # Legacy infrastructure files
    "infrastructure/lambda-labs-deployment.py",
    "infrastructure/lambda-labs-config.yaml",
    "infrastructure/pulumi/lambda-labs.ts",
    "infrastructure/pulumi/lambda-labs-env.yaml",
    "infrastructure/pulumi/clean-architecture-stack.ts",
    "infrastructure/templates/lambda-labs-cloud-init.yaml",
    "infrastructure/esc/lambda-labs-gh200-config.yaml",
    # Legacy workflow files
    ".github/workflows/lambda-labs-deploy.yml",
    ".github/workflows/lambda-labs-monitoring.yml",
    ".github/workflows/deploy_v2_mcp_servers.yml",
    # Deployment summaries and reports (keep for reference but archive)
    "DEPLOYMENT_COMPLETE_SUMMARY.md",
    "GITHUB_ACTIONS_DEPLOYMENT_READY.md",
    "SOPHIA_V2_MCP_DEPLOYMENT_PLAN.md",
    "DEPLOYMENT.md",
    "COMPREHENSIVE_DEPLOYMENT_GUIDE.md",
    "DEPLOYMENT_DOCUMENTATION_RESTRUCTURE_PLAN.md",
    "LAMBDA_LABS_CI_CD_IMPLEMENTATION_REPORT.md",
    "DEPLOYMENT_STATUS_FINAL_REPORT.md",
    "DEPLOYMENT_IMPLEMENTATION_SUMMARY.md",
    "PR_179_IMPLEMENTATION_GUIDE.md",
    "SOPHIA_AI_DOCKER_DEPLOYMENT_PLAN.md",
]

# ESSENTIAL DEPLOYMENT FILES TO KEEP
ESSENTIAL_DEPLOYMENT_FILES = [
    # Current unified deployment
    "scripts/deploy_sophia_unified.sh",
    "scripts/deploy_sophia_platform.sh",
    "scripts/deploy_sophia_simple.sh",
    "scripts/lambda_migration_deploy.sh",
    "scripts/lambda_labs_manager.py",
    # Production Docker configurations
    "deployment/docker-compose-production.yml",
    "deployment/docker-compose-ai-core.yml",
    "deployment/docker-compose-mcp-orchestrator.yml",
    "deployment/docker-compose-data-pipeline.yml",
    "deployment/docker-compose-development.yml",
    "docker-compose.production.yml",
    # Essential documentation
    "deployment/README.md",
    "docs/04-deployment/UNIFIED_DEPLOYMENT.md",
    # Current workflow files
    ".github/workflows/deploy-sophia-platform.yml",
    ".github/workflows/sophia-production-deployment.yml",
]

# DOCKER REFERENCES TO UPDATE (OLD IP ADDRESSES)
OLD_IP_PATTERNS = [
    "146.235.200.1",  # Old Lambda Labs IP
    "146.235.200.2",
    "146.235.200.3",
]


def create_backup_archive():
    """Create backup of files before deletion"""
    from datetime import datetime

    backup_dir = Path(
        f"deployment_cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    backup_dir.mkdir(exist_ok=True)

    print(f"📋 Creating backup at {backup_dir}")
    return backup_dir


def cleanup_legacy_files(backup_dir: Path):
    """Remove legacy deployment files"""
    print("🧹 Cleaning up legacy deployment files...")

    removed_count = 0
    kept_count = 0

    for file_path in LEGACY_DEPLOYMENT_FILES:
        path = Path(file_path)

        if path.exists():
            # Backup before deletion
            backup_path = backup_dir / path.name
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup_path)

            # Remove original
            try:
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
                print(f"   ❌ Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"   ⚠️  Failed to remove {file_path}: {e}")
        else:
            print(f"   ℹ️  Not found: {file_path}")

    print("\n📊 Legacy cleanup summary:")
    print(f"   ❌ Removed: {removed_count} files")

    return removed_count


def update_ip_addresses():
    """Update any remaining old IP addresses in deployment files"""
    print("🔄 Updating IP addresses in deployment files...")

    updated_files = []

    # Find all deployment-related files
    search_patterns = ["**/*.yml", "**/*.yaml", "**/*.sh", "**/*.py", "**/*.md"]

    for pattern in search_patterns:
        for file_path in Path(".").glob(pattern):
            if "backup" in str(file_path) or "archive" in str(file_path):
                continue

            try:
                with open(file_path) as f:
                    content = f.read()

                original_content = content

                # Replace old IP addresses
                for old_ip in OLD_IP_PATTERNS:
                    if old_ip in content:
                        # Don't replace these automatically - log for manual review
                        print(
                            f"   ⚠️  Found old IP {old_ip} in {file_path} - needs manual review"
                        )

                # If content was changed, write back
                if content != original_content:
                    with open(file_path, "w") as f:
                        f.write(content)
                    updated_files.append(str(file_path))
                    print(f"   ✅ Updated: {file_path}")

            except Exception as e:
                print(f"   ❌ Error processing {file_path}: {e}")

    return updated_files


def validate_essential_files():
    """Ensure essential deployment files exist and are correct"""
    print("✅ Validating essential deployment files...")

    missing_files = []
    validated_files = []

    for file_path in ESSENTIAL_DEPLOYMENT_FILES:
        path = Path(file_path)

        if path.exists():
            print(f"   ✅ Found: {file_path}")
            validated_files.append(file_path)
        else:
            print(f"   ❌ Missing: {file_path}")
            missing_files.append(file_path)

    return validated_files, missing_files


def consolidate_deployment_docs():
    """Consolidate deployment documentation"""
    print("📚 Consolidating deployment documentation...")

    # Create unified deployment guide
    unified_guide_content = f"""# Sophia AI Unified Deployment Guide

**Last Updated:** {Path(__file__).stat().st_mtime}
**Architecture:** 5 Lambda Labs GPU Instances + Serverless

## 🏗️ Current Infrastructure

{chr(10).join([f"- **{name}**: `{ip}` ({name.split('-')[-1].upper()})" for name, ip in CURRENT_INFRASTRUCTURE.items()])}

## 🚀 Deployment Methods

### Method 1: GitHub Actions (Recommended)
```bash
# Navigate to GitHub → Actions → "🚀 Sophia AI Unified Deployment"
# Select target instances and deployment options
```

### Method 2: Unified Script Deployment
```bash
# Deploy to all instances
./scripts/deploy_sophia_unified.sh deploy all

# Deploy to specific instance
./scripts/deploy_sophia_unified.sh deploy production
./scripts/deploy_sophia_unified.sh deploy ai-core
```

### Method 3: Individual Instance Deployment
```bash
# Simple deployment to specific instance
./scripts/deploy_sophia_simple.sh 104.171.202.103

# Platform deployment with all components
./scripts/deploy_sophia_platform.sh
```

## 📁 Essential Files

### Deployment Scripts
- `scripts/deploy_sophia_unified.sh` - Main deployment orchestrator
- `scripts/deploy_sophia_platform.sh` - Complete platform deployment
- `scripts/deploy_sophia_simple.sh` - Simple single-instance deployment
- `scripts/lambda_migration_deploy.sh` - Lambda Labs optimized deployment

### Docker Configurations
- `deployment/docker-compose-production.yml` - Production services (RTX6000)
- `deployment/docker-compose-ai-core.yml` - AI/ML services (GH200)
- `deployment/docker-compose-mcp-orchestrator.yml` - MCP services (A6000)
- `deployment/docker-compose-data-pipeline.yml` - Data services (A100)
- `deployment/docker-compose-development.yml` - Dev/monitoring (A10)

### GitHub Actions
- `.github/workflows/deploy-sophia-platform.yml` - Main deployment workflow
- `.github/workflows/sophia-production-deployment.yml` - Production deployment

## 🔧 Configuration Management

All deployments use:
- **Docker Registry**: `scoobyjava15`
- **Environment**: `prod` (default)
- **Secrets**: Pulumi ESC (`scoobyjava-org/default/sophia-ai-production`)
- **Orchestration**: Docker Swarm mode

## 📊 Post-Deployment Validation

After deployment, verify:
```bash
# Check service status
./scripts/deploy_sophia_unified.sh status

# Validate specific instance
./scripts/deploy_sophia_unified.sh validate ai-core

# Monitor deployment
# - Backend: http://104.171.202.103:8000/health
# - Frontend: http://104.171.202.103:3000
# - Monitoring: http://155.248.194.183:3000 (Grafana)
```

## 🚨 Emergency Procedures

### Rollback Deployment
```bash
# Rollback specific service
docker service rollback sophia_backend

# Full stack rollback
./scripts/deploy_sophia_unified.sh rollback
```

### Instance Recovery
```bash
# Restart failed instance
./scripts/deploy_sophia_unified.sh restart <instance-name>

# Redeploy from scratch
./scripts/deploy_sophia_unified.sh deploy <instance-name> --force
```
"""

    # Write consolidated guide
    unified_guide_path = Path("docs/04-deployment/UNIFIED_DEPLOYMENT_GUIDE.md")
    unified_guide_path.parent.mkdir(parents=True, exist_ok=True)

    with open(unified_guide_path, "w") as f:
        f.write(unified_guide_content)

    print(f"   ✅ Created: {unified_guide_path}")

    return str(unified_guide_path)


def main():
    """Main cleanup function"""
    print("🧹 Sophia AI Deployment Scripts Cleanup")
    print("=" * 50)

    # Create backup
    backup_dir = create_backup_archive()

    # Phase 1: Clean up legacy files
    removed_count = cleanup_legacy_files(backup_dir)

    # Phase 2: Update IP addresses
    updated_files = update_ip_addresses()

    # Phase 3: Validate essential files
    validated_files, missing_files = validate_essential_files()

    # Phase 4: Consolidate documentation
    unified_guide = consolidate_deployment_docs()

    # Summary
    print("\n" + "=" * 50)
    print("🎉 Deployment Cleanup Summary")
    print("=" * 50)
    print(f"📋 Backup created: {backup_dir}")
    print(f"❌ Legacy files removed: {removed_count}")
    print(f"🔄 Files with IP updates: {len(updated_files)}")
    print(f"✅ Essential files validated: {len(validated_files)}")
    print(f"❌ Missing essential files: {len(missing_files)}")
    print(f"📚 Unified guide created: {unified_guide}")

    if missing_files:
        print("\n⚠️  Missing essential files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nThese should be reviewed and created if needed.")

    if updated_files:
        print("\n🔄 Files with IP address updates:")
        for file in updated_files:
            print(f"   - {file}")

    print("\n🧪 Next steps:")
    print("1. Review backup files in", backup_dir)
    print("2. Test deployment with: ./scripts/deploy_sophia_unified.sh validate")
    print("3. Update any missing essential files")
    print("4. Commit changes to GitHub")

    return {
        "backup_dir": str(backup_dir),
        "removed_count": removed_count,
        "updated_files": updated_files,
        "validated_files": validated_files,
        "missing_files": missing_files,
        "unified_guide": unified_guide,
    }


if __name__ == "__main__":
    main()
