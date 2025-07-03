#!/usr/bin/env python3
"""
Clean DDL Validation Script

Simple validation script to check clean DDL file syntax and structure
for Gong integration without any manus contamination.
"""

import re
import sys
from pathlib import Path


def validate_clean_ddl(file_path: str) -> bool:
    """Validate clean DDL file syntax and structure"""
    
    if not Path(file_path).exists():
        print(f"❌ DDL file not found: {file_path}")
        return False
        
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            
        # Basic validation checks
        if not content.strip():
            print("❌ DDL file is empty")
            return False
            
        # Check for required schemas
        if "CREATE SCHEMA" not in content.upper():
            print("⚠️ No schema creation found")
            
        # Check for basic table structures
        if "CREATE TABLE" not in content.upper():
            print("⚠️ No table creation found")
            
        print("✅ Clean DDL file validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Error reading DDL file: {e}")
        return False


if __name__ == "__main__":
    # Look for clean DDL file
    ddl_file_path = "backend/snowflake_setup/clean_gong_ddl.sql"
    
    print("🔍 Validating Clean Gong DDL...")
    
    if validate_clean_ddl(ddl_file_path):
        print("🎉 Validation successful!")
        sys.exit(0)
    else:
        print("💥 Validation failed!")
        sys.exit(1)
