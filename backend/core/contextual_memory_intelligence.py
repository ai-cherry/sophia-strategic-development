"""Contextual Memory Intelligence (CMI) Framework.

Tracks decisions with full context and rationale for institutional knowledge retention
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import aioredis
from pydantic import BaseModel, Field
from sqlalchemy import JSON, Column, DateTime, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.core.auto_esc_config import config
from backend.core.enhanced_embedding_manager import EnhancedEmbeddingManager
from backend.vector.vector_integration import VectorIntegration

Base = declarative_base()


class DecisionType(str, Enum):
    """Types of decisions tracked by CMI"""
        ARCHITECTURE = "architecture"
    BUSINESS = "business"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"


class DecisionImpact(str, Enum):
    """Impact levels of decisions"""
        LOW = "low"

    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContextualDecision(BaseModel):
    """Model for a decision with full context"""
        id: str = Field(default_factory=lambda: str(uuid4()))

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    decision_type: DecisionType
    impact_level: DecisionImpact
    title: str
    description: str
    rationale: str
    context: Dict[str, Any]
    alternatives_considered: List[Dict[str, str]]
    stakeholders: List[str]
    outcomes: Optional[Dict[str, Any]] = None
    related_decisions: List[str] = []
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class DecisionRecord(Base):
    """SQLAlchemy model for decision storage"""
        __tablename__ = "contextual_decisions"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    decision_type = Column(String, nullable=False)
    impact_level = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    context = Column(JSON, nullable=False)
    alternatives_considered = Column(JSON, nullable=False)
    stakeholders = Column(JSON, nullable=False)
    outcomes = Column(JSON)
    related_decisions = Column(JSON)
    tags = Column(JSON)
    metadata = Column(JSON)
    embedding_id = Column(String)


class ContextualMemoryIntelligence:
    """CMI system for tracking and retrieving decisions with context"""
    def __init__(self):

        self.redis_client = None
        self.db_engine = None
        self.async_session = None
        self.embedding_manager = EnhancedEmbeddingManager()
        self.vector_integration = VectorIntegration()
        self._initialized = False

    async def initialize(self):
        """Initialize CMI components"""
        if self._initialized:

            return

        # Initialize Redis for caching
        self.redis_client = await aioredis.create_redis_pool(
            config.redis_url or "redis://localhost:6379", encoding="utf-8"
        )

        # Initialize database
        db_url = config.database_url or "postgresql+asyncpg://localhost/sophia_cmi"
        self.db_engine = create_async_engine(db_url)
        self.async_session = sessionmaker(
            self.db_engine, class_=AsyncSession, expire_on_commit=False
        )

        # Create tables if needed
        async with self.db_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Initialize vector components
        await self.embedding_manager.initialize()
        await self.vector_integration.initialize()

        self._initialized = True

    async def record_decision(
        self, decision: ContextualDecision, auto_link: bool = True
    ) -> str:
        """Record a new decision with full context"""
    await self.initialize()

        # Generate embedding for the decision
        decision_text = f"{decision.title} {decision.description} {decision.rationale}"
        embedding = await self.embedding_manager.generate_embedding(decision_text)

        # Store in vector database
        embedding_id = await self.vector_integration.store_embedding(
            embedding=embedding,
            metadata={
                "type": "decision",
                "decision_id": decision.id,
                "decision_type": decision.decision_type,
                "impact_level": decision.impact_level,
                "timestamp": decision.timestamp.isoformat(),
                "tags": decision.tags,
            },
        )

        # Auto-link related decisions if enabled
        if auto_link:
            related = await self._find_related_decisions(decision, embedding)
            decision.related_decisions.extend([r["id"] for r in related[:5]])

        # Store in database
        async with self.async_session() as session:
            record = DecisionRecord(
                id=decision.id,
                timestamp=decision.timestamp,
                decision_type=decision.decision_type,
                impact_level=decision.impact_level,
                title=decision.title,
                description=decision.description,
                rationale=decision.rationale,
                context=decision.context,
                alternatives_considered=decision.alternatives_considered,
                stakeholders=decision.stakeholders,
                outcomes=decision.outcomes,
                related_decisions=decision.related_decisions,
                tags=decision.tags,
                metadata=decision.metadata,
                embedding_id=embedding_id,
            )
            session.add(record)
            await session.commit()

        # Cache in Redis for quick access
        await self._cache_decision(decision)

        # Trigger analysis for patterns
        asyncio.create_task(self._analyze_decision_patterns(decision))

        return decision.id

    async def retrieve_decision(self, decision_id: str) -> Optional[ContextualDecision]:
        """Retrieve a decision by ID"""
await self.initialize()

        # Check cache first
        cached = await self._get_cached_decision(decision_id)
        if cached:
            return cached

        # Retrieve from database
        async with self.async_session() as session:
            result = await session.get(DecisionRecord, decision_id)
            if result:
                decision = ContextualDecision(
                    id=result.id,
                    timestamp=result.timestamp,
                    decision_type=result.decision_type,
                    impact_level=result.impact_level,
                    title=result.title,
                    description=result.description,
                    rationale=result.rationale,
                    context=result.context,
                    alternatives_considered=result.alternatives_considered,
                    stakeholders=result.stakeholders,
                    outcomes=result.outcomes,
                    related_decisions=result.related_decisions,
                    tags=result.tags,
                    metadata=result.metadata,
                )
                await self._cache_decision(decision)
                return decision

        return None

    async def search_decisions(
        self,
        query: str,
        decision_type: Optional[DecisionType] = None,
        impact_level: Optional[DecisionImpact] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[ContextualDecision]:
        """Search decisions using semantic search and filters"""
    await self.initialize()

        # Generate embedding for query
        query_embedding = await self.embedding_manager.generate_embedding(query)

        # Build metadata filter
        metadata_filter = {"type": "decision"}
        if decision_type:
            metadata_filter["decision_type"] = decision_type
        if impact_level:
            metadata_filter["impact_level"] = impact_level
        if tags:
            metadata_filter["tags"] = {"$in": tags}

        # Search in vector database
        results = await self.vector_integration.search_similar(
            embedding=query_embedding, metadata_filter=metadata_filter, limit=limit
        )

        # Retrieve full decision records
        decisions = []
        for result in results:
            decision_id = result["metadata"]["decision_id"]
            decision = await self.retrieve_decision(decision_id)
            if decision:
                decisions.append(decision)

        return decisions

    async def get_decision_timeline(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        decision_type: Optional[DecisionType] = None,
    ) -> List[ContextualDecision]:
        """Get decisions in chronological order"""
await self.initialize()

        async with self.async_session() as session:
            query = session.query(DecisionRecord)

            if start_date:
                query = query.filter(DecisionRecord.timestamp >= start_date)
            if end_date:
                query = query.filter(DecisionRecord.timestamp <= end_date)
            if decision_type:
                query = query.filter(DecisionRecord.decision_type == decision_type)

            query = query.order_by(DecisionRecord.timestamp.desc())

            results = await session.execute(query)
            records = results.scalars().all()

            decisions = []
            for record in records:
                decision = ContextualDecision(
                    id=record.id,
                    timestamp=record.timestamp,
                    decision_type=record.decision_type,
                    impact_level=record.impact_level,
                    title=record.title,
                    description=record.description,
                    rationale=record.rationale,
                    context=record.context,
                    alternatives_considered=record.alternatives_considered,
                    stakeholders=record.stakeholders,
                    outcomes=record.outcomes,
                    related_decisions=record.related_decisions,
                    tags=record.tags,
                    metadata=record.metadata,
                )
                decisions.append(decision)

            return decisions

    async def analyze_decision_impact(self, decision_id: str) -> Dict[str, Any]:
        """Analyze the impact and outcomes of a decision"""
    await self.initialize()

        decision = await self.retrieve_decision(decision_id)
        if not decision:
            return {"error": "Decision not found"}

        # Get related decisions
        related_decisions = []
        for related_id in decision.related_decisions:
            related = await self.retrieve_decision(related_id)
            if related:
                related_decisions.append(related)

        # Analyze patterns
        analysis = {
            "decision_id": decision_id,
            "title": decision.title,
            "impact_level": decision.impact_level,
            "recorded_outcomes": decision.outcomes,
            "related_decisions_count": len(related_decisions),
            "related_decisions": [
                {
                    "id": r.id,
                    "title": r.title,
                    "type": r.decision_type,
                    "impact": r.impact_level,
                }
                for r in related_decisions
            ],
            "stakeholder_involvement": len(decision.stakeholders),
            "alternatives_evaluated": len(decision.alternatives_considered),
            "tags": decision.tags,
            "time_since_decision": (datetime.utcnow() - decision.timestamp).days,
        }

        # Add AI-generated insights
        insights = await self._generate_decision_insights(decision, related_decisions)
        analysis["ai_insights"] = insights

        return analysis

    async def _find_related_decisions(
        self, decision: ContextualDecision, embedding: List[float]
    ) -> List[Dict[str, Any]]:
        """Find decisions related to the current one"""
        # Search for similar decisions.

        results = await self.vector_integration.search_similar(
            embedding=embedding,
            metadata_filter={"type": "decision", "decision_id": {"$ne": decision.id}},
            limit=10,
        )

        related = []
        for result in results:
            if result["score"] > 0.8:  # High similarity threshold
                related.append(
                    {
                        "id": result["metadata"]["decision_id"],
                        "score": result["score"],
                        "type": result["metadata"]["decision_type"],
                    }
                )

        return related

    async def _cache_decision(self, decision: ContextualDecision):
        """Cache decision in Redis"""
        key = f"cmi:decision:{decision.id}".

        value = decision.json()
        await self.redis_client.setex(key, 3600, value)  # 1 hour TTL

    async def _get_cached_decision(
        self, decision_id: str
    ) -> Optional[ContextualDecision]:
        """Get decision from cache"""
        key = f"cmi:decision:{decision_id}"

        value = await self.redis_client.get(key)
        if value:
            return ContextualDecision.parse_raw(value)
        return None

    async def _analyze_decision_patterns(self, decision: ContextualDecision):
        """Analyze patterns in decision-making"""
        # This runs asynchronously to identify patterns.

        # Implementation would include pattern recognition, trend analysis, etc.
        pass

    async def _generate_decision_insights(
        self, decision: ContextualDecision, related_decisions: List[ContextualDecision]
    ) -> Dict[str, Any]:
        """Generate AI insights about the decision"""
        # This would use LLM to generate insights.

        # For now, return structured analysis
        return {
            "pattern_detected": "Similar decisions tend to have positive outcomes",
            "recommendation": "Continue monitoring for 30 days",
            "risk_assessment": "Low risk based on historical patterns",
            "success_probability": 0.85,
        }

    async def export_decision_history(
        self, format: str = "json", filters: Optional[Dict[str, Any]] = None
    ) -> Union[str, bytes]:
        """Export decision history for analysis or backup"""
        await self.initialize()

        # Retrieve decisions based on filters
        decisions = await self.get_decision_timeline()

        if format == "json":
            return json.dumps([d.dict() for d in decisions], default=str, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


# Singleton instance
cmi = ContextualMemoryIntelligence()
