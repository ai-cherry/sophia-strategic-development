#!/usr/bin/env python3
"""
Validate Gong DDL Script

Simple validation script to check the Manus AI DDL file syntax and structure
without requiring Snowflake credentials.
"""

import re
import sys
from pathlib import Path

def validate_ddl_file(file_path: str) -> dict:
    """Validate the DDL file structure and syntax"""
    
    results = {
        "success": True,
        "file_exists": False,
        "file_size": 0,
        "statements_count": 0,
        "tables_found": [],
        "procedures_found": [],
        "tasks_found": [],
        "indexes_found": [],
        "errors": []
    }
    
    try:
        # Check if file exists
        ddl_path = Path(file_path)
        if not ddl_path.exists():
            results["success"] = False
            results["errors"].append(f"DDL file not found: {file_path}")
            return results
        
        results["file_exists"] = True
        results["file_size"] = ddl_path.stat().st_size
        
        # Read and analyze the file
        with open(ddl_path, 'r') as file:
            content = file.read()
        
        # Split into statements
        statements = [stmt.strip() for stmt in content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        results["statements_count"] = len(statements)
        
        # Analyze each statement
        for statement in statements:
            statement_upper = statement.upper()
            
            # Find tables
            if 'CREATE TABLE' in statement_upper:
                table_match = re.search(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\S+)', statement_upper)
                if table_match:
                    results["tables_found"].append(table_match.group(1))
            
            # Find procedures
            if 'CREATE OR REPLACE PROCEDURE' in statement_upper:
                proc_match = re.search(r'CREATE OR REPLACE PROCEDURE\s+(\S+)', statement_upper)
                if proc_match:
                    results["procedures_found"].append(proc_match.group(1))
            
            # Find tasks
            if 'CREATE OR REPLACE TASK' in statement_upper:
                task_match = re.search(r'CREATE OR REPLACE TASK\s+(\S+)', statement_upper)
                if task_match:
                    results["tasks_found"].append(task_match.group(1))
            
            # Find indexes
            if 'CREATE INDEX' in statement_upper:
                index_match = re.search(r'CREATE INDEX\s+(?:IF NOT EXISTS\s+)?(\S+)', statement_upper)
                if index_match:
                    results["indexes_found"].append(index_match.group(1))
        
        # Validate expected components
        expected_tables = [
            'RAW_GONG_CALLS_RAW',
            'RAW_GONG_CALL_TRANSCRIPTS_RAW', 
            'STG_GONG_CALLS',
            'STG_GONG_CALL_TRANSCRIPTS'
        ]
        
        expected_procedures = [
            'TRANSFORM_RAW_GONG_CALLS',
            'TRANSFORM_RAW_GONG_TRANSCRIPTS',
            'ENRICH_GONG_CALLS_WITH_AI'
        ]
        
        expected_tasks = [
            'TASK_TRANSFORM_GONG_CALLS',
            'TASK_TRANSFORM_GONG_TRANSCRIPTS',
            'TASK_AI_ENRICH_GONG_CALLS'
        ]
        
        # Check for missing components
        for table in expected_tables:
            if not any(table in found_table for found_table in results["tables_found"]):
                results["errors"].append(f"Missing expected table: {table}")
        
        for procedure in expected_procedures:
            if not any(procedure in found_proc for found_proc in results["procedures_found"]):
                results["errors"].append(f"Missing expected procedure: {procedure}")
        
        for task in expected_tasks:
            if not any(task in found_task for found_task in results["tasks_found"]):
                results["errors"].append(f"Missing expected task: {task}")
        
        # Check for syntax issues
        if 'VECTOR(FLOAT, 768)' not in content:
            results["errors"].append("Missing AI Memory embedding vector columns")
        
        if 'SNOWFLAKE.CORTEX.' not in content:
            results["errors"].append("Missing Snowflake Cortex AI functions")
        
        if results["errors"]:
            results["success"] = False
        
        return results
        
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Validation error: {str(e)}")
        return results

def main():
    """Main validation function"""
    ddl_file_path = "../backend/snowflake_setup/manus_ai_final_gong_ddl_v2.sql"
    
    print("🔍 Validating Manus AI Gong DDL v2.0...")
    print(f"📁 File: {ddl_file_path}")
    print("="*80)
    
    results = validate_ddl_file(ddl_file_path)
    
    # Print results
    if results["file_exists"]:
        print(f"✅ File exists: {results['file_size']:,} bytes")
        print(f"📊 Statements found: {results['statements_count']}")
        print(f"🗂️  Tables found: {len(results['tables_found'])}")
        for table in results["tables_found"]:
            print(f"   • {table}")
        
        print(f"⚙️  Procedures found: {len(results['procedures_found'])}")
        for procedure in results["procedures_found"]:
            print(f"   • {procedure}")
        
        print(f"⏰ Tasks found: {len(results['tasks_found'])}")
        for task in results["tasks_found"]:
            print(f"   • {task}")
        
        print(f"📇 Indexes found: {len(results['indexes_found'])}")
        for index in results["indexes_found"]:
            print(f"   • {index}")
    
    print("\n" + "="*80)
    
    if results["success"]:
        print("✅ DDL VALIDATION SUCCESSFUL!")
        print("🎯 All expected components found")
        print("🚀 Ready for Snowflake deployment")
    else:
        print("❌ DDL VALIDATION FAILED!")
        print("🚨 Issues found:")
        for error in results["errors"]:
            print(f"   • {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
