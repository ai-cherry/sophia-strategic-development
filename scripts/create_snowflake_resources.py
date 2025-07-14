#!/usr/bin/env python3
"""
Create and configure ModernStack resources for Sophia AI
"""
import os
# REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3
from pathlib import Path

# Load environment
env_file = Path(__file__).parent.parent / "local.env"
if env_file.exists():
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value.strip('"').strip("'")

print("🔍 Setting up ModernStack resources for Sophia AI...")

try:
    conn = self.modern_stack_connection(
        account=os.environ.get("modern_stack_ACCOUNT"),
        user=os.environ.get("modern_stack_USER"),
        password=os.environ.get("modern_stack_PAT"),
        role=os.environ.get("modern_stack_ROLE", "ACCOUNTADMIN"),
    )

    cursor = conn.cursor()

    # Create warehouse
    print("\n🏭 Creating warehouse...")
    cursor.execute(
        """
        CREATE WAREHOUSE IF NOT EXISTS SOPHIA_AI_COMPUTE_WH
        WITH WAREHOUSE_SIZE = 'XSMALL'
        AUTO_SUSPEND = 60
        AUTO_RESUME = TRUE
        INITIALLY_SUSPENDED = FALSE
        COMMENT = 'Warehouse for Sophia AI computations'
    """
    )
    print("✅ Warehouse SOPHIA_AI_COMPUTE_WH created/verified")

    # Use the warehouse
    cursor.execute("USE WAREHOUSE SOPHIA_AI_COMPUTE_WH")
    print("✅ Using warehouse SOPHIA_AI_COMPUTE_WH")

    # Create database if needed
    cursor.execute("CREATE DATABASE IF NOT EXISTS AI_MEMORY")
    cursor.execute("USE DATABASE AI_MEMORY")
    print("✅ Using database AI_MEMORY")

    # Create schemas
    schemas = ["VECTORS", "KNOWLEDGE", "CORTEX", "MEMORY", "MONITORING"]
    for schema in schemas:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        print(f"✅ Schema {schema} created/verified")

    # Use VECTORS schema
    cursor.execute("USE SCHEMA VECTORS")

    # Create tables
    print("\n📋 Creating tables...")

    # Knowledge base table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS KNOWLEDGE_BASE (
            id VARCHAR PRIMARY KEY,
            content TEXT,
            embedding ARRAY,
            metadata VARIANT,
            source VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
    """
    )
    print("✅ Table KNOWLEDGE_BASE created/verified")

    # Memory records table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS MEMORY_RECORDS (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR,
            session_id VARCHAR,
            content TEXT,
            embedding ARRAY,
            metadata VARIANT,
            memory_type VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
    """
    )
    print("✅ Table MEMORY_RECORDS created/verified")

    # Business intelligence table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS BUSINESS_INSIGHTS (
            id VARCHAR PRIMARY KEY,
            insight_type VARCHAR,
            content TEXT,
            embedding ARRAY,
            metadata VARIANT,
            confidence_score FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
    """
    )
    print("✅ Table BUSINESS_INSIGHTS created/verified")

    # Test the setup
    print("\n🧪 Testing setup...")
    cursor.execute(
        """
        INSERT INTO KNOWLEDGE_BASE (id, content, source, metadata)
        SELECT 'test_' || CURRENT_TIMESTAMP()::VARCHAR, 
               'Sophia AI is operational with ModernStack!',
               'system_test',
               OBJECT_CONSTRUCT('test', TRUE, 'version', '4.0.0')
    """
    )
    print("✅ Test data inserted")

    # Query back
    cursor.execute("SELECT COUNT(*) FROM KNOWLEDGE_BASE")
    count = cursor.fetchone()[0]
    print(f"✅ Knowledge base has {count} records")

    # Show final status
    print("\n📊 Final Status:")
    cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()")
    db, schema, warehouse = cursor.fetchone()
    print(f"   Database: {db}")
    print(f"   Schema: {schema}")
    print(f"   Warehouse: {warehouse}")

    cursor.close()
    conn.close()

    print("\n✅ All ModernStack resources are ready!")
    print("\n📝 Configuration to use:")
    print("   # REMOVED: ModernStack dependencySOPHIA_AI_COMPUTE_WH")
    print("   # REMOVED: ModernStack dependencyAI_MEMORY")
    print("   # REMOVED: ModernStack dependencyVECTORS")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()
