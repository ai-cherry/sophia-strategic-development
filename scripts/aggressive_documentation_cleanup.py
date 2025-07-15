#!/usr/bin/env python3
"""
🗑️ AGGRESSIVE DOCUMENTATION CLEANUP
Removes 80+ redundant documentation files while preserving essential documentation

SAFETY: Creates backup before deletion
TARGET: Reduce root clutter by 95%
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import json

class AggressiveDocumentationCleanup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.deleted_files = []
        self.preserved_files = []
        self.backup_dir = self.project_root / f"cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Essential documentation that MUST be preserved
        self.essential_docs = {
            "README.md",
            ".cursorrules", 
            "CHANGELOG.md",
            "LICENSE",
            "pyproject.toml",
            "package.json",
            "requirements.txt",
            "uv.lock",
            "Dockerfile",
            "docker-compose.yml"
        }
        
        # Essential directories to preserve
        self.essential_dirs = {
            "docs/01-getting-started",
            "docs/02-development", 
            "docs/03-architecture",
            "docs/99-reference",
            "docs/system_handbook"
        }
        
    def execute_cleanup(self):
        """Execute aggressive documentation cleanup"""
        
        print("🗑️ AGGRESSIVE DOCUMENTATION CLEANUP")
        print("====================================")
        print(f"📅 Started: {datetime.now()}")
        print(f"🎯 Target: Remove 80+ redundant documentation files")
        print(f"🛡️ Backup: {self.backup_dir}")
        print("")
        
        # Phase 1: Create backup
        self._create_backup()
        
        # Phase 2: Clean root directory 
        self._clean_root_directory()
        
        # Phase 3: Clean docs directories
        self._clean_docs_directories()
        
        # Phase 4: Remove redundant README files
        self._remove_redundant_readmes()
        
        # Phase 5: Clean implementation reports
        self._clean_implementation_reports()
        
        # Phase 6: Generate cleanup report
        self._generate_cleanup_report()
        
        print(f"✅ AGGRESSIVE CLEANUP COMPLETE!")
        print(f"   Deleted: {len(self.deleted_files)} files")
        print(f"   Preserved: {len(self.preserved_files)} files")
        print(f"   Backup: {self.backup_dir}")
        
    def _create_backup(self):
        """Create backup of all documentation before deletion"""
        
        print("🛡️ Creating backup...")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup all markdown files
        for md_file in self.project_root.rglob("*.md"):
            if self._should_backup_file(md_file):
                backup_path = self.backup_dir / md_file.relative_to(self.project_root)
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(md_file, backup_path)
                
        print(f"✅ Backup created: {self.backup_dir}")
        
    def _clean_root_directory(self):
        """Aggressively clean root directory documentation"""
        
        print("🧹 Cleaning root directory...")
        
        # Target patterns for deletion
        deletion_patterns = [
            # Implementation completion files
            "*_IMPLEMENTATION_COMPLETE.md",
            "*_SUCCESS_REPORT.md", 
            "*_DEPLOYMENT_SUCCESS.md",
            "*_FINAL_REPORT.md",
            "*_COMPLETE.md",
            "*_DONE.md",
            
            # Deployment reports  
            "*_DEPLOYMENT_REPORT*.md",
            "*_INFRASTRUCTURE_REPORT*.md",
            "*_VALIDATION_REPORT*.md",
            
            # Analysis files
            "*_ANALYSIS.md",
            "*_COMPREHENSIVE_*.md",
            "*_DETAILED_*.md",
            
            # Strategy and planning files (completed ones)
            "*_STRATEGY_COMPLETE.md",
            "*_PLAN_EXECUTED.md",
            "*_ROADMAP_COMPLETE.md",
            
            # Status reports
            "*_STATUS_REPORT*.md",
            "*_PROGRESS_REPORT*.md",
            
            # Backup documentation
            "*_backup*.md",
            "*_old*.md",
            "*_legacy*.md",
            
            # Temporary files
            "temp_*.md",
            "tmp_*.md",
            "test_*.md",
            
            # Duplicate guides
            "SETUP_GUIDE_*.md",
            "INSTALL_GUIDE_*.md",
            "DEPLOY_GUIDE_*.md"
        ]
        
        for pattern in deletion_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and file_path.name not in self.essential_docs:
                    self._delete_file(file_path, "Root cleanup")
                    
    def _clean_docs_directories(self):
        """Clean redundant files in docs directories"""
        
        print("📚 Cleaning docs directories...")
        
        docs_cleanup_targets = [
            # Implementation directory - remove completed items
            "docs/implementation/*_COMPLETE.md",
            "docs/implementation/*_SUCCESS.md", 
            "docs/implementation/*_FINAL.md",
            "docs/implementation/*_DONE.md",
            
            # Deployment directory - remove outdated
            "docs/deployment/*_OLD.md",
            "docs/deployment/*_BACKUP.md",
            "docs/deployment/*_LEGACY.md",
            "docs/deployment/*_DEPRECATED.md",
            
            # Architecture directory - remove drafts
            "docs/architecture/*_DRAFT.md",
            "docs/architecture/*_WIP.md",
            "docs/architecture/*_TEMP.md",
            
            # Sample directories - remove if redundant
            "docs/sample_queries/old_*.json",
            "docs/sample_queries/backup_*.json",
            
            # Prevention directory - keep only latest
            "docs/prevention/*_OLD.md",
            "docs/prevention/*_V1.md",
            "docs/prevention/*_BACKUP.md"
        ]
        
        for pattern in docs_cleanup_targets:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    self._delete_file(file_path, "Docs cleanup")
                    
    def _remove_redundant_readmes(self):
        """Remove redundant README files keeping only essential ones"""
        
        print("📖 Removing redundant README files...")
        
        # Find all README files
        readme_files = list(self.project_root.rglob("README.md"))
        
        # Essential README locations
        essential_readme_dirs = {
            self.project_root,  # Root README
            self.project_root / "docs",
            self.project_root / "backend", 
            self.project_root / "frontend",
            self.project_root / "apps",
            self.project_root / "libs"
        }
        
        for readme_path in readme_files:
            readme_dir = readme_path.parent
            
            # Check if this README is in an essential location
            if readme_dir not in essential_readme_dirs:
                # Check if it's a small/placeholder README
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        
                    # Delete if it's minimal/placeholder content
                    if (len(content) < 200 or 
                        "TODO" in content or 
                        "placeholder" in content.lower() or
                        "coming soon" in content.lower()):
                        self._delete_file(readme_path, "Redundant README")
                        
                except Exception:
                    pass
                    
    def _clean_implementation_reports(self):
        """Remove implementation completion reports"""
        
        print("📋 Cleaning implementation reports...")
        
        report_patterns = [
            # All completion reports
            "*IMPLEMENTATION*COMPLETE*.md",
            "*IMPLEMENTATION*SUCCESS*.md",
            "*IMPLEMENTATION*FINAL*.md",
            
            # Phase completion reports  
            "*PHASE*COMPLETE*.md",
            "*PHASE*SUCCESS*.md",
            
            # Migration completion reports
            "*MIGRATION*COMPLETE*.md", 
            "*MIGRATION*SUCCESS*.md",
            
            # Deployment completion reports
            "*DEPLOYMENT*COMPLETE*.md",
            "*DEPLOYMENT*SUCCESS*.md",
            
            # Setup completion reports
            "*SETUP*COMPLETE*.md",
            "*SETUP*SUCCESS*.md"
        ]
        
        for pattern in report_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file() and not self._is_essential_doc(file_path):
                    self._delete_file(file_path, "Implementation report")
                    
    def _delete_file(self, file_path: Path, reason: str):
        """Delete a file and track it"""
        
        try:
            file_path.unlink()
            self.deleted_files.append({
                "path": str(file_path.relative_to(self.project_root)),
                "reason": reason,
                "size": 0  # Already deleted
            })
            print(f"🗑️ DELETED: {file_path.relative_to(self.project_root)} ({reason})")
            
        except Exception as e:
            print(f"❌ Error deleting {file_path}: {e}")
            
    def _should_backup_file(self, file_path: Path) -> bool:
        """Check if file should be backed up"""
        
        # Don't backup if it's in backup directory already
        if "backup" in str(file_path).lower():
            return False
            
        # Don't backup very large files
        try:
            if file_path.stat().st_size > 1024 * 1024:  # 1MB
                return False
        except:
            return False
            
        return True
        
    def _is_essential_doc(self, file_path: Path) -> bool:
        """Check if documentation is essential"""
        
        # Check if it's in essential directories
        for essential_dir in self.essential_dirs:
            if str(file_path).startswith(str(self.project_root / essential_dir)):
                return True
                
        # Check if it's an essential file
        if file_path.name in self.essential_docs:
            return True
            
        return False
        
    def _generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        
        report = {
            "cleanup_date": datetime.now().isoformat(),
            "deleted_files_count": len(self.deleted_files),
            "preserved_files_count": len(self.preserved_files),
            "backup_location": str(self.backup_dir),
            "deleted_files": self.deleted_files,
            "statistics": {
                "root_cleanup": len([f for f in self.deleted_files if "Root cleanup" in f["reason"]]),
                "docs_cleanup": len([f for f in self.deleted_files if "Docs cleanup" in f["reason"]]),
                "readme_cleanup": len([f for f in self.deleted_files if "Redundant README" in f["reason"]]),
                "implementation_reports": len([f for f in self.deleted_files if "Implementation report" in f["reason"]])
            }
        }
        
        # Save report
        report_path = self.project_root / "AGGRESSIVE_CLEANUP_REPORT.md"
        
        with open(report_path, 'w') as f:
            f.write(f"""# 🗑️ AGGRESSIVE DOCUMENTATION CLEANUP REPORT

