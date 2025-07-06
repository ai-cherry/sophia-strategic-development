"""
Documentation Loader Service
Implements 3-tier auto-loading system following Claude-Code-Development-Kit patterns
"""

import os
import json
import time
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass
from enum import Enum

from backend.core.auto_esc_config import get_config_value
from backend.utils.custom_logger import logger


class DocumentationTier(Enum):
    """Documentation tiers for auto-loading"""
    FOUNDATION = 1  # Core system knowledge
    COMPONENT = 2   # Service-specific context
    FEATURE = 3     # Task-specific patterns


@dataclass
class DocumentationContext:
    """Documentation context container"""
    tier: DocumentationTier
    task_type: str
    content: Dict[str, Any]
    token_count: int
    loading_time: float


class DocumentationLoaderService:
    """
    3-Tier Documentation Auto-Loading Service
    Implements Claude-Code-Development-Kit auto-loading patterns
    """

    def __init__(self):
        self.docs_root = Path("docs")
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        self.performance_metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_loads": 0,
            "average_load_time": 0.0
        }
        
        # 3-tier documentation structure
        self.tier_structure = {
            DocumentationTier.FOUNDATION: {
                "path": "ai-context",
                "files": [
                    "docs-overview.md",
                    "project-structure.md", 
                    "sophia-brain.md",
                    "data-architecture.md"
                ],
                "priority": "high",
                "max_tokens": 8000
            },
            DocumentationTier.COMPONENT: {
                "path": "components",
                "subdirs": [
                    "mcp-servers",
                    "business-intelligence", 
                    "integrations"
                ],
                "priority": "medium",
                "max_tokens": 4000
            },
            DocumentationTier.FEATURE: {
                "path": "features",
                "subdirs": [
                    "unified-chat",
                    "project-management",
                    "sales-intelligence"
                ],
                "priority": "low",
                "max_tokens": 2000
            }
        }

        # Task type mapping to relevant documentation
        self.task_documentation_mapping = {
            "code_generation": {
                "foundation": ["project-structure.md", "sophia-brain.md"],
                "component": ["mcp-servers", "integrations"],
                "feature": ["unified-chat"]
            },
            "business_intelligence": {
                "foundation": ["data-architecture.md", "sophia-brain.md"],
                "component": ["business-intelligence", "integrations"],
                "feature": ["sales-intelligence", "project-management"]
            },
            "infrastructure": {
                "foundation": ["project-structure.md", "data-architecture.md"],
                "component": ["integrations"],
                "feature": ["unified-chat"]
            },
            "research": {
                "foundation": ["sophia-brain.md"],
                "component": ["business-intelligence"],
                "feature": ["sales-intelligence"]
            },
            "integration": {
                "foundation": ["project-structure.md"],
                "component": ["integrations", "mcp-servers"],
                "feature": ["unified-chat"]
            }
        }

    async def initialize(self):
        """Initialize the documentation loader"""
        # Verify documentation structure exists
        await self._verify_documentation_structure()
        # Pre-load foundation tier for performance
        await self._preload_foundation_tier()
        logger.info("✅ DocumentationLoaderService initialized successfully")

    async def load_tier(self, tier: int, task_type: str) -> DocumentationContext:
        """
        Load documentation for specified tier and task type
        
        Args:
            tier: Documentation tier (1, 2, or 3)
            task_type: Type of task for contextual loading
            
        Returns:
            DocumentationContext with loaded content
        """
        start_time = time.time()
        self.performance_metrics["total_loads"] += 1
        
        # Convert tier number to enum
        doc_tier = DocumentationTier(tier)
        
        # Check cache first
        cache_key = f"{doc_tier.value}_{task_type}"
        if self._is_cache_valid(cache_key):
            self.performance_metrics["cache_hits"] += 1
            return self.cache[cache_key]["content"]
        
        self.performance_metrics["cache_misses"] += 1
        
        # Load documentation content
        content = await self._load_tier_content(doc_tier, task_type)
        
        # Calculate token count (approximate)
        token_count = self._calculate_token_count(content)
        
        loading_time = time.time() - start_time
        
        # Create documentation context
        doc_context = DocumentationContext(
            tier=doc_tier,
            task_type=task_type,
            content=content,
            token_count=token_count,
            loading_time=loading_time
        )
        
        # Cache the result
        self._cache_content(cache_key, doc_context)
        
        # Update performance metrics
        self._update_performance_metrics(loading_time)
        
        return doc_context

    async def load_context_for_complexity(
        self, complexity: str, task_type: str
    ) -> Dict[str, DocumentationContext]:
        """
        Load appropriate documentation tiers based on task complexity
        
        Args:
            complexity: Task complexity (simple, moderate, complex, architecture)
            task_type: Type of task
            
        Returns:
            Dictionary of tier contexts
        """
        tiers_to_load = self._determine_tiers_for_complexity(complexity)
        
        contexts = {}
        for tier in tiers_to_load:
            contexts[f"tier_{tier}"] = await self.load_tier(tier, task_type)
            
        return contexts

    def _determine_tiers_for_complexity(self, complexity: str) -> List[int]:
        """Determine which tiers to load based on complexity"""
        if complexity in ["architecture", "complex"]:
            return [1, 2, 3]  # Foundation + Component + Feature
        elif complexity == "moderate":
            return [2, 3]     # Component + Feature
        else:
            return [3]        # Feature only

    async def _load_tier_content(
        self, tier: DocumentationTier, task_type: str
    ) -> Dict[str, Any]:
        """Load content for a specific tier"""
        tier_config = self.tier_structure[tier]
        content = {}
        
        if tier == DocumentationTier.FOUNDATION:
            # Load foundation files
            relevant_files = self._get_relevant_foundation_files(task_type)
            for file_name in relevant_files:
                file_path = self.docs_root / tier_config["path"] / file_name
                if file_path.exists():
                    content[file_name] = await self._read_file(file_path)
                    
        else:
            # Load component/feature subdirectories
            relevant_subdirs = self._get_relevant_subdirs(tier, task_type)
            for subdir in relevant_subdirs:
                subdir_path = self.docs_root / tier_config["path"] / subdir
                if subdir_path.exists():
                    content[subdir] = await self._read_directory(subdir_path)
                    
        return content

    def _get_relevant_foundation_files(self, task_type: str) -> List[str]:
        """Get relevant foundation files for task type"""
        mapping = self.task_documentation_mapping.get(task_type, {})
        foundation_files = mapping.get("foundation", [])
        
        # Always include docs-overview.md
        if "docs-overview.md" not in foundation_files:
            foundation_files.insert(0, "docs-overview.md")
            
        return foundation_files

    def _get_relevant_subdirs(self, tier: DocumentationTier, task_type: str) -> List[str]:
        """Get relevant subdirectories for tier and task type"""
        mapping = self.task_documentation_mapping.get(task_type, {})
        
        if tier == DocumentationTier.COMPONENT:
            return mapping.get("component", [])
        elif tier == DocumentationTier.FEATURE:
            return mapping.get("feature", [])
        else:
            return []

    async def _read_file(self, file_path: Path) -> str:
        """Read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to read file {file_path}: {e}")
            return ""

    async def _read_directory(self, dir_path: Path) -> Dict[str, str]:
        """Read all markdown files in directory"""
        content = {}
        
        try:
            for file_path in dir_path.glob("*.md"):
                content[file_path.name] = await self._read_file(file_path)
        except Exception as e:
            logger.warning(f"Failed to read directory {dir_path}: {e}")
            
        return content

    def _calculate_token_count(self, content: Dict[str, Any]) -> int:
        """Calculate approximate token count for content"""
        total_chars = 0
        
        def count_chars(obj):
            if isinstance(obj, str):
                return len(obj)
            elif isinstance(obj, dict):
                return sum(count_chars(v) for v in obj.values())
            elif isinstance(obj, list):
                return sum(count_chars(item) for item in obj)
            else:
                return len(str(obj))
        
        total_chars = count_chars(content)
        
        # Approximate token count (1 token ≈ 4 characters)
        return total_chars // 4

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is valid"""
        if cache_key not in self.cache:
            return False
            
        cache_entry = self.cache[cache_key]
        return (time.time() - cache_entry["timestamp"]) < self.cache_ttl

    def _cache_content(self, cache_key: str, doc_context: DocumentationContext):
        """Cache documentation content"""
        self.cache[cache_key] = {
            "content": doc_context,
            "timestamp": time.time()
        }

    def _update_performance_metrics(self, loading_time: float):
        """Update performance metrics"""
        total_loads = self.performance_metrics["total_loads"]
        current_avg = self.performance_metrics["average_load_time"]
        
        # Update running average
        self.performance_metrics["average_load_time"] = (
            (current_avg * (total_loads - 1) + loading_time) / total_loads
        )

    async def _verify_documentation_structure(self):
        """Verify that documentation structure exists"""
        required_paths = [
            self.docs_root / "ai-context",
            self.docs_root / "components", 
            self.docs_root / "features"
        ]
        
        for path in required_paths:
            if not path.exists():
                logger.warning(f"Documentation path missing: {path}")
                # Create directory if it doesn't exist
                path.mkdir(parents=True, exist_ok=True)

    async def _preload_foundation_tier(self):
        """Pre-load foundation tier for performance"""
        try:
            foundation_context = await self.load_tier(1, "general")
            logger.info(f"✅ Pre-loaded foundation tier: {foundation_context.token_count} tokens")
        except Exception as e:
            logger.warning(f"Failed to pre-load foundation tier: {e}")

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        cache_hit_rate = 0
        if self.performance_metrics["total_loads"] > 0:
            cache_hit_rate = (
                self.performance_metrics["cache_hits"] / 
                self.performance_metrics["total_loads"]
            ) * 100
            
        return {
            "cache_hit_rate": round(cache_hit_rate, 2),
            "total_loads": self.performance_metrics["total_loads"],
            "average_load_time": round(self.performance_metrics["average_load_time"], 3),
            "cache_entries": len(self.cache),
            "documentation_tiers": len(self.tier_structure)
        }

    async def clear_cache(self):
        """Clear documentation cache"""
        self.cache.clear()
        logger.info("📝 Documentation cache cleared")

    async def health_check(self) -> Dict[str, Any]:
        """Health check for documentation loader"""
        return {
            "service": "documentation_loader",
            "status": "healthy",
            "documentation_structure": {
                "foundation_tier": len(self.tier_structure[DocumentationTier.FOUNDATION]["files"]),
                "component_tier": len(self.tier_structure[DocumentationTier.COMPONENT]["subdirs"]),
                "feature_tier": len(self.tier_structure[DocumentationTier.FEATURE]["subdirs"])
            },
            "performance_metrics": await self.get_performance_metrics(),
            "cache_ttl": self.cache_ttl,
            "supported_task_types": list(self.task_documentation_mapping.keys())
        }


# Global instance
_loader_instance = None


async def get_documentation_loader() -> DocumentationLoaderService:
    """Get singleton documentation loader instance"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = DocumentationLoaderService()
        await _loader_instance.initialize()
    return _loader_instance