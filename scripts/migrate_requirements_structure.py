#!/usr/bin/env python3
"""
📦 Requirements Structure Migration Script

Migrates from legacy scattered requirements files to organized requirements/ structure.
Part of Phase 2: Dependency Consolidation implementation.

Usage:
    python scripts/migrate_requirements_structure.py --validate
    python scripts/migrate_requirements_structure.py --migrate
    python scripts/migrate_requirements_structure.py --cleanup

Created: July 16, 2025
Phase: 2 - Dependency Consolidation
"""

import os
import shutil
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RequirementsMigrator:
    """Handles migration from legacy requirements to organized structure"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.requirements_dir = self.project_root / "requirements"
        
        # Legacy files mapping
        self.legacy_files = {
            "requirements.txt": "base.txt",
            "requirements-phase2.txt": "cleanup.txt", 
            "requirements.docker.txt": "docker.txt",  # Keep separate for Docker builds
        }
        
        # Validation targets
        self.organized_files = [
            "requirements/base.txt",
            "requirements/development.txt", 
            "requirements/production.txt",
            "requirements/cleanup.txt"
        ]
    
    def validate_structure(self) -> Tuple[bool, List[str]]:
        """Validate the new requirements structure"""
        logger.info("🔍 Validating requirements structure...")
        
        issues = []
        
        # Check if requirements/ directory exists
        if not self.requirements_dir.exists():
            issues.append("requirements/ directory does not exist")
            return False, issues
        
        # Check organized files exist
        for req_file in self.organized_files:
            full_path = self.project_root / req_file
            if not full_path.exists():
                issues.append(f"Missing organized file: {req_file}")
        
        # Test installation capability
        for req_file in self.organized_files:
            result = self._test_requirements_file(req_file)
            if not result[0]:
                issues.append(f"Installation test failed for {req_file}: {result[1]}")
        
        # Check for duplicate dependencies
        duplicates = self._find_duplicate_dependencies()
        if duplicates:
            issues.append(f"Duplicate dependencies found: {duplicates}")
        
        success = len(issues) == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"📊 Validation: {status}")
        
        if issues:
            for issue in issues:
                logger.error(f"  ❌ {issue}")
        else:
            logger.info("  ✅ All requirements files are valid")
            logger.info("  ✅ No duplicate dependencies found")
            logger.info("  ✅ All files can be installed successfully")
        
        return success, issues
    
    def _test_requirements_file(self, req_file: str) -> Tuple[bool, str]:
        """Test if a requirements file can be installed"""
        try:
            full_path = self.project_root / req_file
            # Use --dry-run to test without actually installing
            result = subprocess.run(
                ["python", "-m", "pip", "install", "-r", str(full_path), "--dry-run"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Installation test timed out"
        except Exception as e:
            return False, str(e)
    
    def _find_duplicate_dependencies(self) -> List[str]:
        """Find duplicate dependencies across organized files"""
        all_deps = {}
        duplicates = []
        
        for req_file in self.organized_files:
            full_path = self.project_root / req_file
            if full_path.exists():
                deps = self._parse_requirements_file(full_path)
                for dep in deps:
                    if dep in all_deps:
                        duplicates.append(f"{dep} (in {all_deps[dep]} and {req_file})")
                    else:
                        all_deps[dep] = req_file
        
        return duplicates
    
    def _parse_requirements_file(self, file_path: Path) -> List[str]:
        """Parse requirements file and extract package names"""
        deps = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('-r'):
                        # Extract package name (before ==, >=, etc.)
                        dep_name = line.split('==')[0].split('>=')[0].split('<=')[0]
                        dep_name = dep_name.split('[')[0]  # Remove extras like [standard]
                        deps.append(dep_name)
        except Exception as e:
            logger.warning(f"Could not parse {file_path}: {e}")
        return deps
    
    def migrate_legacy_files(self) -> bool:
        """Migrate legacy requirements files"""
        logger.info("🔄 Migrating legacy requirements files...")
        
        if not self.requirements_dir.exists():
            logger.error("❌ requirements/ directory does not exist. Run with --validate first.")
            return False
        
        migrated = []
        
        # Create backup directory
        backup_dir = self.project_root / "requirements_backup"
        backup_dir.mkdir(exist_ok=True)
        
        for legacy_file, organized_file in self.legacy_files.items():
            legacy_path = self.project_root / legacy_file
            
            if legacy_path.exists():
                # Create backup
                backup_path = backup_dir / legacy_file
                shutil.copy2(legacy_path, backup_path)
                logger.info(f"  📁 Backup created: {backup_path}")
                
                # Add reference comment to organized file if it doesn't already include the legacy content
                organized_path = self.requirements_dir / organized_file
                if organized_path.exists():
                    self._add_migration_comment(organized_path, legacy_file)
                    migrated.append(legacy_file)
                    logger.info(f"  ✅ Migrated: {legacy_file} → requirements/{organized_file}")
        
        if migrated:
            logger.info(f"📊 Migration complete: {len(migrated)} files migrated")
            logger.info("📁 Backups available in requirements_backup/")
            return True
        else:
            logger.info("📊 No legacy files found to migrate")
            return False
    
    def _add_migration_comment(self, organized_file: Path, legacy_file: str):
        """Add migration comment to organized file"""
        try:
            with open(organized_file, 'r') as f:
                content = f.read()
            
            migration_comment = f"# Migrated from {legacy_file} on {os.popen('date').read().strip()}\n"
            
            if migration_comment not in content:
                with open(organized_file, 'w') as f:
                    f.write(migration_comment + content)
        except Exception as e:
            logger.warning(f"Could not add migration comment to {organized_file}: {e}")
    
    def cleanup_legacy_files(self) -> bool:
        """Remove legacy requirements files after successful migration"""
        logger.info("🧹 Cleaning up legacy requirements files...")
        
        removed = []
        
        for legacy_file in self.legacy_files.keys():
            legacy_path = self.project_root / legacy_file
            
            if legacy_path.exists():
                # Don't remove requirements.txt and requirements.docker.txt yet - they might be used by existing workflows
                if legacy_file in ["requirements.txt", "requirements.docker.txt"]:
                    logger.info(f"  ⏭️ Keeping {legacy_file} for backward compatibility")
                    continue
                
                try:
                    os.remove(legacy_path)
                    removed.append(legacy_file)
                    logger.info(f"  🗑️ Removed: {legacy_file}")
                except Exception as e:
                    logger.error(f"  ❌ Could not remove {legacy_file}: {e}")
        
        if removed:
            logger.info(f"📊 Cleanup complete: {len(removed)} legacy files removed")
            return True
        else:
            logger.info("📊 No legacy files to clean up")
            return False

def main():
    parser = argparse.ArgumentParser(description="Migrate requirements structure")
    parser.add_argument("--validate", action="store_true", help="Validate organized requirements structure")
    parser.add_argument("--migrate", action="store_true", help="Migrate legacy files to organized structure")
    parser.add_argument("--cleanup", action="store_true", help="Remove legacy files after migration")
    parser.add_argument("--all", action="store_true", help="Run all operations: validate, migrate, cleanup")
    
    args = parser.parse_args()
    
    if not any([args.validate, args.migrate, args.cleanup, args.all]):
        parser.print_help()
        return
    
    migrator = RequirementsMigrator()
    success = True
    
    if args.all or args.validate:
        validation_success, issues = migrator.validate_structure()
        success = success and validation_success
        
        if not validation_success:
            logger.error("❌ Validation failed. Fix issues before proceeding.")
            return
    
    if args.all or args.migrate:
        migration_success = migrator.migrate_legacy_files()
        success = success and migration_success
    
    if args.all or args.cleanup:
        cleanup_success = migrator.cleanup_legacy_files()
        success = success and cleanup_success
    
    status = "✅ SUCCESS" if success else "❌ FAILED"
    logger.info(f"🎯 Migration operation: {status}")

if __name__ == "__main__":
    main() 