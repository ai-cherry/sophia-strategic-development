#!/usr/bin/env python3
"""
Immediate Snowflake Connectivity Fix
Addresses the 404 errors by updating configuration to correct account details
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.auto_esc_config import get_config_value

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SnowflakeConnectivityFixer:
    """Fix Snowflake connectivity issues"""
    
    def __init__(self):
        self.correct_config = {
            "account": "ZNB04675",
            "user": "SCOOBYJAVA15", 
            "database": "SOPHIA_AI_PROD",
            "warehouse": "SOPHIA_AI_WH",
            "role": "ACCOUNTADMIN",
            "schema": "PROCESSED_AI"
        }
        
    async def diagnose_current_config(self):
        """Diagnose current Snowflake configuration"""
        logger.info("🔍 Diagnosing current Snowflake configuration...")
        
        current_config = {
            "account": get_config_value("snowflake_account"),
            "user": get_config_value("snowflake_user"),
            "database": get_config_value("snowflake_database", "SOPHIA_AI"),
            "warehouse": get_config_value("snowflake_warehouse", "COMPUTE_WH"),
            "role": get_config_value("snowflake_role", "SYSADMIN"),
        }
        
        logger.info("📊 Current Configuration:")
        for key, value in current_config.items():
            status = "✅" if value == self.correct_config.get(key) else "❌"
            logger.info(f"  {status} {key}: {value}")
            
        logger.info("�� Correct Configuration:")
        for key, value in self.correct_config.items():
            logger.info(f"  ✅ {key}: {value}")
            
        return current_config
    
    async def test_snowflake_connection(self, config_dict):
        """Test Snowflake connection with given configuration"""
        try:
            import snowflake.connector
            
            logger.info(f"🔗 Testing connection to {config_dict['account']}...")
            
            connection = snowflake.connector.connect(
                account=config_dict["account"],
                user=config_dict["user"],
                password=get_config_value("snowflake_password"),
                role=config_dict.get("role", "ACCOUNTADMIN"),
                warehouse=config_dict.get("warehouse", "SOPHIA_AI_WH"),
                database=config_dict.get("database", "SOPHIA_AI_PROD"),
                timeout=10
            )
            
            cursor = connection.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            result = cursor.fetchone()
            
            logger.info(f"✅ Connection successful! Snowflake version: {result[0]}")
            
            cursor.close()
            connection.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    async def update_environment_variables(self):
        """Update environment variables with correct configuration"""
        logger.info("🔧 Updating environment variables...")
        
        env_updates = {
            "SNOWFLAKE_ACCOUNT": self.correct_config["account"],
            "SNOWFLAKE_USER": self.correct_config["user"],
            "SNOWFLAKE_DATABASE": self.correct_config["database"],
            "SNOWFLAKE_WAREHOUSE": self.correct_config["warehouse"],
            "SNOWFLAKE_ROLE": self.correct_config["role"],
            "SNOWFLAKE_SCHEMA": self.correct_config["schema"],
        }
        
        for key, value in env_updates.items():
            os.environ[key] = value
            logger.info(f"  ✅ Set {key}={value}")
    
    async def fix_connectivity(self):
        """Main fix process"""
        logger.info("🚀 Starting Snowflake connectivity fix...")
        
        # 1. Diagnose current configuration
        current_config = await self.diagnose_current_config()
        
        # 2. Test correct configuration
        logger.info("🧪 Testing correct configuration...")
        correct_works = await self.test_snowflake_connection(self.correct_config)
        
        if correct_works:
            logger.info("✅ Correct configuration works!")
            # 3. Update environment variables
            await self.update_environment_variables()
            return True
        else:
            logger.error("❌ Correct configuration fails - check credentials!")
            return False


async def main():
    """Main execution function"""
    fixer = SnowflakeConnectivityFixer()
    success = await fixer.fix_connectivity()
    
    if success:
        print("\n🎯 SNOWFLAKE CONNECTIVITY FIXED!")
        print("✅ Environment variables updated with correct configuration")
        print("✅ Ready to restart application")
        sys.exit(0)
    else:
        print("\n🚨 MANUAL INTERVENTION REQUIRED:")
        print("1. Verify Snowflake credentials")
        print("2. Check account permissions")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
