#!/usr/bin/env python3
"""
Pre-Push Technical Debt Prevention
Blocks pushes that would introduce technical debt patterns
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple
import re

class PrePushDebtCheck:
    def __init__(self):
        self.issues = []
        self.warnings = []
        
        # Patterns that indicate one-time scripts
        self.one_time_patterns = [
            r'deploy_.*\.py$',
            r'setup_.*\.py$', 
            r'fix_.*\.py$',
            r'test_.*\.py$',
            r'migrate_.*\.py$',
            r'cleanup_.*\.py$',
            r'install_.*\.py$',
            r'update_.*\.py$',
            r'validate_.*\.py$',
            r'verify_.*\.py$',
            r'patch_.*\.py$',
            r'debug_.*\.py$'
        ]
        
        # Backup file patterns
        self.backup_patterns = [
            r'.*\.backup$',
            r'.*\.bak$',
            r'.*\.old$',
            r'.*\.tmp$',
            r'.*\.temp$',
            r'.*\.orig$',
            r'.*~$'
        ]
        
        # Archive directory patterns
        self.archive_patterns = [
            r'archive/',
            r'backup/',
            r'_archived/',
            r'migration_backup/',
            r'/old/',
            r'/deprecated/',
            r'/temp/',
            r'/draft/'
        ]
        
        # Forbidden documentation patterns
        self.forbidden_doc_patterns = [
            r'.*_IMPLEMENTATION_COMPLETE\.md$',
            r'.*_SUCCESS_REPORT\.md$',
            r'.*_FINAL_SUMMARY\.md$',
            r'.*_COMPLETION_REPORT\.md$',
            r'.*_FINAL_REPORT\.md$',
            r'.*_AUDIT_COMPLETE\.md$'
        ]
        
        # Large file threshold (5MB)
        self.large_file_threshold = 5 * 1024 * 1024
    
    def get_staged_files(self) -> List[str]:
        """Get list of staged files"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True, text=True, check=True
            )
            return [f.strip() for f in result.stdout.split('\n') if f.strip()]
        except subprocess.CalledProcessError:
            print("❌ Error: Could not get staged files from git")
            return []
    
    def check_one_time_scripts(self, files: List[str]) -> None:
        """Check for one-time scripts outside proper directory"""
        for file in files:
            # Skip if already in one_time directory
            if file.startswith('scripts/one_time/'):
                continue
            
            # Check if matches one-time pattern
            for pattern in self.one_time_patterns:
                if re.search(pattern, file):
                    self.issues.append(
                        f"One-time script detected: {file}\n"
                        f"  ➤ Move to scripts/one_time/ with deletion date\n"
                        f"  ➤ Example: scripts/one_time/{Path(file).name.replace('.py', '_DELETE_2025_08_15.py')}"
                    )
                    break
    
    def check_backup_files(self, files: List[str]) -> None:
        """Check for backup files"""
        for file in files:
            for pattern in self.backup_patterns:
                if re.search(pattern, file):
                    self.issues.append(
                        f"Backup file detected: {file}\n"
                        f"  ➤ Use git history instead of backup files\n"
                        f"  ➤ Remove this file and commit the change"
                    )
                    break
    
    def check_archive_directories(self, files: List[str]) -> None:
        """Check for archive directory creation"""
        for file in files:
            for pattern in self.archive_patterns:
                if pattern in file.lower():
                    self.issues.append(
                        f"Archive directory detected: {file}\n"
                        f"  ➤ Archive directories are forbidden\n"
                        f"  ➤ Use git branches/tags for historical versions"
                    )
                    break
    
    def check_forbidden_documentation(self, files: List[str]) -> None:
        """Check for forbidden documentation patterns"""
        for file in files:
            if file.endswith('.md'):
                for pattern in self.forbidden_doc_patterns:
                    if re.search(pattern, file, re.IGNORECASE):
                        self.issues.append(
                            f"Forbidden documentation pattern: {file}\n"
                            f"  ➤ Completion/success reports are not allowed\n"
                            f"  ➤ Update existing documentation instead"
                        )
                        break
    
    def check_large_files(self, files: List[str]) -> None:
        """Check for large files"""
        for file in files:
            file_path = Path(file)
            if file_path.exists() and file_path.is_file():
                size = file_path.stat().st_size
                if size > self.large_file_threshold:
                    size_mb = size / (1024 * 1024)
                    self.warnings.append(
                        f"Large file detected: {file} ({size_mb:.1f}MB)\n"
                        f"  ➤ Consider if this file should be in git\n"
                        f"  ➤ Use Git LFS for large binary files"
                    )
    
    def check_script_headers(self, files: List[str]) -> None:
        """Check if one-time scripts have proper headers"""
        for file in files:
            if (file.startswith('scripts/one_time/') and 
                file.endswith('.py') and 
                Path(file).exists()):
                
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read(500)  # Read first 500 chars
                    
                    # Check for deletion date in filename
                    if 'DELETE_' not in file:
                        self.issues.append(
                            f"One-time script missing deletion date: {file}\n"
                            f"  ➤ Add deletion date to filename: {Path(file).stem}_DELETE_2025_08_15.py\n"
                            f"  ➤ Include deletion reminder in script header"
                        )
                    
                    # Check for proper header
                    if 'DELETE AFTER:' not in content and 'DELETE_' in file:
                        self.warnings.append(
                            f"One-time script should include deletion reminder: {file}\n"
                            f"  ➤ Add 'DELETE AFTER: YYYY-MM-DD' in script header"
                        )
                        
                except Exception:
                    pass  # Skip if can't read file
    
    def check_documentation_categories(self, files: List[str]) -> None:
        """Check if documentation is in appropriate categories"""
        for file in files:
            if file.endswith('.md') and file.startswith('docs/'):
                # Check for temporary documentation in permanent directories
                temp_keywords = ['implementation', 'plan', 'strategy', 'migration', 'deployment']
                
                if any(keyword in file.lower() for keyword in temp_keywords):
                    if (file.startswith('docs/99-reference/') or 
                        file.startswith('docs/01-getting-started/')):
                        self.warnings.append(
                            f"Temporary documentation in permanent directory: {file}\n"
                            f"  ➤ Consider if this belongs in docs/implementation/ instead\n"
                            f"  ➤ Permanent docs should not have implementation/plan keywords"
                        )
    
    def run_checks(self) -> Tuple[bool, int, int]:
        """Run all debt prevention checks"""
        print("🔍 Running technical debt prevention checks...")
        
        # Get staged files
        files = self.get_staged_files()
        if not files:
            print("✅ No files staged for commit")
            return True, 0, 0
        
        print(f"📁 Checking {len(files)} staged files...")
        
        # Run all checks
        self.check_one_time_scripts(files)
        self.check_backup_files(files)
        self.check_archive_directories(files)
        self.check_forbidden_documentation(files)
        self.check_large_files(files)
        self.check_script_headers(files)
        self.check_documentation_categories(files)
        
        return len(self.issues) == 0, len(self.issues), len(self.warnings)
    
    def print_results(self) -> None:
        """Print check results"""
        if self.issues:
            print(f"\n❌ Technical debt detected ({len(self.issues)} issues):")
            print("=" * 60)
            for i, issue in enumerate(self.issues, 1):
                print(f"\n{i}. {issue}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            print("=" * 40)
            for i, warning in enumerate(self.warnings, 1):
                print(f"\n{i}. {warning}")
        
        if not self.issues and not self.warnings:
            print("✅ No technical debt detected!")
        
        if self.issues:
            print(f"\n🚨 COMMIT BLOCKED: Fix {len(self.issues)} issues before committing")
            print("\n💡 Quick fixes:")
            print("  • Move one-time scripts to scripts/one_time/ with deletion dates")
            print("  • Remove backup files (use git history instead)")
            print("  • Avoid creating archive directories")
            print("  • Use proper documentation categories")

def main():
    """Main function"""
    checker = PrePushDebtCheck()
    
    # Run checks
    passed, issues, warnings = checker.run_checks()
    
    # Print results
    checker.print_results()
    
    # Print summary
    print(f"\n📊 Summary: {issues} issues, {warnings} warnings")
    
    # Exit with appropriate code
    if not passed:
        print("\n❌ Pre-push check FAILED")
        sys.exit(1)
    else:
        if warnings > 0:
            print(f"\n⚠️  Pre-push check PASSED with {warnings} warnings")
        else:
            print("\n✅ Pre-push check PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main() 