#!/usr/bin/env python3
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

# Connect
conn = snowflake.connector.connect(
    account=os.environ.get("SNOWFLAKE_ACCOUNT"),
    user=os.environ.get("SNOWFLAKE_USER"),
    password=os.environ.get("SNOWFLAKE_PAT"),
    role="ACCOUNTADMIN",
    warehouse="SOPHIA_AI_COMPUTE_WH",
    database="AI_MEMORY",
    schema="VECTORS",
)

cursor = conn.cursor()

# Simple insert
cursor.execute(
    """
    INSERT INTO KNOWLEDGE_BASE (id, content, source)
    SELECT 'test_001', 'Sophia AI is operational', 'system_test'
"""
)

print("✅ Simple insert successful")

# Query back
cursor.execute("SELECT * FROM KNOWLEDGE_BASE WHERE id = 'test_001'")
row = cursor.fetchone()
print(f"✅ Retrieved: {row}")

cursor.close()
conn.close()
