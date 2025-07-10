#!/usr/bin/env python3
"""
Clean up legacy deployment artifacts from Sophia AI repository.

This script moves old deployment files to an archive directory,
preserving them for reference while cleaning up the main repository.

Note: This is a reusable utility script for repository maintenance.
"""

import shutil
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class LegacyDeploymentCleaner:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.archive_dir = self.root_dir / "archive"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define what to archive
        self.artifacts_to_archive = {
            "docker_compose_files": {
                "pattern": "docker-compose*.yml",
                "target": "legacy-deployment/docker-compose",
                "files": [],
            },
            "deployment_scripts": {
                "pattern": ["scripts/deploy_*.sh", "scripts/deploy_*.py"],
                "target": "legacy-deployment/scripts",
                "files": [],
            },
            "old_workflows": {
                "pattern": ".github/workflows/*.yml",
                "target": "legacy-deployment/github-workflows",
                "exclude": ["unified-deployment.yml", "uv-ci-cd.yml"],
                "files": [],
            },
            "old_reports": {
                "pattern": ["docs/*REPORT*.md", "docs/*PHASE*.md"],
                "target": "reports",
                "files": [],
            },
            "old_plans": {
                "pattern": ["docs/*PLAN*.md", "docs/*MIGRATION*.md"],
                "target": "plans",
                "exclude": ["UPDATED_DEPLOYMENT_TRANSFORMATION_PLAN.md"],
                "files": [],
            },
        }

    def create_archive_structure(self):
        """Create the archive directory structure."""
        directories = [
            "archive/reports",
            "archive/plans",
            "archive/scripts",
            "archive/legacy-deployment/docker-compose",
            "archive/legacy-deployment/scripts",
            "archive/legacy-deployment/github-workflows",
            "archive/one-time-scripts",
        ]

        for directory in directories:
            dir_path = self.root_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")

    def find_artifacts(self):
        """Find all artifacts to archive."""
        for category, config in self.artifacts_to_archive.items():
            patterns = (
                config["pattern"]
                if isinstance(config["pattern"], list)
                else [config["pattern"]]
            )
            exclude = config.get("exclude", [])

            for pattern in patterns:
                for file_path in self.root_dir.glob(pattern):
                    if file_path.name not in exclude and file_path.is_file():
                        config["files"].append(file_path)

            logger.info(f"Found {len(config['files'])} {category}")

    def archive_artifacts(self):
        """Move artifacts to archive directory."""
        total_moved = 0

        for category, config in self.artifacts_to_archive.items():
            if not config["files"]:
                continue

            target_dir = self.archive_dir / config["target"]
            target_dir.mkdir(parents=True, exist_ok=True)

            for file_path in config["files"]:
                # Create archived filename with timestamp
                archived_name = f"{self.timestamp}_{file_path.name}"
                target_path = target_dir / archived_name

                try:
                    shutil.move(str(file_path), str(target_path))
                    logger.info(
                        f"📦 Archived: {file_path.name} → {target_path.relative_to(self.root_dir)}"
                    )
                    total_moved += 1
                except Exception as e:
                    logger.error(f"❌ Failed to archive {file_path}: {e}")

        return total_moved

    def create_archive_readme(self):
        """Create README in archive directory."""
        readme_content = f"""# Sophia AI Archive Directory

**Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Purpose

This directory contains archived deployment artifacts from the Sophia AI repository.
These files have been preserved for historical reference but are no longer actively used.

## Directory Structure

- `legacy-deployment/` - Old Docker Compose and deployment scripts
  - `docker-compose/` - Docker Compose files
  - `scripts/` - Deployment scripts
  - `github-workflows/` - Old GitHub Actions workflows
  
- `reports/` - Historical reports and analysis documents

- `plans/` - Old planning and migration documents

- `scripts/` - Archived utility scripts

- `one-time-scripts/` - Scripts that were used once and archived

## Migration Notes

As of July 2025, Sophia AI has migrated to:
- K3s on Lambda Labs for container orchestration
- Unified GitHub Actions workflow for deployments
- Helm charts for service definitions
- GitOps with Flux for continuous deployment

For current deployment information, see:
- `/kubernetes/` - K8s manifests and Helm charts
- `/.github/workflows/unified-deployment.yml` - Current CI/CD pipeline
- `/docs/deployment/` - Current deployment documentation
"""

        readme_path = self.archive_dir / "README.md"
        readme_path.write_text(readme_content)
        logger.info("📝 Created archive README.md")

    def run(self):
        """Run the cleanup process."""
        logger.info("🧹 Starting legacy deployment cleanup...")
        logger.info(f"Working directory: {self.root_dir}")

        # Create archive structure
        self.create_archive_structure()

        # Find artifacts
        self.find_artifacts()

        # Archive artifacts
        total_moved = self.archive_artifacts()

        # Create README
        self.create_archive_readme()

        logger.info(f"\n✨ Cleanup complete! Archived {total_moved} files.")
        logger.info(f"📁 Archive location: {self.archive_dir}")

        # Summary
        print("\n" + "=" * 60)
        print("LEGACY DEPLOYMENT CLEANUP SUMMARY")
        print("=" * 60)
        for category, config in self.artifacts_to_archive.items():
            if config["files"]:
                print(f"\n{category.replace('_', ' ').title()}:")
                for file_path in config["files"][:5]:  # Show first 5
                    print(f"  - {file_path.name}")
                if len(config["files"]) > 5:
                    print(f"  ... and {len(config['files']) - 5} more")
        print("\n" + "=" * 60)


if __name__ == "__main__":
    cleaner = LegacyDeploymentCleaner()
    cleaner.run()
