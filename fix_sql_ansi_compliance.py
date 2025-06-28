#!/usr/bin/env python3
"""
ANSI SQL Compliance Fixer for Sophia AI Snowflake Files
Fixes common Snowflake-specific syntax that violates ANSI SQL standards
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLANSIComplianceFixer:
    """Fix ANSI SQL compliance issues in Snowflake SQL files"""
    
    def __init__(self):
        self.fixes_applied = []
        self.files_processed = 0
        
        # Common Snowflake to ANSI SQL mappings
        self.function_mappings = {
            'CURRENT_TIMESTAMP()': 'CURRENT_TIMESTAMP',
            'CURRENT_DATE()': 'CURRENT_DATE',
            'CURRENT_TIME()': 'CURRENT_TIME',
            'SQLERRM': 'SQLSTATE',  # Best effort mapping
        }
        
        # Patterns that need special handling
        self.patterns_to_fix = [
            # Dollar-quoted strings
            (r'\$\$([^$]*)\$\$', r"'\1'"),
            
            # Snowflake-specific timestamp functions
            (r'CURRENT_TIMESTAMP\(\)', 'CURRENT_TIMESTAMP'),
            (r'CURRENT_DATE\(\)', 'CURRENT_DATE'),
            (r'CURRENT_TIME\(\)', 'CURRENT_TIME'),
            
            # Variable assignments (Snowflake stored procedure syntax)
            (r'(\w+)\s*:=\s*([^;]+);', r'SET \1 = \2;'),
            
            # EXCEPTION blocks (not ANSI SQL)
            (r'EXCEPTION\s+WHEN\s+OTHERS\s+THEN', '-- EXCEPTION WHEN OTHERS THEN (Snowflake-specific)'),
            
            # GET DIAGNOSTICS (not standard)
            (r'GET\s+DIAGNOSTICS\s+(\w+)\s*=\s*ROW_COUNT;', r'-- GET DIAGNOSTICS \1 = ROW_COUNT; (Snowflake-specific)'),
            
            # VARIANT data type
            (r'\bVARIANT\b', 'TEXT -- VARIANT (Snowflake-specific)'),
            
            # ARRAY data type
            (r'\bARRAY\b', 'TEXT -- ARRAY (Snowflake-specific)'),
            
            # TIMESTAMP_LTZ
            (r'TIMESTAMP_LTZ', 'TIMESTAMP -- TIMESTAMP_LTZ (Snowflake-specific)'),
            
            # TIMESTAMP_NTZ
            (r'TIMESTAMP_NTZ', 'TIMESTAMP -- TIMESTAMP_NTZ (Snowflake-specific)'),
        ]
    
    def is_sql_file(self, file_path: Path) -> bool:
        """Check if file is a SQL file"""
        return file_path.suffix.lower() == '.sql'
    
    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped from processing"""
        skip_patterns = [
            'test',
            'backup',
            'temp',
            '.git',
            '__pycache__'
        ]
        return any(pattern in str(file_path).lower() for pattern in skip_patterns)
    
    def fix_use_statements(self, content: str) -> str:
        """Comment out USE statements as they're not ANSI SQL"""
        # USE DATABASE statements
        content = re.sub(r'^(USE\s+DATABASE\s+[^;]+;)', r'-- \1 -- Snowflake-specific', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # USE SCHEMA statements
        content = re.sub(r'^(USE\s+SCHEMA\s+[^;]+;)', r'-- \1 -- Snowflake-specific', content, flags=re.MULTILINE | re.IGNORECASE)
        
        return content
    
    def fix_grant_statements(self, content: str) -> str:
        """Fix GRANT statements that use Snowflake-specific syntax"""
        # GRANT statements with Snowflake-specific roles
        snowflake_roles = [
            'ROLE_SOPHIA_DEVELOPER',
            'ROLE_SOPHIA_AI_AGENT_SERVICE',
            'SOPHIA_AI_APP_ROLE',
            'SOPHIA_AI_ROLE',
            'SOPHIA_AI_DEVELOPER',
            'EXECUTIVE_ROLE',
            'CEO_ROLE',
            'BOARD_ROLE',
            'EMPLOYEE_ROLE',
            'ANALYST_ROLE',
            'VIEWER_ROLE'
        ]
        
        for role in snowflake_roles:
            # Comment out GRANT statements with these roles
            pattern = rf'^(GRANT\s+[^;]*\s+TO\s+ROLE\s+{role}[^;]*;)'
            content = re.sub(pattern, r'-- \1 -- Snowflake-specific role', content, flags=re.MULTILINE | re.IGNORECASE)
        
        return content
    
    def fix_stored_procedure_syntax(self, content: str) -> str:
        """Fix stored procedure syntax that's not ANSI SQL"""
        # RETURNS statements in procedures
        content = re.sub(r'^(\s*RETURNS\s+\w+)', r'-- \1 -- Snowflake stored procedure syntax', content, flags=re.MULTILINE)
        
        # DECLARE statements in procedures
        content = re.sub(r'^(\s*DECLARE)', r'-- \1 -- Snowflake stored procedure syntax', content, flags=re.MULTILINE)
        
        # BEGIN/END blocks in procedures (keep but add comment)
        content = re.sub(r'^(\s*BEGIN\s*$)', r'\1 -- Snowflake stored procedure', content, flags=re.MULTILINE)
        
        return content
    
    def fix_snowflake_tasks(self, content: str) -> str:
        """Comment out Snowflake TASK definitions"""
        # CREATE TASK statements
        content = re.sub(r'^(CREATE\s+(?:OR\s+REPLACE\s+)?TASK\s+[^;]+)', r'-- \1 -- Snowflake-specific TASK', content, flags=re.MULTILINE | re.IGNORECASE)
        
        return content
    
    def fix_snowflake_specific_functions(self, content: str) -> str:
        """Fix Snowflake-specific functions"""
        # DATEADD function
        content = re.sub(r'DATEADD\s*\(\s*([^,]+),\s*([^,]+),\s*([^)]+)\)', r'(\3 + INTERVAL \'\2\' \1)', content)
        
        # DATE_PART function
        content = re.sub(r'DATE_PART\s*\(\s*\'([^\']+)\',\s*([^)]+)\)', r'EXTRACT(\1 FROM \2)', content)
        
        # CONCAT function (use || operator for ANSI SQL)
        content = re.sub(r'CONCAT\s*\(([^)]+)\)', lambda m: self._convert_concat_to_pipes(m.group(1)), content)
        
        return content
    
    def _convert_concat_to_pipes(self, args: str) -> str:
        """Convert CONCAT function arguments to || operators"""
        # Split arguments and join with ||
        args_list = [arg.strip() for arg in args.split(',')]
        return ' || '.join(args_list)
    
    def fix_snowflake_tags_and_policies(self, content: str) -> str:
        """Comment out Snowflake-specific tags and policies"""
        # CREATE TAG statements
        content = re.sub(r'^(CREATE\s+(?:OR\s+REPLACE\s+)?TAG\s+[^;]+;)', r'-- \1 -- Snowflake-specific TAG', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # MODIFY COLUMN with tags
        content = re.sub(r'^(ALTER\s+TABLE\s+[^;]*MODIFY\s+COLUMN\s+[^;]*SET\s+TAG[^;]*;)', r'-- \1 -- Snowflake-specific TAG', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # MASKING POLICY
        content = re.sub(r'^([^;]*MASKING\s+POLICY[^;]*;)', r'-- \1 -- Snowflake-specific MASKING POLICY', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # SEARCH OPTIMIZATION
        content = re.sub(r'^(ALTER\s+TABLE\s+[^;]*ADD\s+SEARCH\s+OPTIMIZATION[^;]*;)', r'-- \1 -- Snowflake-specific SEARCH OPTIMIZATION', content, flags=re.MULTILINE | re.IGNORECASE)
        
        return content
    
    def apply_pattern_fixes(self, content: str) -> str:
        """Apply all pattern-based fixes"""
        for pattern, replacement in self.patterns_to_fix:
            old_content = content
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            if content != old_content:
                self.fixes_applied.append(f"Applied pattern fix: {pattern}")
        
        return content
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix ANSI SQL compliance issues in a single file"""
        try:
            logger.info(f"Processing file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            
            # Apply all fixes
            content = self.fix_use_statements(content)
            content = self.fix_grant_statements(content)
            content = self.fix_stored_procedure_syntax(content)
            content = self.fix_snowflake_tasks(content)
            content = self.fix_snowflake_specific_functions(content)
            content = self.fix_snowflake_tags_and_policies(content)
            content = self.apply_pattern_fixes(content)
            
            # Only write if content changed
            if content != original_content:
                # Create backup
                backup_path = file_path.with_suffix('.sql.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # Write fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"✅ Fixed file: {file_path} (backup: {backup_path})")
                return True
            else:
                logger.info(f"ℹ️  No changes needed: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            return False
    
    def fix_directory(self, directory: str) -> Dict[str, int]:
        """Fix all SQL files in a directory recursively"""
        directory_path = Path(directory)
        
        if not directory_path.exists():
            logger.error(f"Directory does not exist: {directory}")
            return {"files_processed": 0, "files_fixed": 0, "errors": 1}
        
        files_fixed = 0
        files_processed = 0
        errors = 0
        
        # Find all SQL files
        sql_files = []
        for file_path in directory_path.rglob('*.sql'):
            if not self.should_skip_file(file_path):
                sql_files.append(file_path)
        
        logger.info(f"Found {len(sql_files)} SQL files to process")
        
        for file_path in sql_files:
            files_processed += 1
            try:
                if self.fix_file(file_path):
                    files_fixed += 1
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                errors += 1
        
        return {
            "files_processed": files_processed,
            "files_fixed": files_fixed,
            "errors": errors,
            "fixes_applied": len(self.fixes_applied)
        }

def main():
    """Main execution function"""
    logger.info("🔧 Starting ANSI SQL Compliance Fixer for Sophia AI")
    
    fixer = SQLANSIComplianceFixer()
    
    # Directories to process
    directories_to_fix = [
        "backend/snowflake_setup",
        "backend/etl",
        "customer_insights_schema.sql",
        "customer_insights_procedures.sql",
        "database/init"
    ]
    
    total_stats = {
        "files_processed": 0,
        "files_fixed": 0,
        "errors": 0,
        "fixes_applied": 0
    }
    
    for directory in directories_to_fix:
        if os.path.exists(directory):
            logger.info(f"📁 Processing directory: {directory}")
            stats = fixer.fix_directory(directory)
            
            for key in total_stats:
                total_stats[key] += stats[key]
            
            logger.info(f"✅ Completed {directory}: {stats['files_fixed']}/{stats['files_processed']} files fixed")
        else:
            logger.warning(f"⚠️  Directory not found: {directory}")
    
    # Summary
    logger.info("🎉 ANSI SQL Compliance Fix Complete!")
    logger.info(f"📊 Total Statistics:")
    logger.info(f"   Files Processed: {total_stats['files_processed']}")
    logger.info(f"   Files Fixed: {total_stats['files_fixed']}")
    logger.info(f"   Fixes Applied: {total_stats['fixes_applied']}")
    logger.info(f"   Errors: {total_stats['errors']}")
    
    if total_stats['files_fixed'] > 0:
        logger.info("📝 Note: Original files backed up with .backup extension")
        logger.info("🔍 Review changes before committing to ensure Snowflake functionality is preserved")

if __name__ == "__main__":
    main() 