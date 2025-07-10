#!/usr/bin/env python3
"""
Comprehensive Code Quality Fix Script for Sophia AI

Runs syntax checking, linting, and black formatting on the entire codebase
with proper error handling and progress tracking.
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import List, Tuple, Dict
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeQualityFixer:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.stats = {
            'total_files': 0,
            'files_processed': 0,
            'files_fixed': 0,
            'syntax_errors': 0,
            'linting_errors_before': 0,
            'linting_errors_after': 0,
            'black_formatted': 0,
            'failed_files': []
        }
        
        # Directories to exclude
        self.exclude_dirs = {
            '.venv', 'venv', '__pycache__', '.git', 'node_modules',
            '.pytest_cache', '.mypy_cache', 'build', 'dist',
            'external', 'archive', 'mcp_migration_backup*'
        }
        
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the codebase."""
        python_files = []
        
        for path in self.root_dir.rglob('*.py'):
            # Skip excluded directories
            if any(excluded in path.parts for excluded in self.exclude_dirs):
                continue
            python_files.append(path)
        
        self.stats['total_files'] = len(python_files)
        logger.info(f"Found {len(python_files)} Python files to process")
        return python_files
    
    def check_syntax(self, file_path: Path) -> bool:
        """Check if file has valid Python syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            return True
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            self.stats['syntax_errors'] += 1
            self.stats['failed_files'].append({
                'file': str(file_path),
                'error': f"Syntax error: {e}"
            })
            return False
        except Exception as e:
            logger.error(f"Error checking {file_path}: {e}")
            return False
    
    def run_ruff_check(self) -> Dict:
        """Run ruff check to get current linting stats."""
        try:
            result = subprocess.run(
                ['ruff', 'check', '.', '--statistics', '--output-format', 'json'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                # Parse the statistics from stderr
                stats_output = subprocess.run(
                    ['ruff', 'check', '.', '--statistics'],
                    capture_output=True,
                    text=True
                )
                return {'total_errors': self._parse_ruff_stats(stats_output.stdout)}
            return {'total_errors': 0}
        except Exception as e:
            logger.error(f"Error running ruff check: {e}")
            return {'total_errors': -1}
    
    def _parse_ruff_stats(self, output: str) -> int:
        """Parse ruff statistics output."""
        try:
            lines = output.strip().split('\n')
            for line in lines:
                if 'Found' in line and 'errors' in line:
                    parts = line.split()
                    return int(parts[1])
            return 0
        except:
            return 0
    
    def fix_with_ruff(self, file_path: Path) -> bool:
        """Fix file using ruff with safe and unsafe fixes."""
        try:
            # First try safe fixes
            subprocess.run(
                ['ruff', 'check', str(file_path), '--fix'],
                capture_output=True,
                check=False
            )
            
            # Then try unsafe fixes for specific error types
            subprocess.run(
                ['ruff', 'check', str(file_path), '--fix', '--unsafe-fixes'],
                capture_output=True,
                check=False
            )
            
            return True
        except Exception as e:
            logger.error(f"Error fixing {file_path} with ruff: {e}")
            return False
    
    def format_with_black(self, file_path: Path) -> bool:
        """Format file using black."""
        try:
            result = subprocess.run(
                ['black', str(file_path), '--quiet'],
                capture_output=True,
                check=False
            )
            
            if result.returncode == 0:
                self.stats['black_formatted'] += 1
                return True
            else:
                logger.warning(f"Black could not format {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error formatting {file_path} with black: {e}")
            return False
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single file through all quality checks and fixes."""
        # First check syntax
        if not self.check_syntax(file_path):
            return False
        
        # Fix with ruff
        if self.fix_with_ruff(file_path):
            self.stats['files_fixed'] += 1
        
        # Format with black
        self.format_with_black(file_path)
        
        self.stats['files_processed'] += 1
        return True
    
    def process_critical_files_first(self, files: List[Path]) -> Tuple[List[Path], List[Path]]:
        """Separate critical files to process first."""
        critical_patterns = [
            'backend/app/',
            'backend/services/',
            'backend/api/',
            'backend/core/',
            'mcp-servers/',
            'scripts/deployment/',
            'scripts/quality/'
        ]
        
        critical_files = []
        other_files = []
        
        for file in files:
            file_str = str(file)
            if any(pattern in file_str for pattern in critical_patterns):
                critical_files.append(file)
            else:
                other_files.append(file)
        
        return critical_files, other_files
    
    def run(self):
        """Run the comprehensive code quality fix."""
        logger.info("Starting comprehensive code quality fix...")
        start_time = time.time()
        
        # Get initial linting stats
        initial_stats = self.run_ruff_check()
        self.stats['linting_errors_before'] = initial_stats['total_errors']
        logger.info(f"Initial linting errors: {self.stats['linting_errors_before']}")
        
        # Find all Python files
        all_files = self.find_python_files()
        
        # Separate critical files
        critical_files, other_files = self.process_critical_files_first(all_files)
        logger.info(f"Processing {len(critical_files)} critical files first")
        
        # Process critical files first
        for i, file_path in enumerate(critical_files, 1):
            if i % 100 == 0:
                logger.info(f"Processed {i}/{len(critical_files)} critical files...")
            self.process_file(file_path)
        
        logger.info(f"Completed critical files. Processing {len(other_files)} remaining files...")
        
        # Process remaining files
        for i, file_path in enumerate(other_files, 1):
            if i % 500 == 0:
                logger.info(f"Processed {i}/{len(other_files)} remaining files...")
            self.process_file(file_path)
        
        # Get final linting stats
        final_stats = self.run_ruff_check()
        self.stats['linting_errors_after'] = final_stats['total_errors']
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Print summary
        self.print_summary(duration)
        
        # Save detailed report
        self.save_report()
    
    def print_summary(self, duration: float):
        """Print summary of the code quality fix."""
        print("\n" + "="*60)
        print("CODE QUALITY FIX SUMMARY")
        print("="*60)
        print(f"Total files found: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files with fixes applied: {self.stats['files_fixed']}")
        print(f"Files formatted with black: {self.stats['black_formatted']}")
        print(f"Syntax errors found: {self.stats['syntax_errors']}")
        print(f"Linting errors before: {self.stats['linting_errors_before']}")
        print(f"Linting errors after: {self.stats['linting_errors_after']}")
        
        if self.stats['linting_errors_before'] > 0:
            reduction = (
                (self.stats['linting_errors_before'] - self.stats['linting_errors_after']) 
                / self.stats['linting_errors_before'] * 100
            )
            print(f"Error reduction: {reduction:.1f}%")
        
        print(f"Duration: {duration:.1f} seconds")
        print("="*60)
        
        if self.stats['failed_files']:
            print(f"\n{len(self.stats['failed_files'])} files failed processing:")
            for failed in self.stats['failed_files'][:10]:
                print(f"  - {failed['file']}: {failed['error']}")
            if len(self.stats['failed_files']) > 10:
                print(f"  ... and {len(self.stats['failed_files']) - 10} more")
    
    def save_report(self):
        """Save detailed report to file."""
        report_path = self.root_dir / 'CODE_QUALITY_FIX_REPORT.json'
        
        with open(report_path, 'w') as f:
            json.dump({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'stats': self.stats
            }, f, indent=2)
        
        logger.info(f"Detailed report saved to {report_path}")


def main():
    """Main entry point."""
    fixer = CodeQualityFixer()
    
    # Check if required tools are installed
    required_tools = ['ruff', 'black']
    for tool in required_tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error(f"{tool} is not installed. Please install it first.")
            sys.exit(1)
    
    # Run the fixer
    fixer.run()


if __name__ == '__main__':
    main() 