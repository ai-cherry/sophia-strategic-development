#!/usr/bin/env python3
"""
Initialize Weaviate Schema for Sophia AI
Creates the necessary collections and schemas in Weaviate
"""

import os
import sys
import weaviate
from weaviate.classes.config import Configure, DataType, Property
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_weaviate_client():
    """Create Weaviate client connection"""
    weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    
    try:
        client = weaviate.Client(
            url=weaviate_url,
            timeout_config=(5, 15)  # (connect timeout, read timeout)
        )
        
        # Test connection
        if client.is_ready():
            logger.info(f"✅ Connected to Weaviate at {weaviate_url}")
            return client
        else:
            logger.error(f"❌ Weaviate at {weaviate_url} is not ready")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Failed to connect to Weaviate: {e}")
        sys.exit(1)

def create_knowledge_collection(client):
    """Create the Knowledge collection for general knowledge storage"""
    
    knowledge_schema = {
        "class": "Knowledge",
        "description": "General knowledge and document storage",
        "vectorIndexType": "hnsw",
        "vectorizer": "text2vec-transformers",
        "properties": [
            {
                "name": "content",
                "dataType": ["text"],
                "description": "The main content/text"
            },
            {
                "name": "title",
                "dataType": ["text"],
                "description": "Title or summary of the content"
            },
            {
                "name": "source",
                "dataType": ["text"],
                "description": "Source of the knowledge"
            },
            {
                "name": "metadata",
                "dataType": ["text"],
                "description": "JSON metadata"
            },
            {
                "name": "category",
                "dataType": ["text"],
                "description": "Category or type of knowledge"
            },
            {
                "name": "timestamp",
                "dataType": ["date"],
                "description": "When this was created"
            },
            {
                "name": "user_id",
                "dataType": ["text"],
                "description": "User who created this"
            }
        ]
    }
    
    try:
        # Check if collection exists
        existing = client.schema.get()
        if any(c["class"] == "Knowledge" for c in existing.get("classes", [])):
            logger.info("✓ Knowledge collection already exists")
        else:
            client.schema.create_class(knowledge_schema)
            logger.info("✅ Created Knowledge collection")
    except Exception as e:
        logger.error(f"❌ Error creating Knowledge collection: {e}")

def create_conversation_collection(client):
    """Create the Conversation collection for chat history"""
    
    conversation_schema = {
        "class": "Conversation",
        "description": "Chat conversations and interactions",
        "vectorIndexType": "hnsw",
        "vectorizer": "text2vec-transformers",
        "properties": [
            {
                "name": "message",
                "dataType": ["text"],
                "description": "The message content"
            },
            {
                "name": "role",
                "dataType": ["text"],
                "description": "Role (user/assistant/system)"
            },
            {
                "name": "session_id",
                "dataType": ["text"],
                "description": "Conversation session ID"
            },
            {
                "name": "user_id",
                "dataType": ["text"],
                "description": "User ID"
            },
            {
                "name": "timestamp",
                "dataType": ["date"],
                "description": "Message timestamp"
            },
            {
                "name": "context",
                "dataType": ["text"],
                "description": "Additional context (JSON)"
            }
        ]
    }
    
    try:
        existing = client.schema.get()
        if any(c["class"] == "Conversation" for c in existing.get("classes", [])):
            logger.info("✓ Conversation collection already exists")
        else:
            client.schema.create_class(conversation_schema)
            logger.info("✅ Created Conversation collection")
    except Exception as e:
        logger.error(f"❌ Error creating Conversation collection: {e}")

