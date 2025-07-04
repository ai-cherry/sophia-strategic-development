#!/usr/bin/env python3
"""
Cleanup references to deprecated tools from documentation
Based on our principle: Only add new tools when there's a clear gap
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Tools that should be removed from documentation
DEPRECATED_TOOLS = {
    "SonarQube": "Use Codacy + pre-commit hooks instead",
    "Airflow": "Use Estuary for all ELT needs",
    "Dagster": "Use Estuary for all ELT needs",
    "Prefect": "Use Estuary for all ELT needs",
    r"\.env": "Use Pulumi ESC for all secrets"
}

# Files to exclude from cleanup
EXCLUDE_FILES = [
    "SOPHIA_AI_TOOLING_REVIEW_ANALYSIS.md",
    "MCP_ENHANCEMENT_ANALYSIS.md",
    "DOCUMENTATION_UPDATE_SUMMARY.md",
    "cleanup_deprecated_tool_references.py"
]

# Directories to search
SEARCH_DIRS = ["docs", "scripts", "backend", "frontend", "mcp-servers"]


class DeprecatedToolCleaner:
    def __init__(self):
        self.changes = []
        self.backup_dir = Path(f"backups/tool_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
    def backup_file(self, file_path: Path):
        """Create backup of file before modification"""
        if not file_path.exists():
            return
            
        backup_path = self.backup_dir / file_path.relative_to(Path.cwd())
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_text(file_path.read_text())
        
    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Skip excluded files
        if file_path.name in EXCLUDE_FILES:
            return False
            
        # Skip binary files
        if file_path.suffix in ['.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe']:
            return False
            
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            return False
            
        return True
        
    def clean_file(self, file_path: Path) -> List[Tuple[str, str]]:
        """Clean deprecated tool references from a file"""
        if not self.should_process_file(file_path):
            return []
            
        try:
            content = file_path.read_text()
            original_content = content
            file_changes = []
            
            # Special handling for different file types
            if file_path.suffix == '.md':
                content = self.clean_markdown(content, file_changes)
            elif file_path.suffix in ['.py', '.yml', '.yaml']:
                content = self.clean_code(content, file_changes)
                
            if content != original_content:
                self.backup_file(file_path)
                file_path.write_text(content)
                self.changes.append((str(file_path), file_changes))
                
            return file_changes
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []
            
    def clean_markdown(self, content: str, changes: List) -> str:
        """Clean markdown files"""
        lines = content.split('\n')
        new_lines = []
        skip_section = False
        
        for i, line in enumerate(lines):
            # Skip SonarQube sections
            if "SonarQube" in line and line.strip().startswith('#'):
                skip_section = True
                changes.append(("Removed section", line.strip()))
                continue
                
            if skip_section and line.strip().startswith('#'):
                skip_section = False
                
            if skip_section:
                continue
                
            # Replace tool mentions with alternatives
            original_line = line
            for tool, replacement in DEPRECATED_TOOLS.items():
                if tool in line and "TOOLING_REVIEW" not in line:
                    if tool == r"\.env":
                        line = re.sub(r'\.env(?:\.\w+)?', 'Pulumi ESC configuration', line)
                    else:
                        line = line.replace(tool, f"[REMOVED: {tool} - {replacement}]")
                        
            if line != original_line:
                changes.append(("Modified line", f"{original_line} -> {line}"))
                
            new_lines.append(line)
            
        return '\n'.join(new_lines)
        
    def clean_code(self, content: str, changes: List) -> str:
        """Clean code files"""
        # Remove .env references in comments
        if '.env' in content:
            content = re.sub(
                r'#.*\.env.*',
                '# Use Pulumi ESC for configuration',
                content
            )
            changes.append(("Replaced .env comments", "Updated to Pulumi ESC"))
            
        # Add deprecation warnings for tool imports
        for tool in ["airflow", "dagster", "prefect"]:
            if f"import {tool}" in content.lower():
                changes.append(("Found deprecated import", tool))
                # Don't modify imports, just log them
                
        return content
        
    def generate_report(self):
        """Generate cleanup report"""
        report_path = self.backup_dir / "cleanup_report.md"
        
        with open(report_path, 'w') as f:
            f.write("# Deprecated Tool Reference Cleanup Report\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Files modified: {len(self.changes)}\n")
            f.write(f"- Backup location: {self.backup_dir}\n\n")
            
            f.write("## Deprecated Tools\n\n")
            for tool, reason in DEPRECATED_TOOLS.items():
                f.write(f"- **{tool}**: {reason}\n")
                
            f.write("\n## Changes by File\n\n")
            for file_path, file_changes in self.changes:
                f.write(f"### {file_path}\n\n")
                for change_type, detail in file_changes:
                    f.write(f"- {change_type}: {detail}\n")
                f.write("\n")
                
        print(f"\n✅ Report generated: {report_path}")
        
    def run(self):
        """Run the cleanup process"""
        print("🧹 Starting deprecated tool reference cleanup...")
        print(f"📁 Creating backups in: {self.backup_dir}")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        for search_dir in SEARCH_DIRS:
            if not Path(search_dir).exists():
                continue
                
            for file_path in Path(search_dir).rglob('*'):
                if file_path.is_file():
                    self.clean_file(file_path)
                    
        if self.changes:
            self.generate_report()
            print(f"\n✅ Cleaned {len(self.changes)} files")
            print("📋 Review the report and backups before committing")
        else:
            print("\n✅ No deprecated tool references found!")
            
        # Provide git commands
        if self.changes:
            print("\n📝 To review changes:")
            print("   git diff")
            print("\n📝 To commit changes:")
            print("   git add -A")
            print('   git commit -m "chore: Remove deprecated tool references"')
            
        print("\n🗑️  After review, you can delete this script:")
        print(f"   rm {__file__}")


def main():
    """Main execution"""
    cleaner = DeprecatedToolCleaner()
    
    print("⚠️  This will modify documentation files!")
    print("   Backups will be created before any changes")
    
    response = input("\nProceed with cleanup? (y/N): ")
    if response.lower() == 'y':
        cleaner.run()
    else:
        print("❌ Cleanup cancelled")


if __name__ == "__main__":
    main() 