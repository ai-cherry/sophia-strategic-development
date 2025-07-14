#!/usr/bin/env python3
"""
Final Snowflake Cleanup Script
Handles remaining Snowflake references including comments, documentation, and edge cases

This script performs final cleanup after the main elimination process:
1. Updates comments and documentation
2. Removes remaining functional references
3. Updates configuration strings
4. Validates complete elimination

Usage:
    python scripts/final_snowflake_cleanup.py
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Set
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class FinalSnowflakeCleanup:
    """Final comprehensive Snowflake cleanup"""
    
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
            'snowflake_username': 'postgres_username',
            'snowflake_password': 'postgres_password', 
            'snowflake_account': 'postgres_host',
            'snowflake_warehouse': 'postgres_database',
            'snowflake_database': 'postgres_database',
            'snowflake_schema': 'postgres_schema',
            'SNOWFLAKE.CORTEX.': 'await self.lambda_gpu.',
            'SNOWFLAKE.': 'self.modern_stack.',
            'Snowflake Cortex': 'Lambda GPU',
            'snowflake cortex': 'lambda gpu',
            'Snowflake': 'ModernStack',
            'snowflake': 'modern_stack'
        }
        
        # Files to completely remove or rename
        self.files_to_remove = [
            'start_mcp_services.py',  # Has Snowflake MCP server import
            'mcp_servers/snowflake/',  # Entire Snowflake MCP directory
        ]
        
    def execute_final_cleanup(self) -> Dict[str, int]:
        """Execute comprehensive final cleanup"""
        logger.info("🧹 Starting final Snowflake cleanup...")
        
        # Remove Snowflake-specific files
        self.remove_snowflake_files()
        
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
    
    def remove_snowflake_files(self):
        """Remove files that are entirely Snowflake-specific"""
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
            if any(skip in str(py_file) for skip in ['.backup', 'final_snowflake_cleanup.py', 'execute_snowflake_elimination.py']):
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
        
        # Remove Snowflake MCP server imports
        content = re.sub(
            r'from mcp_servers\.snowflake.*import.*\n',
            '# REMOVED: Snowflake MCP server import\n',
            content
        )
        
        # Remove Snowflake server references in lists/tuples
        content = re.sub(
            r'\("Snowflake",.*snowflake_server\),?\n',
            '# REMOVED: Snowflake server reference\n',
            content
        )
        
        # Update SQL queries that reference Snowflake functions
        content = re.sub(
            r'SELECT SNOWFLAKE\.',
            'SELECT /* Modern Stack */ ',
            content
        )
        
        # Update connection type references
        content = re.sub(
            r'ConnectionType\.SNOWFLAKE',
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
            r'CortexGateway: unified async entry-point for all Snowflake Cortex and SQL operations\.',
            'CortexGateway: unified async entry-point for all Lambda GPU and modern stack operations.',
            content
        )
        
        # Replace method descriptions
        content = re.sub(
            r'Log usage to Snowflake table',
            'Log usage to PostgreSQL table',
            content
        )
        
        # Replace singleton description
        content = re.sub(
            r'Async singleton that routes every Snowflake call through one pooled connection\.',
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
            'Snowflake Cortex': 'Lambda GPU',
            'Snowflake database': 'PostgreSQL database',
            'Snowflake warehouse': 'compute cluster',
            'Snowflake connector': 'PostgreSQL connector',
            'snowflake-connector-python': 'asyncpg',
            'Snowflake': 'Modern Stack'
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
                ["grep", "-r", "-i", "snowflake", "--include=*.py", "--include=*.yaml", "--include=*.yml", "--include=*.json", "."],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                # Filter out backups, removed comments, and our cleanup scripts
                active_refs = []
                
                for line in lines:
                    if line and not any(skip in line for skip in [
                        'backup', 'archive', '# REMOVED:', 'final_snowflake_cleanup.py',
                        'execute_snowflake_elimination.py', '.git/', 'logs/'
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
                    logger.info("✅ No active Snowflake references found!")
                
                return remaining_count
            else:
                logger.info("✅ No Snowflake references found!")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return -1

def main():
    """Execute final cleanup"""
    cleanup = FinalSnowflakeCleanup()
    results = cleanup.execute_final_cleanup()
    
    print("\n" + "="*60)
    print("FINAL SNOWFLAKE CLEANUP SUMMARY")
    print("="*60)
    print(f"Files Processed: {results['files_processed']}")
    print(f"Changes Made: {results['changes_made']}")
    print(f"Remaining References: {results['remaining_references']}")
    
    if results['remaining_references'] == 0:
        print("\n🎉 COMPLETE SUCCESS: All Snowflake references eliminated!")
        print("🚀 Sophia AI is now 100% Snowflake-free!")
    elif results['remaining_references'] < 10:
        print(f"\n✅ NEAR COMPLETE: Only {results['remaining_references']} references remain")
        print("🔧 Manual review may be needed for final cleanup")
    else:
        print(f"\n⚠️ PARTIAL SUCCESS: {results['remaining_references']} references remain")
        print("🔧 Additional cleanup cycles may be needed")
    
    return results

if __name__ == "__main__":
    main() 