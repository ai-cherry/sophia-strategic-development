"""
Sophia AI Enhanced Chat v4
Full chat with persona/RAG/X/video injection
Target: <180ms snarky responses

Date: July 12, 2025
"""

import asyncio
import json
import logging
import time
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, AsyncGenerator

from fastapi import HTTPException
from prometheus_client import Counter, Histogram

from backend.services.sophia_unified_orchestrator import get_orchestrator
from backend.services.personality_engine import PersonalityEngine
from backend.services.sophia_unified_memory_service import SophiaUnifiedMemoryService

logger = logging.getLogger(__name__)

# Prometheus metrics
chat_requests = Counter('sophia_chat_v4_requests_total', 'Total chat requests')
chat_latency = Histogram('sophia_chat_v4_latency_seconds', 'Chat response latency')
streaming_chunks = Counter('sophia_chat_v4_streaming_chunks_total', 'Total streaming chunks')
snarky_responses = Counter('sophia_chat_v4_snarky_responses_total', 'Snarky responses generated')


class StreamingBuffer:
    """Buffer for streaming responses"""
    
    def __init__(self, chunk_size: int = 50):
        self.buffer = []
        self.chunk_size = chunk_size
        
    def add(self, text: str) -> List[str]:
        """Add text and return chunks if ready"""
        self.buffer.append(text)
        
        if len(self.buffer) >= self.chunk_size:
            chunk = ''.join(self.buffer)
            self.buffer = []
            return [chunk]
        return []
    
    def flush(self) -> str:
        """Flush remaining buffer"""
        if self.buffer:
            chunk = ''.join(self.buffer)
            self.buffer = []
            return chunk
        return ""


