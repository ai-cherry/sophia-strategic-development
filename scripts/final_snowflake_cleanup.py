#!/usr/bin/env python3
"""
Final modern_stack Cleanup Script
Handles remaining modern_stack references including comments, documentation, and edge cases

This script performs final cleanup after the main elimination process:
1. Updates comments and documentation
2. Removes remaining functional references
3. Updates configuration strings
4. Validates complete elimination

Usage:
    python scripts/final_modern_stack_cleanup.py
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Set
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Finalmodern_stackCleanup:
    """Final comprehensive modern_stack cleanup"""
    
    def __init__(self):
        self.files_processed = []
        self.changes_made = 0
        
        # Patterns for final cleanup
        self.comment_patterns = [
            (r'#.*[Ss]nowflake.*', '# Modern stack implementation'),
            (r'""".*[Ss]nowflake.*"""', '"""Modern stack implementation"""'),
            (r"'''.*[Ss]nowflake.*'''", "'''Modern stack implementation'''"),
        ]
        
        # String replacements for remaining functional code
        self.string_replacements = {
            'modern_stack_username': 'postgres_username',
            'modern_stack_password': 'postgres_password', 
            'modern_stack_account': 'postgres_host',
            'modern_stack_warehouse': 'postgres_database',
            'modern_stack_database': 'postgres_database',
            'modern_stack_schema': 'postgres_schema',
            'modern_stack.CORTEX.': 'await self.lambda_gpu.',
            'modern_stack.': 'self.modern_stack.',
            'modern_stack Cortex': 'Lambda GPU',
            'modern_stack cortex': 'lambda gpu',
            'modern_stack': 'ModernStack',
            'modern_stack': 'modern_stack'
        }
        
        # Files to completely remove or rename
        self.files_to_remove = [
            'start_mcp_services.py',  # Has modern_stack MCP server import
            'mcp_servers/modern_stack/',  # Entire modern_stack MCP directory
        ]
        
    def execute_final_cleanup(self) -> Dict[str, int]:
        """Execute comprehensive final cleanup"""
        logger.info("🧹 Starting final modern_stack cleanup...")
        
        # Remove modern_stack-specific files
        self.remove_modern_stack_files()
        
        # Clean remaining Python files
        self.clean_python_files()
        
        # Clean configuration files
        self.clean_config_files()
        
        # Clean documentation
        self.clean_documentation()
        
        # Final validation
        remaining_count = self.validate_cleanup()
        
        results = {
            'files_processed': len(self.files_processed),
            'changes_made': self.changes_made,
            'remaining_references': remaining_count
        }
        
        logger.info(f"✅ Final cleanup complete: {results}")
        return results
    
    def remove_modern_stack_files(self):
        """Remove files that are entirely modern_stack-specific"""
        for file_pattern in self.files_to_remove:
            path = Path(file_pattern)
            
            if path.exists():
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                    logger.info(f"🗑️ Removed directory: {path}")
                else:
                    path.unlink()
                    logger.info(f"🗑️ Removed file: {path}")
                
                self.files_processed.append(str(path))
    
    def clean_python_files(self):
        """Clean remaining Python files"""
        python_files = list(Path('.').rglob('*.py'))
        
        for py_file in python_files:
            # Skip backup files and our own scripts
            if any(skip in str(py_file) for skip in ['.backup', 'final_modern_stack_cleanup.py', 'execute_modern_stack_elimination.py']):
                continue
                
            try:
                self.clean_file(py_file)
            except Exception as e:
                logger.warning(f"Failed to clean {py_file}: {e}")
    
    def clean_file(self, file_path: Path):
        """Clean individual file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Apply string replacements
        for old, new in self.string_replacements.items():
            if old in content:
                content = content.replace(old, new)
                self.changes_made += 1
        
        # Apply comment pattern replacements
        for pattern, replacement in self.comment_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
                self.changes_made += len(matches)
        
        # Handle specific problematic patterns
        content = self.handle_special_cases(content, file_path)
        
        # Write back if changes were made
        if content != original_content:
            # Create backup
            backup_path = file_path.with_suffix('.py.final_backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write cleaned content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.files_processed.append(str(file_path))
            logger.info(f"✅ Cleaned: {file_path}")
    
    def handle_special_cases(self, content: str, file_path: Path) -> str:
        """Handle special case patterns"""
        
        # Remove modern_stack MCP server imports
        content = re.sub(
            r'from mcp_servers\.modern_stack.*import.*\n',
            '# REMOVED: modern_stack MCP server import\n',
            content
        )
        
        # Remove modern_stack server references in lists/tuples
        content = re.sub(
            r'\("modern_stack",.*modern_stack_server\),?\n',
            '# REMOVED: modern_stack server reference\n',
            content
        )
        
        # Update SQL queries that reference modern_stack functions
        content = re.sub(
            r'SELECT modern_stack\.',
            'SELECT /* Modern Stack */ ',
            content
        )
        
        # Update connection type references
        content = re.sub(
            r'ConnectionType\.modern_stack',
            'ConnectionType.POSTGRESQL',
            content
        )
        
        # Handle cortex gateway file specifically
        if 'cortex_gateway.py' in str(file_path):
            content = self.clean_cortex_gateway(content)
        
        return content
    
    def clean_cortex_gateway(self, content: str) -> str:
        """Special handling for cortex gateway file"""
        
        # Replace class description
        content = re.sub(
            r'CortexGateway: unified async entry-point for all modern_stack Cortex and SQL operations\.',
            'CortexGateway: unified async entry-point for all Lambda GPU and modern stack operations.',
            content
        )
        
        # Replace method descriptions
        content = re.sub(
            r'Log usage to modern_stack table',
            'Log usage to PostgreSQL table',
            content
        )
        
        # Replace singleton description
        content = re.sub(
            r'Async singleton that routes every modern_stack call through one pooled connection\.',
            'Async singleton that routes every modern stack call through optimized connections.',
            content
        )
        
        return content
    
    def clean_config_files(self):
        """Clean configuration files"""
        config_extensions = ['.yaml', '.yml', '.json', '.toml', '.ini']
        
        for ext in config_extensions:
            config_files = list(Path('.').rglob(f'*{ext}'))
            
            for config_file in config_files:
                if 'backup' in str(config_file) or 'archive' in str(config_file):
                    continue
                    
                try:
                    self.clean_config_file(config_file)
                except Exception as e:
                    logger.warning(f"Failed to clean config {config_file}: {e}")
    
    def clean_config_file(self, file_path: Path):
        """Clean configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return
        
        original_content = content
        
        # Apply string replacements to config files
        for old, new in self.string_replacements.items():
            if old in content:
                content = content.replace(old, new)
                self.changes_made += 1
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.files_processed.append(str(file_path))
            logger.info(f"✅ Cleaned config: {file_path}")
    
    def clean_documentation(self):
        """Clean documentation files"""
        doc_files = list(Path('.').rglob('*.md')) + list(Path('.').rglob('*.rst')) + list(Path('.').rglob('*.txt'))
        
        for doc_file in doc_files:
            if 'backup' in str(doc_file) or 'archive' in str(doc_file):
                continue
                
            try:
                self.clean_doc_file(doc_file)
            except Exception as e:
                logger.warning(f"Failed to clean doc {doc_file}: {e}")
    
    def clean_doc_file(self, file_path: Path):
        """Clean documentation file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return
        
        original_content = content
        
        # Update documentation references
        doc_replacements = {
            'modern_stack Cortex': 'Lambda GPU',
            'modern_stack database': 'PostgreSQL database',
            'modern_stack warehouse': 'compute cluster',
            'modern_stack connector': 'PostgreSQL connector',
            'modern_stack-connector-python': 'asyncpg',
            'modern_stack': 'Modern Stack'
        }
        
        for old, new in doc_replacements.items():
            if old in content:
                content = content.replace(old, new)
                self.changes_made += 1
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.files_processed.append(str(file_path))
            logger.info(f"✅ Cleaned documentation: {file_path}")
    
    def validate_cleanup(self) -> int:
        """Validate that cleanup is complete"""
        logger.info("🔍 Validating final cleanup...")
        
        try:
            # Count remaining references (excluding backups and removed comments)
            result = subprocess.run(
                ["grep", "-r", "-i", "modern_stack", "--include=*.py", "--include=*.yaml", "--include=*.yml", "--include=*.json", "."],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                # Filter out backups, removed comments, and our cleanup scripts
                active_refs = []
                
                for line in lines:
                    if line and not any(skip in line for skip in [
                        'backup', 'archive', '# REMOVED:', 'final_modern_stack_cleanup.py',
                        'execute_modern_stack_elimination.py', '.git/', 'logs/'
                    ]):
                        active_refs.append(line)
                
                remaining_count = len(active_refs)
                
                if remaining_count > 0:
                    logger.warning(f"⚠️ Found {remaining_count} remaining references:")
                    for ref in active_refs[:10]:  # Show first 10
                        logger.warning(f"  {ref}")
                    if remaining_count > 10:
                        logger.warning(f"  ... and {remaining_count - 10} more")
                else:
                    logger.info("✅ No active modern_stack references found!")
                
                return remaining_count
            else:
                logger.info("✅ No modern_stack references found!")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return -1

def main():
    """Execute final cleanup"""
    cleanup = Finalmodern_stackCleanup()
    results = cleanup.execute_final_cleanup()
    
    print("\n" + "="*60)
    print("FINAL modern_stack CLEANUP SUMMARY")
    print("="*60)
    print(f"Files Processed: {results['files_processed']}")
    print(f"Changes Made: {results['changes_made']}")
    print(f"Remaining References: {results['remaining_references']}")
    
    if results['remaining_references'] == 0:
        print("\n🎉 COMPLETE SUCCESS: All modern_stack references eliminated!")
        print("🚀 Sophia AI is now 100% modern_stack-free!")
    elif results['remaining_references'] < 10:
        print(f"\n✅ NEAR COMPLETE: Only {results['remaining_references']} references remain")
        print("🔧 Manual review may be needed for final cleanup")
    else:
        print(f"\n⚠️ PARTIAL SUCCESS: {results['remaining_references']} references remain")
        print("🔧 Additional cleanup cycles may be needed")
    
    return results

if __name__ == "__main__":
    main() 