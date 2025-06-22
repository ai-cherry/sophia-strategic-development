#!/usr/bin/env python3
"""
Fix remaining syntax errors in Python files with more aggressive patterns.
"""

import re
import ast
from pathlib import Path
import logging

TRIPLE = '"""'

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def fix_unterminated_strings(content):
    """Fix unterminated string literals."""
    lines = content.split('\n')
    fixed_lines = []
    in_triple_quote = False
    triple_quote_char = None
    
    for i, line in enumerate(lines):
        # Check for triple quotes
        if '"""' in line or "'''" in line:
            # Count occurrences
            double_count = line.count('"""')
            single_count = line.count("'''")
            
            if double_count % 2 == 1:  # Odd number means state change
                if not in_triple_quote:
                    in_triple_quote = True
                    triple_quote_char = '"""'
                elif triple_quote_char == '"""':
                    in_triple_quote = False
                    
            if single_count % 2 == 1:  # Odd number means state change
                if not in_triple_quote:
                    in_triple_quote = True
                    triple_quote_char = "'''"
                elif triple_quote_char == "'''":
                    in_triple_quote = False
        
        # Fix lines that have docstring immediately followed by code
        if TRIPLE in line and not in_triple_quote:
            # Pattern: triple-quoted text immediately followed by code -> split into separate lines
            pattern = rf'^(\s*)({TRIPLE}.*?{TRIPLE})([^#\s].*)$'
            match = re.match(pattern, line)
            if match:
                indent, docstring, code = match.groups()
                fixed_lines.append(indent + docstring)
                fixed_lines.append(indent + code)
                continue
                
        fixed_lines.append(line)
    
    # If we're still in a triple quote at the end, close it
    if in_triple_quote:
        fixed_lines.append(triple_quote_char)
    
    return '\n'.join(fixed_lines)

def fix_indentation_errors(content):
    """Fix common indentation errors."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            fixed_lines.append(line)
            continue
            
        # Check if previous line ends with : and current line has wrong indent
        if i > 0 and fixed_lines[-1].rstrip().endswith(':'):
            prev_indent = len(fixed_lines[-1]) - len(fixed_lines[-1].lstrip())
            curr_indent = len(line) - len(line.lstrip())
            
            # If current line has same or less indent, fix it
            if curr_indent <= prev_indent and line.strip():
                fixed_line = ' ' * (prev_indent + 4) + line.lstrip()
                fixed_lines.append(fixed_line)
                continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_try_except_blocks(content):
    """Fix try/except blocks with missing indentation."""
    lines = content.split('\n')
    fixed_lines = []
    in_try_block = False
    try_indent = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if stripped.startswith('try:'):
            in_try_block = True
            try_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
        elif in_try_block and (stripped.startswith('except') or stripped.startswith('finally')):
            # Make sure except/finally is at same level as try
            fixed_line = ' ' * try_indent + stripped
            fixed_lines.append(fixed_line)
            in_try_block = False
        elif in_try_block and i > 0 and fixed_lines[-1].strip().endswith('try:'):
            # Line after try: should be indented
            if len(line) - len(line.lstrip()) <= try_indent:
                fixed_line = ' ' * (try_indent + 4) + line.lstrip()
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_file(filepath):
    """Fix syntax errors in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return False
    
    original_content = content
    
    # Apply fixes
    content = fix_unterminated_strings(content)
    content = fix_indentation_errors(content)
    content = fix_try_except_blocks(content)
    
    # Try to parse the fixed content
    try:
        ast.parse(content)
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Fixed {filepath}")
            return True
        return False
    except SyntaxError as e:
        logger.warning(f"Syntax error remains in {filepath}: {e}")
        # Still write if we made changes
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

def main():
    # Files identified as having errors
    error_files = [
        "backend/minimal_main.py",
        "backend/main.py",
        "backend/containerized_main.py",
        "backend/database/schema_migration_system.py",
        "backend/pipeline/data_pipeline_architecture.py",
        "backend/core/auto_esc_config.py",
        "backend/agents/core/base_agent.py",
        "backend/agents/core/agent_framework.py",
        "backend/agents/specialized/pay_ready_agents.py",
        "backend/agents/specialized/client_health_agent.py",
        "backend/pipelines/gong_snowflake_pipeline.py",
        "backend/integrations/snowflake_integration.py"
    ]
    
    fixed_count = 0
    for filepath in error_files:
        if Path(filepath).exists():
            if fix_file(filepath):
                fixed_count += 1
        else:
            logger.warning(f"File not found: {filepath}")
    
    logger.info(f"\nFixed {fixed_count} files")
    
    # Run a final check
    remaining_errors = []
    for filepath in error_files:
        if Path(filepath).exists():
            try:
                with open(filepath, 'r') as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                remaining_errors.append((filepath, str(e)))
    
    if remaining_errors:
        logger.warning(f"\nFiles with remaining errors: {len(remaining_errors)}")
        for filepath, error in remaining_errors:
            logger.warning(f"  - {filepath}: {error}")
    else:
        logger.info("\nAll syntax errors fixed!")

if __name__ == "__main__":
    main()
