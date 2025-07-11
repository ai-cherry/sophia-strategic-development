#!/usr/bin/env python3
"""
Test Snowflake Connection with Password
Try connecting with the regular password
"""

import snowflake.connector
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_snowflake_connection():
    """Test Snowflake connection with password"""

    # Credentials
    account = "UHDECNO-CVB64222"
    user = "Scoobyjava15"  # Note: case sensitive, using exact case from user
    password = "Huskers1983Huskers1983"

    print("🧪 TESTING SNOWFLAKE CONNECTION WITH PASSWORD")
    print("=" * 60)
    print(f"Account: {account}")
    print(f"User: {user}")
    print(f"Password: {'*' * len(password)}")

    try:
        print("\n📡 Connecting to Snowflake (AWS Oregon)...")

        # Create connection
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            role="ACCOUNTADMIN",
            warehouse="SOPHIA_AI_COMPUTE_WH",
        )

        print("✅ Connected successfully!")

        # Test query
        cursor = conn.cursor()

        # Get version
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()
        print(f"\n📊 Snowflake Version: {version[0] if version else 'Unknown'}")

        # Get current user info
        cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE()")
        user_info = cursor.fetchone()
        print(f"Current User: {user_info[0]}")
        print(f"Current Role: {user_info[1]}")

        # List available warehouses
        cursor.execute("SHOW WAREHOUSES")
        warehouses = cursor.fetchall()
        print("\n📊 Available Warehouses:")
        for wh in warehouses:
            print(f"   - {wh[0]} (Size: {wh[3]}, State: {wh[2]})")

        # Check if we need to create warehouse
        cursor.execute("SHOW WAREHOUSES LIKE 'SOPHIA_AI_COMPUTE_WH'")
        sophia_wh = cursor.fetchall()

        if not sophia_wh:
            print("\n🔨 Creating SOPHIA_AI_COMPUTE_WH...")
            cursor.execute(
                """
                CREATE WAREHOUSE IF NOT EXISTS SOPHIA_AI_COMPUTE_WH
                WITH WAREHOUSE_SIZE = 'XSMALL'
                AUTO_SUSPEND = 60
                AUTO_RESUME = TRUE
            """
            )
            print("✅ Warehouse created")

        # Use the warehouse
        cursor.execute("USE WAREHOUSE SOPHIA_AI_COMPUTE_WH")
        print("✅ Using SOPHIA_AI_COMPUTE_WH")

        # Check databases
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print("\n📊 Available Databases:")
        for db in databases[:5]:  # Show first 5
            print(f"   - {db[1]}")

        cursor.close()
        conn.close()

        print("\n✅ CONNECTION TEST SUCCESSFUL!")
        print("\n🎯 Updating configuration to use these credentials...")

        # Update local.env with working credentials
        env_file = project_root / "local.env"
        env_updates = {
            "SNOWFLAKE_ACCOUNT": account,
            "SNOWFLAKE_USER": user,
            "SNOWFLAKE_PASSWORD": password,
            "SNOWFLAKE_WAREHOUSE": "SOPHIA_AI_COMPUTE_WH",
            "SNOWFLAKE_ROLE": "ACCOUNTADMIN",
        }

        # Read existing
        lines = []
        if env_file.exists():
            with open(env_file, "r") as f:
                lines = f.readlines()

        # Update
        updated = set()
        new_lines = []
        for line in lines:
            if "=" in line:
                key = line.split("=")[0].strip()
                if key in env_updates:
                    new_lines.append(f"{key}={env_updates[key]}\n")
                    updated.add(key)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Add missing
        for key, value in env_updates.items():
            if key not in updated:
                new_lines.append(f"{key}={value}\n")

        # Write back
        with open(env_file, "w") as f:
            f.writelines(new_lines)

        print("✅ Updated local.env with working credentials")

        return True

    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")

        # Try with different user case
        if "Scoobyjava15" in str(user):
            print("\n🔄 Retrying with uppercase user...")
            return test_with_uppercase_user()

        return False


def test_with_uppercase_user():
    """Try with uppercase username"""
    account = "UHDECNO-CVB64222"
    user = "SCOOBYJAVA15"
    password = "Huskers1983Huskers1983"

    try:
        conn = snowflake.connector.connect(
            account=account, user=user, password=password, role="ACCOUNTADMIN"
        )

        print("✅ Connected with uppercase username!")

        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_USER()")
        result = cursor.fetchone()
        print(f"Current User: {result[0]}")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Uppercase also failed: {e}")
        return False


if __name__ == "__main__":
    test_snowflake_connection()
