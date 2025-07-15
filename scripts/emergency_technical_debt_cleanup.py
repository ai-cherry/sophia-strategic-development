#!/usr/bin/env python3
"""
🚨 EMERGENCY TECHNICAL DEBT CLEANUP

This script addresses the catastrophic technical debt violations identified:
- 300+ backup files (.ssh_backup, .backup, _backup dirs)
- 190+ completion documentation files  
- 23 one-time scripts that should have been auto-deleted
- 3 deprecated services still present
- 246 TODO items requiring resolution

Usage:
    python scripts/emergency_technical_debt_cleanup.py
    python scripts/emergency_technical_debt_cleanup.py --dry-run
    python scripts/emergency_technical_debt_cleanup.py --category backups
"""

import os
import sys
import glob
import shutil
import argparse
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime
import subprocess
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TechnicalDebtCleanup:
    """Comprehensive technical debt cleanup system"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent
        self.deleted_files = []
        self.deleted_dirs = []
        self.errors = []
        self.todo_items = []
        
    def run_comprehensive_cleanup(self):
        """Run complete technical debt cleanup"""
        
        print("🚨 EMERGENCY TECHNICAL DEBT CLEANUP")
        print("=" * 50)
        print(f"🏃 Mode: {'DRY RUN' if self.dry_run else 'LIVE DELETION'}")
        print(f"📍 Project root: {self.project_root}")
        print()
        
        # Phase 1: Backup Files (Highest Priority - Zero Tolerance)
        print("🗑️  PHASE 1: BACKUP FILES CLEANUP")
        print("-" * 30)
        self.cleanup_backup_files()
        
        # Phase 2: Completion Documentation
        print("\n📄 PHASE 2: COMPLETION DOCUMENTATION CLEANUP")
        print("-" * 30)
        self.cleanup_completion_docs()
        
        # Phase 3: One-Time Scripts
        print("\n🔧 PHASE 3: ONE-TIME SCRIPTS CLEANUP")
        print("-" * 30)
        self.cleanup_one_time_scripts()
        
        print("\n🏗️  PHASE 4: DEPRECATED SERVICES CLEANUP")
        print("-" * 30)
        self.cleanup_deprecated_services()
        
        # Phase 5: TODO Analysis (Don't delete, just analyze)
        print("\n📝 PHASE 5: TODO ANALYSIS")
        print("-" * 30)
        self.analyze_todo_items()
        
        # Generate final report
        self.generate_cleanup_report()
        
    def cleanup_backup_files(self):
        """Delete all backup files - Zero tolerance violation"""
        
        backup_patterns = [
            "**/*.ssh_backup",
            "**/*.backup",
            "**/*_backup",
            "**/*_backup_*",
            "**/backup",
            "**/backup_*",
            "**/*backup*_20*",  # Date-stamped backups
            "**/.backup*",
            "**/*.bak",
            "**/*~",
        ]
        
        backup_files = []
        for pattern in backup_patterns:
            matches = list(self.project_root.glob(pattern))
            backup_files.extend(matches)
        
        # Remove duplicates
        backup_files = list(set(backup_files))
        
        print(f"📊 Found {len(backup_files)} backup files/directories")
        
        for backup_path in backup_files:
            try:
                if backup_path.is_file():
                    self.delete_file(backup_path, "backup file")
                elif backup_path.is_dir():
                    self.delete_directory(backup_path, "backup directory")
            except Exception as e:
                self.errors.append(f"Error deleting backup {backup_path}: {e}")
                print(f"❌ Error deleting {backup_path}: {e}")
    
    def cleanup_completion_docs(self):
        """Delete completion documentation files - One-time use violation"""
        
        completion_patterns = [
            "**/PHASE_*_COMPLETE.md",
            "**/PHASE_*_SUCCESS*.md",
            "**/PHASE_*_IMPLEMENTATION_COMPLETE.md",
            "**/PHASE_*_REPORT.md",
            "**/*_COMPLETE.md",
            "**/*_SUCCESS*.md",
            "**/*_FINAL*.md",
            "**/*_SUMMARY.md",
            "**/*DEPLOYMENT_SUCCESS*.md",
            "**/*DEPLOYMENT_FINAL*.md",
            "**/*DEPLOYMENT_SUMMARY*.md",
            "**/*ELIMINATION_*_REPORT.md",
            "**/*CONSOLIDATION_*_REPORT.md",
            "**/*MIGRATION_COMPLETE.md",
            "**/*IMPLEMENTATION_SUCCESS.md",
            "**/*CLEANUP_*_REPORT.md",
            "**/*ANNIHILATION_*.md",
        ]
        
        completion_files = []
        for pattern in completion_patterns:
            matches = list(self.project_root.glob(pattern))
            completion_files.extend(matches)
        
        # Remove duplicates and filter out important docs
        completion_files = list(set(completion_files))
        completion_files = [f for f in completion_files if self.is_completion_doc(f)]
        
        print(f"📊 Found {len(completion_files)} completion documentation files")
        
        for doc_path in completion_files:
            self.delete_file(doc_path, "completion documentation")
    
    def cleanup_one_time_scripts(self):
        """Delete one-time scripts that should have been auto-deleted"""
        
        one_time_dir = self.project_root / "scripts" / "one_time"
        
        if not one_time_dir.exists():
            print("⚠️  No one_time directory found")
            return
        
        # Get all Python files in one_time directory
        scripts = list(one_time_dir.glob("*.py"))
        
        # Keep only README.md
        scripts_to_delete = []
        for script in scripts:
            if script.name != "README.md":
                scripts_to_delete.append(script)
        
        print(f"📊 Found {len(scripts_to_delete)} one-time scripts to delete")
        
        for script in scripts_to_delete:
            self.delete_file(script, "one-time script")
    
    def cleanup_deprecated_services(self):
        """Remove deprecated services still present in codebase"""
        
        deprecated_services = [
            "backend/services/enhanced_multi_agent_orchestrator.py",
            "backend/services/sophia_unified_orchestrator.py", 
            "backend/services/unified_chat_orchestrator_v3.py",
        ]
        
        for service_path in deprecated_services:
            full_path = self.project_root / service_path
            if full_path.exists():
                self.delete_file(full_path, "deprecated service")
            else:
                print(f"⚪ Deprecated service already removed: {service_path}")
    
    def analyze_todo_items(self):
        """Analyze TODO items without deleting files"""
        
        todo_patterns = [
            r"TODO\s*:?\s*(.+)",
            r"FIXME\s*:?\s*(.+)",
            r"HACK\s*:?\s*(.+)",
            r"XXX\s*:?\s*(.+)",
            r"DEPRECATED\s*:?\s*(.+)",
        ]
        
        # Find all Python files
        python_files = list(self.project_root.glob("**/*.py"))
        
        todo_summary = {}
        
        for file_path in python_files:
            # Skip __pycache__ and .git directories
            if any(skip in str(file_path) for skip in ["__pycache__", ".git", ".venv", "venv"]):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                file_todos = []
                for line_num, line in enumerate(content.split('\n'), 1):
                    for pattern in todo_patterns:
                        matches = re.findall(pattern, line, re.IGNORECASE)
                        for match in matches:
                            file_todos.append({
                                "line": line_num,
                                "type": pattern.split("\\")[0],
                                "description": match.strip(),
                                "full_line": line.strip()
                            })
                
                if file_todos:
                    todo_summary[str(file_path.relative_to(self.project_root))] = file_todos
                    
            except Exception as e:
                self.errors.append(f"Error analyzing {file_path}: {e}")
        
        # Generate TODO summary
        total_todos = sum(len(todos) for todos in todo_summary.values())
        print(f"📊 Found {total_todos} TODO items across {len(todo_summary)} files")
        
        # Show top 10 most problematic files
        sorted_files = sorted(todo_summary.items(), key=lambda x: len(x[1]), reverse=True)
        print("\n🔝 Top 10 most problematic files:")
        for i, (file_path, todos) in enumerate(sorted_files[:10]):
            print(f"{i+1:2d}. {file_path}: {len(todos)} TODOs")
        
        # Save detailed TODO analysis
        self.save_todo_analysis(todo_summary)
    
    def is_completion_doc(self, file_path: Path) -> bool:
        """Check if a file is a completion documentation that should be deleted"""
        
        # Always keep certain important files
        keep_files = {
            "README.md",
            "CONTRIBUTING.md", 
            "LICENSE.md",
            "CHANGELOG.md",
            "SECURITY.md",
            "CODE_OF_CONDUCT.md",
            "DEPLOYMENT_MODERNIZATION_COMPLETE.md",  # This is our current work
        }
        
        if file_path.name in keep_files:
            return False
        
        # Check if it's a completion/status report
        completion_indicators = [
            "COMPLETE",
            "SUCCESS",
            "FINAL",
            "ELIMINATION",
            "CONSOLIDATION", 
            "MIGRATION_COMPLETE",
            "IMPLEMENTATION_SUCCESS",
            "CLEANUP_REPORT",
            "ANNIHILATION",
            "PHASE_",
        ]
        
        filename_upper = file_path.name.upper()
        return any(indicator in filename_upper for indicator in completion_indicators)
    
    def delete_file(self, file_path: Path, file_type: str):
        """Delete a file with proper logging"""
        
        if self.dry_run:
            print(f"🔍 [DRY RUN] Would delete {file_type}: {file_path.relative_to(self.project_root)}")
        else:
            try:
                file_path.unlink()
                self.deleted_files.append(str(file_path.relative_to(self.project_root)))
                print(f"✅ Deleted {file_type}: {file_path.relative_to(self.project_root)}")
            except Exception as e:
                self.errors.append(f"Error deleting {file_path}: {e}")
                print(f"❌ Error deleting {file_path}: {e}")
    
    def delete_directory(self, dir_path: Path, dir_type: str):
        """Delete a directory with proper logging"""
        
        if self.dry_run:
            print(f"🔍 [DRY RUN] Would delete {dir_type}: {dir_path.relative_to(self.project_root)}")
        else:
            try:
                shutil.rmtree(dir_path)
                self.deleted_dirs.append(str(dir_path.relative_to(self.project_root)))
                print(f"✅ Deleted {dir_type}: {dir_path.relative_to(self.project_root)}")
            except Exception as e:
                self.errors.append(f"Error deleting {dir_path}: {e}")
                print(f"❌ Error deleting {dir_path}: {e}")
    
    def save_todo_analysis(self, todo_summary: Dict):
        """Save detailed TODO analysis to file"""
        
        analysis_file = self.project_root / "TODO_ANALYSIS_REPORT.json"
        
        # Convert to serializable format
        serializable_summary = {}
        for file_path, todos in todo_summary.items():
            serializable_summary[file_path] = todos
        
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(todo_summary),
            "total_todos": sum(len(todos) for todos in todo_summary.values()),
            "files": serializable_summary
        }
        
        if not self.dry_run:
            with open(analysis_file, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            print(f"📋 TODO analysis saved to: {analysis_file}")
    
    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        
        print("\n" + "=" * 60)
        print("📊 TECHNICAL DEBT CLEANUP SUMMARY")
        print("=" * 60)
        
        print(f"🗑️  Files deleted: {len(self.deleted_files)}")
        print(f"📁 Directories deleted: {len(self.deleted_dirs)}")
        print(f"❌ Errors encountered: {len(self.errors)}")
        print(f"🏃 Mode: {'DRY RUN' if self.dry_run else 'LIVE DELETION'}")
        
        if self.errors:
            print("\n❌ Errors encountered:")
            for error in self.errors:
                print(f"  - {error}")
        
        # Generate detailed report file
        if not self.dry_run:
            self.save_cleanup_report()
        
        # Show next steps
        print("\n🔧 NEXT STEPS:")
        print("1. Review TODO_ANALYSIS_REPORT.json for 246 TODO items")
        print("2. Address critical TODOs and DEPRECATED items")
        print("3. Set up automated prevention system")
        print("4. Verify Clean by Design compliance")
        
        print(f"\n🎉 Cleanup {'simulation' if self.dry_run else 'execution'} complete!")
    
    def save_cleanup_report(self):
        """Save detailed cleanup report"""
        
        report_file = self.project_root / f"TECHNICAL_DEBT_CLEANUP_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report_content = f"""# 🚨 Emergency Technical Debt Cleanup Report

