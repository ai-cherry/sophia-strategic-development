#!/usr/bin/env python3
"""
Aggressive syntax fixer that targets all common syntax errors.
This script is more comprehensive and handles edge cases better.
"""

import json
import re
from pathlib import Path
from typing import List, Tuple

def fix_file_aggressively(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix syntax errors aggressively in a file."""
    fixes = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: Fix all instances of ":." anywhere
        content = re.sub(r':\.(\s|$)', r':\1', content, flags=re.MULTILINE)
        
        # Pattern 2: Fix all instances of ")." at end of lines
        content = re.sub(r'\)\.\s*$', ')', content, flags=re.MULTILINE)
        
        # Pattern 3: Fix all instances of "]." at end of lines
        content = re.sub(r'\]\.\s*$', ']', content, flags=re.MULTILINE)
        
        # Pattern 4: Fix all instances of "}." at end of lines
        content = re.sub(r'\}\.\s*$', '}', content, flags=re.MULTILINE)
        
        # Pattern 5: Fix docstrings that are concatenated with function definitions
        # This handles: def func():."""Docstring"""
        content = re.sub(
            r'(def\s+\w+\s*\([^)]*\)\s*):\s*\.?\s*"""([^"]+)"""',
            r'\1:\n    """\2"""',
            content,
            flags=re.MULTILINE
        )
        
        # Pattern 6: Fix docstrings that are concatenated without proper spacing
        # This handles: """Docstring"""code
        content = re.sub(
            r'"""([^"]+)"""([a-zA-Z_])',
            r'"""\1"""\n\2',
            content
        )
        
        # Pattern 7: Fix list/dict definitions with periods
        content = re.sub(r'=\s*\[\.\s*$', '= [', content, flags=re.MULTILINE)
        content = re.sub(r'=\s*\{\.\s*$', '= {', content, flags=re.MULTILINE)
        
        # Pattern 8: Process line by line for more complex fixes
        lines = content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            original_line = line
            
            # Skip empty lines and pure comments
            if not line.strip() or line.strip().startswith('#'):
                fixed_lines.append(line)
                i += 1
                continue
            
            # Fix lines ending with period (but not ellipsis)
            if line.strip().endswith('.') and not line.strip().endswith('...'):
                # Check if it's not inside a string
                # Simple heuristic: count quotes
                single_quotes = line.count("'")
                double_quotes = line.count('"')
                
                # If even number of quotes, likely not in a string
                if single_quotes % 2 == 0 and double_quotes % 2 == 0:
                    line = line.rstrip().rstrip('.')
                    fixes.append(f"Line {i+1}: Removed trailing period")
            
            # Fix specific statement patterns
            # Pattern: variable = value.
            line = re.sub(r'^(\s*\w+\s*=\s*[^.]+)\.\s*$', r'\1', line)
            
            # Pattern: return value.
            line = re.sub(r'^(\s*return\s+[^.]+)\.\s*$', r'\1', line)
            
            # Pattern: logger.info(...).
            line = re.sub(r'(logger\.\w+\([^)]+\))\.\s*$', r'\1', line)
            
            # Pattern: self.something = value.
            line = re.sub(r'^(\s*self\.\w+\s*=\s*[^.]+)\.\s*$', r'\1', line)
            
            # Fix docstring issues
            if '"""' in line:
                # Check if docstring starts on same line as def
                match = re.match(r'^(\s*)(def\s+\w+\s*\([^)]*\)\s*):\s*\.?\s*"""(.*)$', line)
                if match:
                    indent = match.group(1)
                    func_def = match.group(2)
                    rest = match.group(3)
                    fixed_lines.append(f"{indent}{func_def}:")
                    
                    # Check if docstring ends on same line
                    if rest.endswith('"""'):
                        docstring_content = rest[:-3]
                        fixed_lines.append(f'{indent}    """{docstring_content}"""')
                    else:
                        fixed_lines.append(f'{indent}    """{rest}')
                    
                    fixes.append(f"Line {i+1}: Fixed docstring placement")
                    i += 1
                    continue
            
            if line != original_line:
                fixes.append(f"Line {i+1}: Fixed syntax")
            
            fixed_lines.append(line)
            i += 1
        
        content = '\n'.join(fixed_lines)
        
        # Final pass: Fix any remaining problematic patterns
        # Fix incomplete parentheses patterns
        content = re.sub(r'return\s*\[\.\s*$', 'return [', content, flags=re.MULTILINE)
        content = re.sub(r'self\.register_tool\s*\(\.\s*$', 'self.register_tool(', content, flags=re.MULTILINE)
        
        # Fix def __init__(.
        content = re.sub(r'def\s+__init__\s*\(\.\s*$', 'def __init__(self):', content, flags=re.MULTILINE)
        
        if content != original_content:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, fixes if fixes else ["Applied aggressive syntax fixes"]
        
        return False, []
        
    except Exception as e:
        return False, [f"Error: {str(e)}"]

def main():
    """Main function to fix syntax errors aggressively."""
    print("🔧 Aggressive Syntax Error Fixing")
    print("=" * 60)
    
    try:
        with open('syntax_validation_report.json', 'r') as f:
            report = json.load(f)
        
        errors = report.get('errors', {})
        fixed_count = 0
        total_errors = 0
        
        for file_path_str, error_msg in errors.items():
            # Skip node_modules
            if 'node_modules' in file_path_str:
                continue
            
            total_errors += 1
            file_path = Path(file_path_str)
            
            if file_path.exists():
                print(f"\n📄 Processing {file_path}...")
                print(f"   Error: {error_msg.split('\\n')[0]}")
                
                fixed, fixes = fix_file_aggressively(file_path)
                
                if fixed:
                    fixed_count += 1
                    print(f"✅ Fixed {file_path}")
                    for fix in fixes[:5]:  # Show first 5 fixes
                        print(f"   - {fix}")
                    if len(fixes) > 5:
                        print(f"   ... and {len(fixes) - 5} more fixes")
                else:
                    if fixes:  # Error occurred
                        print(f"❌ Error: {fixes[0]}")
            else:
                print(f"⚠️  File not found: {file_path}")
        
        print(f"\n📊 Summary:")
        print(f"Total error files: {total_errors}")
        print(f"Files fixed: {fixed_count}")
        print(f"Success rate: {fixed_count/total_errors*100:.1f}%")
        
        print("\n💡 Next steps:")
        print("1. Run 'python scripts/validate_current_syntax.py' to check remaining errors")
        print("2. Backup files created with .bak extension")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
