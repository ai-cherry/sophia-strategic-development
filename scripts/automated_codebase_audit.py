#!/usr/bin/env python3
"""
🔍 AUTOMATED CODEBASE AUDIT SCRIPT
Implements key patterns from the comprehensive audit prompt for immediate cleanup opportunities.

Usage: python scripts/automated_codebase_audit.py [--mode=scan|report|safe-cleanup]
"""

import os
import re
import ast
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json

@dataclass
class AuditResult:
    unused_files: List[str]
    duplicate_files: List[Tuple[str, str]]
    empty_files: List[str]
    large_files: List[Tuple[str, int]]
    backup_files: List[str]
    dead_imports: Dict[str, List[str]]
    orphaned_scripts: List[str]
    consolidation_opportunities: List[Dict]

class CodebaseAuditor:
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.ignore_patterns = {
            ".git", "__pycache__", ".pytest_cache", "node_modules", 
            ".venv", "venv", ".mypy_cache", ".ruff_cache", "dist", "build"
        }
        self.safe_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".json", ".yaml", ".yml"}
    
    def scan_for_backup_files(self) -> List[str]:
        """Find obvious backup and temporary files"""
        backup_patterns = [
            r".*\.backup$", r".*\.bak$", r".*\.old$", r".*_backup\..*$",
            r".*\.tmp$", r".*\.temp$", r"temp_.*", r".*~$", r".*\.swp$"
        ]
        
        backup_files = []
        for pattern in backup_patterns:
            for file_path in self.repo_root.rglob("*"):
                if any(ignore in file_path.parts for ignore in self.ignore_patterns):
                    continue
                if re.match(pattern, file_path.name):
                    backup_files.append(str(file_path))
        
        return sorted(backup_files)
    
    def find_empty_files(self) -> List[str]:
        """Find files that are empty or contain only whitespace/comments"""
        empty_files = []
        
        for file_path in self.repo_root.rglob("*"):
            if any(ignore in file_path.parts for ignore in self.ignore_patterns):
                continue
            
            if file_path.is_file() and file_path.suffix in self.safe_extensions:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore').strip()
                    if not content or self._is_only_comments_and_imports(content, file_path.suffix):
                        empty_files.append(str(file_path))
                except Exception:
                    continue
        
        return sorted(empty_files)
    
    def _is_only_comments_and_imports(self, content: str, suffix: str) -> bool:
        """Check if file contains only comments and imports"""
        if suffix == ".py":
            try:
                tree = ast.parse(content)
                # Only imports and constants, no functions/classes
                for node in tree.body:
                    if not isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign)):
                        return False
                return True
            except:
                return False
        
        # For other files, check if only comments/empty lines
        lines = [line.strip() for line in content.split('\n')]
        non_empty_lines = [line for line in lines if line]
        
        if suffix in [".js", ".jsx", ".ts", ".tsx"]:
            comment_patterns = [r"^//", r"^/\*", r"^\*", r"^\*/", r"^import ", r"^export "]
        elif suffix == ".md":
            return len(non_empty_lines) < 3  # Very short markdown files
        else:
            comment_patterns = [r"^#", r"^<!--", r"^-->"]
        
        for line in non_empty_lines:
            if not any(re.match(pattern, line) for pattern in comment_patterns):
                return False
        
        return True
    
    def find_duplicate_files(self) -> List[Tuple[str, str]]:
        """Find files with identical content"""
        file_hashes = defaultdict(list)
        duplicates = []
        
        for file_path in self.repo_root.rglob("*"):
            if any(ignore in file_path.parts for ignore in self.ignore_patterns):
                continue
            
            if file_path.is_file() and file_path.suffix in self.safe_extensions:
                try:
                    content = file_path.read_bytes()
                    if len(content) > 100:  # Only check files with substantial content
                        file_hash = hashlib.md5(content).hexdigest()
                        file_hashes[file_hash].append(str(file_path))
                except Exception:
                    continue
        
        for files in file_hashes.values():
            if len(files) > 1:
                for i in range(len(files)):
                    for j in range(i + 1, len(files)):
                        duplicates.append((files[i], files[j]))
        
        return duplicates
    
    def find_large_files(self, size_mb: int = 10) -> List[Tuple[str, int]]:
        """Find unusually large files that might be artifacts"""
        large_files = []
        size_bytes = size_mb * 1024 * 1024
        
        for file_path in self.repo_root.rglob("*"):
            if any(ignore in file_path.parts for ignore in self.ignore_patterns):
                continue
            
            if file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    if file_size > size_bytes:
                        large_files.append((str(file_path), file_size))
                except Exception:
                    continue
        
        return sorted(large_files, key=lambda x: x[1], reverse=True)
    
    def find_orphaned_scripts(self) -> List[str]:
        """Find scripts that aren't referenced anywhere"""
        scripts_dir = self.repo_root / "scripts"
        if not scripts_dir.exists():
            return []
        
        orphaned = []
        
        for script_path in scripts_dir.rglob("*.sh"):
            script_name = script_path.name
            
            # Search for references to this script
            try:
                result = subprocess.run([
                    "grep", "-r", script_name, str(self.repo_root),
                    "--exclude-dir=.git", "--exclude-dir=scripts"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:  # No matches found
                    orphaned.append(str(script_path))
            except Exception:
                continue
        
        return sorted(orphaned)
    
    def analyze_dead_python_imports(self) -> Dict[str, List[str]]:
        """Find unused imports in Python files"""
        dead_imports = {}
        
        for py_file in self.repo_root.rglob("*.py"):
            if any(ignore in py_file.parts for ignore in self.ignore_patterns):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                imports = set()
                
                # Collect all imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
                        for alias in node.names:
                            imports.add(alias.name)
                
                # Check which imports are actually used
                unused = []
                for imp in imports:
                    if imp not in content or content.count(imp) <= 1:  # Only in import line
                        unused.append(imp)
                
                if unused:
                    dead_imports[str(py_file)] = unused
                    
            except Exception:
                continue
        
        return dead_imports
    
    def find_consolidation_opportunities(self) -> List[Dict]:
        """Find files that could be consolidated"""
        opportunities = []
        
        # Find multiple similar named files
        file_groups = defaultdict(list)
        
        for file_path in self.repo_root.rglob("*"):
            if any(ignore in file_path.parts for ignore in self.ignore_patterns):
                continue
            
            if file_path.is_file():
                # Group by similar names (removing numbers, suffixes)
                base_name = re.sub(r'[_-]?\d+[_-]?', '', file_path.stem.lower())
                base_name = re.sub(r'[_-]?(v\d+|new|old|backup|temp|copy)[_-]?', '', base_name)
                
                if len(base_name) > 3:  # Avoid grouping very short names
                    file_groups[base_name].append(str(file_path))
        
        # Find groups with multiple files
        for base_name, files in file_groups.items():
            if len(files) > 2:
                opportunities.append({
                    "type": "similar_names",
                    "base_name": base_name,
                    "files": files,
                    "suggestion": f"Review if {len(files)} files with similar names can be consolidated"
                })
        
        return opportunities
    
    def run_comprehensive_audit(self) -> AuditResult:
        """Run all audit checks"""
        print("🔍 Starting comprehensive codebase audit...")
        
        print("📁 Scanning for backup files...")
        backup_files = self.scan_for_backup_files()
        
        print("📄 Finding empty files...")
        empty_files = self.find_empty_files()
        
        print("🔍 Detecting duplicate files...")
        duplicate_files = self.find_duplicate_files()
        
        print("📊 Checking for large files...")
        large_files = self.find_large_files()
        
        print("🔗 Finding orphaned scripts...")
        orphaned_scripts = self.find_orphaned_scripts()
        
        print("🐍 Analyzing Python imports...")
        dead_imports = self.analyze_dead_python_imports()
        
        print("🔄 Finding consolidation opportunities...")
        consolidation_opportunities = self.find_consolidation_opportunities()
        
        return AuditResult(
            unused_files=[],  # Would need deeper analysis
            duplicate_files=duplicate_files,
            empty_files=empty_files,
            large_files=large_files,
            backup_files=backup_files,
            dead_imports=dead_imports,
            orphaned_scripts=orphaned_scripts,
            consolidation_opportunities=consolidation_opportunities
        )
    
    def generate_report(self, results: AuditResult) -> str:
        """Generate comprehensive audit report"""
        report = []
        report.append("# 🔍 CODEBASE AUDIT REPORT")
        report.append(f"**Generated**: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}")
        report.append("")
        
        # Immediate deletion candidates
        report.append("## 🗑️ IMMEDIATE DELETION CANDIDATES")
        report.append("")
        
        if results.backup_files:
            report.append("### Backup/Temporary Files:")
            for file in results.backup_files[:20]:  # Limit output
                report.append(f"- [ ] `{file}` - Backup/temporary file")
            if len(results.backup_files) > 20:
                report.append(f"- ... and {len(results.backup_files) - 20} more backup files")
            report.append("")
        
        if results.empty_files:
            report.append("### Empty/Minimal Files:")
            for file in results.empty_files[:15]:
                report.append(f"- [ ] `{file}` - Empty or minimal content")
            if len(results.empty_files) > 15:
                report.append(f"- ... and {len(results.empty_files) - 15} more empty files")
            report.append("")
        
        # Duplicate files
        if results.duplicate_files:
            report.append("## 🔄 DUPLICATE FILES")
            report.append("")
            for file1, file2 in results.duplicate_files[:10]:
                report.append(f"- [ ] **Duplicate**: `{file1}` ↔ `{file2}`")
            if len(results.duplicate_files) > 10:
                report.append(f"- ... and {len(results.duplicate_files) - 10} more duplicate pairs")
            report.append("")
        
        # Large files
        if results.large_files:
            report.append("## 📊 LARGE FILES (Potential Artifacts)")
            report.append("")
            for file, size in results.large_files[:10]:
                size_mb = size / (1024 * 1024)
                report.append(f"- [ ] `{file}` - {size_mb:.1f} MB")
            report.append("")
        
        # Dead imports
        if results.dead_imports:
            report.append("## 🐍 PYTHON FILES WITH UNUSED IMPORTS")
            report.append("")
            for file, imports in list(results.dead_imports.items())[:10]:
                report.append(f"- [ ] `{file}` - Unused: {', '.join(imports[:5])}")
            if len(results.dead_imports) > 10:
                report.append(f"- ... and {len(results.dead_imports) - 10} more files with unused imports")
            report.append("")
        
        # Orphaned scripts
        if results.orphaned_scripts:
            report.append("## 📜 ORPHANED SCRIPTS")
            report.append("")
            for script in results.orphaned_scripts:
                report.append(f"- [ ] `{script}` - No references found")
            report.append("")
        
        # Consolidation opportunities
        if results.consolidation_opportunities:
            report.append("## 🔄 CONSOLIDATION OPPORTUNITIES")
            report.append("")
            for opp in results.consolidation_opportunities[:5]:
                report.append(f"- [ ] **{opp['base_name']}**: {len(opp['files'])} files")
                report.append(f"  - {opp['suggestion']}")
                for file in opp['files'][:3]:
                    report.append(f"    - `{file}`")
                if len(opp['files']) > 3:
                    report.append(f"    - ... and {len(opp['files']) - 3} more")
                report.append("")
        
        # Summary
        total_issues = (
            len(results.backup_files) + len(results.empty_files) + 
            len(results.duplicate_files) + len(results.orphaned_scripts)
        )
        
        report.append("## 📈 AUDIT SUMMARY")
        report.append("")
        report.append(f"- **Backup/temp files**: {len(results.backup_files)}")
        report.append(f"- **Empty files**: {len(results.empty_files)}")
        report.append(f"- **Duplicate file pairs**: {len(results.duplicate_files)}")
        report.append(f"- **Large files**: {len(results.large_files)}")
        report.append(f"- **Files with dead imports**: {len(results.dead_imports)}")
        report.append(f"- **Orphaned scripts**: {len(results.orphaned_scripts)}")
        report.append(f"- **Consolidation opportunities**: {len(results.consolidation_opportunities)}")
        report.append("")
        report.append(f"**Total cleanup opportunities**: {total_issues}")
        
        # Estimated impact
        backup_size = sum(
            Path(f).stat().st_size for f in results.backup_files 
            if Path(f).exists()
        ) / (1024 * 1024)
        
        report.append("")
        report.append(f"**Estimated space savings**: {backup_size:.1f} MB from backup files alone")
        
        return "\n".join(report)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated codebase audit")
    parser.add_argument("--mode", choices=["scan", "report", "safe-cleanup"], 
                       default="report", help="Audit mode")
    parser.add_argument("--output", default="CODEBASE_AUDIT_REPORT.md", 
                       help="Output file for report")
    
    args = parser.parse_args()
    
    auditor = CodebaseAuditor()
    results = auditor.run_comprehensive_audit()
    
    if args.mode in ["scan", "report"]:
        report = auditor.generate_report(results)
        
        with open(args.output, 'w') as f:
            f.write(report)
        
        print(f"✅ Audit complete! Report saved to {args.output}")
        
        # Print summary
        total_issues = (
            len(results.backup_files) + len(results.empty_files) + 
            len(results.duplicate_files) + len(results.orphaned_scripts)
        )
        print(f"🔍 Found {total_issues} cleanup opportunities")
        print(f"📊 {len(results.backup_files)} backup files can be safely deleted")
        print(f"📄 {len(results.empty_files)} empty/minimal files found")
        print(f"🔄 {len(results.duplicate_files)} duplicate file pairs detected")
    
    elif args.mode == "safe-cleanup":
        print("🧹 Safe cleanup mode - removing obvious artifacts...")
        
        # Only delete obvious backup files
        safe_patterns = [r".*\.backup$", r".*\.bak$", r".*\.tmp$", r".*~$"]
        deleted_count = 0
        
        for backup_file in results.backup_files:
            file_path = Path(backup_file)
            if any(re.match(pattern, file_path.name) for pattern in safe_patterns):
                try:
                    if file_path.exists():
                        file_path.unlink()
                        deleted_count += 1
                        print(f"🗑️ Deleted: {backup_file}")
                except Exception as e:
                    print(f"❌ Failed to delete {backup_file}: {e}")
        
        print(f"✅ Safe cleanup complete! Deleted {deleted_count} obvious backup files")

if __name__ == "__main__":
    main() 