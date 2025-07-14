"""
Pure Qdrant Memory Architecture Configuration
Eliminates all Weaviate dependencies for consistent architecture
"""

from dataclasses import dataclass
from typing import Dict, Any
from backend.core.auto_esc_config import get_qdrant_config

@dataclass
class QdrantMemoryTier:
    """Pure Qdrant memory tier configuration"""
    name: str
    collection_name: str
    ttl_seconds: int
    max_entries: int
    vector_size: int = 1024
    distance_metric: str = "cosine"
    
    def to_qdrant_config(self) -> Dict[str, Any]:
        """Convert to Qdrant collection configuration"""
        return {
            "collection_name": self.collection_name,
            "vector_size": self.vector_size,
            "distance": self.distance_metric,
            "ttl": self.ttl_seconds,
            "max_entries": self.max_entries
        }

class PureQdrantArchitecture:
    """Pure Qdrant-centric memory architecture"""
    
    def __init__(self):
        self.qdrant_config = get_qdrant_config()
        
        # Pure Qdrant memory tiers
        self.memory_tiers = {
            "episodic": QdrantMemoryTier(
                name="Episodic Memory",
                collection_name="sophia_episodic",
                ttl_seconds=3600,  # 1 hour
                max_entries=10000,
                vector_size=1024
            ),
            "semantic": QdrantMemoryTier(
                name="Semantic Memory", 
                collection_name="sophia_semantic",
                ttl_seconds=86400 * 30,  # 30 days
                max_entries=100000,
                vector_size=1024
            ),
            "visual": QdrantMemoryTier(
                name="Visual Memory",
                collection_name="sophia_visual",
                ttl_seconds=86400 * 7,  # 7 days
                max_entries=50000,
                vector_size=1024
            ),
            "procedural": QdrantMemoryTier(
                name="Procedural Memory",
                collection_name="sophia_procedural",
                ttl_seconds=86400 * 14,  # 14 days
                max_entries=25000,
                vector_size=1024
            )
        }
    
    def get_tier_config(self, tier_name: str) -> Dict[str, Any]:
        """Get Qdrant configuration for a specific tier"""
        if tier_name not in self.memory_tiers:
            raise ValueError(f"Unknown memory tier: {tier_name}")
        
        return self.memory_tiers[tier_name].to_qdrant_config()
    
    def get_all_collections(self) -> List[str]:
        """Get all Qdrant collection names"""
        return [tier.collection_name for tier in self.memory_tiers.values()]