class EnhancedChatV4:
    """Enhanced chat service with full features"""
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.personality = PersonalityEngine()
        self.memory_service = SophiaUnifiedMemoryService()
        self.initialized = False
        
        # Performance targets
        self.target_latency_ms = 180
        self.snarky_threshold = 0.7
        
    async def initialize(self):
        """Initialize services"""
        if self.initialized:
            return
            
        await self.orchestrator.initialize()
        await self.memory_service.initialize()
        self.initialized = True
        logger.info("Enhanced Chat v4 initialized")
    
    async def chat(
        self,
        message: str,
        user_id: str,
        session_id: Optional[str] = None,
        mode: str = "snarky",
        include_trends: bool = True,
        include_video: bool = True,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Main chat endpoint with all features"""
        start_time = time.time()
        chat_requests.inc()
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Build context
            context = {
                'session_id': session_id,
                'include_trends': include_trends,
                'include_video': include_video,
                'target_latency_ms': self.target_latency_ms,
                'mode': mode
            }
            
            # Get user history for personalization
            user_history = await self._get_user_history(user_id, session_id)
            if user_history:
                context['user_history'] = user_history
            
            # Check for repeated questions (trigger extra snark)
            if self._is_repeated_question(message, user_history):
                context['repeated_question'] = True
                snarky_responses.inc()
            
            # Orchestrate response
            result = await self.orchestrator.orchestrate(
                message,
                user_id,
                mode,
                context
            )
            
            # Measure performance
            latency_ms = (time.time() - start_time) * 1000
            chat_latency.observe(latency_ms / 1000)
            
            # Build response
            response = {
                'message': result['response'],
                'user_id': user_id,
                'session_id': session_id,
                'mode': mode,
                'timestamp': datetime.now(UTC).isoformat(),
                'performance': {
                    'latency_ms': latency_ms,
                    'target_met': latency_ms < self.target_latency_ms,
                    'route': result['performance']['route']
                }
            }
            
            # Add enrichments
            if 'trends' in result:
                response['trends'] = result['trends']
                
            if 'videos' in result:
                response['videos'] = result['videos']
            
            # Store in memory
            await self._store_interaction(user_id, session_id, message, response)
            
            # Stream if requested
            if stream:
                return await self._stream_response(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def chat_stream(
        self,
        message: str,
        user_id: str,
        session_id: Optional[str] = None,
        mode: str = "snarky",
        include_trends: bool = True,
        include_video: bool = True
    ) -> AsyncGenerator[str, None]:
        """Streaming chat endpoint"""
        time.time()
        buffer = StreamingBuffer()
        
        try:
            # Get full response
            response = await self.chat(
                message=message,
                user_id=user_id,
                session_id=session_id,
                mode=mode,
                include_trends=include_trends,
                include_video=include_video,
                stream=False
            )
            
            # Stream the message
            message_text = response['message']
            words = message_text.split()
            
            for i, word in enumerate(words):
                chunks = buffer.add(word + ' ')
                for chunk in chunks:
                    streaming_chunks.inc()
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                    await asyncio.sleep(0.01)  # Small delay for streaming effect
            
            # Flush remaining
            final_chunk = buffer.flush()
            if final_chunk:
                yield f"data: {json.dumps({'chunk': final_chunk, 'done': False})}\n\n"
            
            # Send metadata
            metadata = {
                'done': True,
                'performance': response['performance'],
                'trends': response.get('trends', []),
                'videos': response.get('videos', [])
            }
            yield f"data: {json.dumps(metadata)}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    async def _get_user_history(self, user_id: str, session_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get user conversation history"""
        try:
            # Query recent interactions
            filter_dict = {'user_id': user_id}
            if session_id:
                filter_dict['session_id'] = session_id
            
            results = await self.memory_service.search_knowledge(
                f"user:{user_id} conversations",
                limit=10,
                metadata_filter=filter_dict
            )
            
            return results
            
        except Exception as e:
            logger.warning(f"Failed to get user history: {e}")
            return []
    
    def _is_repeated_question(self, message: str, history: List[Dict[str, Any]]) -> bool:
        """Check if question was recently asked"""
        if not history:
            return False
        
        # Simple check - in production would use embeddings
        message_lower = message.lower().strip()
        
        for item in history[:5]:  # Check last 5 interactions
            if 'content' in item:
                prev_message = item['content'].lower().strip()
                if message_lower in prev_message or prev_message in message_lower:
                    return True
        
        return False
    
    async def _store_interaction(
        self,
        user_id: str,
        session_id: Optional[str],
        message: str,
        response: Dict[str, Any]
    ):
        """Store interaction in memory"""
        try:
            metadata = {
                'user_id': user_id,
                'session_id': session_id,
                'timestamp': datetime.now(UTC).isoformat(),
                'mode': response.get('mode', 'snarky'),
                'latency_ms': response['performance']['latency_ms']
            }
            
            content = f"User: {message}\nAssistant: {response['message']}"
            
            await self.memory_service.add_knowledge(
                content=content,
                source="chat_v4",
                metadata=metadata
            )
            
        except Exception as e:
            logger.warning(f"Failed to store interaction: {e}")
    
    async def get_session_summary(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Get summary of a chat session"""
        try:
            # Get all interactions for session
            results = await self.memory_service.search_knowledge(
                f"session:{session_id}",
                limit=100,
                metadata_filter={'user_id': user_id, 'session_id': session_id}
            )
            
            if not results:
                return {
                    'session_id': session_id,
                    'user_id': user_id,
                    'summary': 'No interactions found',
                    'interaction_count': 0
                }
            
            # Calculate stats
            total_interactions = len(results)
            avg_latency = sum(r['metadata'].get('latency_ms', 0) for r in results) / total_interactions
            modes_used = set(r['metadata'].get('mode', 'unknown') for r in results)
            
            # Generate summary
            summary = {
                'session_id': session_id,
                'user_id': user_id,
                'interaction_count': total_interactions,
                'avg_latency_ms': avg_latency,
                'modes_used': list(modes_used),
                'first_interaction': results[-1]['metadata']['timestamp'],
                'last_interaction': results[0]['metadata']['timestamp'],
                'topics_discussed': self._extract_topics(results)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get session summary: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _extract_topics(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract main topics from conversations"""
        # Simple keyword extraction - in production would use NLP
        topics = set()
        keywords = ['revenue', 'sales', 'customer', 'product', 'marketing', 'finance', 'operations']
        
        for result in results:
            content = result.get('content', '').lower()
            for keyword in keywords:
                if keyword in content:
                    topics.add(keyword)
        
        return list(topics)


# Singleton instance
_chat_service = None

def get_chat_service() -> EnhancedChatV4:
    """Get singleton chat service"""
    global _chat_service
    if _chat_service is None:
        _chat_service = EnhancedChatV4()
    return _chat_service 