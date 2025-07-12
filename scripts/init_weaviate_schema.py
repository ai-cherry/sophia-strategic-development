#!/usr/bin/env python3
"""
Initialize Weaviate Schema for Sophia AI
July 12, 2025
"""

import asyncio
import weaviate
import weaviate.classes as wvc
from weaviate.classes.config import Property, DataType
import structlog

logger = structlog.get_logger()


async def create_knowledge_schema():
    """Create the Knowledge class schema in Weaviate"""

    try:
        # Connect to Weaviate
        client = weaviate.connect_to_local(
            host="localhost",
            port=8080,
            grpc_port=50051,
        )

        # Check if Knowledge class already exists
        try:
            existing = client.collections.get("Knowledge")
            logger.info("Knowledge class already exists, deleting and recreating...")
            client.collections.delete("Knowledge")
        except:
            logger.info("Knowledge class doesn't exist, creating...")

        # Create Knowledge collection with proper schema
        knowledge_collection = client.collections.create(
            name="Knowledge",
            properties=[
                Property(
                    name="content",
                    data_type=DataType.TEXT,
                    description="The main content of the knowledge item",
                    vectorize_property_name=True,
                ),
                Property(
                    name="source",
                    data_type=DataType.TEXT,
                    description="Source of the knowledge (e.g., mcp/gong, chat, document)",
                    vectorize_property_name=False,
                ),
                Property(
                    name="user_id",
                    data_type=DataType.TEXT,
                    description="User ID associated with this knowledge",
                    vectorize_property_name=False,
                ),
                Property(
                    name="timestamp",
                    data_type=DataType.DATE,
                    description="When this knowledge was created",
                    vectorize_property_name=False,
                ),
                Property(
                    name="metadata",
                    data_type=DataType.TEXT,
                    description="JSON metadata",
                    vectorize_property_name=False,
                ),
                Property(
                    name="category",
                    data_type=DataType.TEXT,
                    description="Category of knowledge (sales, project, technical, etc.)",
                    vectorize_property_name=False,
                ),
                Property(
                    name="importance",
                    data_type=DataType.NUMBER,
                    description="Importance score (0-1)",
                    vectorize_property_name=False,
                ),
            ],
            # Use text2vec-transformers for embedding
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_transformers(
                model="sentence-transformers/all-MiniLM-L6-v2",
                vectorize_collection_name=False,
            ),
            # Configure vector index
            vector_index_config=wvc.config.Configure.VectorIndex.hnsw(
                distance_metric=wvc.config.VectorDistances.COSINE,
                ef=128,
                ef_construction=200,
                max_connections=64,
            ),
            # Enable BM25 for hybrid search
            inverted_index_config=wvc.config.Configure.inverted_index(
                bm25=wvc.config.Configure.BM25(k1=1.2, b=0.75),
                stopwords_preset=wvc.config.StopwordsPreset.EN,
            ),
        )

        logger.info("✅ Knowledge schema created successfully!")

        # Create UserProfile class for personality adaptation
        try:
            client.collections.get("UserProfile")
            logger.info("UserProfile class already exists, deleting and recreating...")
            client.collections.delete("UserProfile")
        except:
            pass

        profile_collection = client.collections.create(
            name="UserProfile",
            properties=[
                Property(
                    name="user_id",
                    data_type=DataType.TEXT,
                    description="Unique user identifier",
                    vectorize_property_name=False,
                ),
                Property(
                    name="personality_preferences",
                    data_type=DataType.TEXT,
                    description="JSON of personality preferences (sass_level, formality, etc.)",
                    vectorize_property_name=True,
                ),
                Property(
                    name="interaction_history",
                    data_type=DataType.TEXT,
                    description="Summary of past interactions",
                    vectorize_property_name=True,
                ),
                Property(
                    name="domain_expertise",
                    data_type=DataType.TEXT_ARRAY,
                    description="Areas of expertise",
                    vectorize_property_name=True,
                ),
                Property(
                    name="communication_style",
                    data_type=DataType.TEXT,
                    description="Preferred communication style",
                    vectorize_property_name=False,
                ),
                Property(
                    name="last_updated",
                    data_type=DataType.DATE,
                    description="Last profile update",
                    vectorize_property_name=False,
                ),
            ],
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_transformers(
                model="sentence-transformers/all-MiniLM-L6-v2",
                vectorize_collection_name=False,
            ),
        )

        logger.info("✅ UserProfile schema created successfully!")

        # Create some test data
        logger.info("Adding test data...")

        # Add CEO profile
        profile_collection.data.insert(
            {
                "user_id": "ceo_user",
                "personality_preferences": '{"sass_level": 0.9, "formality": 0.3, "technical_depth": 0.8, "humor": "dark", "directness": 0.95}',
                "interaction_history": "CEO prefers direct, no-bullshit answers with technical depth. Appreciates dark humor and sarcasm. Hates corporate speak.",
                "domain_expertise": ["sales", "product", "strategy", "engineering"],
                "communication_style": "direct_snarky",
                "last_updated": "2025-07-12T09:00:00Z",
            }
        )

        # Add sample knowledge
        knowledge_collection.data.insert(
            {
                "content": "The deployment is currently at 60% operational. Backend running on port 8001 with v4 endpoints. Weaviate schema needs initialization.",
                "source": "system_status",
                "user_id": "system",
                "timestamp": "2025-07-12T09:00:00Z",
                "metadata": '{"deployment_phase": 6, "operational_percentage": 60}',
                "category": "technical",
                "importance": 0.9,
            }
        )

        logger.info("✅ Test data added successfully!")

        # Verify collections
        collections = client.collections.list_all()
        logger.info(f"Available collections: {list(collections.keys())}")

        client.close()

        return True

    except Exception as e:
        logger.error(f"Failed to create Weaviate schema: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(create_knowledge_schema())
