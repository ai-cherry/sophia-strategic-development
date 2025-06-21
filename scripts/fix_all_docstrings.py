#!/usr/bin/env python3
"""Safe docstring formatter using regex pattern matching."""

import re
import sys
from pathlib import Path


def fix_docstring_content(content: str) -> str:
    """Fix the content of a docstring.
    
    Args:
        content: The docstring content (without quotes)
        
    Returns:
        The fixed content
    """
    if not content:
        return content
    
    # Remove leading/trailing whitespace from the whole content
    content = content.strip()
    
    # Split into lines
    lines = content.split('\n')
    
    # Single line docstring
    if len(lines) == 1:
        line = lines[0].strip()
        if line and not line.endswith(('.', '!', '?', ':')):
            line += '.'
        return line
    
    # Multi-line docstring
    # First line is the summary
    first_line = lines[0].strip()
    
    # Add period to first line if missing
    if first_line and not first_line.endswith(('.', '!', '?', ':')):
        first_line += '.'
    
    # Process remaining lines
    remaining_lines = [line.rstrip() for line in lines[1:]]
    
    # Remove leading empty lines
    while remaining_lines and not remaining_lines[0]:
        remaining_lines.pop(0)
    
    # If there are remaining lines, ensure blank line after summary
    if remaining_lines:
        result = first_line + '\n\n' + '\n'.join(remaining_lines)
    else:
        result = first_line
    
    return result


def process_file(filepath: Path) -> bool:
    """Process a single Python file to fix docstrings.
    
    Args:
        filepath: Path to the file to process
        
    Returns:
        True if changes were made, False otherwise
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False
    
    original_content = content
    changes_made = False
    
    # Pattern to match docstrings (both """ and ''')
    # This pattern captures:
    # 1. Leading whitespace
    # 2. Opening quotes (""" or ''')
    # 3. Content (including newlines)
    # 4. Closing quotes
    docstring_pattern = re.compile(
        r'^(\s*)("""|\'\'\')((?:[^"\'\\]|\\.|"(?!"")|\'(?!\'\'))*?)\2',
        re.MULTILINE | re.DOTALL
    )
    
    def replace_docstring(match):
        nonlocal changes_made
        indent = match.group(1)
        quotes = match.group(2)
        content = match.group(3)
        
        # Skip empty docstrings
        if not content.strip():
            return match.group(0)
        
        # Fix the content
        fixed_content = fix_docstring_content(content)
        
        if fixed_content != content:
            changes_made = True
        
        # Reconstruct the docstring
        if '\n' not in fixed_content:
            # Single line
            return f'{indent}{quotes}{fixed_content}{quotes}'
        else:
            # Multi-line - need to properly indent
            lines = fixed_content.split('\n')
            result = f'{indent}{quotes}{lines[0]}'
            for line in lines[1:]:
                if line:  # Non-empty line
                    result += f'\n{indent}{line}'
                else:  # Empty line
                    result += '\n'
            result += f'\n{indent}{quotes}'
            return result
    
    # Replace all docstrings
    content = docstring_pattern.sub(replace_docstring, content)
    
    if changes_made:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False
    
    return False


def main():
    """Main function to process files."""
    if len(sys.argv) < 2:
        print("Usage: fix_all_docstrings.py <file_or_directory> [file_or_directory ...]")
        sys.exit(1)
    
    files_to_process = []
    
    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.is_file() and path.suffix == '.py':
            files_to_process.append(path)
        elif path.is_dir():
            # Find all Python files in directory
            files_to_process.extend(path.rglob('*.py'))
    
    if not files_to_process:
        print("No Python files found to process")
        sys.exit(1)
    
    fixed_count = 0
    for filepath in files_to_process:
        if process_file(filepath):
            fixed_count += 1
            print(f"Fixed: {filepath}")
    
    print(f"\nFixed {fixed_count} files out of {len(files_to_process)} processed")


if __name__ == "__main__":
    main()
