#!/usr/bin/env python3
"""
Clean up and archive old Lambda Labs deployment files.
This script identifies outdated deployment artifacts and moves them to archive.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Set

# Files and patterns to clean up
CLEANUP_PATTERNS = {
    "old_deployment_scripts": [
        "scripts/deploy_to_lambda_labs.py",
        "scripts/lambda_labs_deployment.py",
        "scripts/deploy_lambda_infrastructure.py",
        "scripts/lambda_labs_ssh_key_setup.py",
        "scripts/setup_lambda_labs.sh",
        "scripts/deploy_to_146.235.200.1.sh"
    ],
    
    "old_workflows": [
        ".github/workflows/lambda-labs-deployment.yml",
        ".github/workflows/deploy-to-lambda.yml",
        ".github/workflows/lambda-deploy-old.yml"
    ],
    
    "old_documentation": [
        "LAMBDA_LABS_OLD_DEPLOYMENT.md",
        "docs/lambda-labs-legacy.md",
        "docs/deployment/old-lambda-guide.md"
    ],
    
    "old_configs": [
        "lambda-labs-old-config.yaml",
        "infrastructure/old-lambda-labs.ts",
        "config/lambda-labs-legacy.json"
    ],
    
    "deployment_artifacts": [
        "sophia-deployment-*.tar.gz",
        "lambda-deployment-*.zip",
        "deployment-backup-*.tar"
    ]
}

# Files to keep (do not delete)
KEEP_FILES = {
    "scripts/lambda_labs_manager.py",
    "scripts/deploy_sophia_complete.py",
    "scripts/setup_github_secrets.sh",
    ".github/workflows/main-deployment.yml",
    "docs/deployment/LAMBDA_LABS_GUIDE.md",
    "infrastructure/lambda-labs-config.yaml",
    "infrastructure/pulumi/lambda-labs.ts"
}

# Old IP addresses to search for
OLD_IPS = [
    "146.235.200.1",
    "137.131.6.213",
    "104.171.202.103",
    "192.222.58.232",
    "104.171.202.117",
    "104.171.202.134",
    "155.248.194.183",
    "192.222.51.122"
]

class LambdaLabsCleanup:
    def __init__(self):
        self.archive_dir = Path(f"archive/lambda-labs-cleanup-{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.files_to_archive = []
        self.files_with_old_ips = []
        self.errors = []
        
    def create_archive_dir(self):
        """Create archive directory structure"""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        (self.archive_dir / "scripts").mkdir(exist_ok=True)
        (self.archive_dir / "workflows").mkdir(exist_ok=True)
        (self.archive_dir / "docs").mkdir(exist_ok=True)
        (self.archive_dir / "configs").mkdir(exist_ok=True)
        
    def scan_for_old_ips(self):
        """Scan files for references to old IP addresses"""
        print("🔍 Scanning for old IP addresses...")
        
        for root, dirs, files in os.walk('.'):
            # Skip certain directories
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', 'archive']):
                continue
                
            for file in files:
                if file.endswith(('.py', '.sh', '.yml', '.yaml', '.md', '.json')):
                    filepath = Path(root) / file
                    
                    # Skip if it's a file we want to keep
                    if str(filepath) in KEEP_FILES:
                        continue
                        
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for old_ip in OLD_IPS:
                            if old_ip in content:
                                self.files_with_old_ips.append((str(filepath), old_ip))
                                break
                                
                    except Exception as e:
                        self.errors.append(f"Error reading {filepath}: {e}")
                        
    def identify_files_to_archive(self):
        """Identify files that should be archived"""
        print("📋 Identifying files to archive...")
        
        # Check cleanup patterns
        for category, patterns in CLEANUP_PATTERNS.items():
            for pattern in patterns:
                if '*' in pattern:
                    # Handle glob patterns
                    for file in Path('.').glob(pattern):
                        if file.exists() and str(file) not in KEEP_FILES:
                            self.files_to_archive.append((str(file), category))
                else:
                    # Direct file path
                    file = Path(pattern)
                    if file.exists() and str(file) not in KEEP_FILES:
                        self.files_to_archive.append((str(file), category))
                        
        # Add files with old IPs (but not in keep list)
        for filepath, old_ip in self.files_with_old_ips:
            if filepath not in KEEP_FILES and filepath not in [f[0] for f in self.files_to_archive]:
                self.files_to_archive.append((filepath, "contains_old_ip"))
                
    def archive_files(self, dry_run: bool = False):
        """Archive identified files"""
        if dry_run:
            print("\n🔄 DRY RUN - No files will be moved")
        else:
            self.create_archive_dir()
            
        archived_count = 0
        
        for filepath, category in self.files_to_archive:
            source = Path(filepath)
            
            # Determine destination
            if category == "old_deployment_scripts":
                dest_dir = self.archive_dir / "scripts"
            elif category == "old_workflows":
                dest_dir = self.archive_dir / "workflows"
            elif category == "old_documentation":
                dest_dir = self.archive_dir / "docs"
            elif category == "old_configs":
                dest_dir = self.archive_dir / "configs"
            else:
                dest_dir = self.archive_dir / "misc"
                dest_dir.mkdir(exist_ok=True)
                
            dest = dest_dir / source.name
            
            if dry_run:
                print(f"Would archive: {filepath} → {dest}")
            else:
                try:
                    shutil.move(str(source), str(dest))
                    print(f"✅ Archived: {filepath} → {dest}")
                    archived_count += 1
                except Exception as e:
                    self.errors.append(f"Error archiving {filepath}: {e}")
                    
        return archived_count
        
    def update_gitignore(self):
        """Update .gitignore to exclude archive directory"""
        gitignore_path = Path('.gitignore')
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
                
            if 'archive/' not in content:
                with open(gitignore_path, 'a') as f:
                    f.write('\n# Lambda Labs cleanup archives\narchive/\n')
                print("✅ Updated .gitignore")
                
    def generate_report(self, dry_run: bool, archived_count: int):
        """Generate cleanup report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "mode": "dry_run" if dry_run else "executed",
            "archive_directory": str(self.archive_dir),
            "statistics": {
                "files_with_old_ips": len(self.files_with_old_ips),
                "files_to_archive": len(self.files_to_archive),
                "files_archived": archived_count,
                "errors": len(self.errors)
            },
            "files_with_old_ips": self.files_with_old_ips,
            "files_archived": self.files_to_archive,
            "errors": self.errors
        }
        
        # Save JSON report
        report_path = f"lambda_labs_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Generate markdown report
        md_report = f"""# Lambda Labs Cleanup Report

**Timestamp**: {report['timestamp']}
**Mode**: {report['mode'].upper()}
**Archive Directory**: {report['archive_directory']}

## Summary

- **Files with Old IPs**: {report['statistics']['files_with_old_ips']}
- **Files to Archive**: {report['statistics']['files_to_archive']}
- **Files Archived**: {report['statistics']['files_archived']}
- **Errors**: {report['statistics']['errors']}

## Files with Old IP Addresses

"""
        
        if self.files_with_old_ips:
            for filepath, old_ip in self.files_with_old_ips[:20]:  # Show first 20
                md_report += f"- `{filepath}` (contains {old_ip})\n"
                
            if len(self.files_with_old_ips) > 20:
                md_report += f"\n... and {len(self.files_with_old_ips) - 20} more files\n"
        else:
            md_report += "No files found with old IP addresses.\n"
            
        md_report += "\n## Files Archived\n\n"
        
        if self.files_to_archive:
            current_category = None
            for filepath, category in sorted(self.files_to_archive, key=lambda x: x[1]):
                if category != current_category:
                    md_report += f"\n### {category.replace('_', ' ').title()}\n"
                    current_category = category
                md_report += f"- `{filepath}`\n"
        else:
            md_report += "No files to archive.\n"
            
        if self.errors:
            md_report += "\n## Errors\n\n"
            for error in self.errors:
                md_report += f"- {error}\n"
                
        # Save markdown report
        md_path = report_path.replace('.json', '.md')
        with open(md_path, 'w') as f:
            f.write(md_report)
            
        print(f"\n📊 Reports generated:")
        print(f"  - JSON: {report_path}")
        print(f"  - Markdown: {md_path}")
        
    def run(self, dry_run: bool = False):
        """Run the cleanup process"""
        print("🧹 Lambda Labs Deployment Cleanup")
        print("=" * 50)
        
        # Scan for old IPs
        self.scan_for_old_ips()
        
        # Identify files to archive
        self.identify_files_to_archive()
        
        # Archive files
        archived_count = self.archive_files(dry_run)
        
        # Update .gitignore
        if not dry_run and archived_count > 0:
            self.update_gitignore()
            
        # Generate report
        self.generate_report(dry_run, archived_count)
        
        # Summary
        print("\n📈 Summary:")
        print(f"  - Files with old IPs: {len(self.files_with_old_ips)}")
        print(f"  - Files to archive: {len(self.files_to_archive)}")
        print(f"  - Files archived: {archived_count}")
        
        if self.errors:
            print(f"\n⚠️  Errors encountered: {len(self.errors)}")
            for error in self.errors[:5]:
                print(f"  - {error}")
                
        if not dry_run and archived_count > 0:
            print(f"\n✅ Files archived to: {self.archive_dir}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean up old Lambda Labs deployment files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned up without making changes"
    )
    
    args = parser.parse_args()
    
    cleanup = LambdaLabsCleanup()
    cleanup.run(dry_run=args.dry_run)


if __name__ == "__main__":
    main() 