#!/usr/bin/env python3
"""
Systematic Fix for Docstring Corruption in Sophia AI Codebase

This script fixes the systematic corruption where docstrings are malformed
and code immediately follows them without proper line breaks.

Pattern: '''docstring text.'''code_immediately_following
Should be: '''docstring text.'''
           code_properly_separated
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocstringCorruptionFixer:
    """Fixes systematic docstring corruption across Python files."""
    
    def __init__(self, root_dir: str = "backend"):
        self.root_dir = Path(root_dir)
        self.patterns = [
            # Pattern 1: """docstring."""code
            (r'("""[^"]*""")\s*([A-Za-z_][A-Za-z0-9_]*\s*[=:])', r'\1\n        \2'),
            
            # Pattern 2: """docstring."""try:
            (r'("""[^"]*""")\s*(try:)', r'\1\n        \2'),
            
            # Pattern 3: """docstring."""if 
            (r'("""[^"]*""")\s*(if\s+)', r'\1\n        \2'),
            
            # Pattern 4: """docstring."""return
            (r'("""[^"]*""")\s*(return\s+)', r'\1\n        \2'),
            
            # Pattern 5: """docstring."""async def
            (r'("""[^"]*""")\s*(async def)', r'\1\n    \2'),
            
            # Pattern 6: """docstring."""def
            (r'("""[^"]*""")\s*(def\s+)', r'\1\n    \2'),
            
            # Pattern 7: """docstring."""class
            (r'("""[^"]*""")\s*(class\s+)', r'\1\n\n\nclass '),
            
            # Pattern 8: """docstring."""# comment
            (r'("""[^"]*""")\s*(#[^\n]*)', r'\1\n        \2'),
            
            # Pattern 9: Handle malformed enum values like ACTIVE = "active".
            (r'(\w+)\s*=\s*"([^"]+)"\s*\.', r'\1 = "\2"'),
            
            # Pattern 10: Fix malformed cursor execute calls
            (r'(cursor\.execute\([^)]+)\s*\.\s*', r'\1'),
        ]
        
        self.files_processed = 0
        self.files_modified = 0
        self.total_fixes = 0

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the backend directory."""
        python_files = []
        for root, dirs, files in os.walk(self.root_dir):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files

    def fix_file(self, file_path: Path) -> Tuple[bool, int]:
        """Fix docstring corruption in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return False, 0

        modified_content = original_content
        fixes_made = 0

        # Apply each pattern fix
        for pattern, replacement in self.patterns:
            new_content = re.sub(pattern, replacement, modified_content, flags=re.MULTILINE)
            if new_content != modified_content:
                fixes_count = len(re.findall(pattern, modified_content, flags=re.MULTILINE))
                fixes_made += fixes_count
                modified_content = new_content
                logger.debug(f"Applied pattern '{pattern}' to {file_path}: {fixes_count} fixes")

        # Additional custom fixes for specific patterns
        modified_content = self._apply_custom_fixes(modified_content, file_path)

        if modified_content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                logger.info(f"Fixed {file_path}: {fixes_made} corrections")
                return True, fixes_made
            except Exception as e:
                logger.error(f"Error writing to {file_path}: {e}")
                return False, 0
        
        return False, 0

    def _apply_custom_fixes(self, content: str, file_path: Path) -> str:
        """Apply custom fixes for specific file patterns."""
        
        # Fix dataclass field definitions that got corrupted
        if '@dataclass' in content:
            # Fix corrupted dataclass fields like: id: str.
            content = re.sub(r'^(\s+)(\w+):\s*(\w+)\s*\.\s*$', r'\1\2: \3', content, flags=re.MULTILINE)
        
        # Fix method definitions that got corrupted
        content = re.sub(r'(async def \w+\([^)]*\))\s*\.\s*"""([^"]+)"""', r'\1:\n        """\2"""', content)
        content = re.sub(r'(def \w+\([^)]*\))\s*\.\s*"""([^"]+)"""', r'\1:\n        """\2"""', content)
        
        # Fix SQL query corruption
        content = re.sub(r'(""")\s*cursor\.execute\(query,', r'\1\n            cursor.execute(query,', content)
        
        # Fix import statements that might have gotten corrupted
        content = re.sub(r'("""[^"]*""")\s*(import\s+)', r'\1\n\n\2', content)
        content = re.sub(r'("""[^"]*""")\s*(from\s+)', r'\1\n\n\2', content)
        
        return content

    def validate_syntax(self, file_path: Path) -> bool:
        """Validate that the fixed file has valid Python syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            compile(content, str(file_path), 'exec')
            return True
        except SyntaxError as e:
            logger.warning(f"Syntax error remains in {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")
            return False

    def fix_all_files(self) -> dict:
        """Fix docstring corruption in all Python files."""
        python_files = self.find_python_files()
        logger.info(f"Found {len(python_files)} Python files to process")
        
        syntax_errors = []
        
        for file_path in python_files:
            self.files_processed += 1
            
            was_modified, fixes_count = self.fix_file(file_path)
            if was_modified:
                self.files_modified += 1
                self.total_fixes += fixes_count
                
                # Validate syntax after fixing
                if not self.validate_syntax(file_path):
                    syntax_errors.append(file_path)
        
        results = {
            'files_processed': self.files_processed,
            'files_modified': self.files_modified,
            'total_fixes': self.total_fixes,
            'syntax_errors': syntax_errors
        }
        
        logger.info(f"Processing complete: {self.files_modified}/{self.files_processed} files modified")
        logger.info(f"Total fixes applied: {self.total_fixes}")
        
        if syntax_errors:
            logger.warning(f"Files with remaining syntax errors: {len(syntax_errors)}")
            for file_path in syntax_errors:
                logger.warning(f"  - {file_path}")
        
        return results


def main():
    """Main function to run the docstring corruption fix."""
    fixer = DocstringCorruptionFixer()
    results = fixer.fix_all_files()
    
    print("\n" + "="*60)
    print("DOCSTRING CORRUPTION FIX RESULTS")
    print("="*60)
    print(f"Files processed: {results['files_processed']}")
    print(f"Files modified: {results['files_modified']}")
    print(f"Total fixes applied: {results['total_fixes']}")
    
    if results['syntax_errors']:
        print(f"\nFiles with remaining syntax errors: {len(results['syntax_errors'])}")
        for file_path in results['syntax_errors']:
            print(f"  - {file_path}")
        print("\nThese files may need manual review.")
    else:
        print("\n✅ All files have valid syntax after fixes!")
    
    return len(results['syntax_errors']) == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 