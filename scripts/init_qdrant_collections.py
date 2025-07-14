#!/usr/bin/env python3
"""
Initialize Qdrant Collections for Sophia AI
Replaces the old Weaviate schema initialization
"""

import asyncio
import os
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, CollectionConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_qdrant_client():
    """Create Qdrant client connection"""
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    try:
        client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=30
        )
        
        # Test connection
        client.get_collections()
        logger.info(f"✅ Connected to Qdrant at {qdrant_url}")
        return client
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Qdrant: {e}")
        raise

def create_collection(client: QdrantClient, name: str, vector_size: int = 768):
    """Create Qdrant collection if it doesn't exist"""
    try:
        client.get_collection(name)
        logger.info(f"Collection {name} already exists")
        return
    except:
        pass  # Collection doesn't exist, create it
    
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
    logger.info(f"✅ Created Qdrant collection: {name}")

def initialize_sophia_collections():
    """Initialize all Sophia AI collections"""
    logger.info("🚀 Initializing Qdrant Collections for Sophia AI")
    
    client = create_qdrant_client()
    
    # Core collections
    collections = [
        "sophia_episodic",
        "sophia_semantic", 
        "sophia_visual",
        "sophia_procedural",
        "sophia_competitors",
        "sophia_competitor_events",
        "sophia_competitor_analytics"
    ]
    
    for collection in collections:
        create_collection(client, collection)
    
    logger.info("✅ Qdrant schema initialization complete!")

if __name__ == "__main__":
    initialize_sophia_collections()
