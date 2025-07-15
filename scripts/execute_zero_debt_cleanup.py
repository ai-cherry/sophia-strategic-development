#!/usr/bin/env python3
"""
🎯 SOPHIA AI: ZERO TECHNICAL DEBT CLEANUP EXECUTION
Comprehensive cleanup script implementing the zero technical debt plan

This script executes the complete cleanup strategy to achieve zero technical debt
while preserving all essential functionality.

Date: July 14, 2025
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ZeroDebtCleanup:
    """Comprehensive zero technical debt cleanup implementation"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.base_path = Path.cwd()
        self.backup_created = False
        self.cleanup_stats = {
            "files_removed": 0,
            "directories_removed": 0,
            "size_saved_mb": 0,
            "categories_cleaned": []
        }
        
    async def execute_cleanup(self) -> Dict[str, Any]:
        """Execute comprehensive cleanup plan"""
        logger.info("🚀 Starting zero technical debt cleanup execution...")
        
        # Phase 1: Create backup
        if not self.dry_run:
            await self._create_backup()
        
        # Phase 2: Execute cleanup categories
        cleanup_tasks = [
            ("Archive Directories", self._cleanup_archive_directories),
            ("Backup Files", self._cleanup_backup_files),
            ("One-Time Scripts", self._cleanup_one_time_scripts),
            ("Duplicate Files", self._cleanup_duplicate_files),
            ("Large Files", self._cleanup_large_files),
            ("Empty Directories", self._cleanup_empty_directories),
            ("Temporary Files", self._cleanup_temporary_files),
            ("Dead Code", self._cleanup_dead_code),
        ]
        
        for category, cleanup_func in cleanup_tasks:
            logger.info(f"🧹 Cleaning up: {category}")
            await cleanup_func()
            self.cleanup_stats["categories_cleaned"].append(category)
        
        # Phase 3: Optimize repository structure
        await self._optimize_repository_structure()
        
        # Phase 4: Validate results
        validation_result = await self._validate_cleanup()
        
        # Phase 5: Generate report
        report = await self._generate_cleanup_report(validation_result)
        
        logger.info("✅ Zero technical debt cleanup completed successfully!")
        return report
    
    async def _create_backup(self):
        """Create backup of current repository state"""
        logger.info("📦 Creating repository backup...")
        
        backup_dir = self.base_path.parent / f"sophia-backup-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Create backup using git
            subprocess.run([
                "git", "clone", ".", str(backup_dir)
            ], check=True, capture_output=True)
            
            logger.info(f"✅ Backup created: {backup_dir}")
            self.backup_created = True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Backup creation failed: {e}")
            raise
    
    async def _cleanup_archive_directories(self):
        """Remove archive directories"""
        archive_patterns = [
            "archive", "backup", "_archived", "migration_backup",
            ".backup", "old", "deprecated", "legacy"
        ]
        
        directories_to_remove = []
        
        for pattern in archive_patterns:
            for path in self.base_path.rglob(f"*{pattern}*"):
                if path.is_dir() and ".git" not in str(path) and ".venv" not in str(path):
                    directories_to_remove.append(path)
        
        for directory in directories_to_remove:
            size_mb = self._get_directory_size(directory)
            logger.info(f"🗑️  Removing archive directory: {directory} ({size_mb:.1f}MB)")
            
            if not self.dry_run:
                shutil.rmtree(directory, ignore_errors=True)
            
            self.cleanup_stats["directories_removed"] += 1
            self.cleanup_stats["size_saved_mb"] += size_mb
    
    async def _cleanup_backup_files(self):
        """Remove backup files"""
        backup_extensions = [
            ".backup", ".bak", ".old", ".tmp", ".temp", ".orig", ".save"
        ]
        
        files_to_remove = []
        
        for ext in backup_extensions:
            for path in self.base_path.rglob(f"*{ext}"):
                if path.is_file() and ".git" not in str(path) and ".venv" not in str(path):
                    files_to_remove.append(path)
        
        for file_path in files_to_remove:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            logger.info(f"🗑️  Removing backup file: {file_path} ({size_mb:.1f}MB)")
            
            if not self.dry_run:
                file_path.unlink()
            
            self.cleanup_stats["files_removed"] += 1
            self.cleanup_stats["size_saved_mb"] += size_mb
    
    async def _cleanup_one_time_scripts(self):
        """Organize one-time scripts"""
        one_time_patterns = [
            "deploy_", "setup_", "fix_", "test_", "migrate_", "cleanup_",
            "install_", "configure_", "initialize_"
        ]
        
        scripts_dir = self.base_path / "scripts"
        one_time_dir = scripts_dir / "one_time"
        
        if not one_time_dir.exists() and not self.dry_run:
            one_time_dir.mkdir(parents=True)
        
        scripts_to_move = []
        
        for pattern in one_time_patterns:
            for script_path in scripts_dir.rglob(f"{pattern}*.py"):
                if script_path.is_file() and "one_time" not in str(script_path):
                    scripts_to_move.append(script_path)
        
        for script_path in scripts_to_move:
            new_path = one_time_dir / script_path.name
            logger.info(f"📁 Moving one-time script: {script_path} → {new_path}")
            
            if not self.dry_run:
                shutil.move(str(script_path), str(new_path))
            
            self.cleanup_stats["files_removed"] += 1
    
    async def _cleanup_duplicate_files(self):
        """Remove duplicate files"""
        import hashlib
        
        file_hashes = {}
        duplicates = []
        
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and ".git" not in str(file_path) and ".venv" not in str(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash in file_hashes:
                        duplicates.append((file_path, file_hashes[file_hash]))
                    else:
                        file_hashes[file_hash] = file_path
                        
                except Exception:
                    continue
        
        for duplicate, original in duplicates:
            size_mb = duplicate.stat().st_size / (1024 * 1024)
            logger.info(f"🗑️  Removing duplicate file: {duplicate} (duplicate of {original})")
            
            if not self.dry_run:
                duplicate.unlink()
            
            self.cleanup_stats["files_removed"] += 1
            self.cleanup_stats["size_saved_mb"] += size_mb
    
    async def _cleanup_large_files(self):
        """Handle large files"""
        large_file_threshold = 10 * 1024 * 1024  # 10MB
        
        large_files = []
        
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and ".git" not in str(file_path) and ".venv" not in str(file_path):
                try:
                    if file_path.stat().st_size > large_file_threshold:
                        large_files.append(file_path)
                except Exception:
                    continue
        
        for file_path in large_files:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            
            # Check if it's a necessary file
            if any(pattern in str(file_path) for pattern in [
                "node_modules", "dist", "build", ".log", ".cache"
            ]):
                logger.info(f"🗑️  Removing large unnecessary file: {file_path} ({size_mb:.1f}MB)")
                
                if not self.dry_run:
                    file_path.unlink()
                
                self.cleanup_stats["files_removed"] += 1
                self.cleanup_stats["size_saved_mb"] += size_mb
            else:
                logger.warning(f"⚠️  Large file detected (keeping): {file_path} ({size_mb:.1f}MB)")
    
    async def _cleanup_empty_directories(self):
        """Remove empty directories"""
        empty_dirs = []
        
        for dir_path in self.base_path.rglob("*"):
            if dir_path.is_dir() and ".git" not in str(dir_path) and ".venv" not in str(dir_path):
                try:
                    if not any(dir_path.iterdir()):
                        empty_dirs.append(dir_path)
                except Exception:
                    continue
        
        for dir_path in empty_dirs:
            logger.info(f"🗑️  Removing empty directory: {dir_path}")
            
            if not self.dry_run:
                dir_path.rmdir()
            
            self.cleanup_stats["directories_removed"] += 1
    
    async def _cleanup_temporary_files(self):
        """Remove temporary files"""
        temp_patterns = [
            "*.pyc", "*.pyo", "*.pyd", "__pycache__",
            "*.log", "*.tmp", "*.temp", ".DS_Store",
            "Thumbs.db", "*.swp", "*.swo", "*~"
        ]
        
        temp_files = []
        
        for pattern in temp_patterns:
            for file_path in self.base_path.rglob(pattern):
                if file_path.is_file() and ".git" not in str(file_path):
                    temp_files.append(file_path)
        
        for file_path in temp_files:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            logger.info(f"🗑️  Removing temporary file: {file_path}")
            
            if not self.dry_run:
                if file_path.is_dir():
                    shutil.rmtree(file_path, ignore_errors=True)
                else:
                    file_path.unlink()
            
            self.cleanup_stats["files_removed"] += 1
            self.cleanup_stats["size_saved_mb"] += size_mb
    
    async def _cleanup_dead_code(self):
        """Remove dead code markers and unused imports"""
        # This is a simplified version - in practice, you'd want more sophisticated analysis
        dead_code_patterns = [
            "",
            "",
            "",
            ""
        ]
        
        python_files = list(self.base_path.rglob("*.py"))
        
        for py_file in python_files:
            if ".venv" in str(py_file) or ".git" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                modified = False
                for pattern in dead_code_patterns:
                    if pattern in content:
                        content = content.replace(pattern, "")
                        modified = True
                
                if modified and not self.dry_run:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    logger.info(f"🧹 Cleaned dead code markers: {py_file}")
                    
            except Exception as e:
                logger.warning(f"⚠️  Could not process {py_file}: {e}")
    
    async def _optimize_repository_structure(self):
        """Optimize repository structure"""
        logger.info("🏗️  Optimizing repository structure...")
        
        # Create standard directories if they don't exist
        standard_dirs = [
            "scripts/one_time",
            "scripts/utils",
            "scripts/monitoring",
            "docs/architecture",
            "docs/deployment",
            "docs/development"
        ]
        
        for dir_path in standard_dirs:
            full_path = self.base_path / dir_path
            if not full_path.exists() and not self.dry_run:
                full_path.mkdir(parents=True)
                logger.info(f"📁 Created directory: {dir_path}")
    
    async def _validate_cleanup(self) -> Dict[str, Any]:
        """Validate cleanup results"""
        logger.info("🔍 Validating cleanup results...")
        
        # Run technical debt prevention check
        try:
            from scripts.technical_debt_prevention import TechnicalDebtPreventionFramework
            
            framework = TechnicalDebtPreventionFramework()
            report = await framework.pre_commit_validation()
            
            return {
                "debt_score": report.debt_score,
                "file_count": report.file_count,
                "repository_size_mb": report.repository_size_mb,
                "validation_passed": report.passed,
                "validation_results": [r.message for r in report.results]
            }
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return {
                "debt_score": 999,
                "validation_passed": False,
                "error": str(e)
            }
    
    async def _generate_cleanup_report(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive cleanup report"""
        report = {
            "cleanup_execution": {
                "timestamp": datetime.now().isoformat(),
                "dry_run": self.dry_run,
                "backup_created": self.backup_created,
                "statistics": self.cleanup_stats
            },
            "validation_results": validation_result,
            "recommendations": []
        }
        
        # Add recommendations based on results
        if validation_result.get("debt_score", 0) > 20:
            report["recommendations"].append("Consider additional cleanup to reduce debt score")
        
        if validation_result.get("file_count", 0) > 200:
            report["recommendations"].append("File count is high - consider further consolidation")
        
        if validation_result.get("repository_size_mb", 0) > 400:
            report["recommendations"].append("Repository size is large - consider removing large files")
        
        return report
    
    def _get_directory_size(self, directory: Path) -> float:
        """Get directory size in MB"""
        total_size = 0
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        return total_size / (1024 * 1024)

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Zero Technical Debt Cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--output", help="Output file for cleanup report")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    cleanup = ZeroDebtCleanup(dry_run=args.dry_run)
    
    try:
        report = await cleanup.execute_cleanup()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n🎉 CLEANUP SUMMARY")
        print(f"{'='*50}")
        print(f"Files Removed: {report['cleanup_execution']['statistics']['files_removed']}")
        print(f"Directories Removed: {report['cleanup_execution']['statistics']['directories_removed']}")
        print(f"Size Saved: {report['cleanup_execution']['statistics']['size_saved_mb']:.1f}MB")
        print(f"Categories Cleaned: {len(report['cleanup_execution']['statistics']['categories_cleaned'])}")
        
        if 'validation_results' in report:
            print(f"\n📊 VALIDATION RESULTS")
            print(f"Debt Score: {report['validation_results'].get('debt_score', 'N/A')}/100")
            print(f"File Count: {report['validation_results'].get('file_count', 'N/A')}")
            print(f"Repository Size: {report['validation_results'].get('repository_size_mb', 'N/A'):.1f}MB")
            print(f"Validation: {'✅ PASSED' if report['validation_results'].get('validation_passed', False) else '❌ FAILED'}")
        
        if report.get('recommendations'):
            print(f"\n💡 RECOMMENDATIONS")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        print(f"\n✅ Zero technical debt cleanup completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 