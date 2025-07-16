"""
OpenAI Service for embeddings and LLM operations
"""

import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API operations"""
    
    def __init__(self):
        self.api_key = get_config_value("openai_api_key")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.embedding_model = "text-embedding-3-small"
        self.chat_model = "gpt-4o-mini"
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text"""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return []
    
    async def chat_completion(self, messages: List[Dict[str, Any]], temperature: float = 0.1) -> str:
        """Get chat completion"""
        try:
            # Type ignore for OpenAI messages - the API accepts Dict[str, Any]
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,  # type: ignore
                temperature=temperature
            )
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            logger.error(f"Error getting chat completion: {e}")
            return ""
