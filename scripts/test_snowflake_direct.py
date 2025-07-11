#!/usr/bin/env python3
"""
Test Snowflake Connection Directly
Verify we can connect to Snowflake with the provided credentials
"""

import snowflake.connector
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_snowflake_connection():
    """Test direct Snowflake connection"""

    # Credentials
    account = "UHDECNO-CVB64222"
    user = "SCOOBYJAVA15"
    pat_token = "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A"

    print("🧪 TESTING DIRECT SNOWFLAKE CONNECTION")
    print("=" * 60)
    print(f"Account: {account}")
    print(f"User: {user}")
    print(f"PAT Token: {pat_token[:20]}...{pat_token[-20:]}")

    try:
        print("\n📡 Connecting to Snowflake...")

        # Create connection
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=pat_token,  # Use PAT as password
            role="ACCOUNTADMIN",
            warehouse="SOPHIA_AI_COMPUTE_WH",
            database="AI_MEMORY",
            schema="VECTORS",
        )

        print("✅ Connected successfully!")

        # Test query
        cursor = conn.cursor()

        # Get version
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()
        print(f"\n📊 Snowflake Version: {version[0] if version else 'Unknown'}")

        # Get current database info
        cursor.execute(
            "SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()"
        )
        db_info = cursor.fetchone()
        print(f"Database: {db_info[0]}")
        print(f"Schema: {db_info[1]}")
        print(f"Warehouse: {db_info[2]}")

        # Check if AI_MEMORY database exists
        cursor.execute("SHOW DATABASES LIKE 'AI_MEMORY'")
        databases = cursor.fetchall()

        if not databases:
            print("\n🔨 Creating AI_MEMORY database...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS AI_MEMORY")
            print("✅ Database created")

        # Use AI_MEMORY database
        cursor.execute("USE DATABASE AI_MEMORY")

        # Check for VECTORS schema
        cursor.execute("SHOW SCHEMAS LIKE 'VECTORS'")
        schemas = cursor.fetchall()

        if not schemas:
            print("\n🔨 Creating VECTORS schema...")
            cursor.execute("CREATE SCHEMA IF NOT EXISTS VECTORS")
            print("✅ Schema created")

        cursor.execute("USE SCHEMA VECTORS")

        # Create knowledge base table if not exists
        print("\n🔨 Creating KNOWLEDGE_BASE table if not exists...")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS KNOWLEDGE_BASE (
            id VARCHAR PRIMARY KEY DEFAULT UUID_STRING(),
            content TEXT NOT NULL,
            embedding VECTOR(FLOAT, 768),
            source VARCHAR,
            metadata VARIANT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """

        cursor.execute(create_table_sql)
        print("✅ Table ready")

        # Test Cortex embedding
        print("\n🧠 Testing Snowflake Cortex embedding...")
        test_text = "Sophia AI deployment successful on July 10, 2025"

        try:
            cursor.execute(
                """
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s) as embedding
            """,
                (test_text,),
            )

            result = cursor.fetchone()
            if result:
                print("✅ Cortex embedding working!")
                print("   Embedding dimension: 768")
            else:
                print("⚠️  Cortex embedding returned no result")

        except Exception as e:
            print(f"❌ Cortex embedding error: {e}")

        # Insert test data
        print("\n📝 Inserting test data...")
        insert_sql = """
        INSERT INTO KNOWLEDGE_BASE (content, source, metadata)
        VALUES (%s, %s, PARSE_JSON(%s))
        """

        import json

        metadata = {
            "type": "deployment_test",
            "timestamp": "2025-07-10T17:30:00Z",
            "system": "sophia_ai",
        }

        cursor.execute(
            insert_sql,
            (
                "Sophia AI full deployment completed with Snowflake integration",
                "deployment_script",
                json.dumps(metadata),
            ),
        )

        print("✅ Test data inserted")

        # Query the data
        print("\n🔍 Querying test data...")
        cursor.execute(
            """
            SELECT id, content, source, metadata, created_at
            FROM KNOWLEDGE_BASE
            ORDER BY created_at DESC
            LIMIT 5
        """
        )

        rows = cursor.fetchall()
        print(f"Found {len(rows)} records:")

        for row in rows:
            print(f"\n   ID: {row[0]}")
            print(f"   Content: {row[1][:100]}...")
            print(f"   Source: {row[2]}")
            print(f"   Created: {row[4]}")

        cursor.close()
        conn.close()

        print("\n✅ SNOWFLAKE CONNECTION TEST SUCCESSFUL!")
        print(
            "\n🎯 Next: Update UnifiedMemoryService to use these exact connection parameters"
        )

        return True

    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False


if __name__ == "__main__":
    test_snowflake_connection()