def create_agent_memory_collection(client):
    """Create the AgentMemory collection for MCP agent memories"""
    
    agent_memory_schema = {
        "class": "AgentMemory",
        "description": "MCP agent memories and learnings",
        "vectorIndexType": "hnsw",
        "vectorizer": "text2vec-transformers",
        "properties": [
            {
                "name": "memory",
                "dataType": ["text"],
                "description": "The memory content"
            },
            {
                "name": "agent_name",
                "dataType": ["text"],
                "description": "Name of the MCP agent"
            },
            {
                "name": "memory_type",
                "dataType": ["text"],
                "description": "Type of memory (fact/procedure/insight)"
            },
            {
                "name": "importance",
                "dataType": ["number"],
                "description": "Importance score (0-1)"
            },
            {
                "name": "tags",
                "dataType": ["text[]"],
                "description": "Associated tags"
            },
            {
                "name": "created_at",
                "dataType": ["date"],
                "description": "When memory was created"
            },
            {
                "name": "last_accessed",
                "dataType": ["date"],
                "description": "Last access time"
            },
            {
                "name": "access_count",
                "dataType": ["int"],
                "description": "Number of times accessed"
            }
        ]
    }
    
    try:
        existing = client.schema.get()
        if any(c["class"] == "AgentMemory" for c in existing.get("classes", [])):
            logger.info("✓ AgentMemory collection already exists")
        else:
            client.schema.create_class(agent_memory_schema)
            logger.info("✅ Created AgentMemory collection")
    except Exception as e:
        logger.error(f"❌ Error creating AgentMemory collection: {e}")

def create_business_insights_collection(client):
    """Create the BusinessInsights collection for business intelligence"""
    
    insights_schema = {
        "class": "BusinessInsights",
        "description": "Business insights and analytics",
        "vectorIndexType": "hnsw",
        "vectorizer": "text2vec-transformers",
        "properties": [
            {
                "name": "insight",
                "dataType": ["text"],
                "description": "The business insight"
            },
            {
                "name": "source_system",
                "dataType": ["text"],
                "description": "Source system (HubSpot/Gong/etc)"
            },
            {
                "name": "insight_type",
                "dataType": ["text"],
                "description": "Type of insight"
            },
            {
                "name": "entities",
                "dataType": ["text[]"],
                "description": "Related entities"
            },
            {
                "name": "metrics",
                "dataType": ["text"],
                "description": "Associated metrics (JSON)"
            },
            {
                "name": "confidence",
                "dataType": ["number"],
                "description": "Confidence score"
            },
            {
                "name": "timestamp",
                "dataType": ["date"],
                "description": "When insight was generated"
            }
        ]
    }
    
    try:
        existing = client.schema.get()
        if any(c["class"] == "BusinessInsights" for c in existing.get("classes", [])):
            logger.info("✓ BusinessInsights collection already exists")
        else:
            client.schema.create_class(insights_schema)
            logger.info("✅ Created BusinessInsights collection")
    except Exception as e:
        logger.error(f"❌ Error creating BusinessInsights collection: {e}")

def verify_schema(client):
    """Verify all schemas are created"""
    try:
        schema = client.schema.get()
        collections = [c["class"] for c in schema.get("classes", [])]
        
        logger.info("\n📊 Weaviate Collections Status:")
        required = ["Knowledge", "Conversation", "AgentMemory", "BusinessInsights"]
        
        for collection in required:
            if collection in collections:
                logger.info(f"  ✅ {collection}")
            else:
                logger.error(f"  ❌ {collection} - MISSING")
                
        return len(set(required) & set(collections)) == len(required)
        
    except Exception as e:
        logger.error(f"❌ Error verifying schema: {e}")
        return False

def main():
    """Main initialization function"""
    logger.info("🚀 Initializing Weaviate Schema for Sophia AI")
    
    # Create client
    client = create_weaviate_client()
    
    # Create collections
    create_knowledge_collection(client)
    create_conversation_collection(client)
    create_agent_memory_collection(client)
    create_business_insights_collection(client)
    
    # Verify
    if verify_schema(client):
        logger.info("\n✅ Weaviate schema initialization complete!")
        logger.info("🎯 Ready for Sophia AI deployment")
    else:
        logger.error("\n❌ Schema initialization incomplete")
        sys.exit(1)

if __name__ == "__main__":
    main()
