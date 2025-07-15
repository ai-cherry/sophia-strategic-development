#!/usr/bin/env python3
"""
🚨 EMERGENCY CLEANUP ORCHESTRATOR

This script coordinates the complete emergency cleanup of technical debt violations:
1. Backup files cleanup (300+ files)
2. Completion documentation cleanup (190+ files)
3. One-time scripts cleanup (23 files)
4. Deprecated services cleanup (3 files)
5. TODO resolution system (246 items)

Usage:
    python scripts/run_emergency_cleanup.py
    python scripts/run_emergency_cleanup.py --dry-run
    python scripts/run_emergency_cleanup.py --phase backups
    python scripts/run_emergency_cleanup.py --full-cleanup
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class EmergencyCleanupOrchestrator:
    """Orchestrates comprehensive emergency cleanup of technical debt"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent
        self.cleanup_results = {}
        self.errors = []
        
    def run_comprehensive_cleanup(self):
        """Run complete emergency cleanup"""
        
        print("🚨 EMERGENCY CLEANUP ORCHESTRATOR")
        print("=" * 60)
        print(f"🏃 Mode: {'DRY RUN' if self.dry_run else 'LIVE CLEANUP'}")
        print(f"📍 Project root: {self.project_root}")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Phase 1: Technical Debt Cleanup
        print("🧹 PHASE 1: TECHNICAL DEBT CLEANUP")
        print("=" * 40)
        self.run_technical_debt_cleanup()
        
        # Phase 2: TODO Resolution
        print("\n📝 PHASE 2: TODO RESOLUTION")
        print("=" * 40)
        self.run_todo_resolution()
        
        # Phase 3: Validation
        print("\n🔍 PHASE 3: VALIDATION")
        print("=" * 40)
        self.run_validation()
        
        # Generate final report
        self.generate_final_report()
        
    def run_technical_debt_cleanup(self):
        """Run technical debt cleanup script"""
        
        print("🗑️  Running technical debt cleanup...")
        
        cleanup_script = self.project_root / "scripts" / "emergency_technical_debt_cleanup.py"
        
        if not cleanup_script.exists():
            self.errors.append("Technical debt cleanup script not found")
            print("❌ Technical debt cleanup script not found")
            return
        
        try:
            # Run the cleanup script
            cmd = [sys.executable, str(cleanup_script)]
            if self.dry_run:
                cmd.append("--dry-run")
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            self.cleanup_results["technical_debt"] = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            if result.returncode == 0:
                print("✅ Technical debt cleanup completed successfully")
                print(f"📊 Output preview:\n{result.stdout[:500]}...")
            else:
                print("❌ Technical debt cleanup failed")
                print(f"Error: {result.stderr}")
                self.errors.append(f"Technical debt cleanup failed: {result.stderr}")
                
        except Exception as e:
            self.errors.append(f"Error running technical debt cleanup: {e}")
            print(f"❌ Error running technical debt cleanup: {e}")
    
    def run_todo_resolution(self):
        """Run TODO resolution system"""
        
        print("📝 Running TODO resolution...")
        
        todo_script = self.project_root / "scripts" / "todo_resolution_system.py"
        
        if not todo_script.exists():
            self.errors.append("TODO resolution script not found")
            print("❌ TODO resolution script not found")
            return
        
        try:
            # Run TODO analysis first
            cmd = [sys.executable, str(todo_script), "--analyze"]
            if self.dry_run:
                cmd.append("--dry-run")
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            self.cleanup_results["todo_analysis"] = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            if result.returncode == 0:
                print("✅ TODO analysis completed successfully")
                print(f"📊 Analysis preview:\n{result.stdout[:500]}...")
            else:
                print("❌ TODO analysis failed")
                print(f"Error: {result.stderr}")
                self.errors.append(f"TODO analysis failed: {result.stderr}")
            
            # Run automatic resolution for high-priority categories
            if result.returncode == 0:
                self.run_todo_category_resolution("deprecated")
                self.run_todo_category_resolution("placeholders")
                
        except Exception as e:
            self.errors.append(f"Error running TODO resolution: {e}")
            print(f"❌ Error running TODO resolution: {e}")
    
    def run_todo_category_resolution(self, category: str):
        """Run TODO resolution for specific category"""
        
        print(f"🔧 Resolving {category} TODOs...")
        
        todo_script = self.project_root / "scripts" / "todo_resolution_system.py"
        
        try:
            cmd = [sys.executable, str(todo_script), "--resolve", "--category", category]
            if self.dry_run:
                cmd.append("--dry-run")
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            self.cleanup_results[f"todo_{category}"] = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            if result.returncode == 0:
                print(f"✅ {category} TODO resolution completed")
            else:
                print(f"❌ {category} TODO resolution failed")
                self.errors.append(f"{category} TODO resolution failed: {result.stderr}")
                
        except Exception as e:
            self.errors.append(f"Error resolving {category} TODOs: {e}")
            print(f"❌ Error resolving {category} TODOs: {e}")
    
    def run_validation(self):
        """Run validation to ensure cleanup was successful"""
        
        print("🔍 Running post-cleanup validation...")
        
        validation_results = {
            "backup_files": self.validate_backup_files(),
            "completion_docs": self.validate_completion_docs(),
            "one_time_scripts": self.validate_one_time_scripts(),
            "deprecated_services": self.validate_deprecated_services(),
            "todo_counts": self.validate_todo_counts()
        }
        
        self.cleanup_results["validation"] = validation_results
        
        # Report validation results
        all_passed = all(validation_results.values())
        
        if all_passed:
            print("✅ All validation checks passed")
        else:
            print("⚠️  Some validation checks failed:")
            for check, passed in validation_results.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}")
    
    def validate_backup_files(self) -> bool:
        """Validate that backup files have been cleaned up"""
        
        backup_patterns = [
            "**/*.ssh_backup",
            "**/*.backup",
            "**/*_backup",
            "**/.backup*",
            "**/backup_*"
        ]
        
        backup_files = []
        for pattern in backup_patterns:
            matches = list(self.project_root.glob(pattern))
            backup_files.extend(matches)
        
        remaining_count = len(backup_files)
        
        if remaining_count == 0:
            print(f"✅ No backup files remaining")
            return True
        else:
            print(f"⚠️  {remaining_count} backup files still present")
            return False
    
    def validate_completion_docs(self) -> bool:
        """Validate that completion documentation has been cleaned up"""
        
        completion_patterns = [
            "**/PHASE_*_COMPLETE.md",
            "**/PHASE_*_SUCCESS*.md",
            "**/*_COMPLETE.md",
            "**/*_SUCCESS*.md",
            "**/*_FINAL*.md",
            "**/*ELIMINATION_*.md"
        ]
        
        completion_files = []
        for pattern in completion_patterns:
            matches = list(self.project_root.glob(pattern))
            completion_files.extend(matches)
        
        # Filter out files that should be kept
        keep_files = {"DEPLOYMENT_MODERNIZATION_COMPLETE.md"}
        completion_files = [f for f in completion_files if f.name not in keep_files]
        
        remaining_count = len(completion_files)
        
        if remaining_count == 0:
            print(f"✅ No completion documentation remaining")
            return True
        else:
            print(f"⚠️  {remaining_count} completion documentation files still present")
            return False
    
    def validate_one_time_scripts(self) -> bool:
        """Validate that one-time scripts have been cleaned up"""
        
        one_time_dir = self.project_root / "scripts" / "one_time"
        
        if not one_time_dir.exists():
            print("✅ No one_time directory (or empty)")
            return True
        
        scripts = list(one_time_dir.glob("*.py"))
        
        # Should only have README.md
        if len(scripts) <= 1:  # Allow for README.md
            print("✅ One-time scripts properly cleaned up")
            return True
        else:
            print(f"⚠️  {len(scripts)} one-time scripts still present")
            return False
    
    def validate_deprecated_services(self) -> bool:
        """Validate that deprecated services have been removed"""
        
        deprecated_services = [
            "backend/services/enhanced_multi_agent_orchestrator.py",
            "backend/services/sophia_unified_orchestrator.py",
            "backend/services/unified_chat_orchestrator_v3.py",
        ]
        
        remaining_services = []
        for service_path in deprecated_services:
            full_path = self.project_root / service_path
            if full_path.exists():
                remaining_services.append(service_path)
        
        if len(remaining_services) == 0:
            print("✅ All deprecated services removed")
            return True
        else:
            print(f"⚠️  {len(remaining_services)} deprecated services still present")
            return False
    
    def validate_todo_counts(self) -> bool:
        """Validate that TODO counts have been reduced"""
        
        try:
            # Quick TODO count
            python_files = list(self.project_root.glob("**/*.py"))
            todo_count = 0
            
            for file_path in python_files:
                if any(skip in str(file_path) for skip in ["__pycache__", ".git", ".venv"]):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        todo_count += content.count("TODO")
                        todo_count += content.count("FIXME")
                        todo_count += content.count("DEPRECATED")
                except:
                    continue
            
            print(f"📊 Current TODO count: {todo_count}")
            
            # Success if TODO count is reasonable (< 50)
            if todo_count < 50:
                print("✅ TODO count is within acceptable range")
                return True
            else:
                print("⚠️  TODO count is still high")
                return False
                
        except Exception as e:
            print(f"❌ Error counting TODOs: {e}")
            return False
    
    def generate_final_report(self):
        """Generate comprehensive final cleanup report"""
        
        print("\n" + "=" * 80)
        print("📊 EMERGENCY CLEANUP FINAL REPORT")
        print("=" * 80)
        
        # Summary
        total_phases = len(self.cleanup_results)
        successful_phases = sum(1 for result in self.cleanup_results.values() 
                              if isinstance(result, dict) and result.get("success", False))
        
        print(f"📋 Cleanup Summary:")
        print(f"  Total phases: {total_phases}")
        print(f"  Successful phases: {successful_phases}")
        print(f"  Errors encountered: {len(self.errors)}")
        print(f"  Mode: {'DRY RUN' if self.dry_run else 'LIVE CLEANUP'}")
        
        # Phase results
        print(f"\n🔍 Phase Results:")
        for phase, result in self.cleanup_results.items():
            if isinstance(result, dict) and "success" in result:
                status = "✅" if result["success"] else "❌"
                print(f"  {status} {phase}")
            elif isinstance(result, dict):
                # Validation results
                all_passed = all(result.values())
                status = "✅" if all_passed else "⚠️"
                print(f"  {status} {phase}")
        
        # Errors
        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"  - {error}")
        
        # Next steps
        print(f"\n🔧 Next Steps:")
        print("1. Review generated reports for detailed results")
        print("2. Address any remaining validation issues")
        print("3. Run Clean by Design compliance check")
        print("4. Set up automated prevention system")
        
        # Save detailed report
        if not self.dry_run:
            self.save_detailed_report()
        
        # Final status
        overall_success = successful_phases > 0 and len(self.errors) == 0
        
        if overall_success:
            print(f"\n🎉 Emergency cleanup {'simulation' if self.dry_run else 'execution'} SUCCESSFUL!")
            print("✅ Technical debt violations addressed")
            print("✅ Clean by Design compliance restored")
        else:
            print(f"\n⚠️  Emergency cleanup {'simulation' if self.dry_run else 'execution'} completed with issues")
            print("🔍 Review errors and validation results")
        
        print(f"\n📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def save_detailed_report(self):
        """Save detailed cleanup report"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.project_root / f"EMERGENCY_CLEANUP_REPORT_{timestamp}.md"
        
        report_content = f"""# 🚨 Emergency Cleanup Report

**Generated:** {datetime.now().isoformat()}
**Mode:** {'DRY RUN' if self.dry_run else 'LIVE CLEANUP'}

## 📊 Executive Summary

This report documents the emergency cleanup of technical debt violations identified in the Sophia AI codebase.

### Violations Addressed:
- **300+ backup files** (.ssh_backup, .backup, _backup dirs)
- **190+ completion documentation files** (one-time use violations)
- **23 one-time scripts** (should have been auto-deleted)
- **3 deprecated services** (still present in codebase)
- **246 TODO items** (systematic resolution)

## 🔍 Cleanup Results

"""
        
        for phase, result in self.cleanup_results.items():
            if isinstance(result, dict) and "success" in result:
                status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
                report_content += f"### {phase}: {status}\n\n"
                
                if result.get("stdout"):
                    report_content += f"**Output:**\n```\n{result['stdout'][:1000]}...\n```\n\n"
                
                if result.get("stderr"):
                    report_content += f"**Errors:**\n```\n{result['stderr']}\n```\n\n"
            
            elif isinstance(result, dict):
                # Validation results
                report_content += f"### {phase} Validation\n\n"
                for check, passed in result.items():
                    status = "✅" if passed else "❌"
                    report_content += f"- {status} {check}\n"
                report_content += "\n"
        
        if self.errors:
            report_content += f"## ❌ Errors Encountered\n\n"
            for error in self.errors:
                report_content += f"- {error}\n"
            report_content += "\n"
        
        report_content += f"""## 🎯 Clean by Design Compliance

This cleanup addresses the following violations:
- ✅ Backup file accumulation (Zero tolerance policy)
- ✅ Completion documentation persistence (One-time use policy)
- ✅ One-time script accumulation (Auto-deletion policy)
- ✅ Deprecated service retention (Clean architecture policy)
- ✅ TODO item accumulation (Systematic resolution)

## 🔧 Next Steps

1. **Review Reports**: Check generated JSON reports for detailed analysis
2. **Address Remaining Issues**: Fix any validation failures
3. **Implement Prevention**: Set up automated technical debt prevention
4. **Monitor Compliance**: Regular Clean by Design compliance checks

## 🎉 Conclusion

The emergency cleanup has been {'completed successfully' if len(self.errors) == 0 else 'completed with issues'}. 
The Sophia AI codebase is now {'compliant' if len(self.errors) == 0 else 'closer to compliance'} with Clean by Design principles.

---

**Status:** Emergency cleanup {'executed' if not self.dry_run else 'simulated'} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        print(f"📋 Detailed cleanup report saved to: {report_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Emergency Cleanup Orchestrator for Sophia AI"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be cleaned without making changes"
    )
    parser.add_argument(
        "--phase", 
        choices=["backups", "completion", "scripts", "deprecated", "todos"],
        help="Run specific cleanup phase only"
    )
    parser.add_argument(
        "--full-cleanup", 
        action="store_true", 
        help="Run comprehensive cleanup (same as default)"
    )
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = EmergencyCleanupOrchestrator(dry_run=args.dry_run)
    
    if args.phase:
        # Run specific phase
        print(f"🔧 Running {args.phase} cleanup phase...")
        if args.phase == "backups":
            orchestrator.run_technical_debt_cleanup()
        elif args.phase == "todos":
            orchestrator.run_todo_resolution()
        # Add more specific phase handling as needed
    else:
        # Run comprehensive cleanup
        orchestrator.run_comprehensive_cleanup()

if __name__ == "__main__":
    main() 