#!/usr/bin/env python3
"""
Clean up and archive old deployment files for Sophia AI.
Moves deprecated files to archive and updates references.
"""

import os
import shutil
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

# Files and patterns to archive
ARCHIVE_PATTERNS = {
    'workflows': [
        '.github/workflows/production-deployment.yml',
        '.github/workflows/sophia-prod.yml',
        '.github/workflows/deploy-phase2.yml',
        '.github/workflows/deploy_v2_mcp_servers.yml',
        '.github/workflows/production.yml',
        '.github/workflows/lambda-labs-deployment.yml',
        '.github/workflows/deploy-sophia-intel-ai.yml',
        '.github/workflows/sophia-unified-deployment.yml',
        '.github/workflows/deploy-mcp-production.yml',
        '.github/workflows/deploy-estuary-flow.yml',
    ],
    'docker_files': [
        'docker-compose.prod.yml',
        'docker-compose.override.yml',
        'docker-compose.unified.yml',
        'docker-compose.cloud.v2.yml',
        'Dockerfile.optimized',
        'Dockerfile.uv',
    ],
    'scripts': [
        'scripts/deploy_enhanced.sh',
        'scripts/cloud-deploy-estuary.sh',
        'scripts/deploy_lambda_infrastructure.py',
        'scripts/deploy_sophia_intel_ai.py',
        'scripts/focused_deployment.sh',
        'scripts/create_enhanced_mcp_template.sh',
        'scripts/scaffold_mcp_server_v3.sh',
    ],
    'docs': [
        'DEPLOYMENT_README.md',
        'DEPLOYMENT_COMPLETE_SUMMARY.md',
        'UNIFIED_DEPLOYMENT_COMPLETE.md',
        'SOPHIA_AI_DEPLOYMENT_STATUS_SUMMARY.md',
        'SOPHIA_AI_PLATFORM_DEPLOYMENT_GUIDE.md',
        'UNIFIED_DEPLOYMENT_IMPROVEMENT_PLAN.md',
        'COMPREHENSIVE_DEPLOYMENT_STATUS_REVIEW.md',
        'docs/04-deployment/DEPLOYMENT_GUIDE.md',  # Old location
        'docs/04-deployment/DOCKER_GUIDE.md',
        'docs/04-deployment/LAMBDA_LABS_MCP_DEPLOYMENT_GUIDE.md',
    ]
}

# Files to keep (don't archive these)
KEEP_FILES = {
    '.github/workflows/main-deployment.yml',
    '.github/workflows/mcp-deployment.yml',
    '.github/workflows/secret-sync.yml',
    '.github/workflows/infrastructure.yml',
    '.github/workflows/monitoring.yml',
    'docker-compose.yml',
    'docker-compose.cloud.yml',
    'Dockerfile',
    'Dockerfile.production',
    'scripts/deployment/deploy.py',
    'scripts/deployment/health_check.py',
    'scripts/lambda_labs_manager.py',
}


