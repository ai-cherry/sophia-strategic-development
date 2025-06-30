#!/usr/bin/env python3
"""
Snowflake PAT Token Connection Test
Test different PAT token formats
"""

import snowflake.connector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_pat_connection():
    """Test Snowflake connection with PAT token."""

    # Credentials from user
    account = "UHDECNO-CVB64222"
    user = "SCOOBYJAVA15"
    role = "ACCOUNTADMIN"

    # PAT token components
    password_prefix = "Huskers1983Huskers1983"
    jwt_token = "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A"

    # Test different PAT formats
    test_formats = [
        # Format 1: Combined password + JWT
        f"{password_prefix}{jwt_token}",
        # Format 2: Just the JWT token
        jwt_token,
        # Format 3: Just the password prefix
        password_prefix,
        # Format 4: JWT with Bearer prefix
        f"Bearer {jwt_token}",
    ]

    for i, password_format in enumerate(test_formats, 1):
        logger.info(f"🔍 Testing PAT format {i}: {password_format[:50]}...")

        try:
            conn = snowflake.connector.connect(
                account=account, user=user, password=password_format, role=role
            )

            logger.info(f"✅ SUCCESS with format {i}!")

            # Test basic query
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()")
            result = cursor.fetchone()

            logger.info(f"✅ Connection details:")
            logger.info(f"   Account: {result[0]}")
            logger.info(f"   User: {result[1]}")
            logger.info(f"   Role: {result[2]}")

            cursor.close()
            conn.close()

            return password_format

        except Exception as e:
            logger.error(f"❌ Format {i} failed: {e}")
            continue

    logger.error("❌ All PAT formats failed")
    return None


def test_authenticator_methods():
    """Test different authenticator methods for PAT."""

    account = "UHDECNO-CVB64222"
    user = "SCOOBYJAVA15"
    role = "ACCOUNTADMIN"
    jwt_token = "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A"

    # Test with JWT authenticator
    logger.info("🔍 Testing with JWT authenticator...")

    try:
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            token=jwt_token,  # Use token parameter instead of password
            authenticator="oauth",
            role=role,
        )

        logger.info("✅ SUCCESS with JWT authenticator!")

        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()")
        result = cursor.fetchone()

        logger.info(f"✅ Connection details:")
        logger.info(f"   Account: {result[0]}")
        logger.info(f"   User: {result[1]}")
        logger.info(f"   Role: {result[2]}")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        logger.error(f"❌ JWT authenticator failed: {e}")

    # Test with external browser (for PAT)
    logger.info("🔍 Testing with external_browser authenticator...")

    try:
        conn = snowflake.connector.connect(
            account=account, user=user, authenticator="externalbrowser", role=role
        )

        logger.info("✅ SUCCESS with external browser authenticator!")
        return True

    except Exception as e:
        logger.error(f"❌ External browser authenticator failed: {e}")

    return False


if __name__ == "__main__":
    logger.info("🚀 Starting PAT token connection tests")

    # Test different password formats
    working_format = test_pat_connection()

    if working_format:
        logger.info(f"🎉 Working PAT format found: {working_format[:50]}...")
    else:
        logger.info("🔍 Testing alternative authenticator methods...")
        test_authenticator_methods()
