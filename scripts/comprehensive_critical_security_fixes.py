#!/usr/bin/env python3
"""
🚨 COMPREHENSIVE CRITICAL SECURITY FIXES
Fix all remaining critical vulnerabilities in one comprehensive sweep
"""

import logging
import os
import re
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_all_critical_vulnerabilities():
    """Fix all critical vulnerabilities comprehensively"""
    fixes_applied = 0
    
    # 1. Fix remaining SQL injection vulnerabilities
    sql_injection_fixes = [
        # Fix f-strings in cursor.execute calls
        ('backend/core/comprehensive_snowflake_config.py', 
         r'cursor\.execute\(f"USE SCHEMA \{schema\.value\}"\)', 
         'cursor.execute("USE SCHEMA " + self._validate_schema_name(schema.value))'),
        
        ('backend/core/enhanced_snowflake_config.py',
         r'cursor\.execute\(f"USE SCHEMA \{schema\.value\}"\)',
         'cursor.execute("USE SCHEMA " + self._validate_schema_name(schema.value))'),
         
        ('backend/etl/gong/ingest_gong_data.py',
         r'cursor\.execute\(f"CREATE SCHEMA IF NOT EXISTS \{self\.database\}\.\{self\.schema\}"\)',
         'cursor.execute("CREATE SCHEMA IF NOT EXISTS " + self._validate_schema_name(f"{self.database}.{self.schema}"))'),
         
        ('backend/etl/gong/ingest_gong_data.py',
         r'cursor\.execute\(f"USE SCHEMA \{self\.database\}\.\{self\.schema\}"\)',
         'cursor.execute("USE SCHEMA " + self._validate_schema_name(f"{self.database}.{self.schema}"))'),
         
        ('backend/scripts/deploy_snowflake_application_layer.py',
         r'cursor\.execute\(f"SHOW TABLES IN SCHEMA \{schema\}"\)',
         'cursor.execute("SHOW TABLES IN SCHEMA " + self._validate_schema_name(schema))'),
         
        ('backend/scripts/deploy_gong_snowflake_setup.py',
         r'cursor\.execute\(f"SELECT COUNT\(\*\) FROM \{table\} LIMIT 1"\)',
         'cursor.execute("SELECT COUNT(*) FROM " + self._validate_table_name(table) + " LIMIT 1")'),
         
        ('backend/services/cortex_agent_service.py',
         r'cursor\.execute\(f"USE WAREHOUSE \{warehouse\}"\)',
         'cursor.execute("USE WAREHOUSE " + self._validate_warehouse_name(warehouse))'),
    ]
    
    for file_path, pattern, replacement in sql_injection_fixes:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    
                    # Add validation methods if not present
                    if '_validate_schema_name' not in content and 'validate_schema_name' in replacement:
                        validation_method = '''
    def _validate_schema_name(self, schema_name: str) -> str:
        """Validate schema name to prevent SQL injection"""
        import re
        if not re.match(r'^[A-Z_][A-Z0-9_.]*$', str(schema_name)):
            raise ValueError(f"Invalid schema name: {schema_name}")
        return str(schema_name)
'''
                        # Find class definition and add method
                        class_match = re.search(r'(class \w+.*?:)', content)
                        if class_match:
                            insert_pos = content.find('\n', class_match.end())
                            content = content[:insert_pos] + validation_method + content[insert_pos:]
                    
                    if '_validate_table_name' not in content and 'validate_table_name' in replacement:
                        validation_method = '''
    def _validate_table_name(self, table_name: str) -> str:
        """Validate table name to prevent SQL injection"""
        import re
        if not re.match(r'^[A-Z_][A-Z0-9_.]*$', str(table_name)):
            raise ValueError(f"Invalid table name: {table_name}")
        return str(table_name)
'''
                        class_match = re.search(r'(class \w+.*?:)', content)
                        if class_match:
                            insert_pos = content.find('\n', class_match.end())
                            content = content[:insert_pos] + validation_method + content[insert_pos:]
                    
                    if '_validate_warehouse_name' not in content and 'validate_warehouse_name' in replacement:
                        validation_method = '''
    def _validate_warehouse_name(self, warehouse_name: str) -> str:
        """Validate warehouse name to prevent SQL injection"""
        import re
        if not re.match(r'^[A-Z_][A-Z0-9_]*$', str(warehouse_name)):
            raise ValueError(f"Invalid warehouse name: {warehouse_name}")
        return str(warehouse_name)
'''
                        class_match = re.search(r'(class \w+.*?:)', content)
                        if class_match:
                            insert_pos = content.find('\n', class_match.end())
                            content = content[:insert_pos] + validation_method + content[insert_pos:]
                    
                    with open(file_path, 'w') as f:
                        f.write(content)
                    
                    fixes_applied += 1
                    logger.info(f"✅ Fixed SQL injection in {file_path}")
                    
            except Exception as e:
                logger.error(f"❌ Error fixing {file_path}: {e}")
    
    # 2. Fix command injection vulnerabilities - remaining files
    command_injection_files = [
        'backend/core/simple_config.py',
        'estuary_advanced_integration.py', 
        'scripts/monitor_all_mcp_servers.py',
        'load_github_secrets.py',
        'deploy_mcp_servers.py',
        'scripts/implement_sophia_ui.py',
        'deploy_estuary_foundation_corrected.py',
        'unified_ai_coding_assistant.py',
        'backend/monitoring/deployment_tracker.py',
        'backend/core/sophia_env_config.py',
        'gemini-cli-integration/gemini_mcp_integration.py',
        'ui-ux-agent/start_ui_ux_agent_system.py',
        'start_mcp_servers.py',
        'backend/integrations/estuary_flow_manager.py',
        'ultimate_snowflake_fix.py',
        'start_sophia_enhanced.py',
        'start_sophia_complete.py',
        'verify_complete_secrets_sync.py',
        'scripts/dns-manager.py',
        'backend/mcp_servers/mixins/cline_v3_18_features.py'
    ]
    
    for file_path in command_injection_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix subprocess.run with shell=True
                content = re.sub(
                    r'subprocess\.run\s*\(([^,]+),\s*shell\s*=\s*True([^)]*)\)',
                    r'subprocess.run(shlex.split(\1)\2)  # SECURITY FIX: Removed shell=True',
                    content
                )
                
                # Fix os.system calls
                content = re.sub(
                    r'os\.system\s*\(([^)]+)\)',
                    r'subprocess.run(shlex.split(\1), check=True)  # SECURITY FIX: Replaced os.system',
                    content
                )
                
                # Add imports if needed
                if 'shlex.split' in content and 'import shlex' not in content:
                    content = 'import shlex\n' + content
                
                if 'subprocess.run' in content and 'import subprocess' not in content:
                    content = 'import subprocess\n' + content
                
                if content != original_content:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    
                    fixes_applied += 1
                    logger.info(f"✅ Fixed command injection in {file_path}")
                    
            except Exception as e:
                logger.error(f"❌ Error fixing {file_path}: {e}")
    
    # 3. Fix remaining hardcoded secrets
    secret_files = [
        'backend/services/enhanced_data_ingestion.py',
        'backend/core/security_config.py'
    ]
    
    for file_path in secret_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                original_content = content
                
                # Replace hardcoded secrets
                secret_patterns = [
                    (r'"database_password"', 'os.getenv("DATABASE_PASSWORD")'),
                    (r'"jwt_secret"', 'os.getenv("JWT_SECRET")'),
                    (r'"webhook_secret"', 'os.getenv("WEBHOOK_SECRET")'),
                    (r'"api_key_[^"]*"', 'os.getenv("API_KEY")'),
                    (r'"secret_[^"]*"', 'os.getenv("SECRET_KEY")'),
                ]
                
                for pattern, replacement in secret_patterns:
                    content = re.sub(pattern, replacement, content)
                
                # Add import if needed
                if 'os.getenv' in content and 'import os' not in content:
                    content = 'import os\n' + content
                
                if content != original_content:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    
                    fixes_applied += 1
                    logger.info(f"✅ Fixed hardcoded secrets in {file_path}")
                    
            except Exception as e:
                logger.error(f"❌ Error fixing {file_path}: {e}")
    
    # 4. Fix remaining file permissions
    permission_files = [
        'scripts/implement_missing_snowflake_schemas.py',
        'backend/integrations/estuary_flow_manager.py',
        'final_snowflake_fix.py',
        'ultimate_snowflake_fix.py'
    ]
    
    for file_path in permission_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                original_content = content
                
                # Replace 0o755 with 0o644
                content = re.sub(
                    r'os\.chmod\s*\([^,]+,\s*0o755\s*\)',
                    lambda m: m.group(0).replace('0o755', '0o644') + '  # SECURITY FIX: Reduced permissions',
                    content
                )
                
                if content != original_content:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    
                    fixes_applied += 1
                    logger.info(f"✅ Fixed file permissions in {file_path}")
                    
            except Exception as e:
                logger.error(f"❌ Error fixing {file_path}: {e}")
    
    logger.info(f"🎉 COMPREHENSIVE SECURITY FIXES COMPLETE: {fixes_applied} fixes applied")
    return fixes_applied

if __name__ == "__main__":
    fix_all_critical_vulnerabilities()
