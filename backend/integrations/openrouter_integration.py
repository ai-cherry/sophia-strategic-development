"""
OpenRouter Integration for Dynamic Model Selection
Provides access to all OpenRouter models with real-time discovery
"""
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional, AsyncIterator
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for OpenRouter API with dynamic model discovery"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.models_cache = None
        self.cache_timestamp = None
        self.cache_duration = timedelta(hours=1)
        
    async def get_models(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Get available models with caching"""
        # Check cache
        if (not force_refresh and 
            self.models_cache and 
            self.cache_timestamp and 
            datetime.utcnow() - self.cache_timestamp < self.cache_duration):
            return self.models_cache
        
        # Fetch fresh model list
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with session.get(f"{self.base_url}/models", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.models_cache = data.get("data", [])
                    self.cache_timestamp = datetime.utcnow()
                    return self.models_cache
                else:
                    logger.error(f"Failed to fetch models: {response.status}")
                    return []
    
    async def chat_completion(
        self, 
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a chat completion with the specified model"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://payready.com",  # Required by OpenRouter
                "X-Title": "Sophia AI Executive Dashboard"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                **kwargs
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            if stream:
                return await self._stream_completion(session, headers, payload)
            else:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "content": data["choices"][0]["message"]["content"],
                            "model": data["model"],
                            "usage": data.get("usage", {})
                        }
                    else:
                        error = await response.text()
                        logger.error(f"Chat completion failed: {error}")
                        raise Exception(f"OpenRouter API error: {error}")
    
    async def _stream_completion(
        self, 
        session: aiohttp.ClientSession,
        headers: Dict[str, str],
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle streaming chat completion"""
        payload["stream"] = True
        full_content = ""
        
        async with session.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error = await response.text()
                raise Exception(f"OpenRouter streaming error: {error}")
            
            async for line in response.content:
                if line:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith("data: "):
                        data_str = line_text[6:]
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                full_content += delta["content"]
                        except json.JSONDecodeError:
                            continue
        
        return {
            "content": full_content,
            "model": payload["model"],
            "stream": True
        }
    
    async def get_model_details(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific model"""
        models = await self.get_models()
        for model in models:
            if model.get("id") == model_id:
                return model
        return None
    
    def categorize_model(self, model: Dict[str, Any]) -> str:
        """Categorize a model based on its capabilities"""
        model_id = model.get("id", "").lower()
        
        # Advanced reasoning models
        if any(x in model_id for x in ["o1-preview", "o1-mini"]):
            return "advanced_reasoning"
        
        # Deep analysis models
        elif any(x in model_id for x in ["claude-3-opus", "claude-3.5-sonnet"]):
            return "deep_analysis"
        
        # Fast response models
        elif any(x in model_id for x in ["gpt-4-turbo", "claude-3-haiku"]):
            return "fast_response"
        
        # Vision models
        elif "vision" in model_id:
            return "vision"
        
        # Code models
        elif any(x in model_id for x in ["code", "codestral"]):
            return "code_generation"
        
        # Cost-optimized models
        elif any(x in model_id for x in ["llama", "mixtral", "qwen"]):
            return "cost_optimized"
        
        else:
            return "general_purpose"
    
    def get_model_capabilities(self, model: Dict[str, Any]) -> List[str]:
        """Extract capabilities from model metadata"""
        capabilities = []
        model_id = model.get("id", "").lower()
        
        # Check for specific capabilities
        if model.get("architecture", {}).get("modality") == "text->text, image->text":
            capabilities.append("vision")
        
        if model.get("context_length", 0) >= 100000:
            capabilities.append("large_context")
        
        if model.get("context_length", 0) >= 200000:
            capabilities.append("extra_large_context")
        
        # Infer from model name
        if "instruct" in model_id:
            capabilities.append("instruction_following")
        
        if any(x in model_id for x in ["chat", "assistant"]):
            capabilities.append("conversational")
        
        if "code" in model_id:
            capabilities.append("code_generation")
        
        # Performance characteristics
        pricing = model.get("pricing", {})
        if pricing.get("prompt", 0) < 0.001:
            capabilities.append("cost_efficient")
        
        return capabilities
    
    async def select_optimal_model(
        self,
        query_type: str,
        context_size: int = 0,
        require_vision: bool = False,
        max_cost_per_token: Optional[float] = None
    ) -> str:
        """Intelligently select the best model for a given task"""
        models = await self.get_models()
        
        # Filter models based on requirements
        suitable_models = []
        for model in models:
            # Check context window
            if context_size > model.get("context_length", 0):
                continue
            
            # Check vision requirement
            if require_vision and "vision" not in self.get_model_capabilities(model):
                continue
            
            # Check cost constraint
            if max_cost_per_token:
                pricing = model.get("pricing", {})
                if pricing.get("prompt", float('inf')) > max_cost_per_token:
                    continue
            
            suitable_models.append(model)
        
        # Select based on query type
        if query_type == "strategic_analysis":
            # Prefer deep reasoning models
            for model in suitable_models:
                if "claude-3.5-sonnet" in model.get("id", ""):
                    return model["id"]
                elif "o1-preview" in model.get("id", ""):
                    return model["id"]
        
        elif query_type == "quick_response":
            # Prefer fast models
            for model in suitable_models:
                if "gpt-4-turbo" in model.get("id", ""):
                    return model["id"]
                elif "claude-3-haiku" in model.get("id", ""):
                    return model["id"]
        
        elif query_type == "code_generation":
            # Prefer code-specific models
            for model in suitable_models:
                if "codestral" in model.get("id", ""):
                    return model["id"]
                elif "gpt-4" in model.get("id", ""):
                    return model["id"]
        
        elif query_type == "cost_optimized":
            # Sort by cost and return cheapest
            suitable_models.sort(key=lambda m: m.get("pricing", {}).get("prompt", float('inf')))
            if suitable_models:
                return suitable_models[0]["id"]
        
        # Default fallback
        if suitable_models:
            # Return GPT-4 Turbo as default if available
            for model in suitable_models:
                if "gpt-4-turbo" in model.get("id", ""):
                    return model["id"]
            # Otherwise return first suitable model
            return suitable_models[0]["id"]
        
        # If no suitable models found, return a default
        return "openai/gpt-4-turbo"
