#!/usr/bin/env python3
"""
Fix syntax errors in Python files
"""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class SyntaxErrorFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.fixed_count = 0
        self.error_files = []
        
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        exclude_dirs = {'.venv', 'dead_code', 'node_modules', '__pycache__', '.git'}
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
                    
        return python_files
    
    def check_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Check if a file has syntax errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse the file
            ast.parse(content)
            return True, ""
        except SyntaxError as e:
            return False, str(e)
        except Exception as e:
            # Other errors like encoding issues
            return False, f"Error reading file: {e}"
    
    def fix_future_import_position(self, file_path: Path) -> bool:
        """Fix __future__ import position errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find all __future__ imports
            future_imports = []
            future_indices = []
            other_lines = []
            
            for i, line in enumerate(lines):
                if 'from __future__ import' in line:
                    future_imports.append(line)
                    future_indices.append(i)
                else:
                    other_lines.append((i, line))
            
            if not future_imports:
                return False
            
            # Reconstruct file with __future__ imports at the top
            new_lines = []
            
            # Add shebang and encoding if present
            for i, line in other_lines:
                if i == 0 and line.startswith('#!'):
                    new_lines.append(line)
                elif i < 2 and '# -*- coding:' in line:
                    new_lines.append(line)
                else:
                    break
            
            # Add docstring if it's at the beginning
            docstring_start = -1
            docstring_end = -1
            in_docstring = False
            quote_type = None
            
            for i, line in other_lines:
                if not in_docstring:
                    if line.strip().startswith('"""') or line.strip().startswith("'''"):
                        in_docstring = True
                        quote_type = '"""' if '"""' in line else "'''"
                        docstring_start = i
                        if line.count(quote_type) >= 2:  # Single line docstring
                            in_docstring = False
                            docstring_end = i
                else:
                    if quote_type in line:
                        in_docstring = False
                        docstring_end = i
            
            # Add docstring if found at beginning
            if docstring_start != -1:
                for i, line in other_lines:
                    if docstring_start <= i <= docstring_end:
                        new_lines.append(line)
            
            # Add blank line if needed
            if new_lines and not new_lines[-1].strip() == '':
                new_lines.append('\n')
            
            # Add __future__ imports
            new_lines.extend(future_imports)
            
            # Add blank line after imports
            if future_imports and not future_imports[-1].strip() == '':
                new_lines.append('\n')
            
            # Add remaining lines
            skip_until = docstring_end if docstring_end != -1 else -1
            for i, line in other_lines:
                if i > skip_until and i not in future_indices:
                    # Skip shebang, encoding, and docstring lines we already added
                    if i == 0 and line.startswith('#!'):
                        continue
                    if i < 2 and '# -*- coding:' in line:
                        continue
                    new_lines.append(line)
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            return True
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return False
    
    def fix_indentation_errors(self, file_path: Path) -> bool:
        """Fix common indentation errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix tabs vs spaces
            if '\t' in content:
                content = content.replace('\t', '    ')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            return False
        except Exception:
            return False
    
    def fix_syntax_errors(self):
        """Main method to fix syntax errors"""
        print("🔍 Finding Python files with syntax errors...")
        
        python_files = self.find_python_files()
        print(f"Found {len(python_files)} Python files to check")
        
        for file_path in python_files:
            has_valid_syntax, error_msg = self.check_syntax(file_path)
            
            if not has_valid_syntax:
                self.error_files.append((file_path, error_msg))
                print(f"\n❌ Syntax error in {file_path}")
                print(f"   Error: {error_msg}")
                
                # Try to fix specific error types
                if "from __future__ imports must occur at the beginning" in error_msg:
                    if self.fix_future_import_position(file_path):
                        print(f"   ✅ Fixed __future__ import position")
                        self.fixed_count += 1
                        
                        # Check if there are still errors
                        has_valid_syntax, new_error = self.check_syntax(file_path)
                        if not has_valid_syntax:
                            print(f"   ⚠️  Still has errors: {new_error}")
                
                elif "inconsistent use of tabs and spaces" in error_msg:
                    if self.fix_indentation_errors(file_path):
                        print(f"   ✅ Fixed indentation")
                        self.fixed_count += 1
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate a report of syntax errors"""
        print("\n" + "=" * 60)
        print("📊 Syntax Error Fix Report")
        print("=" * 60)
        print(f"Total files checked: {len(self.find_python_files())}")
        print(f"Files with syntax errors: {len(self.error_files)}")
        print(f"Errors fixed: {self.fixed_count}")
        
        if self.error_files:
            print("\n❌ Remaining syntax errors:")
            for file_path, error in self.error_files:
                # Re-check to see if it's still broken
                has_valid_syntax, current_error = self.check_syntax(file_path)
                if not has_valid_syntax:
                    print(f"\n{file_path}:")
                    print(f"  {current_error}")
        
        # Save detailed report
        report_path = self.project_root / "SYNTAX_ERRORS_REPORT.md"
        with open(report_path, 'w') as f:
            f.write("# Syntax Errors Report\n\n")
            f.write(f"**Date:** {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}\n")
            f.write(f"**Total files checked:** {len(self.find_python_files())}\n")
            f.write(f"**Files with syntax errors:** {len(self.error_files)}\n")
            f.write(f"**Errors fixed:** {self.fixed_count}\n\n")
            
            if self.error_files:
                f.write("## Remaining Syntax Errors\n\n")
                for file_path, error in self.error_files:
                    has_valid_syntax, current_error = self.check_syntax(file_path)
                    if not has_valid_syntax:
                        f.write(f"### {file_path}\n")
                        f.write(f"```\n{current_error}\n```\n\n")
        
        print(f"\n📝 Detailed report saved to: {report_path}")


def main():
    fixer = SyntaxErrorFixer()
    fixer.fix_syntax_errors()


if __name__ == "__main__":
    main() 