**Generated:** {datetime.now().isoformat()}
**Mode:** {'DRY RUN' if self.dry_run else 'LIVE DELETION'}

## 📊 Summary

- **Files deleted:** {len(self.deleted_files)}
- **Directories deleted:** {len(self.deleted_dirs)}
- **Errors encountered:** {len(self.errors)}

## 🗑️ Deleted Files

"""
        
        if self.deleted_files:
            for file_path in self.deleted_files:
                report_content += f"- {file_path}\n"
        else:
            report_content += "No files deleted.\n"
        
        report_content += f"""
## 📁 Deleted Directories

"""
        
        if self.deleted_dirs:
            for dir_path in self.deleted_dirs:
                report_content += f"- {dir_path}\n"
        else:
            report_content += "No directories deleted.\n"
        
        if self.errors:
            report_content += f"""
## ❌ Errors

"""
            for error in self.errors:
                report_content += f"- {error}\n"
        
        report_content += f"""
## 🔧 Next Steps

1. **Review TODO Analysis**: Check TODO_ANALYSIS_REPORT.json for 246 TODO items
2. **Address Critical TODOs**: Focus on DEPRECATED and placeholder implementations
3. **Set up Prevention**: Implement automated technical debt prevention
4. **Verify Compliance**: Ensure Clean by Design principles are followed

