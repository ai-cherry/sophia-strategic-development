#!/usr/bin/env python3
"""
Fix broken references in the Sophia AI codebase.
This script updates import statements to use correct paths.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define replacement mappings
IMPORT_REPLACEMENTS = {
    # Core module fixes
    r'from core\.config_manager import get_config_value': 'from backend.core.auto_esc_config import get_config_value',
    r'import core\.config_manager': 'import backend.core.auto_esc_config',
    r'from core\.auto_esc_config import': 'from backend.core.auto_esc_config import',
    
    # Infrastructure fixes
    r'from backend\.infrastructure\.': 'from infrastructure.',
    r'import backend\.infrastructure\.': 'import infrastructure.',
    
    # Shared module fixes
    r'from shared\.utils\.custom_logger import': 'from backend.utils.logging import',
    r'from shared\.utils\.errors import': 'from backend.utils.errors import',
    r'from shared\.security_config import': 'from backend.security.config import',
    
    # Config module fixes
    r'from config\.infrastructure import': 'from infrastructure.config import',
    r'from config\.production_infrastructure import': 'from infrastructure.config.production import',
    
    # Core services fixes
    r'from core\.services\.': 'from backend.services.',
    r'from core\.agents\.': 'from backend.agents.',
    r'from core\.workflows\.': 'from backend.workflows.',
    
    # Performance and monitoring fixes
    r'from core\.performance_monitor import': 'from backend.monitoring.performance import',
    r'from core\.optimized_connection_manager import': 'from backend.core.database import',
    r'from core\.logger import': 'from backend.utils.logging import',
}

def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files in the project."""
    python_files = []
    for path in root_dir.rglob('*.py'):
        # Skip virtual environments and cache directories
        if any(part in path.parts for part in ['venv', 'env', '.env', '__pycache__', '.git']):
            continue
        python_files.append(path)
    return python_files

def fix_imports_in_file(file_path: Path, dry_run: bool = True) -> List[Tuple[str, str]]:
    """Fix imports in a single file."""
    changes = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply replacements
        for pattern, replacement in IMPORT_REPLACEMENTS.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                original = match.group(0)
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    changes.append((original, replacement))
        
        # Write changes if not dry run
        if changes and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        
    return changes

def create_missing_modules(root_dir: Path, dry_run: bool = True):
    """Create missing module stubs."""
    missing_modules = {
        'backend/utils/errors.py': '''"""Error classes for Sophia AI."""

class APIError(Exception):
    """Base API error."""
    pass

class RateLimitError(APIError):
    """Rate limit exceeded error."""
    pass

class AuthenticationError(APIError):
    """Authentication failed error."""
    pass
''',
        'backend/utils/logging.py': '''"""Logging utilities for Sophia AI."""

import logging
import sys

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Set up a logger with standard configuration."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Default logger instance
logger = setup_logger(__name__)
''',
        'backend/monitoring/performance.py': '''"""Performance monitoring utilities."""

import time
from contextlib import contextmanager
from typing import Dict, Any

class PerformanceMonitor:
    """Simple performance monitoring."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
    
    @contextmanager
    def measure(self, operation: str):
        """Measure operation performance."""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.metrics[operation] = {
                'duration': duration,
                'timestamp': time.time()
            }

performance_monitor = PerformanceMonitor()
''',
        'infrastructure/config/__init__.py': '''"""Infrastructure configuration."""

from .infrastructure import InfrastructureConfig, ServiceType, LambdaInstance, InstanceRole

__all__ = ['InfrastructureConfig', 'ServiceType', 'LambdaInstance', 'InstanceRole']
''',
    }
    
    for file_path, content in missing_modules.items():
        full_path = root_dir / file_path
        if not full_path.exists():
            logger.info(f"Would create: {file_path}")
            if not dry_run:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix broken references in Sophia AI codebase')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--create-missing', action='store_true', help='Create missing module stubs')
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Root directory of the project')
    
    args = parser.parse_args()
    
    logger.info(f"Scanning for Python files in {args.root}")
    python_files = find_python_files(args.root)
    logger.info(f"Found {len(python_files)} Python files")
    
    # Fix imports
    total_changes = 0
    files_with_changes = 0
    
    for file_path in python_files:
        changes = fix_imports_in_file(file_path, args.dry_run)
        if changes:
            files_with_changes += 1
            total_changes += len(changes)
            logger.info(f"{file_path}: {len(changes)} changes")
            for old, new in changes:
                logger.debug(f"  {old} -> {new}")
    
    logger.info(f"\nSummary: {total_changes} changes in {files_with_changes} files")
    
    # Create missing modules if requested
    if args.create_missing:
        logger.info("\nCreating missing modules...")
        create_missing_modules(args.root, args.dry_run)
    
    if args.dry_run:
        logger.info("\nDry run complete. Use without --dry-run to apply changes.")

if __name__ == '__main__':
    main()
