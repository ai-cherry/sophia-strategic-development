#!/usr/bin/env python3
"""
Simple Snowflake Connection Test
Test the corrected configuration with proper interface
"""

import asyncio
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_snowflake_connection():
    """Test Snowflake connection using OptimizedConnectionManager"""
    logger.info("🔗 Testing Snowflake connection with corrected configuration...")
    
    try:
        from backend.core.optimized_connection_manager import OptimizedConnectionManager, ConnectionType
        
        # Initialize connection manager
        manager = OptimizedConnectionManager()
        await manager.initialize()
        
        # Test connection using context manager
        async with manager.get_connection(ConnectionType.SNOWFLAKE) as conn:
            logger.info("✅ Snowflake connection successful!")
            
            # Test a simple query
            try:
                # Execute a simple test query
                cursor = conn.cursor()
                cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_DATABASE()")
                result = cursor.fetchone()
                cursor.close()
                
                logger.info(f"✅ Query successful:")
                logger.info(f"   Account: {result[0]}")
                logger.info(f"   User: {result[1]}")
                logger.info(f"   Database: {result[2]}")
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Query failed: {e}")
                return False
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False

async def main():
    """Main test function"""
    # Set environment variables
    os.environ['SNOWFLAKE_ACCOUNT'] = 'ZNB04675'
    os.environ['SNOWFLAKE_USER'] = 'SCOOBYJAVA15'
    os.environ['SNOWFLAKE_ROLE'] = 'ACCOUNTADMIN'
    os.environ['SNOWFLAKE_WAREHOUSE'] = 'SOPHIA_AI_WH'
    os.environ['SNOWFLAKE_DATABASE'] = 'SOPHIA_AI'
    os.environ['SNOWFLAKE_SCHEMA'] = 'PROCESSED_AI'
    
    logger.info("🚀 Starting simple Snowflake connection test...")
    
    success = await test_snowflake_connection()
    
    if success:
        logger.info("🎉 Snowflake connection test PASSED!")
        logger.info("✅ System ready for Cursor AI implementation")
    else:
        logger.error("❌ Snowflake connection test FAILED")
        logger.error("   Manual investigation required")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