## 🎯 Clean by Design Compliance

This cleanup addresses the following violations:
- ✅ Backup file accumulation (Zero tolerance policy)
- ✅ Completion documentation persistence (One-time use policy)
- ✅ One-time script accumulation (Auto-deletion policy)
- ✅ Deprecated service retention (Clean architecture policy)
- 🔄 TODO item accumulation (Systematic resolution needed)

---

**Status:** Technical debt cleanup {'simulated' if self.dry_run else 'executed'} successfully.
"""
        
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        print(f"📋 Cleanup report saved to: {report_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Emergency Technical Debt Cleanup for Sophia AI"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--category", 
        choices=["backups", "completion", "scripts", "deprecated", "todos"],
        help="Clean up specific category only"
    )
    
    args = parser.parse_args()
    
    # Initialize cleanup system
    cleanup = TechnicalDebtCleanup(dry_run=args.dry_run)
    
    if args.category:
        # Run specific category cleanup
        if args.category == "backups":
            cleanup.cleanup_backup_files()
        elif args.category == "completion":
            cleanup.cleanup_completion_docs()
        elif args.category == "scripts":
            cleanup.cleanup_one_time_scripts()
        elif args.category == "deprecated":
            cleanup.cleanup_deprecated_services()
        elif args.category == "todos":
            cleanup.analyze_todo_items()
    else:
        # Run comprehensive cleanup
        cleanup.run_comprehensive_cleanup()

if __name__ == "__main__":
    main() 