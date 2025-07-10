#!/usr/bin/env python3
"""
Fix Critical Issues in Sophia AI Codebase

Focuses on syntax errors and critical linting issues that prevent the code from running.
"""

import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Fix critical issues in the codebase."""
    logger.info("Starting critical issue fixes...")
    
    # First, let's get the list of files with syntax errors
    logger.info("Finding files with syntax errors...")
    result = subprocess.run(
        ['ruff', 'check', '.', '--select', 'E999'],
        capture_output=True,
        text=True
    )
    
    syntax_error_files = []
    for line in result.stdout.split('\n'):
        if '.py:' in line and 'E999' in line:
            file_path = line.split(':')[0]
            if file_path not in syntax_error_files:
                syntax_error_files.append(file_path)
    
    logger.info(f"Found {len(syntax_error_files)} files with syntax errors")
    
    # Fix undefined names (F821) - critical for runtime
    logger.info("Fixing undefined names...")
    subprocess.run(
        ['ruff', 'check', '.', '--select', 'F821', '--fix', '--unsafe-fixes'],
        capture_output=True
    )
    
    # Fix module import issues (E402)
    logger.info("Fixing module import order issues...")
    subprocess.run(
        ['ruff', 'check', '.', '--select', 'E402', '--fix'],
        capture_output=True
    )
    
    # Fix unused imports (F401) to clean up
    logger.info("Removing unused imports...")
    subprocess.run(
        ['ruff', 'check', '.', '--select', 'F401', '--fix'],
        capture_output=True
    )
    
    # Apply black formatting to critical directories
    critical_dirs = [
        'backend/app',
        'backend/services',
        'backend/api', 
        'backend/core',
        'mcp-servers',
        'scripts'
    ]
    
    for dir_path in critical_dirs:
        if Path(dir_path).exists():
            logger.info(f"Formatting {dir_path} with black...")
            subprocess.run(
                ['black', dir_path, '--quiet'],
                capture_output=True
            )
    
    # Run final check
    logger.info("Running final check...")
    final_result = subprocess.run(
        ['ruff', 'check', '.', '--statistics'],
        capture_output=True,
        text=True
    )
    
    print("\n" + "="*60)
    print("CRITICAL FIXES COMPLETE")
    print("="*60)
    print("\nRemaining issues:")
    print(final_result.stdout)
    
    # Check for remaining syntax errors
    syntax_check = subprocess.run(
        ['ruff', 'check', '.', '--select', 'E999'],
        capture_output=True,
        text=True
    )
    
    if syntax_check.returncode == 0:
        print("\n✅ No syntax errors remaining!")
    else:
        print("\n⚠️  Some syntax errors still exist - manual intervention required")
        print("Run 'ruff check . --select E999' to see details")

if __name__ == '__main__':
    main() 