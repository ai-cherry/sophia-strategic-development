#!/usr/bin/env python3
"""
Test Snowflake connection and show what's available
"""
import os
import snowflake.connector
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

# Connect to Snowflake
print("🔍 Connecting to Snowflake...")
try:
    conn = snowflake.connector.connect(
        account=os.environ.get("SNOWFLAKE_ACCOUNT"),
        user=os.environ.get("SNOWFLAKE_USER"),
        password=os.environ.get("SNOWFLAKE_PAT"),
        role=os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    )

    cursor = conn.cursor()

    # Show current context
    cursor.execute("SELECT CURRENT_VERSION()")
    version = cursor.fetchone()[0]
    print(f"✅ Connected! Snowflake version: {version}")

    cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_ACCOUNT()")
    user, role, account = cursor.fetchone()
    print(f"   User: {user}")
    print(f"   Role: {role}")
    print(f"   Account: {account}")

    # Show databases
    print("\n📊 Databases:")
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    for db in databases:
        print(f"   - {db[1]} (created: {db[4]})")

    # Check if AI_MEMORY exists
    cursor.execute("USE DATABASE AI_MEMORY")
    print("\n✅ Using database AI_MEMORY")

    # Show schemas
    print("\n📁 Schemas in AI_MEMORY:")
    cursor.execute("SHOW SCHEMAS")
    schemas = cursor.fetchall()
    for schema in schemas:
        print(f"   - {schema[1]}")

    # Use VECTORS schema
    cursor.execute("USE SCHEMA VECTORS")
    print("\n✅ Using schema AI_MEMORY.VECTORS")

    # Show tables
    print("\n📋 Tables in AI_MEMORY.VECTORS:")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    if tables:
        for table in tables:
            print(f"   - {table[1]} (rows: {table[5] if len(table) > 5 else 'N/A'})")
    else:
        print("   (No tables yet)")

    # Create a test table
    print("\n🔨 Creating test table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS test_connection (
            id INTEGER AUTOINCREMENT,
            message VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
    """
    )
    print("✅ Test table created")

    # Insert test data
    cursor.execute(
        """
        INSERT INTO test_connection (message) 
        VALUES ('Sophia AI connected successfully!')
    """
    )
    print("✅ Test data inserted")

    # Query it back
    cursor.execute("SELECT * FROM test_connection")
    rows = cursor.fetchall()
    print("\n📊 Test data:")
    for row in rows:
        print(f"   ID: {row[0]}, Message: {row[1]}, Created: {row[2]}")

    cursor.close()
    conn.close()
    print("\n✅ Snowflake test complete!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
