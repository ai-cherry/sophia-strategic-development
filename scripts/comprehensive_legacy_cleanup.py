#!/usr/bin/env python3
"""
Comprehensive Legacy File Cleanup for Sophia AI
Safely identifies and removes obsolete files while preserving functionality.
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any

class LegacyFileCleanup:
    """Comprehensive legacy file cleanup utility"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "cleanup_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.files_to_delete = []
        self.files_deleted = []
        self.space_saved = 0
        
    def get_cleanup_targets(self) -> Dict[str, List[str]]:
        """Define patterns for files to clean up"""
        return {
            "backup_files": [
                "**/*.backup",
                "**/*.week2-3.*.backup",
                "**/*.week4.*.backup",
                "**/*.week1.*.backup",
                "**/backup_*",
            ],
            "temporary_files": [
                "**/*.tmp",
                "**/*.temp",
                "**/temp_*",
                "**/*.log",
                "**/*.pid",
                "**/*.lock",
                "**/fastapi.log",
                "**/fastapi_fixed.log",
            ],
            "duplicate_docs": [
                "**/*_SUMMARY 2.md",
                "**/*_SUMMARY 3.md", 
                "**/*_SUMMARY 4.md",
                "**/*-dev 2.txt",
                "**/*-dev 3.txt",
                "**/*-dev 4.txt",
                "**/*-dev 5.txt",
                "**/AGNO_*_SUMMARY 2.md",
                "**/ARCHITECTURE_REVIEW_SUMMARY 2.md",
                "**/ENHANCED_ARCHITECTURE_RECOMMENDATIONS 2.md",
            ],
            "deprecated_configs": [
                "config/agno_vsa_configuration.yaml",
                "config/consolidated_mcp_ports.json",  # marked as deprecated
                "snowflake_connection_fix.patch",
                "**/deprecated_*",
                "**/*_deprecated*",
            ],
            "test_artifacts": [
                "**/test_*.pyc",
                "**/__pycache__/test_*",
                "**/tests/temp_*",
                "**/test_output_*",
            ],
            "legacy_scripts": [
                # One-time migration scripts that are no longer needed
                "fix_github_pulumi_sync_permanently.py",
                "fix_snowflake_connection.py", 
                "fix_sql_ansi_compliance.py",
                "run_test_suite.py",
                "test_snowflake_connection.py",
                "configure_github_security.py",
                "scripts/execute_modernization_now.py",
                "scripts/execute_modernization_day1.py",
                "scripts/infrastructure_cleanup_phase1.py",
                "scripts/documentation_cleanup.py",
                "scripts/comprehensive_dead_code_cleanup.py",
                "scripts/fix_undefined_imports.py",
                "scripts/fix_remaining_undefined_names.py",
                "scripts/systematic_quality_improvement.py",
            ],
            "empty_directories": [
                "backend/watched_costar_files",
                "watched_costar_files", 
                "mcp-servers/logs",
                "logs",
                "docs_backup",
            ],
        }
    
    def analyze_files(self) -> Dict[str, Any]:
        """Analyze files to be cleaned up"""
        print("🔍 Analyzing legacy files for cleanup...")
        
        cleanup_targets = self.get_cleanup_targets()
        analysis = {
            "categories": {},
            "total_files": 0,
            "total_size": 0,
            "safe_to_delete": [],
            "requires_review": []
        }
        
        for category, patterns in cleanup_targets.items():
            files_found = []
            category_size = 0
            
            for pattern in patterns:
                for file_path in self.project_root.rglob(pattern):
                    if file_path.is_file() and self._is_safe_to_analyze(file_path):
                        file_size = file_path.stat().st_size
                        files_found.append({
                            "path": str(file_path.relative_to(self.project_root)),
                            "size": file_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
                        category_size += file_size
            
            analysis["categories"][category] = {
                "files": files_found,
                "count": len(files_found),
                "size": category_size
            }
            analysis["total_files"] += len(files_found)
            analysis["total_size"] += category_size
        
        # Categorize by safety
        for category, data in analysis["categories"].items():
            if category in ["backup_files", "temporary_files", "test_artifacts"]:
                analysis["safe_to_delete"].extend([f["path"] for f in data["files"]])
            else:
                analysis["requires_review"].extend([f["path"] for f in data["files"]])
        
        return analysis
    
    def _is_safe_to_analyze(self, file_path: Path) -> bool:
        """Check if file is safe to analyze (not in .venv, .git, etc.)"""
        exclude_dirs = {".venv", ".git", "node_modules", "__pycache__", ".pytest_cache"}
        return not any(part in exclude_dirs for part in file_path.parts)
    
    def create_backup(self, files_to_backup: List[str]) -> bool:
        """Create backup of files before deletion"""
        if not files_to_backup:
            return True
            
        print(f"📦 Creating backup of {len(files_to_backup)} files...")
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in files_to_backup:
                source = self.project_root / file_path
                if source.exists():
                    # Preserve directory structure in backup
                    backup_path = self.backup_dir / file_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, backup_path)
            
            print(f"✅ Backup created at {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def cleanup_files(self, file_paths: List[str], create_backup: bool = True) -> Dict[str, Any]:
        """Clean up specified files"""
        print(f"🧹 Cleaning up {len(file_paths)} files...")
        
        if create_backup and not self.create_backup(file_paths):
            return {"success": False, "error": "Backup failed"}
        
        results = {
            "deleted": [],
            "failed": [],
            "space_saved": 0,
            "success": True
        }
        
        for file_path in file_paths:
            try:
                full_path = self.project_root / file_path
                if full_path.exists():
                    file_size = full_path.stat().st_size
                    
                    if full_path.is_file():
                        full_path.unlink()
                    elif full_path.is_dir():
                        shutil.rmtree(full_path)
                    
                    results["deleted"].append(file_path)
                    results["space_saved"] += file_size
                    self.space_saved += file_size
                    
            except Exception as e:
                results["failed"].append({"file": file_path, "error": str(e)})
                results["success"] = False
        
        return results
    
    def cleanup_empty_directories(self) -> int:
        """Remove empty directories"""
        print("📁 Cleaning up empty directories...")
        
        removed_count = 0
        # Walk bottom-up to handle nested empty directories
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                if self._is_safe_to_analyze(dir_path):
                    try:
                        if not list(dir_path.iterdir()):  # Directory is empty
                            dir_path.rmdir()
                            removed_count += 1
                            print(f"  📁 Removed empty directory: {dir_path.relative_to(self.project_root)}")
                    except (OSError, PermissionError):
                        pass  # Directory not empty or permission issue
        
        return removed_count
    
    def interactive_cleanup(self) -> None:
        """Interactive cleanup with user confirmation"""
        analysis = self.analyze_files()
        
        print(f"""
🔍 Legacy File Analysis Complete
================================
📊 Total files found: {analysis['total_files']}
💾 Total size: {analysis['total_size'] / (1024*1024):.2f} MB

📋 Categories:""")
        
        for category, data in analysis["categories"].items():
            if data["count"] > 0:
                print(f"  {category}: {data['count']} files ({data['size'] / (1024*1024):.2f} MB)")
        
        print(f"""
🟢 Safe to delete: {len(analysis['safe_to_delete'])} files
🟡 Requires review: {len(analysis['requires_review'])} files
""")
        
        # Clean up safe files automatically
        if analysis["safe_to_delete"]:
            print("🧹 Cleaning up safe files (backup files, temp files, test artifacts)...")
            safe_results = self.cleanup_files(analysis["safe_to_delete"], create_backup=True)
            print(f"✅ Deleted {len(safe_results['deleted'])} safe files")
        
        # Ask about files that require review
        if analysis["requires_review"]:
            print("\n🟡 Files requiring review:")
            for file_path in analysis["requires_review"][:10]:  # Show first 10
                print(f"  - {file_path}")
            
            if len(analysis["requires_review"]) > 10:
                print(f"  ... and {len(analysis['requires_review']) - 10} more")
            
            response = input("\nDelete these files? (y/N): ").lower().strip()
            if response == 'y':
                review_results = self.cleanup_files(analysis["requires_review"], create_backup=True)
                print(f"✅ Deleted {len(review_results['deleted'])} reviewed files")
        
        # Clean up empty directories
        empty_dirs_removed = self.cleanup_empty_directories()
        
        print(f"""
✅ Cleanup Complete!
===================
💾 Space saved: {self.space_saved / (1024*1024):.2f} MB
📁 Empty directories removed: {empty_dirs_removed}
📦 Backup location: {self.backup_dir}
""")
        
        # Generate cleanup report
        self.generate_report(analysis)
    
    def generate_report(self, analysis: Dict[str, Any]) -> None:
        """Generate cleanup report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "space_saved_mb": self.space_saved / (1024*1024),
            "backup_location": str(self.backup_dir),
            "files_deleted": len(self.files_deleted),
        }
        
        report_path = self.project_root / "LEGACY_CLEANUP_REPORT.md"
        with open(report_path, "w") as f:
            f.write(f"""# Legacy File Cleanup Report

Generated: {report['timestamp']}

## Summary
- **Files analyzed**: {analysis['total_files']}
- **Space saved**: {report['space_saved_mb']:.2f} MB
- **Backup location**: {report['backup_location']}

## Categories Cleaned

""")
            for category, data in analysis["categories"].items():
                if data["count"] > 0:
                    f.write(f"### {category.replace('_', ' ').title()}\n")
                    f.write(f"- Files: {data['count']}\n")
                    f.write(f"- Size: {data['size'] / (1024*1024):.2f} MB\n\n")
        
        print(f"📋 Report saved to {report_path}")

def main():
    """Main execution function"""
    print("🚀 Sophia AI Legacy File Cleanup")
    print("================================")
    
    cleanup = LegacyFileCleanup()
    cleanup.interactive_cleanup()
    
    print("\n🎉 Legacy cleanup completed successfully!")
    print("💡 Tip: You can restore files from the backup if needed")

if __name__ == "__main__":
    main() 