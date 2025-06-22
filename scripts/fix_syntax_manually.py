#!/usr/bin/env python3
"""
Manually fix the specific syntax errors in the critical files.
"""

import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def fix_minimal_main():
    """Fix backend/minimal_main.py specifically."""
    filepath = Path("backend/minimal_main.py")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix the specific indentation issues
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Fix line 71-74 where return statement has wrong indent
        if i == 70 and line.strip() == '"""Root endpoint."""':
            fixed_lines.append(line)
            # Next line should have proper indentation
            continue
        elif i == 71 and line.strip().startswith('return'):
            # This return is incorrectly indented
            fixed_lines.append('    return {')
            continue
        elif i == 82 and line.strip() == '"""Health check endpoint."""':
            fixed_lines.append(line)
            continue
        elif i == 83 and line.strip().startswith('try:'):
            # This try is incorrectly indented
            fixed_lines.append('    try:')
            continue
        elif i == 84 and line.strip().startswith('# Test ESC'):
            fixed_lines.append('        # Test ESC configuration access')
            continue
        elif i == 117 and line.strip() == '"""Get configuration status and basic info."""':
            fixed_lines.append(line)
            continue
        elif i == 118 and line.strip().startswith('try:'):
            fixed_lines.append('    try:')
            continue
        elif i == 119 and line.strip().startswith('config_data'):
            fixed_lines.append('        config_data = config.get_all_values()')
            continue
        elif i == 135 and line.strip().startswith('except'):
            fixed_lines.append('    except Exception as e:')
            continue
        elif i == 145 and line.strip() == '"""Test secret access without exposing values."""':
            fixed_lines.append(line)
            continue
        elif i == 146 and line.strip().startswith('try:'):
            fixed_lines.append('    try:')
            continue
        elif i == 147 and line.strip().startswith('config_data'):
            fixed_lines.append('        config_data = config.get_all_values()')
            continue
        elif i == 175 and line.strip().startswith('except'):
            fixed_lines.append('    except Exception as e:')
            continue
        else:
            fixed_lines.append(line)
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    logger.info(f"Fixed {filepath}")

def fix_auto_esc_config():
    """Fix backend/core/auto_esc_config.py specifically."""
    filepath = Path("backend/core/auto_esc_config.py")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix the specific indentation issues
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Look for lines that start with unexpected indentation after docstrings
        if i > 0 and lines[i-1].strip().endswith('"""') and line.strip() and not line[0].isspace():
            # This line should be indented
            if 'def ' in line or 'class ' in line:
                fixed_lines.append(line)  # These are OK at root level
            else:
                # Add proper indentation
                fixed_lines.append('    ' + line)
        else:
            fixed_lines.append(line)
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    logger.info(f"Fixed {filepath}")

def fix_main_py():
    """Fix backend/main.py specifically."""
    filepath = Path("backend/main.py")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix unterminated string literal issue
    # Look for strings that span multiple lines incorrectly
    content = re.sub(r'(".*?)\n([^"]*?")', r'\1\\n\2', content, flags=re.MULTILINE)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    logger.info(f"Fixed {filepath}")

def main():
    """Fix the critical files manually."""
    try:
        fix_minimal_main()
        fix_auto_esc_config()
        fix_main_py()
        logger.info("Manual fixes applied to critical files")
    except Exception as e:
        logger.error(f"Error during manual fixes: {e}")

if __name__ == "__main__":
    main()
