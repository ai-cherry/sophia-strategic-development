import os
import snowflake.connector
import sys

try:
    conn = snowflake.connector.connect(
        account=os.environ.get("SNOWFLAKE_ACCOUNT"),
        user=os.environ.get("SNOWFLAKE_USER"),
        password=os.environ.get("SNOWFLAKE_PAT"),  # Use PAT as password
        role=os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "SOPHIA_AI_COMPUTE_WH"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "AI_MEMORY"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "VECTORS"),
    )

    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION()")
    version = cursor.fetchone()[0]
    print(f"✅ Snowflake connection successful! Version: {version}")

    # Create warehouse if it doesn't exist
    cursor.execute("SHOW WAREHOUSES LIKE 'SOPHIA_AI_COMPUTE_WH'")
    if not cursor.fetchone():
        print("Creating SOPHIA_AI_COMPUTE_WH warehouse...")
        cursor.execute(
            """
            CREATE WAREHOUSE IF NOT EXISTS SOPHIA_AI_COMPUTE_WH
            WITH WAREHOUSE_SIZE = 'XSMALL'
            AUTO_SUSPEND = 60
            AUTO_RESUME = TRUE
        """
        )
        print("✅ Warehouse created")

    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS AI_MEMORY")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS AI_MEMORY.VECTORS")
    print("✅ Database and schema ready")

    cursor.close()
    conn.close()
    sys.exit(0)

except Exception as e:
    print(f"❌ Snowflake connection failed: {e}")
    sys.exit(1)