class DeploymentCleaner:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.project_root = Path.cwd()
        self.archive_dir = self.project_root / 'archive' / 'deployment' / datetime.now().strftime('%Y%m%d_%H%M%S')
        self.moved_files: List[Dict] = []
        self.updated_files: List[str] = []
        
    def run(self):
        """Run the complete cleanup process."""
        print("🧹 Sophia AI Deployment Cleanup")
        print("=" * 80)
        
        if self.dry_run:
            print("🔍 Running in DRY RUN mode - no files will be modified")
        else:
            print("⚠️  Running in LIVE mode - files will be moved and modified")
            
        # Create archive directory
        if not self.dry_run:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            
        # Archive old files
        self.archive_old_files()
        
        # Update references
        self.update_references()
        
        # Generate report
        self.generate_report()
        
    def archive_old_files(self):
        """Archive old deployment files."""
        print("\n📦 Archiving old deployment files...")
        
        for category, patterns in ARCHIVE_PATTERNS.items():
            category_dir = self.archive_dir / category
            
            for pattern in patterns:
                file_path = self.project_root / pattern
                
                # Skip if file is in keep list
                if str(file_path.relative_to(self.project_root)) in KEEP_FILES:
                    continue
                    
                if file_path.exists():
                    # Determine archive path
                    archive_path = category_dir / file_path.name
                    
                    print(f"  Moving: {file_path.relative_to(self.project_root)}")
                    print(f"      To: {archive_path.relative_to(self.project_root)}")
                    
                    if not self.dry_run:
                        # Create category directory
                        category_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Move file
                        shutil.move(str(file_path), str(archive_path))
                        
                    self.moved_files.append({
                        'original': str(file_path.relative_to(self.project_root)),
                        'archived': str(archive_path.relative_to(self.project_root)),
                        'category': category
                    })
                    
    def update_references(self):
        """Update references to moved files."""
        print("\n🔄 Updating references...")
        
        # Files that might contain references
        reference_files = [
            'README.md',
            '.cursorrules',
            'docs/README.md',
            'docs/deployment/README.md',
            '.github/README.md',
        ]
        
        for ref_file in reference_files:
            file_path = self.project_root / ref_file
            if file_path.exists():
                self.update_file_references(file_path)
                
    def update_file_references(self, file_path: Path):
        """Update references in a single file."""
        try:
            content = file_path.read_text()
            original_content = content
            
            # Update references to moved files
            for moved in self.moved_files:
                old_ref = moved['original']
                new_ref = moved['archived']
                
                # Update various reference patterns
                patterns = [
                    f"({old_ref})",
                    f"[{old_ref}]",
                    f"`{old_ref}`",
                    f'"{old_ref}"',
                    f"'{old_ref}'",
                ]
                
                for pattern in patterns:
                    if pattern in content:
                        # Create reference to archived location
                        archive_ref = pattern.replace(old_ref, new_ref)
                        content = content.replace(pattern, archive_ref)
                        
            # Only update if changes were made
            if content != original_content:
                print(f"  Updating: {file_path.relative_to(self.project_root)}")
                
                if not self.dry_run:
                    file_path.write_text(content)
                    
                self.updated_files.append(str(file_path.relative_to(self.project_root)))
                
        except Exception as e:
            print(f"  Error updating {file_path}: {e}")
            
    def generate_report(self):
        """Generate cleanup report."""
        print("\n📊 Cleanup Report")
        print("=" * 80)
        
        # Summary
        print(f"\n📈 Summary:")
        print(f"  Files archived: {len(self.moved_files)}")
        print(f"  References updated: {len(self.updated_files)}")
        print(f"  Archive location: {self.archive_dir.relative_to(self.project_root)}")
        
        # Archived files by category
        if self.moved_files:
            print(f"\n📦 Archived Files by Category:")
            categories = {}
            for moved in self.moved_files:
                cat = moved['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(moved['original'])
                
            for cat, files in categories.items():
                print(f"\n  {cat.title()} ({len(files)} files):")
                for f in sorted(files):
                    print(f"    - {f}")
                    
        # Updated references
        if self.updated_files:
            print(f"\n🔄 Updated References:")
            for f in sorted(self.updated_files):
                print(f"  - {f}")
                
        # Save detailed report
        if not self.dry_run:
            report_path = self.archive_dir / 'CLEANUP_REPORT.md'
            self.save_detailed_report(report_path)
            print(f"\n📄 Detailed report saved to: {report_path.relative_to(self.project_root)}")
            
    def save_detailed_report(self, report_path: Path):
        """Save detailed cleanup report."""
        report = f"""# Deployment Cleanup Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Mode**: {'DRY RUN' if self.dry_run else 'LIVE'}

## Summary

- **Files Archived**: {len(self.moved_files)}
- **References Updated**: {len(self.updated_files)}
- **Archive Location**: `{self.archive_dir.relative_to(self.project_root)}`

## Archived Files

"""
        # Group by category
        categories = {}
        for moved in self.moved_files:
            cat = moved['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(moved)
            
        for cat, moves in categories.items():
            report += f"\n### {cat.title()}\n\n"
            for move in moves:
                report += f"- `{move['original']}` → `{move['archived']}`\n"
                
        # Updated references
        if self.updated_files:
            report += "\n## Updated References\n\n"
            for f in sorted(self.updated_files):
                report += f"- `{f}`\n"
                
        # Next steps
        report += """
## Next Steps

1. Review the archived files to ensure nothing critical was moved
2. Update any documentation that references old deployment procedures
3. Test the deployment process with the new structure
4. Consider deleting the archive after verification (30 days recommended)

## Restoration

If you need to restore any archived files:

```bash
# Restore specific file
cp archive/deployment/*/workflows/production-deployment.yml .github/workflows/

# Restore all files
cp -r archive/deployment/*/. .
```
"""
        
        report_path.write_text(report)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up old deployment files')
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run in live mode (actually move files)'
    )
    
    args = parser.parse_args()
    
    cleaner = DeploymentCleaner(dry_run=not args.live)
    cleaner.run()


if __name__ == '__main__':
    main() 