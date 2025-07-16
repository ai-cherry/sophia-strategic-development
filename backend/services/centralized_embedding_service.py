"""
Centralized Embedding Service for Sophia AI
Eliminates redundant embedding operations across services
"""

import asyncio
import logging
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from backend.core.auto_esc_config import get_config_value
from backend.core.redis_connection_manager import RedisConnectionManager

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Embedding result with metadata"""
    text: str
    embedding: List[float]
    model: str
    dimensions: int
    hash: str
    cached: bool = False

class CentralizedEmbeddingService:
    """Centralized service for all embedding operations"""
    
    def __init__(self):
        self.redis_manager = RedisConnectionManager()
        self.embedding_models = {
            "text-embedding-ada-002": {"dimensions": 1536, "provider": "openai"},
            "text-embedding-3-small": {"dimensions": 1536, "provider": "openai"},
            "text-embedding-3-large": {"dimensions": 3072, "provider": "openai"},
        }
        self.default_model = "text-embedding-ada-002"
        self.cache_ttl = 7 * 24 * 3600  # 7 days
        
    async def initialize(self):
        """Initialize embedding service"""
        await self.redis_manager.initialize()
        logger.info("✅ Centralized Embedding Service initialized")
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        use_cache: bool = True
    ) -> List[EmbeddingResult]:
        """Generate embeddings for list of texts"""
        if not texts:
            return []
        
        model = model or self.default_model
        results = []
        
        # Check cache first
        cached_results = {}
        if use_cache:
            cached_results = await self._check_cache(texts, model)
        
        # Generate embeddings for non-cached texts
        non_cached_texts = [text for text in texts if text not in cached_results]
        
        if non_cached_texts:
            new_embeddings = await self._generate_new_embeddings(non_cached_texts, model)
            
            # Cache new embeddings
            if use_cache:
                await self._cache_embeddings(new_embeddings, model)
            
            # Add to results
            for text in non_cached_texts:
                if text in new_embeddings:
                    embedding = new_embeddings[text]
                    text_hash = self._get_text_hash(text, model)
                    results.append(EmbeddingResult(
                        text=text,
                        embedding=embedding,
                        model=model,
                        dimensions=len(embedding),
                        hash=text_hash,
                        cached=False
                    ))
        
        # Add cached results
        for text, cached_data in cached_results.items():
            results.append(EmbeddingResult(
                text=text,
                embedding=cached_data["embedding"],
                model=model,
                dimensions=cached_data["dimensions"],
                hash=cached_data["hash"],
                cached=True
            ))
        
        logger.info(f"Generated {len(results)} embeddings ({len(cached_results)} cached, {len(non_cached_texts)} new)")
        return results
    
    async def generate_single_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        use_cache: bool = True
    ) -> EmbeddingResult:
        """Generate embedding for single text"""
        results = await self.generate_embeddings([text], model, use_cache)
        return results[0] if results else None
    
    def _get_text_hash(self, text: str, model: str) -> str:
        """Generate hash for text and model combination"""
        combined = f"{text}:{model}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    async def _check_cache(self, texts: List[str], model: str) -> Dict[str, Dict[str, Any]]:
        """Check cache for existing embeddings"""
        redis_client = await self.redis_manager.get_async_client()
        cached_results = {}
        
        for text in texts:
            cache_key = f"embedding:{self._get_text_hash(text, model)}"
            cached_data = await redis_client.get(cache_key)
            
            if cached_data:
                try:
                    import json
                    parsed_data = json.loads(cached_data)
                    cached_results[text] = parsed_data
                except Exception as e:
                    logger.warning(f"Failed to parse cached embedding: {e}")
        
        return cached_results
    
    async def _generate_new_embeddings(self, texts: List[str], model: str) -> Dict[str, List[float]]:
        """Generate new embeddings using AI provider"""
        try:
            if self.embedding_models[model]["provider"] == "openai":
                return await self._generate_openai_embeddings(texts, model)
            else:
                raise ValueError(f"Unsupported embedding provider for model: {model}")
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return {}
    
    async def _generate_openai_embeddings(self, texts: List[str], model: str) -> Dict[str, List[float]]:
        """Generate embeddings using OpenAI API"""
        try:
            import openai
            
            api_key = get_config_value("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            
            client = openai.AsyncOpenAI(api_key=api_key)
            
            response = await client.embeddings.create(
                model=model,
                input=texts
            )
            
            results = {}
            for i, text in enumerate(texts):
                if i < len(response.data):
                    results[text] = response.data[i].embedding
            
            return results
            
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {e}")
            return {}
    
    async def _cache_embeddings(self, embeddings: Dict[str, List[float]], model: str):
        """Cache embeddings in Redis"""
        redis_client = await self.redis_manager.get_async_client()
        
        for text, embedding in embeddings.items():
            cache_key = f"embedding:{self._get_text_hash(text, model)}"
            cache_data = {
                "embedding": embedding,
                "model": model,
                "dimensions": len(embedding),
                "hash": self._get_text_hash(text, model),
                "created_at": asyncio.get_event_loop().time()
            }
            
            try:
                import json
                await redis_client.setex(cache_key, self.cache_ttl, json.dumps(cache_data))
            except Exception as e:
                logger.warning(f"Failed to cache embedding: {e}")
    
    async def clear_cache(self, pattern: Optional[str] = None):
        """Clear embedding cache"""
        redis_client = await self.redis_manager.get_async_client()
        
        pattern = pattern or "embedding:*"
        keys = await redis_client.keys(pattern)
        
        if keys:
            await redis_client.delete(*keys)
            logger.info(f"Cleared {len(keys)} cached embeddings")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        redis_client = await self.redis_manager.get_async_client()
        
        keys = await redis_client.keys("embedding:*")
        total_size = 0
        
        for key in keys[:100]:  # Sample first 100 keys for size estimation
            size = await redis_client.memory_usage(key)
            if size:
                total_size += size
        
        estimated_total_size = total_size * (len(keys) / min(100, len(keys))) if keys else 0
        
        return {
            "total_embeddings": len(keys),
            "estimated_size_bytes": estimated_total_size,
            "estimated_size_mb": estimated_total_size / (1024 * 1024),
            "cache_ttl_seconds": self.cache_ttl
        }

# Global service instance
_embedding_service = None

async def get_embedding_service() -> CentralizedEmbeddingService:
    """Get global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = CentralizedEmbeddingService()
        await _embedding_service.initialize()
    return _embedding_service