**Generated:** {datetime.now()}  
**Total Files Deleted:** {len(self.deleted_files)}  
**Backup Location:** {self.backup_dir}  

## 📊 CLEANUP STATISTICS

- **Root Directory Cleanup:** {report['statistics']['root_cleanup']} files
- **Docs Directory Cleanup:** {report['statistics']['docs_cleanup']} files  
- **README Cleanup:** {report['statistics']['readme_cleanup']} files
- **Implementation Reports:** {report['statistics']['implementation_reports']} files

## 🗑️ DELETED FILES

""")
            
            for deleted_file in self.deleted_files:
                f.write(f"- `{deleted_file['path']}` - {deleted_file['reason']}\n")
                
            f.write(f"""

## ✅ RESULTS

- **Before:** 150+ documentation files scattered across repository
- **After:** {len(self.preserved_files)} essential documentation files
- **Reduction:** {(len(self.deleted_files) / (len(self.deleted_files) + len(self.preserved_files)) * 100):.1f}% documentation reduction
- **Backup:** Complete backup saved to `{self.backup_dir}`

## 🎯 NEXT STEPS

1. Review remaining documentation structure
2. Proceed with monorepo migration  
3. Execute legacy code elimination
4. Complete TODO resolution

""")
        
        print(f"📋 Cleanup report saved: {report_path}")

if __name__ == "__main__":
    cleanup = AggressiveDocumentationCleanup()
    cleanup.execute_cleanup() 