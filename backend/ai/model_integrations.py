"""
HuggingFace and Together AI Model Integrations for Sophia AI
Optimized integrations for accessing diverse AI models and capabilities
"""

import os
import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Union, Generator
from datetime import datetime
import aiohttp
import requests
from dataclasses import dataclass
from transformers import AutoTokenizer, AutoModel, pipeline
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelCapability:
    """Model capability definition"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    max_tokens: int
    cost_per_token: float

@dataclass
class ModelConfig:
    """Model configuration"""
    model_id: str
    provider: str
    capabilities: List[ModelCapability]
    parameters: Dict[str, Any]
    priority: int = 1

class HuggingFaceService:
    """
    HuggingFace model integration service
    Provides access to HuggingFace models via API and local inference
    """
    
    def __init__(self):
        """Initialize HuggingFace service"""
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        self.base_url = "https://api-inference.huggingface.co/models"
        
        if not self.api_token:
            raise ValueError("HUGGINGFACE_API_TOKEN must be set")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Optimized model configurations for Sophia AI
        self.models = {
            "text_generation": {
                "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.1",
                "llama2-7b": "meta-llama/Llama-2-7b-chat-hf",
                "codellama": "codellama/CodeLlama-7b-Python-hf",
                "zephyr": "HuggingFaceH4/zephyr-7b-beta"
            },
            "embeddings": {
                "sentence-transformers": "sentence-transformers/all-MiniLM-L6-v2",
                "e5-large": "intfloat/e5-large-v2",
                "bge-large": "BAAI/bge-large-en-v1.5"
            },
            "classification": {
                "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "emotion": "j-hartmann/emotion-english-distilroberta-base",
                "toxicity": "unitary/toxic-bert"
            },
            "summarization": {
                "bart": "facebook/bart-large-cnn",
                "pegasus": "google/pegasus-xsum",
                "t5": "t5-base"
            },
            "question_answering": {
                "roberta": "deepset/roberta-base-squad2",
                "distilbert": "distilbert-base-cased-distilled-squad"
            }
        }
        
        # Local model cache
        self.local_models = {}
        self.tokenizers = {}
        
        logger.info("HuggingFace service initialized successfully")
    
    async def generate_text(self, 
                          prompt: str,
                          model: str = "mistral-7b",
                          max_tokens: int = 512,
                          temperature: float = 0.7,
                          use_local: bool = False) -> Dict[str, Any]:
        """
        Generate text using HuggingFace models
        
        Args:
            prompt: Input prompt
            model: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            use_local: Whether to use local inference
            
        Returns:
            Dict with generation results
        """
        try:
            if use_local:
                return await self._generate_local(prompt, model, max_tokens, temperature)
            else:
                return await self._generate_api(prompt, model, max_tokens, temperature)
                
        except Exception as e:
            logger.error(f"Error in text generation: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_api(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Generate text using HuggingFace API"""
        model_id = self.models["text_generation"].get(model, model)
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/{model_id}",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "")
                        return {
                            "success": True,
                            "model": model_id,
                            "generated_text": generated_text,
                            "prompt": prompt
                        }
                    else:
                        return {"error": "Unexpected response format"}
                else:
                    error_text = await response.text()
                    logger.error(f"HuggingFace API error: {response.status} - {error_text}")
                    return {"error": f"API error: {response.status}"}
    
    async def _generate_local(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Generate text using local HuggingFace model"""
        try:
            model_id = self.models["text_generation"].get(model, model)
            
            # Load model if not cached
            if model_id not in self.local_models:
                await self._load_local_model(model_id)
            
            # Generate text
            generator = self.local_models[model_id]
            result = generator(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=generator.tokenizer.eos_token_id
            )
            
            generated_text = result[0]["generated_text"]
            # Remove the original prompt from the result
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return {
                "success": True,
                "model": model_id,
                "generated_text": generated_text,
                "prompt": prompt,
                "local_inference": True
            }
            
        except Exception as e:
            logger.error(f"Error in local generation: {str(e)}")
            return {"error": str(e)}
    
    async def _load_local_model(self, model_id: str):
        """Load a model for local inference"""
        try:
            logger.info(f"Loading local model: {model_id}")
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Create pipeline for text generation
            generator = pipeline(
                "text-generation",
                model=model_id,
                tokenizer=tokenizer,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            self.local_models[model_id] = generator
            self.tokenizers[model_id] = tokenizer
            
            logger.info(f"Successfully loaded local model: {model_id}")
            
        except Exception as e:
            logger.error(f"Error loading local model {model_id}: {str(e)}")
            raise
    
    async def get_embeddings(self, 
                           texts: Union[str, List[str]],
                           model: str = "sentence-transformers") -> Dict[str, Any]:
        """
        Get embeddings for text(s)
        
        Args:
            texts: Text or list of texts to embed
            model: Embedding model to use
            
        Returns:
            Dict with embeddings
        """
        try:
            model_id = self.models["embeddings"].get(model, model)
            
            if isinstance(texts, str):
                texts = [texts]
            
            payload = {
                "inputs": texts
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{model_id}",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        embeddings = await response.json()
                        
                        return {
                            "success": True,
                            "model": model_id,
                            "embeddings": embeddings,
                            "input_count": len(texts)
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"HuggingFace embeddings error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error getting embeddings: {str(e)}")
            return {"error": str(e)}
    
    async def classify_text(self, 
                          text: str,
                          task: str = "sentiment",
                          model: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify text using HuggingFace models
        
        Args:
            text: Text to classify
            task: Classification task (sentiment, emotion, toxicity)
            model: Specific model to use
            
        Returns:
            Dict with classification results
        """
        try:
            if not model:
                model_id = self.models["classification"].get(task)
                if not model_id:
                    return {"error": f"Unknown classification task: {task}"}
            else:
                model_id = model
            
            payload = {
                "inputs": text
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{model_id}",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            "success": True,
                            "model": model_id,
                            "task": task,
                            "text": text,
                            "predictions": result
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"HuggingFace classification error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error in text classification: {str(e)}")
            return {"error": str(e)}

class TogetherAIService:
    """
    Together AI model integration service
    Provides access to Together AI's optimized model inference
    """
    
    def __init__(self):
        """Initialize Together AI service"""
        self.api_key = os.getenv("TOGETHER_AI_API_KEY")
        self.base_url = "https://api.together.xyz/v1"
        
        if not self.api_key:
            raise ValueError("TOGETHER_AI_API_KEY must be set")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Optimized model configurations for Sophia AI
        self.models = {
            "chat": {
                "llama2-70b": "meta-llama/Llama-2-70b-chat-hf",
                "llama2-13b": "meta-llama/Llama-2-13b-chat-hf",
                "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.1",
                "mixtral-8x7b": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "qwen-72b": "Qwen/Qwen1.5-72B-Chat"
            },
            "code": {
                "codellama-34b": "codellama/CodeLlama-34b-Instruct-hf",
                "codellama-13b": "codellama/CodeLlama-13b-Instruct-hf",
                "deepseek-coder": "deepseek-ai/deepseek-coder-33b-instruct"
            },
            "embeddings": {
                "e5-large": "togethercomputer/m2-bert-80M-8k-retrieval",
                "bge-large": "BAAI/bge-large-en-v1.5"
            }
        }
        
        logger.info("Together AI service initialized successfully")
    
    async def chat_completion(self,
                            messages: List[Dict[str, str]],
                            model: str = "llama2-70b",
                            max_tokens: int = 512,
                            temperature: float = 0.7,
                            stream: bool = False) -> Dict[str, Any]:
        """
        Create chat completion using Together AI
        
        Args:
            messages: List of message dictionaries
            model: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            
        Returns:
            Dict with completion results
        """
        try:
            model_id = self.models["chat"].get(model, model)
            
            payload = {
                "model": model_id,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": stream
            }
            
            if stream:
                return await self._stream_completion(payload)
            else:
                return await self._complete_completion(payload)
                
        except Exception as e:
            logger.error(f"Error in Together AI chat completion: {str(e)}")
            return {"error": str(e)}
    
    async def _complete_completion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Complete non-streaming chat completion"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    return {
                        "success": True,
                        "model": payload["model"],
                        "response": result,
                        "message": result["choices"][0]["message"]["content"] if result.get("choices") else ""
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Together AI API error: {response.status} - {error_text}")
                    return {"error": f"API error: {response.status}"}
    
    async def _stream_completion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle streaming chat completion"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        content_chunks = []
                        
                        async for line in response.content:
                            line = line.decode('utf-8').strip()
                            if line.startswith('data: '):
                                data = line[6:]  # Remove 'data: ' prefix
                                if data == '[DONE]':
                                    break
                                try:
                                    chunk = json.loads(data)
                                    if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
                                        content_chunks.append(chunk["choices"][0]["delta"]["content"])
                                except json.JSONDecodeError:
                                    continue
                        
                        full_content = "".join(content_chunks)
                        
                        return {
                            "success": True,
                            "model": payload["model"],
                            "message": full_content,
                            "stream": True
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Together AI streaming error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error in streaming completion: {str(e)}")
            return {"error": str(e)}
    
    async def code_completion(self,
                            prompt: str,
                            model: str = "codellama-34b",
                            max_tokens: int = 1024,
                            temperature: float = 0.1) -> Dict[str, Any]:
        """
        Generate code using Together AI code models
        
        Args:
            prompt: Code prompt
            model: Code model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (lower for code)
            
        Returns:
            Dict with code generation results
        """
        try:
            model_id = self.models["code"].get(model, model)
            
            # Format prompt for code generation
            messages = [
                {"role": "system", "content": "You are an expert programmer. Generate clean, efficient, and well-documented code."},
                {"role": "user", "content": prompt}
            ]
            
            payload = {
                "model": model_id,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            result = await self._complete_completion(payload)
            
            if result.get("success"):
                result["code"] = result.get("message", "")
                result["prompt"] = prompt
            
            return result
            
        except Exception as e:
            logger.error(f"Error in code completion: {str(e)}")
            return {"error": str(e)}
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models from Together AI"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        models = await response.json()
                        return {
                            "success": True,
                            "models": models
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Together AI models error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            return {"error": str(e)}

class SophiaModelIntegrationManager:
    """
    Unified manager for HuggingFace and Together AI integrations
    """
    
    def __init__(self):
        """Initialize model integration manager"""
        self.huggingface = HuggingFaceService()
        self.together = TogetherAIService()
        
        # Integration configuration
        self.config = {
            "default_text_provider": "together",
            "default_embedding_provider": "huggingface",
            "default_classification_provider": "huggingface",
            "enable_local_inference": False,
            "model_selection_strategy": "cost_optimized"
        }
        
        logger.info("Sophia model integration manager initialized successfully")
    
    async def generate_text(self,
                          prompt: str,
                          provider: Optional[str] = None,
                          model: Optional[str] = None,
                          **kwargs) -> Dict[str, Any]:
        """
        Generate text using optimal provider and model
        
        Args:
            prompt: Input prompt
            provider: Specific provider to use
            model: Specific model to use
            **kwargs: Additional parameters
            
        Returns:
            Dict with generation results
        """
        try:
            # Determine provider
            if not provider:
                provider = self.config["default_text_provider"]
            
            # Route to appropriate provider
            if provider == "together":
                messages = [{"role": "user", "content": prompt}]
                return await self.together.chat_completion(messages, model or "llama2-70b", **kwargs)
            elif provider == "huggingface":
                return await self.huggingface.generate_text(prompt, model or "mistral-7b", **kwargs)
            else:
                return {"error": f"Unknown provider: {provider}"}
                
        except Exception as e:
            logger.error(f"Error in text generation: {str(e)}")
            return {"error": str(e)}
    
    async def get_embeddings(self,
                           texts: Union[str, List[str]],
                           provider: str = "huggingface",
                           model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get embeddings using optimal provider
        
        Args:
            texts: Text(s) to embed
            provider: Provider to use
            model: Specific model to use
            
        Returns:
            Dict with embeddings
        """
        try:
            if provider == "huggingface":
                return await self.huggingface.get_embeddings(texts, model or "sentence-transformers")
            else:
                return {"error": f"Embeddings not supported for provider: {provider}"}
                
        except Exception as e:
            logger.error(f"Error getting embeddings: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_text(self,
                         text: str,
                         analysis_type: str = "sentiment",
                         provider: str = "huggingface") -> Dict[str, Any]:
        """
        Analyze text using classification models
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis
            provider: Provider to use
            
        Returns:
            Dict with analysis results
        """
        try:
            if provider == "huggingface":
                return await self.huggingface.classify_text(text, analysis_type)
            else:
                return {"error": f"Text analysis not supported for provider: {provider}"}
                
        except Exception as e:
            logger.error(f"Error in text analysis: {str(e)}")
            return {"error": str(e)}

# Global manager instance
sophia_models = None

def get_model_manager() -> SophiaModelIntegrationManager:
    """Get or create global model integration manager"""
    global sophia_models
    if sophia_models is None:
        sophia_models = SophiaModelIntegrationManager()
    return sophia_models

# Convenience functions
async def sophia_generate(prompt: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for text generation"""
    manager = get_model_manager()
    return await manager.generate_text(prompt, **kwargs)

async def sophia_embed(texts: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
    """Convenience function for embeddings"""
    manager = get_model_manager()
    return await manager.get_embeddings(texts, **kwargs)

async def sophia_analyze(text: str, analysis_type: str = "sentiment", **kwargs) -> Dict[str, Any]:
    """Convenience function for text analysis"""
    manager = get_model_manager()
    return await manager.analyze_text(text, analysis_type, **kwargs)

