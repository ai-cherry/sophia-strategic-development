"""
Enhanced Multi-Modal Embedding Manager
Implements advanced embedding strategies for comprehensive memory enhancement
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os

from sentence_transformers import SentenceTransformer
from transformers import AutoModel, AutoTokenizer
import torch
import openai
from PIL import Image
import librosa

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingMetadata:
    """Metadata for embeddings"""
    embedding_id: str
    content_type: str  # text, audio, image, multimodal
    model_name: str
    model_version: str
    embedding_dimension: int
    created_timestamp: datetime
    content_hash: str
    domain_specific: bool = False
    language: str = "en"
    quality_score: float = 1.0

class EnhancedEmbeddingManager:
    """Advanced embedding manager with multi-modal and domain-specific capabilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Text embedding models
        self.general_text_model = None
        self.domain_specific_model = None
        self.multilingual_model = None
        
        # Multi-modal models
        self.vision_model = None
        self.audio_model = None
        
        # OpenAI client for advanced embeddings
        self.openai_client = None
        
        # Model configurations
        self.model_configs = {
            "general_text": {
                "model_name": "all-MiniLM-L6-v2",
                "dimension": 384,
                "max_length": 512
            },
            "domain_specific": {
                "model_name": "sentence-transformers/all-mpnet-base-v2",
                "dimension": 768,
                "max_length": 512
            },
            "multilingual": {
                "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                "dimension": 384,
                "max_length": 512
            },
            "openai_ada": {
                "model_name": "text-embedding-ada-002",
                "dimension": 1536,
                "max_length": 8191
            }
        }
        
        # Embedding cache
        self.embedding_cache = {}
        self.cache_size_limit = 10000
        
        # Performance tracking
        self.embedding_stats = {
            "total_embeddings": 0,
            "cache_hits": 0,
            "avg_generation_time": 0.0,
            "model_usage": {}
        }
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize all embedding models"""
        if self.initialized:
            return
        
        try:
            self.logger.info("Initializing enhanced embedding manager...")
            
            # Initialize text models
            self.general_text_model = SentenceTransformer(
                self.model_configs["general_text"]["model_name"]
            )
            
            self.domain_specific_model = SentenceTransformer(
                self.model_configs["domain_specific"]["model_name"]
            )
            
            self.multilingual_model = SentenceTransformer(
                self.model_configs["multilingual"]["model_name"]
            )
            
            # Initialize OpenAI client
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
            
            # Initialize vision model (CLIP)
            try:
                from transformers import CLIPModel, CLIPProcessor
                self.vision_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.vision_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            except Exception as e:
                self.logger.warning(f"Failed to initialize vision model: {e}")
            
            self.initialized = True
            self.logger.info("Enhanced embedding manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize embedding manager: {e}")
            raise
    
    async def generate_text_embedding(
        self, 
        text: str, 
        model_type: str = "general_text",
        domain_context: Optional[str] = None
    ) -> Tuple[List[float], EmbeddingMetadata]:
        """Generate text embedding with specified model"""
        
        if not self.initialized:
            await self.initialize()
        
        # Check cache first
        cache_key = self._generate_cache_key(text, model_type)
        if cache_key in self.embedding_cache:
            self.embedding_stats["cache_hits"] += 1
            return self.embedding_cache[cache_key]
        
        start_time = datetime.now()
        
        try:
            # Select model based on type
            if model_type == "general_text":
                model = self.general_text_model
                config = self.model_configs["general_text"]
            elif model_type == "domain_specific":
                model = self.domain_specific_model
                config = self.model_configs["domain_specific"]
            elif model_type == "multilingual":
                model = self.multilingual_model
                config = self.model_configs["multilingual"]
            elif model_type == "openai_ada" and self.openai_client:
                return await self._generate_openai_embedding(text)
            else:
                # Fallback to general model
                model = self.general_text_model
                config = self.model_configs["general_text"]
            
            # Apply domain-specific preprocessing if context provided
            if domain_context and model_type == "domain_specific":
                text = self._apply_domain_preprocessing(text, domain_context)
            
            # Generate embedding
            embedding = model.encode([text])[0].tolist()
            
            # Create metadata
            metadata = EmbeddingMetadata(
                embedding_id=self._generate_embedding_id(text, model_type),
                content_type="text",
                model_name=config["model_name"],
                model_version="1.0",
                embedding_dimension=len(embedding),
                created_timestamp=datetime.now(),
                content_hash=hashlib.md5(text.encode()).hexdigest(),
                domain_specific=(model_type == "domain_specific"),
                quality_score=self._calculate_text_quality_score(text)
            )
            
            # Cache result
            result = (embedding, metadata)
            self._cache_embedding(cache_key, result)
            
            # Update stats
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(model_type, processing_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate text embedding: {e}")
            raise
    
    async def generate_multimodal_embedding(
        self,
        text: Optional[str] = None,
        image_path: Optional[str] = None,
        audio_path: Optional[str] = None
    ) -> Tuple[List[float], EmbeddingMetadata]:
        """Generate multi-modal embedding combining text, image, and audio"""
        
        if not self.initialized:
            await self.initialize()
        
        embeddings = []
        content_types = []
        
        try:
            # Text embedding
            if text:
                text_emb, _ = await self.generate_text_embedding(text, "domain_specific")
                embeddings.append(text_emb)
                content_types.append("text")
            
            # Image embedding
            if image_path and self.vision_model:
                image_emb = await self._generate_image_embedding(image_path)
                embeddings.append(image_emb)
                content_types.append("image")
            
            # Audio embedding
            if audio_path:
                audio_emb = await self._generate_audio_embedding(audio_path)
                embeddings.append(audio_emb)
                content_types.append("audio")
            
            if not embeddings:
                raise ValueError("At least one modality must be provided")
            
            # Combine embeddings using weighted average
            combined_embedding = self._combine_embeddings(embeddings, content_types)
            
            # Create metadata
            metadata = EmbeddingMetadata(
                embedding_id=self._generate_embedding_id(
                    f"{text or ''}{image_path or ''}{audio_path or ''}", 
                    "multimodal"
                ),
                content_type="multimodal",
                model_name="multimodal_ensemble",
                model_version="1.0",
                embedding_dimension=len(combined_embedding),
                created_timestamp=datetime.now(),
                content_hash=hashlib.md5(
                    f"{text or ''}{image_path or ''}{audio_path or ''}".encode()
                ).hexdigest(),
                domain_specific=True,
                quality_score=self._calculate_multimodal_quality_score(content_types)
            )
            
            return combined_embedding, metadata
            
        except Exception as e:
            self.logger.error(f"Failed to generate multimodal embedding: {e}")
            raise
    
    async def _generate_openai_embedding(self, text: str) -> Tuple[List[float], EmbeddingMetadata]:
        """Generate embedding using OpenAI API"""
        
        try:
            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            embedding = response.data[0].embedding
            
            metadata = EmbeddingMetadata(
                embedding_id=self._generate_embedding_id(text, "openai_ada"),
                content_type="text",
                model_name="text-embedding-ada-002",
                model_version="002",
                embedding_dimension=len(embedding),
                created_timestamp=datetime.now(),
                content_hash=hashlib.md5(text.encode()).hexdigest(),
                domain_specific=False,
                quality_score=0.95  # OpenAI embeddings are generally high quality
            )
            
            return embedding, metadata
            
        except Exception as e:
            self.logger.error(f"Failed to generate OpenAI embedding: {e}")
            raise
    
    async def _generate_image_embedding(self, image_path: str) -> List[float]:
        """Generate image embedding using CLIP"""
        
        try:
            # Load and process image
            image = Image.open(image_path)
            inputs = self.vision_processor(images=image, return_tensors="pt")
            
            # Generate embedding
            with torch.no_grad():
                image_features = self.vision_model.get_image_features(**inputs)
                embedding = image_features.squeeze().numpy().tolist()
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Failed to generate image embedding: {e}")
            raise
    
    async def _generate_audio_embedding(self, audio_path: str) -> List[float]:
        """Generate audio embedding using librosa features"""
        
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=22050)
            
            # Extract features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            
            # Combine features
            features = np.concatenate([
                np.mean(mfccs, axis=1),
                np.mean(spectral_centroids),
                np.mean(spectral_rolloff),
                np.mean(zero_crossing_rate)
            ])
            
            return features.tolist()
            
        except Exception as e:
            self.logger.error(f"Failed to generate audio embedding: {e}")
            raise
    
    def _combine_embeddings(self, embeddings: List[List[float]], content_types: List[str]) -> List[float]:
        """Combine multiple embeddings using weighted average"""
        
        # Define weights for different modalities
        weights = {
            "text": 0.5,
            "image": 0.3,
            "audio": 0.2
        }
        
        # Normalize embeddings to same dimension
        max_dim = max(len(emb) for emb in embeddings)
        normalized_embeddings = []
        
        for i, emb in enumerate(embeddings):
            if len(emb) < max_dim:
                # Pad with zeros
                padded_emb = emb + [0.0] * (max_dim - len(emb))
            else:
                # Truncate if necessary
                padded_emb = emb[:max_dim]
            
            # Apply weight
            weight = weights.get(content_types[i], 0.33)
            weighted_emb = [x * weight for x in padded_emb]
            normalized_embeddings.append(weighted_emb)
        
        # Combine using element-wise average
        combined = [0.0] * max_dim
        for emb in normalized_embeddings:
            for i, val in enumerate(emb):
                combined[i] += val
        
        # Normalize
        norm = np.linalg.norm(combined)
        if norm > 0:
            combined = [x / norm for x in combined]
        
        return combined
    
    def _apply_domain_preprocessing(self, text: str, domain_context: str) -> str:
        """Apply domain-specific preprocessing to text"""
        
        if domain_context == "apartment_industry":
            # Add apartment industry context
            apartment_terms = {
                "unit": "apartment unit",
                "lease": "rental lease agreement",
                "tenant": "apartment tenant",
                "property": "rental property",
                "maintenance": "apartment maintenance"
            }
            
            for term, replacement in apartment_terms.items():
                text = text.replace(term, replacement)
        
        return text
    
    def _calculate_text_quality_score(self, text: str) -> float:
        """Calculate quality score for text content"""
        
        # Basic quality metrics
        length_score = min(len(text) / 100, 1.0)  # Prefer longer text up to 100 chars
        word_count = len(text.split())
        word_score = min(word_count / 20, 1.0)  # Prefer more words up to 20
        
        # Check for meaningful content
        meaningful_chars = sum(1 for c in text if c.isalnum())
        meaningful_score = meaningful_chars / len(text) if text else 0
        
        return (length_score + word_score + meaningful_score) / 3
    
    def _calculate_multimodal_quality_score(self, content_types: List[str]) -> float:
        """Calculate quality score for multimodal content"""
        
        # Higher score for more modalities
        modality_score = len(content_types) / 3  # Max 3 modalities
        
        # Bonus for text + image combination
        if "text" in content_types and "image" in content_types:
            modality_score += 0.2
        
        return min(modality_score, 1.0)
    
    def _generate_cache_key(self, content: str, model_type: str) -> str:
        """Generate cache key for embedding"""
        return hashlib.md5(f"{content}:{model_type}".encode()).hexdigest()
    
    def _generate_embedding_id(self, content: str, model_type: str) -> str:
        """Generate unique embedding ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{content}:{model_type}:{timestamp}".encode()).hexdigest()
    
    def _cache_embedding(self, cache_key: str, result: Tuple[List[float], EmbeddingMetadata]):
        """Cache embedding result"""
        
        if len(self.embedding_cache) >= self.cache_size_limit:
            # Remove oldest entry
            oldest_key = next(iter(self.embedding_cache))
            del self.embedding_cache[oldest_key]
        
        self.embedding_cache[cache_key] = result
    
    def _update_stats(self, model_type: str, processing_time: float):
        """Update embedding statistics"""
        
        self.embedding_stats["total_embeddings"] += 1
        
        # Update average processing time
        total = self.embedding_stats["total_embeddings"]
        current_avg = self.embedding_stats["avg_generation_time"]
        self.embedding_stats["avg_generation_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Update model usage
        if model_type not in self.embedding_stats["model_usage"]:
            self.embedding_stats["model_usage"][model_type] = 0
        self.embedding_stats["model_usage"][model_type] += 1
    
    async def get_embedding_stats(self) -> Dict[str, Any]:
        """Get embedding generation statistics"""
        return {
            **self.embedding_stats,
            "cache_size": len(self.embedding_cache),
            "cache_hit_rate": (
                self.embedding_stats["cache_hits"] / 
                max(self.embedding_stats["total_embeddings"], 1)
            )
        }
    
    async def clear_cache(self):
        """Clear embedding cache"""
        self.embedding_cache.clear()
        self.logger.info("Embedding cache cleared")

# Global instance
enhanced_embedding_manager = EnhancedEmbeddingManager()

