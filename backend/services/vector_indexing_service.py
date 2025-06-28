# File: backend/services/vector_indexing_service.py

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

from backend.services.semantic_layer_service import SemanticLayerService
from backend.integrations.gong_api_client import GongAPIClient
from backend.core.auto_esc_config import get_config_value
import logging

logger = logging.getLogger(__name__)

@dataclass
class VectorDocument:
    """Document structure for vector indexing"""
    id: str
    content: str
    metadata: Dict[str, Any]
    source_type: str
    embedding: Optional[List[float]] = None

class VectorIndexingService:
    """
    Comprehensive vector indexing service for all unstructured content.
    Integrates with Snowflake Cortex Search.
    """
    
    def __init__(self):
        self.semantic_service = SemanticLayerService()
        gong_api_key = get_config_value("gong_access_key")
        if not gong_api_key:
            logger.warning("Gong API key not configured. Gong integration will be disabled.")
            self.gong_client = None
        else:
            self.gong_client = GongAPIClient(api_key=gong_api_key)
        
    async def _create_cortex_search_index(self, config: Dict[str, Any]) -> None:
        """Creates a Snowflake Cortex Search index."""
        # This is a placeholder for the actual index creation logic.
        # The exact DDL will depend on the final table structures and Cortex Search features.
        index_name = config['name']
        table_name = config['table']
        content_column = config['content_column']
        
        # In a real implementation, this would be a DDL query.
        logger.info(f"Placeholder: Would create Cortex Search index '{index_name}' on table '{table_name}' for content column '{content_column}'.")
        # Example DDL might look like:
        # CREATE OR REPLACE SNOWFLAKE.CORTEX.SEARCH_INDEX my_index
        # ON my_table(text_column)
        # SEARCH_METHOD = 'VECTOR';
        await asyncio.sleep(0.1) # Simulate async operation
        return

    async def initialize_vector_indexes(self) -> bool:
        """Initialize vector search indexes for all content types"""
        try:
            # Create Cortex Search indexes for different content types
            index_configs = [
                {
                    'name': 'SLACK_MESSAGES_INDEX',
                    'table': 'SLACK_DATA.MESSAGES_VECTORIZED',
                    'content_column': 'message_text',
                    'metadata_columns': ['channel_name', 'user_id', 'timestamp', 'thread_ts']
                },
                {
                    'name': 'GONG_TRANSCRIPTS_INDEX', 
                    'table': 'GONG_DATA.CALL_TRANSCRIPTS_VECTORIZED',
                    'content_column': 'transcript_segment',
                    'metadata_columns': ['call_id', 'speaker_id', 'timestamp', 'sentiment_score']
                },
                {
                    'name': 'KNOWLEDGE_BASE_INDEX',
                    'table': 'FOUNDATIONAL_KNOWLEDGE.DOCUMENTS_VECTORIZED', 
                    'content_column': 'document_content',
                    'metadata_columns': ['document_type', 'category', 'last_updated', 'author']
                }
            ]
            
            for config in index_configs:
                await self._create_cortex_search_index(config)
                
            logger.info("Vector indexes initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vector indexes: {e}")
            return False
    
    async def index_slack_content(self) -> int:
        """Index all Slack messages with vector embeddings"""
        logger.info("Starting Slack content indexing.")
        query = """
        SELECT message_id, message_text, channel_name, user_id, timestamp, thread_ts
        FROM SLACK_DATA.MESSAGES 
        WHERE message_text IS NOT NULL AND LENGTH(message_text) > 10
        ORDER BY timestamp DESC
        LIMIT 10000;
        """
        
        messages = await self.semantic_service._execute_query(query)
        indexed_count = 0
        
        for message in messages:
            try:
                # Generate embedding using Snowflake Cortex
                embedding_query = "SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s) as embedding;"
                
                embedding_result = await self.semantic_service._execute_query(
                    embedding_query, [message['message_text']]
                )
                
                if embedding_result and 'embedding' in embedding_result[0]:
                    embedding_vector = embedding_result[0]['embedding']
                    # Store vectorized content
                    insert_query = """
                    INSERT INTO SLACK_DATA.MESSAGES_VECTORIZED 
                    (message_id, message_text, embedding, channel_name, user_id, timestamp, thread_ts)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """
                    
                    await self.semantic_service._execute_query(insert_query, [
                        message['message_id'],
                        message['message_text'], 
                        json.dumps(embedding_vector),
                        message['channel_name'],
                        message['user_id'],
                        message['timestamp'],
                        message['thread_ts']
                    ])
                    
                    indexed_count += 1
                else:
                    logger.warning(f"Could not generate embedding for message {message['message_id']}")
                    
            except Exception as e:
                logger.warning(f"Failed to index message {message['message_id']}: {e}")
                continue
                
        logger.info(f"Indexed {indexed_count} Slack messages")
        return indexed_count
    
    async def index_gong_transcripts(self) -> int:
        """Index Gong call transcripts with vector embeddings"""
        logger.info("Starting Gong transcript indexing.")
        query = """
        SELECT call_id, transcript, call_date, participants, sentiment_score
        FROM GONG_DATA.CALLS 
        WHERE transcript IS NOT NULL
        ORDER BY call_date DESC
        LIMIT 1000;
        """
        
        calls = await self.semantic_service._execute_query(query)
        indexed_count = 0
        
        for call in calls:
            # Segment transcript into chunks
            segments = self._segment_transcript(call['transcript'])
            
            for i, segment in enumerate(segments):
                try:
                    # Generate embedding
                    embedding_query = "SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s) as embedding;"
                    
                    embedding_result = await self.semantic_service._execute_query(
                        embedding_query, [segment]
                    )
                    
                    if embedding_result and 'embedding' in embedding_result[0]:
                        embedding_vector = embedding_result[0]['embedding']
                        # Store vectorized segment
                        insert_query = """
                        INSERT INTO GONG_DATA.CALL_TRANSCRIPTS_VECTORIZED
                        (call_id, segment_id, transcript_segment, embedding, call_date, 
                         participants, sentiment_score, segment_order)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                        """
                        
                        await self.semantic_service._execute_query(insert_query, [
                            call['call_id'],
                            f"{call['call_id']}_segment_{i}",
                            segment,
                            json.dumps(embedding_vector),
                            call['call_date'],
                            json.dumps(call['participants']),
                            call['sentiment_score'],
                            i
                        ])
                        
                        indexed_count += 1
                    else:
                        logger.warning(f"Could not generate embedding for call segment {call['call_id']}_{i}")
                except Exception as e:
                    logger.warning(f"Failed to index call segment {call['call_id']}_{i}: {e}")
                    continue
                    
        logger.info(f"Indexed {indexed_count} Gong transcript segments")
        return indexed_count
    
    def _segment_transcript(self, transcript: str, max_length: int = 500) -> List[str]:
        """Segment long transcripts into searchable chunks"""
        if not transcript:
            return []
        
        sentences = transcript.split('. ')
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            if not sentence:
                continue
            if len(current_segment) + len(sentence) + 2 < max_length:
                current_segment += sentence + ". "
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence + ". "
                
        if current_segment:
            segments.append(current_segment.strip())
            
        return segments

    async def health_check(self) -> Dict[str, Any]:
        """Performs a health check on the vector indexing service."""
        # For now, this just checks the semantic service health.
        # A more complete implementation would check for index existence, etc.
        semantic_health = await self.semantic_service.health_check()
        if semantic_health['status'] == 'healthy':
            return {"status": "healthy", "message": "Dependent services are healthy."}
        else:
            return {"status": "unhealthy", "message": "SemanticLayerService is unhealthy."} 
