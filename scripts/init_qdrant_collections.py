#!/usr/bin/env python3
"""
Initialize Qdrant Collections for Sophia AI
Replaces the old Weaviate schema initialization
"""

import asyncio
import os
import sys
import logging
from QDRANT_client import QdrantClient
from QDRANT_client.models import Distance, VectorParams, CollectionConfig

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core.auto_esc_config import get_QDRANT_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_QDRANT_client():
    """Create Qdrant client connection using auto ESC config"""
    try:
        config = get_QDRANT_config()
        
        client = QdrantClient(
            url=config["url"],
            api_key=config["api_key"],
            timeout=config["timeout"]
        )
        
        # Test connection
        collections = client.get_collections()
        logger.info(f"✅ Connected to Qdrant at {config['url']}")
        logger.info(f"📊 Found {len(collections.collections)} existing collections")
        return client
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Qdrant: {e}")
        raise

def create_collection(client: QdrantClient, name: str, vector_size: int = 768):
    """Create Qdrant collection if it doesn't exist"""
    try:
        client.get_collection(name)
        logger.info(f"✅ Collection '{name}' already exists")
        return False
    except Exception:
        # Collection doesn't exist, create it
        try:
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Created collection '{name}' with vector size {vector_size}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create collection '{name}': {e}")
            raise

def initialize_sophia_collections():
    """Initialize all Sophia AI collections"""
    logger.info("🚀 Initializing Qdrant Collections for Sophia AI")
    
    try:
        client = create_QDRANT_client()
        
        # Define collections for Sophia AI
        collections = [
            ("knowledge_base", 768),
            ("conversations", 768),
            ("business_intelligence", 768),
            ("competitor_intelligence", 768),
            ("customer_insights", 768),
            ("market_research", 768),
            ("sales_intelligence", 768)
        ]
        
        created_count = 0
        for name, vector_size in collections:
            if create_collection(client, name, vector_size):
                created_count += 1
        
        logger.info(f"🎉 Initialization complete! Created {created_count} new collections")
        
        # List all collections
        collections_info = client.get_collections()
        logger.info("📋 Current collections:")
        for collection in collections_info.collections:
            logger.info(f"  - {collection.name}")
            
    except Exception as e:
        logger.error(f"💥 Failed to initialize collections: {e}")
        raise

if __name__ == "__main__":
    initialize_sophia_collections()
