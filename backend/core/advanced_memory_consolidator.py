"""
Advanced Memory Consolidation and Summarization System
Implements intelligent memory hierarchy and automatic summarization
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

from ..vector.vector_integration_updated import VectorIntegration
from ..agents.core.persistent_memory import PersistentMemory
from .enhanced_embedding_manager import enhanced_embedding_manager

logger = logging.getLogger(__name__)

class MemoryTier(Enum):
    """Memory tier levels"""
    SHORT_TERM = "short_term"      # 0-24 hours
    MEDIUM_TERM = "medium_term"    # 1-30 days
    LONG_TERM = "long_term"        # 30+ days
    ARCHIVED = "archived"          # Compressed/summarized

@dataclass
class MemoryConsolidationRule:
    """Rules for memory consolidation"""
    source_tier: MemoryTier
    target_tier: MemoryTier
    age_threshold: timedelta
    importance_threshold: float
    consolidation_ratio: float  # How much to compress (0.1 = 90% compression)
    preserve_keywords: List[str]

@dataclass
class ConsolidatedMemory:
    """Consolidated memory structure"""
    memory_id: str
    original_memories: List[str]  # IDs of original memories
    consolidated_content: str
    summary: str
    key_points: List[str]
    importance_score: float
    consolidation_timestamp: datetime
    tier: MemoryTier
    metadata: Dict[str, Any]

class AdvancedMemoryConsolidator:
    """Advanced memory consolidation and summarization system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.vector_integration = VectorIntegration()
        
        # Consolidation rules
        self.consolidation_rules = [
            MemoryConsolidationRule(
                source_tier=MemoryTier.SHORT_TERM,
                target_tier=MemoryTier.MEDIUM_TERM,
                age_threshold=timedelta(hours=24),
                importance_threshold=0.6,
                consolidation_ratio=0.3,
                preserve_keywords=["decision", "action", "revenue", "customer", "urgent"]
            ),
            MemoryConsolidationRule(
                source_tier=MemoryTier.MEDIUM_TERM,
                target_tier=MemoryTier.LONG_TERM,
                age_threshold=timedelta(days=30),
                importance_threshold=0.7,
                consolidation_ratio=0.1,
                preserve_keywords=["strategic", "important", "milestone", "achievement"]
            ),
            MemoryConsolidationRule(
                source_tier=MemoryTier.LONG_TERM,
                target_tier=MemoryTier.ARCHIVED,
                age_threshold=timedelta(days=365),
                importance_threshold=0.8,
                consolidation_ratio=0.05,
                preserve_keywords=["critical", "breakthrough", "major", "significant"]
            )
        ]
        
        # Memory importance weights
        self.importance_weights = {
            "business_intelligence": 0.3,
            "decision_value": 0.25,
            "sentiment_score": 0.15,
            "topic_confidence": 0.15,
            "recency": 0.15
        }
        
        # Consolidation statistics
        self.consolidation_stats = {
            "total_consolidations": 0,
            "memories_consolidated": 0,
            "compression_ratio": 0.0,
            "last_consolidation": None
        }
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize the memory consolidator"""
        if self.initialized:
            return
        
        try:
            await self.vector_integration.initialize()
            await enhanced_embedding_manager.initialize()
            
            self.initialized = True
            self.logger.info("Advanced memory consolidator initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize memory consolidator: {e}")
            raise
    
    async def consolidate_memories(self, agent_id: str) -> Dict[str, Any]:
        """Consolidate memories for a specific agent"""
        
        if not self.initialized:
            await self.initialize()
        
        consolidation_results = {
            "consolidations_performed": 0,
            "memories_processed": 0,
            "compression_achieved": 0.0,
            "new_consolidated_memories": []
        }
        
        try:
            # Process each consolidation rule
            for rule in self.consolidation_rules:
                result = await self._apply_consolidation_rule(agent_id, rule)
                
                consolidation_results["consolidations_performed"] += result["consolidations"]
                consolidation_results["memories_processed"] += result["memories_processed"]
                consolidation_results["new_consolidated_memories"].extend(result["new_memories"])
            
            # Calculate overall compression
            if consolidation_results["memories_processed"] > 0:
                consolidation_results["compression_achieved"] = (
                    1 - (consolidation_results["consolidations_performed"] / 
                         consolidation_results["memories_processed"])
                )
            
            # Update statistics
            self._update_consolidation_stats(consolidation_results)
            
            self.logger.info(
                f"Memory consolidation completed for agent {agent_id}: "
                f"{consolidation_results['consolidations_performed']} consolidations, "
                f"{consolidation_results['compression_achieved']:.2%} compression"
            )
            
            return consolidation_results
            
        except Exception as e:
            self.logger.error(f"Memory consolidation failed for agent {agent_id}: {e}")
            raise
    
    async def _apply_consolidation_rule(
        self, 
        agent_id: str, 
        rule: MemoryConsolidationRule
    ) -> Dict[str, Any]:
        """Apply a specific consolidation rule"""
        
        result = {
            "consolidations": 0,
            "memories_processed": 0,
            "new_memories": []
        }
        
        try:
            # Find memories eligible for consolidation
            eligible_memories = await self._find_eligible_memories(agent_id, rule)
            result["memories_processed"] = len(eligible_memories)
            
            if not eligible_memories:
                return result
            
            # Group related memories
            memory_groups = await self._group_related_memories(eligible_memories)
            
            # Consolidate each group
            for group in memory_groups:
                if len(group) >= 2:  # Only consolidate if multiple memories
                    consolidated = await self._consolidate_memory_group(group, rule)
                    
                    if consolidated:
                        # Store consolidated memory
                        await self._store_consolidated_memory(agent_id, consolidated)
                        
                        # Mark original memories as consolidated
                        await self._mark_memories_consolidated(group)
                        
                        result["consolidations"] += 1
                        result["new_memories"].append(consolidated.memory_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to apply consolidation rule: {e}")
            return result
    
    async def _find_eligible_memories(
        self, 
        agent_id: str, 
        rule: MemoryConsolidationRule
    ) -> List[Dict[str, Any]]:
        """Find memories eligible for consolidation based on rule"""
        
        try:
            # Calculate cutoff time
            cutoff_time = datetime.now() - rule.age_threshold
            
            # Search for memories in the source tier older than threshold
            search_filter = {
                "agent_id": agent_id,
                "tier": rule.source_tier.value,
                "created_timestamp": {"$lt": cutoff_time.isoformat()},
                "consolidated": {"$ne": True}
            }
            
            # Use vector search to find relevant memories
            memories = await self.vector_integration.search_pinecone(
                query=f"agent:{agent_id} tier:{rule.source_tier.value}",
                top_k=1000,  # Get many memories for consolidation
                filter_metadata=search_filter
            )
            
            # Filter by importance threshold
            eligible_memories = []
            for memory in memories:
                importance = self._calculate_memory_importance(memory)
                if importance >= rule.importance_threshold:
                    memory["importance_score"] = importance
                    eligible_memories.append(memory)
            
            return eligible_memories
            
        except Exception as e:
            self.logger.error(f"Failed to find eligible memories: {e}")
            return []
    
    async def _group_related_memories(
        self, 
        memories: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group related memories for consolidation"""
        
        try:
            if len(memories) <= 1:
                return [memories] if memories else []
            
            # Calculate similarity matrix
            embeddings = []
            for memory in memories:
                # Generate embedding for memory content
                content = memory.get("metadata", {}).get("content", "")
                if content:
                    embedding, _ = await enhanced_embedding_manager.generate_text_embedding(
                        content, "domain_specific"
                    )
                    embeddings.append(embedding)
                else:
                    embeddings.append([0.0] * 768)  # Default dimension
            
            # Group memories by similarity
            groups = []
            used_indices = set()
            similarity_threshold = 0.7
            
            for i, memory in enumerate(memories):
                if i in used_indices:
                    continue
                
                group = [memory]
                used_indices.add(i)
                
                # Find similar memories
                for j, other_memory in enumerate(memories):
                    if j in used_indices or i == j:
                        continue
                    
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(embeddings[i], embeddings[j])
                    
                    if similarity >= similarity_threshold:
                        group.append(other_memory)
                        used_indices.add(j)
                
                groups.append(group)
            
            return groups
            
        except Exception as e:
            self.logger.error(f"Failed to group related memories: {e}")
            return [memories]  # Return all as one group if grouping fails
    
    async def _consolidate_memory_group(
        self, 
        memory_group: List[Dict[str, Any]], 
        rule: MemoryConsolidationRule
    ) -> Optional[ConsolidatedMemory]:
        """Consolidate a group of related memories"""
        
        try:
            # Extract content from all memories
            contents = []
            metadata_list = []
            
            for memory in memory_group:
                content = memory.get("metadata", {}).get("content", "")
                if content:
                    contents.append(content)
                    metadata_list.append(memory.get("metadata", {}))
            
            if not contents:
                return None
            
            # Generate summary using advanced summarization
            summary = await self._generate_intelligent_summary(
                contents, rule.consolidation_ratio, rule.preserve_keywords
            )
            
            # Extract key points
            key_points = await self._extract_key_points(contents, rule.preserve_keywords)
            
            # Calculate consolidated importance score
            importance_scores = [mem.get("importance_score", 0.5) for mem in memory_group]
            avg_importance = sum(importance_scores) / len(importance_scores)
            
            # Create consolidated memory
            consolidated = ConsolidatedMemory(
                memory_id=f"consolidated_{datetime.now().isoformat()}_{len(memory_group)}",
                original_memories=[mem.get("id", "") for mem in memory_group],
                consolidated_content=summary["consolidated_content"],
                summary=summary["summary"],
                key_points=key_points,
                importance_score=avg_importance,
                consolidation_timestamp=datetime.now(),
                tier=rule.target_tier,
                metadata={
                    "original_count": len(memory_group),
                    "consolidation_rule": rule.source_tier.value + "_to_" + rule.target_tier.value,
                    "compression_ratio": rule.consolidation_ratio,
                    "preserved_keywords": rule.preserve_keywords,
                    "original_metadata": metadata_list
                }
            )
            
            return consolidated
            
        except Exception as e:
            self.logger.error(f"Failed to consolidate memory group: {e}")
            return None
    
    async def _generate_intelligent_summary(
        self, 
        contents: List[str], 
        compression_ratio: float,
        preserve_keywords: List[str]
    ) -> Dict[str, str]:
        """Generate intelligent summary with keyword preservation"""
        
        try:
            # Combine all content
            full_content = "\n\n".join(contents)
            
            # Calculate target length
            target_length = int(len(full_content) * compression_ratio)
            
            # Extract sentences containing preserve keywords
            preserved_sentences = []
            remaining_sentences = []
            
            sentences = full_content.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Check if sentence contains preserve keywords
                contains_keyword = any(
                    keyword.lower() in sentence.lower() 
                    for keyword in preserve_keywords
                )
                
                if contains_keyword:
                    preserved_sentences.append(sentence)
                else:
                    remaining_sentences.append(sentence)
            
            # Build summary
            summary_parts = []
            current_length = 0
            
            # Add preserved sentences first
            for sentence in preserved_sentences:
                if current_length + len(sentence) <= target_length:
                    summary_parts.append(sentence)
                    current_length += len(sentence)
            
            # Add remaining sentences by importance
            remaining_sentences.sort(key=len, reverse=True)  # Prefer longer sentences
            
            for sentence in remaining_sentences:
                if current_length + len(sentence) <= target_length:
                    summary_parts.append(sentence)
                    current_length += len(sentence)
                else:
                    break
            
            consolidated_content = ". ".join(summary_parts) + "."
            
            # Generate executive summary (even more compressed)
            executive_summary = self._generate_executive_summary(
                consolidated_content, preserve_keywords
            )
            
            return {
                "consolidated_content": consolidated_content,
                "summary": executive_summary
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate intelligent summary: {e}")
            return {
                "consolidated_content": "\n\n".join(contents[:3]),  # Fallback
                "summary": "Summary generation failed"
            }
    
    def _generate_executive_summary(
        self, 
        content: str, 
        preserve_keywords: List[str]
    ) -> str:
        """Generate executive summary from consolidated content"""
        
        try:
            sentences = content.split('.')
            
            # Find most important sentences
            important_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Score sentence importance
                score = 0
                
                # Keyword presence
                for keyword in preserve_keywords:
                    if keyword.lower() in sentence.lower():
                        score += 2
                
                # Length (prefer medium-length sentences)
                if 50 <= len(sentence) <= 150:
                    score += 1
                
                # Numbers (often important)
                if any(char.isdigit() for char in sentence):
                    score += 1
                
                if score >= 2:
                    important_sentences.append(sentence)
            
            # Take top 3 sentences
            executive_summary = ". ".join(important_sentences[:3])
            
            if not executive_summary:
                # Fallback to first sentence
                executive_summary = sentences[0] if sentences else "No summary available"
            
            return executive_summary + "."
            
        except Exception as e:
            self.logger.error(f"Failed to generate executive summary: {e}")
            return "Executive summary generation failed"
    
    async def _extract_key_points(
        self, 
        contents: List[str], 
        preserve_keywords: List[str]
    ) -> List[str]:
        """Extract key points from content"""
        
        try:
            key_points = []
            full_content = "\n\n".join(contents)
            
            # Extract sentences with preserve keywords
            sentences = full_content.split('.')
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Check for preserve keywords
                for keyword in preserve_keywords:
                    if keyword.lower() in sentence.lower():
                        # Clean up the sentence
                        clean_sentence = sentence.replace('\n', ' ').strip()
                        if clean_sentence and clean_sentence not in key_points:
                            key_points.append(clean_sentence)
                        break
            
            # Limit to top 5 key points
            return key_points[:5]
            
        except Exception as e:
            self.logger.error(f"Failed to extract key points: {e}")
            return []
    
    def _calculate_memory_importance(self, memory: Dict[str, Any]) -> float:
        """Calculate importance score for a memory"""
        
        try:
            metadata = memory.get("metadata", {})
            
            # Extract importance factors
            business_intelligence = metadata.get("business_intelligence", {})
            decision_value = metadata.get("decision_value", 0)
            sentiment_score = abs(metadata.get("sentiment_score", 0))
            topic_confidence = metadata.get("topic_confidence", 0)
            
            # Calculate recency score
            created_timestamp = metadata.get("created_timestamp")
            if created_timestamp:
                try:
                    created_time = datetime.fromisoformat(created_timestamp.replace('Z', '+00:00'))
                    age_hours = (datetime.now() - created_time).total_seconds() / 3600
                    recency_score = max(0, 1 - (age_hours / (24 * 7)))  # Decay over a week
                except:
                    recency_score = 0.5
            else:
                recency_score = 0.5
            
            # Calculate business intelligence score
            bi_score = 0
            if isinstance(business_intelligence, dict):
                revenue_potential = business_intelligence.get("revenue_potential", 0)
                technology_relevance = business_intelligence.get("technology_relevance", 0)
                performance_impact = business_intelligence.get("performance_impact", 0)
                bi_score = (revenue_potential + technology_relevance + performance_impact) / 3
            
            # Weighted importance calculation
            importance = (
                self.importance_weights["business_intelligence"] * bi_score +
                self.importance_weights["decision_value"] * min(decision_value, 1.0) +
                self.importance_weights["sentiment_score"] * sentiment_score +
                self.importance_weights["topic_confidence"] * topic_confidence +
                self.importance_weights["recency"] * recency_score
            )
            
            return min(importance, 1.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate memory importance: {e}")
            return 0.5  # Default importance
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        
        try:
            if len(vec1) != len(vec2):
                return 0.0
            
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0
    
    async def _store_consolidated_memory(
        self, 
        agent_id: str, 
        consolidated: ConsolidatedMemory
    ):
        """Store consolidated memory in vector database"""
        
        try:
            # Generate embedding for consolidated content
            embedding, emb_metadata = await enhanced_embedding_manager.generate_text_embedding(
                consolidated.consolidated_content, "domain_specific"
            )
            
            # Prepare metadata for storage
            storage_metadata = {
                "agent_id": agent_id,
                "memory_type": "consolidated",
                "tier": consolidated.tier.value,
                "importance_score": consolidated.importance_score,
                "original_count": len(consolidated.original_memories),
                "consolidation_timestamp": consolidated.consolidation_timestamp.isoformat(),
                "summary": consolidated.summary,
                "key_points": json.dumps(consolidated.key_points),
                **consolidated.metadata
            }
            
            # Store in vector database
            await self.vector_integration.index_content(
                content_id=consolidated.memory_id,
                text=consolidated.consolidated_content,
                metadata=storage_metadata
            )
            
            self.logger.info(f"Stored consolidated memory {consolidated.memory_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to store consolidated memory: {e}")
    
    async def _mark_memories_consolidated(self, memory_group: List[Dict[str, Any]]):
        """Mark original memories as consolidated"""
        
        try:
            for memory in memory_group:
                memory_id = memory.get("id")
                if memory_id:
                    # Update metadata to mark as consolidated
                    updated_metadata = memory.get("metadata", {})
                    updated_metadata["consolidated"] = True
                    updated_metadata["consolidation_timestamp"] = datetime.now().isoformat()
                    
                    # Update in vector database
                    await self.vector_integration.index_content(
                        content_id=memory_id,
                        text=memory.get("metadata", {}).get("content", ""),
                        metadata=updated_metadata
                    )
            
        except Exception as e:
            self.logger.error(f"Failed to mark memories as consolidated: {e}")
    
    def _update_consolidation_stats(self, results: Dict[str, Any]):
        """Update consolidation statistics"""
        
        self.consolidation_stats["total_consolidations"] += results["consolidations_performed"]
        self.consolidation_stats["memories_consolidated"] += results["memories_processed"]
        self.consolidation_stats["last_consolidation"] = datetime.now().isoformat()
        
        # Update compression ratio
        if self.consolidation_stats["memories_consolidated"] > 0:
            self.consolidation_stats["compression_ratio"] = (
                1 - (self.consolidation_stats["total_consolidations"] / 
                     self.consolidation_stats["memories_consolidated"])
            )
    
    async def get_consolidation_stats(self) -> Dict[str, Any]:
        """Get consolidation statistics"""
        return self.consolidation_stats.copy()
    
    async def schedule_automatic_consolidation(self, agent_id: str, interval_hours: int = 24):
        """Schedule automatic memory consolidation"""
        
        async def consolidation_task():
            while True:
                try:
                    await asyncio.sleep(interval_hours * 3600)  # Convert to seconds
                    await self.consolidate_memories(agent_id)
                except Exception as e:
                    self.logger.error(f"Automatic consolidation failed: {e}")
        
        # Start background task
        asyncio.create_task(consolidation_task())
        self.logger.info(f"Scheduled automatic consolidation for agent {agent_id} every {interval_hours} hours")

# Global instance
advanced_memory_consolidator = AdvancedMemoryConsolidator()

