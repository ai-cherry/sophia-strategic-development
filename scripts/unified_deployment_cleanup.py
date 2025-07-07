#!/usr/bin/env python3
"""
Unified Deployment Cleanup Script
This script removes all legacy deployment files and ensures only unified components remain
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


class UnifiedDeploymentCleanup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = self.project_root / f"backup_deployment_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.files_to_delete = []
        self.files_to_keep = []
        self.summary = {
            "deleted": [],
            "backed_up": [],
            "kept": [],
            "errors": []
        }

    def identify_legacy_files(self):
        """Identify all legacy deployment files that should be removed"""

        # Legacy deployment scripts
        legacy_scripts = [
            "deploy_production_complete.sh",
            "deploy_production_sophia.sh",
            "setup_k3s_cluster.sh",
            "setup_swarm.sh",
            "deploy_to_lambda.sh",
            "scripts/deploy_to_lambda.sh",
            "scripts/setup_docker_swarm.sh",
            "scripts/k3s_deploy.sh",
            "scripts/check_swarm_health.sh",
            "scripts/monitor_k3s.sh",
            "deploy_sophia_production.sh",
            "deploy_k3s.sh",
        ]

        # Legacy docker compose files
        legacy_compose = [
            "docker-compose.production.yml",
            "docker-compose.ai.yml",
            "docker-compose.mcp.yml",
            "docker-compose.platform.yml",
            "docker-compose.cloud.yml.optimized",
            "docker-compose.containerized.yml",
            "docker-compose.lambda.yml",
            "docker-compose.monitoring.yml",
            "docker-compose.n8n.yml",
            "docker-compose.redis.yml",
            "docker-compose.services.yml",
            "docker-compose.sophia.yml",
            "docker-compose.test.yml",
            "docker-compose.weaviate.yml",
        ]

        # Legacy secret management
        legacy_secrets = [
            "scripts/ci/sync_from_gh_to_pulumi.py",
            "scripts/sync_secrets_to_esc.py",
            "scripts/test_esc_secrets.py",
            "create_docker_secrets.sh",
            "scripts/create_secrets.sh",
            "scripts/sync_github_secrets.py",
        ]

        # All legacy files
        self.files_to_delete = legacy_scripts + legacy_compose + legacy_secrets

        # Unified files to keep
        self.files_to_keep = [
            "unified_deployment.sh",
            "unified_docker_secrets.sh",
            "unified_monitoring.sh",
            "unified_troubleshooting.sh",
            "scripts/unified_secret_sync.py",
            "scripts/unified_secret_management_audit.py",
            "scripts/unified_deployment_cleanup.py",
            "docker-compose.cloud.yml",
            "docker-compose.override.yml",  # Keep for development
            "UNIFIED_DEPLOYMENT_STRATEGY.md",
            "UNIFIED_SECRET_MANAGEMENT_STRATEGY.md",
            "UNIFIED_INFRASTRUCTURE.md",
        ]

    def backup_files(self):
        """Create backup of files before deletion"""
        print(f"📁 Creating backup directory: {self.backup_dir}")
        self.backup_dir.mkdir(exist_ok=True)

        for file_path in self.files_to_delete:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    backup_path = self.backup_dir / file_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(full_path, backup_path)
                    self.summary["backed_up"].append(str(file_path))
                    print(f"  ✅ Backed up: {file_path}")
                except Exception as e:
                    self.summary["errors"].append(f"Failed to backup {file_path}: {e}")
                    print(f"  ❌ Failed to backup: {file_path}: {e}")

    def delete_legacy_files(self):
        """Delete all legacy deployment files"""
        print("\n🗑️  Deleting legacy files...")

        for file_path in self.files_to_delete:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    full_path.unlink()
                    self.summary["deleted"].append(str(file_path))
                    print(f"  ✅ Deleted: {file_path}")
                except Exception as e:
                    self.summary["errors"].append(f"Failed to delete {file_path}: {e}")
                    print(f"  ❌ Failed to delete: {file_path}: {e}")

    def verify_unified_files(self):
        """Verify all unified files exist"""
        print("\n✅ Verifying unified files...")

        for file_path in self.files_to_keep:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.summary["kept"].append(str(file_path))
                print(f"  ✅ Found: {file_path}")
            else:
                print(f"  ⚠️  Missing: {file_path}")

    def update_documentation(self):
        """Update documentation to reflect unified approach"""
        print("\n📝 Documentation updates needed:")
        print("  1. Update DEPLOYMENT.md to reference unified scripts")
        print("  2. Update System Handbook deployment section")
        print("  3. Remove references to Kubernetes/K3s")
        print("  4. Update all deployment guides to use unified approach")

    def print_summary(self):
        """Print cleanup summary"""
        print("\n" + "="*60)
        print("🎯 UNIFIED DEPLOYMENT CLEANUP SUMMARY")
        print("="*60)

        print(f"\n📁 Backup location: {self.backup_dir}")

        print(f"\n✅ Deleted {len(self.summary['deleted'])} legacy files:")
        for file in self.summary['deleted'][:10]:
            print(f"  - {file}")
        if len(self.summary['deleted']) > 10:
            print(f"  ... and {len(self.summary['deleted']) - 10} more")

        print(f"\n✅ Kept {len(self.summary['kept'])} unified files:")
        for file in self.summary['kept']:
            print(f"  - {file}")

        if self.summary['errors']:
            print(f"\n❌ Errors ({len(self.summary['errors'])}):")
            for error in self.summary['errors']:
                print(f"  - {error}")

        print("\n🎯 Next Steps:")
        print("  1. Review and update documentation")
        print("  2. Test unified deployment: ./unified_deployment.sh")
        print("  3. Remove backup after verification: rm -rf " + str(self.backup_dir))
        print("  4. Commit changes with: git add -A && git commit -m 'Complete unified deployment cleanup'")

    def run(self):
        """Execute the cleanup process"""
        print("🚀 Starting Unified Deployment Cleanup")
        print("="*60)

        self.identify_legacy_files()
        self.backup_files()
        self.delete_legacy_files()
        self.verify_unified_files()
        self.update_documentation()
        self.print_summary()

if __name__ == "__main__":
    cleanup = UnifiedDeploymentCleanup()
    cleanup.run()
