#!/usr/bin/env python3
"""
Test Qdrant Connection
Debug script to verify cloud connectivity
"""

import os
import sys
import logging

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core.auto_esc_config import get_qdrant_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_qdrant_connection():
    """Test Qdrant connection with debug info"""
    logger.info("🔍 Testing Qdrant Connection")
    
    try:
        config = get_qdrant_config()
        
        logger.info("📋 Qdrant Configuration:")
        logger.info(f"  URL: {config['url']}")
        logger.info(f"  API Key: {'*' * 20 if config['api_key'] else 'None'}")
        logger.info(f"  Timeout: {config['timeout']}")
        
        # Test if we can import qdrant_client
        try:
            from qdrant_client import QdrantClient
            logger.info("✅ Qdrant client imported successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import qdrant_client: {e}")
            return False
        
        # Test connection with a shorter timeout first
        logger.info("🔗 Testing connection...")
        client = QdrantClient(
            url=config["url"],
            api_key=config["api_key"],
            timeout=10  # Shorter timeout for testing
        )
        
        # Test basic connection
        collections = client.get_collections()
        logger.info(f"✅ Connected successfully!")
        logger.info(f"📊 Found {len(collections.collections)} collections")
        
        for collection in collections.collections:
            logger.info(f"  - {collection.name}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_qdrant_connection()
    sys.exit(0 if success else 1) 