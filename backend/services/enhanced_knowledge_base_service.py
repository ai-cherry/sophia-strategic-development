#!/usr/bin/env python3
"""
Enhanced Knowledge Base Service with Interactive Teaching
Priority #1: Critical NOW implementation for Sophia AI
"""

import logging
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class KnowledgeType(str, Enum):
    """Types of knowledge in the system"""

    COMPANY_INFO = "company_info"
    SALES_PLAYBOOK = "sales_playbook"
    PRODUCT_INFO = "product_info"
    PROCESS_DOCUMENTATION = "process_documentation"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    CUSTOMER_SUCCESS = "customer_success"
    TECHNICAL_DOCS = "technical_docs"


@dataclass
class KnowledgeItem:
    """Enhanced knowledge item with rich metadata"""

    knowledge_id: str
    title: str
    content: str
    knowledge_type: KnowledgeType
    tags: List[str]
    confidence_score: float
    created_at: datetime


class EnhancedKnowledgeBaseService:
    """
    Enhanced Knowledge Base Service with Interactive Teaching

    Core capabilities:
    - Interactive knowledge ingestion with contextual tagging
    - Context-aware knowledge retrieval for universal chat
    - Interactive teaching interface for knowledge refinement
    """

    def __init__(self):
        self.knowledge_cache: Dict[str, KnowledgeItem] = {}
        self.usage_analytics: Dict[str, Any] = {
            "total_queries": 0,
            "successful_retrievals": 0,
            "teaching_sessions": 0,
            "knowledge_items": 0,
        }
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the Enhanced Knowledge Base Service"""
        if self.initialized:
            return

        try:
            logger.info("Initializing Enhanced Knowledge Base Service...")
            self.initialized = True
            logger.info("✅ Enhanced Knowledge Base Service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Knowledge Base Service: {e}")
            raise

    async def interactive_knowledge_ingestion(
        self, content: str, source: str, metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Interactive knowledge ingestion with contextual tagging"""
        if not self.initialized:
            await self.initialize()

        try:
            knowledge_id = f"kb_{int(datetime.now().timestamp())}_{source}"
            title = self._extract_title(content)
            knowledge_type = self._classify_knowledge_type(content)
            tags = self._extract_tags(content)

            knowledge_item = KnowledgeItem(
                knowledge_id=knowledge_id,
                title=title,
                content=content,
                knowledge_type=knowledge_type,
                tags=tags,
                confidence_score=0.8,
                created_at=datetime.now(),
            )

            self.knowledge_cache[knowledge_id] = knowledge_item
            self.usage_analytics["knowledge_items"] += 1

            result = {
                "success": True,
                "knowledge_id": knowledge_id,
                "title": title,
                "knowledge_type": knowledge_type.value,
                "tags": tags,
            }

            logger.info(f"Successfully ingested knowledge: {title} ({knowledge_id})")
            return result

        except Exception as e:
            logger.error(f"Error in knowledge ingestion: {e}")
            return {"success": False, "error": str(e)}

    async def contextual_knowledge_retrieval(
        self, query: str, context: Dict[str, Any] = None, limit: int = 5
    ) -> Dict[str, Any]:
        """Context-aware knowledge retrieval for universal chat"""
        if not self.initialized:
            await self.initialize()

        try:
            results = []
            for item in self.knowledge_cache.values():
                if (
                    query.lower() in item.content.lower()
                    or query.lower() in item.title.lower()
                ):
                    results.append(
                        {
                            "knowledge_id": item.knowledge_id,
                            "title": item.title,
                            "content": item.content,
                            "knowledge_type": item.knowledge_type.value,
                            "tags": item.tags,
                            "relevance_score": 0.8,
                        }
                    )

            results = results[:limit]

            self.usage_analytics["total_queries"] += 1
            if results:
                self.usage_analytics["successful_retrievals"] += 1

            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "knowledge_items": results,
            }

        except Exception as e:
            logger.error(f"Error in contextual knowledge retrieval: {e}")
            return {"success": False, "error": str(e)}

    async def knowledge_teaching_interface(
        self, teaching_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Interactive teaching interface for knowledge refinement"""
        if not self.initialized:
            await self.initialize()

        try:
            session_id = f"teach_{int(datetime.now().timestamp())}"
            feedback = teaching_data.get("feedback", "")
            knowledge_id = teaching_data.get("knowledge_id")

            if knowledge_id and knowledge_id in self.knowledge_cache:
                item = self.knowledge_cache[knowledge_id]
                if feedback and len(feedback) > 5:
                    new_tags = feedback.lower().split()[:3]
                    item.tags.extend(new_tags)
                    item.tags = list(set(item.tags))

            self.usage_analytics["teaching_sessions"] += 1

            result = {
                "success": True,
                "session_id": session_id,
                "improvements_made": {"tags_updated": True if knowledge_id else False},
            }

            logger.info(f"Teaching session completed: {session_id}")
            return result

        except Exception as e:
            logger.error(f"Error in knowledge teaching interface: {e}")
            return {"success": False, "error": str(e)}

    def _extract_title(self, content: str) -> str:
        """Extract title from content"""
        lines = content.split("\n")
        for line in lines[:3]:
            if line.strip() and len(line.strip()) < 100:
                return line.strip()
        return f"Knowledge Item {datetime.now().strftime('%Y%m%d%H%M%S')}"

    def _classify_knowledge_type(self, content: str) -> KnowledgeType:
        """Classify knowledge type"""
        content_lower = content.lower()

        if any(word in content_lower for word in ["sales", "deal", "prospect"]):
            return KnowledgeType.SALES_PLAYBOOK
        elif any(word in content_lower for word in ["product", "feature"]):
            return KnowledgeType.PRODUCT_INFO
        elif any(word in content_lower for word in ["process", "procedure"]):
            return KnowledgeType.PROCESS_DOCUMENTATION
        elif any(word in content_lower for word in ["competitor", "competitive"]):
            return KnowledgeType.COMPETITIVE_INTELLIGENCE
        elif any(word in content_lower for word in ["customer", "support"]):
            return KnowledgeType.CUSTOMER_SUCCESS
        elif any(word in content_lower for word in ["technical", "api", "code"]):
            return KnowledgeType.TECHNICAL_DOCS
        else:
            return KnowledgeType.COMPANY_INFO

    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content"""
        content_lower = content.lower()
        tags = []

        keywords = ["sales", "product", "customer", "technical", "process", "training"]
        for keyword in keywords:
            if keyword in content_lower:
                tags.append(keyword)

        return tags or ["general"]

    async def get_knowledge_analytics(self) -> Dict[str, Any]:
        """Get comprehensive knowledge base analytics"""
        try:
            # Service analytics
            analytics = {
                **self.usage_analytics,
                "cached_items": len(self.knowledge_cache),
                "knowledge_types": {},
                "performance_metrics": {
                    "average_confidence": 0.0,
                    "average_relevance": 0.0,
                    "cache_hit_rate": 0.85,  # Placeholder
                },
            }

            # Analyze cached knowledge items
            if self.knowledge_cache:
                confidence_scores = []
                knowledge_types = {}

                for item in self.knowledge_cache.values():
                    confidence_scores.append(item.confidence_score)

                    # Count knowledge types
                    ktype = item.knowledge_type.value
                    knowledge_types[ktype] = knowledge_types.get(ktype, 0) + 1

                analytics["performance_metrics"]["average_confidence"] = sum(
                    confidence_scores
                ) / len(confidence_scores)
                analytics["knowledge_types"] = knowledge_types

            return analytics

        except Exception as e:
            logger.error(f"Error getting knowledge analytics: {e}")
            return {"error": str(e), "service": "enhanced_knowledge_base"}
