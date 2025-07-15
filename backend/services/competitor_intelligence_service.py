"""
Competitor Intelligence Service for Sophia AI
Provides comprehensive competitor analysis and intelligence using Qdrant vector storage
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, 
    Range, MatchValue, UpdateStatus, ScoredPoint
)

logger = logging.getLogger(__name__)

class CompetitorCategory(Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    EMERGING = "emerging"
    SUBSTITUTE = "substitute"

class IntelligenceType(Enum):
    PRODUCT_UPDATE = "product_update"
    PRICING_CHANGE = "pricing_change"
    FUNDING_NEWS = "funding_news"
    PARTNERSHIP = "partnership"
    MARKET_MOVE = "market_move"
    PERSONNEL_CHANGE = "personnel_change"
    ACQUISITION = "acquisition"
    STRATEGY_SHIFT = "strategy_shift"

@dataclass
class CompetitorProfile:
    """Competitor profile data structure"""
    id: str
    name: str
    category: CompetitorCategory
    description: str
    website: str
    founded_year: Optional[int]
    headquarters: str
    employee_count: Optional[int]
    funding_total: Optional[float]
    valuation: Optional[float]
    key_products: List[str]
    target_market: List[str]
    strengths: List[str]
    weaknesses: List[str]
    threat_level: int  # 1-10 scale
    market_share: Optional[float]
    growth_rate: Optional[float]
    last_updated: datetime
    metadata: Dict[str, Any]

@dataclass
class CompetitorIntelligence:
    """Competitor intelligence data structure"""
    id: str
    competitor_id: str
    intelligence_type: IntelligenceType
    title: str
    description: str
    source: str
    source_url: Optional[str]
    impact_score: int  # 1-10 scale
    confidence_score: float  # 0-1 scale
    timestamp: datetime
    tags: List[str]
    metadata: Dict[str, Any]

class CompetitorIntelligenceService:
    """Service for managing competitor intelligence with Qdrant vector storage"""
    
    def __init__(self, qdrant_client: QdrantClient):
        self.client = qdrant_client
        self.profiles_collection = "competitor_profiles"
        self.intelligence_collection = "competitor_intelligence"
        self.embeddings_dimension = 768
        self._initialized = False
        
    async def _ensure_initialized(self):
        """Ensure collections are initialized (lazy initialization)"""
        if not self._initialized:
            await self.initialize_collections()
            self._initialized = True
    
    async def initialize_collections(self):
        """Initialize Qdrant collections for competitor intelligence"""
        try:
            # Create competitor profiles collection
            try:
                self.client.get_collection(self.profiles_collection)
                logger.info(f"✅ Collection '{self.profiles_collection}' already exists")
            except Exception:
                self.client.create_collection(
                    collection_name=self.profiles_collection,
                    vectors_config=VectorParams(
                        size=self.embeddings_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created collection '{self.profiles_collection}'")
            
            # Create competitor intelligence collection
            try:
                self.client.get_collection(self.intelligence_collection)
                logger.info(f"✅ Collection '{self.intelligence_collection}' already exists")
            except Exception:
                self.client.create_collection(
                    collection_name=self.intelligence_collection,
                    vectors_config=VectorParams(
                        size=self.embeddings_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created collection '{self.intelligence_collection}'")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize collections: {e}")
            raise
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (placeholder - would use actual embedding service)"""
        # This is a placeholder - in production, you'd use OpenAI, Anthropic, or local embedding model
        import hashlib
        import struct
        
        # Simple hash-based embedding for demo purposes
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to float vector
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                float_val = struct.unpack('>f', chunk)[0]
                embedding.append(float_val)
        
        # Pad or truncate to desired dimension
        while len(embedding) < self.embeddings_dimension:
            embedding.extend(embedding[:min(len(embedding), self.embeddings_dimension - len(embedding))])
        
        return embedding[:self.embeddings_dimension]
    
    async def add_competitor_profile(self, profile: CompetitorProfile) -> bool:
        """Add or update competitor profile"""
        try:
            # Ensure collections are initialized
            await self._ensure_initialized()
            
            # Generate embedding from profile text
            profile_text = f"{profile.name} {profile.description} {' '.join(profile.key_products)} {' '.join(profile.target_market)}"
            embedding = self._generate_embedding(profile_text)
            
            # Create point for Qdrant
            point = PointStruct(
                id=profile.id,
                vector=embedding,
                payload={
                    **asdict(profile),
                    "last_updated": profile.last_updated.isoformat(),
                    "category": profile.category.value,
                    "search_text": profile_text
                }
            )
            
            # Upsert to Qdrant
            result = self.client.upsert(
                collection_name=self.profiles_collection,
                points=[point]
            )
            
            if result.status == UpdateStatus.COMPLETED:
                logger.info(f"✅ Added competitor profile: {profile.name}")
                return True
            else:
                logger.error(f"❌ Failed to add competitor profile: {profile.name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error adding competitor profile {profile.name}: {e}")
            return False
    
    async def add_intelligence(self, intelligence: CompetitorIntelligence) -> bool:
        """Add competitor intelligence"""
        try:
            # Generate embedding from intelligence text
            intelligence_text = f"{intelligence.title} {intelligence.description} {' '.join(intelligence.tags)}"
            embedding = self._generate_embedding(intelligence_text)
            
            # Create point for Qdrant
            point = PointStruct(
                id=intelligence.id,
                vector=embedding,
                payload={
                    **asdict(intelligence),
                    "timestamp": intelligence.timestamp.isoformat(),
                    "intelligence_type": intelligence.intelligence_type.value,
                    "search_text": intelligence_text
                }
            )
            
            # Upsert to Qdrant
            result = self.client.upsert(
                collection_name=self.intelligence_collection,
                points=[point]
            )
            
            if result.status == UpdateStatus.COMPLETED:
                logger.info(f"✅ Added intelligence: {intelligence.title}")
                return True
            else:
                logger.error(f"❌ Failed to add intelligence: {intelligence.title}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error adding intelligence {intelligence.title}: {e}")
            return False
    
    async def search_competitors(self, query: str, limit: int = 10, category: Optional[CompetitorCategory] = None) -> List[Dict[str, Any]]:
        """Search competitors by query"""
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Build filter
            filter_conditions = []
            if category:
                filter_conditions.append(
                    FieldCondition(key="category", match=MatchValue(value=category.value))
                )
            
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Search Qdrant
            results = self.client.search(
                collection_name=self.profiles_collection,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit
            )
            
            # Format results
            competitors = []
            for result in results:
                competitor = result.payload.copy()
                competitor["similarity_score"] = result.score
                competitors.append(competitor)
            
            logger.info(f"🔍 Found {len(competitors)} competitors for query: {query}")
            return competitors
            
        except Exception as e:
            logger.error(f"❌ Error searching competitors: {e}")
            return []
    
    async def search_intelligence(self, query: str, limit: int = 20, competitor_id: Optional[str] = None, 
                                intelligence_type: Optional[IntelligenceType] = None,
                                days_back: int = 30) -> List[Dict[str, Any]]:
        """Search competitor intelligence"""
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Build filter
            filter_conditions = []
            
            if competitor_id:
                filter_conditions.append(
                    FieldCondition(key="competitor_id", match=MatchValue(value=competitor_id))
                )
            
            if intelligence_type:
                filter_conditions.append(
                    FieldCondition(key="intelligence_type", match=MatchValue(value=intelligence_type.value))
                )
            
            # Date range filter
            cutoff_date = datetime.now() - timedelta(days=days_back)
            filter_conditions.append(
                FieldCondition(
                    key="timestamp",
                    range=Range(gte=cutoff_date.isoformat())
                )
            )
            
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Search Qdrant
            results = self.client.search(
                collection_name=self.intelligence_collection,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit
            )
            
            # Format results
            intelligence_items = []
            for result in results:
                item = result.payload.copy()
                item["similarity_score"] = result.score
                intelligence_items.append(item)
            
            logger.info(f"🔍 Found {len(intelligence_items)} intelligence items for query: {query}")
            return intelligence_items
            
        except Exception as e:
            logger.error(f"❌ Error searching intelligence: {e}")
            return []
    
    async def get_competitor_profile(self, competitor_id: str) -> Optional[Dict[str, Any]]:
        """Get competitor profile by ID"""
        try:
            result = self.client.retrieve(
                collection_name=self.profiles_collection,
                ids=[competitor_id]
            )
            
            if result:
                return result[0].payload
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving competitor profile {competitor_id}: {e}")
            return None
    
    async def get_competitor_intelligence(self, competitor_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all intelligence for a specific competitor"""
        try:
            # Search with competitor filter
            results = self.client.scroll(
                collection_name=self.intelligence_collection,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="competitor_id", match=MatchValue(value=competitor_id))
                    ]
                ),
                limit=limit
            )
            
            intelligence_items = []
            for result in results[0]:  # results is a tuple (points, next_page_offset)
                intelligence_items.append(result.payload)
            
            # Sort by timestamp (most recent first)
            intelligence_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            logger.info(f"📊 Retrieved {len(intelligence_items)} intelligence items for competitor {competitor_id}")
            return intelligence_items
            
        except Exception as e:
            logger.error(f"❌ Error retrieving intelligence for competitor {competitor_id}: {e}")
            return []
    
    async def get_threat_analysis(self) -> Dict[str, Any]:
        """Get comprehensive threat analysis"""
        try:
            # Get all competitor profiles
            all_profiles = self.client.scroll(
                collection_name=self.profiles_collection,
                limit=1000
            )[0]
            
            # Analyze threat levels
            threat_analysis = {
                "total_competitors": len(all_profiles),
                "threat_distribution": {
                    "critical": 0,  # 8-10
                    "high": 0,      # 6-7
                    "medium": 0,    # 4-5
                    "low": 0        # 1-3
                },
                "category_distribution": {
                    "direct": 0,
                    "indirect": 0,
                    "emerging": 0,
                    "substitute": 0
                },
                "top_threats": [],
                "emerging_threats": [],
                "market_insights": {
                    "total_market_share": 0,
                    "average_growth_rate": 0,
                    "funding_trends": []
                }
            }
            
            total_growth = 0
            growth_count = 0
            
            for profile in all_profiles:
                payload = profile.payload
                threat_level = payload.get("threat_level", 0)
                category = payload.get("category", "")
                
                # Threat distribution
                if threat_level >= 8:
                    threat_analysis["threat_distribution"]["critical"] += 1
                elif threat_level >= 6:
                    threat_analysis["threat_distribution"]["high"] += 1
                elif threat_level >= 4:
                    threat_analysis["threat_distribution"]["medium"] += 1
                else:
                    threat_analysis["threat_distribution"]["low"] += 1
                
                # Category distribution
                if category in threat_analysis["category_distribution"]:
                    threat_analysis["category_distribution"][category] += 1
                
                # Top threats
                if threat_level >= 7:
                    threat_analysis["top_threats"].append({
                        "name": payload.get("name", ""),
                        "threat_level": threat_level,
                        "category": category,
                        "key_products": payload.get("key_products", [])
                    })
                
                # Emerging threats
                if category == "emerging":
                    threat_analysis["emerging_threats"].append({
                        "name": payload.get("name", ""),
                        "threat_level": threat_level,
                        "growth_rate": payload.get("growth_rate", 0)
                    })
                
                # Market insights
                market_share = payload.get("market_share", 0)
                if market_share:
                    threat_analysis["market_insights"]["total_market_share"] += market_share
                
                growth_rate = payload.get("growth_rate", 0)
                if growth_rate:
                    total_growth += growth_rate
                    growth_count += 1
            
            # Calculate averages
            if growth_count > 0:
                threat_analysis["market_insights"]["average_growth_rate"] = total_growth / growth_count
            
            # Sort top threats
            threat_analysis["top_threats"].sort(key=lambda x: x["threat_level"], reverse=True)
            threat_analysis["emerging_threats"].sort(key=lambda x: x["growth_rate"], reverse=True)
            
            logger.info(f"📈 Generated threat analysis for {len(all_profiles)} competitors")
            return threat_analysis
            
        except Exception as e:
            logger.error(f"❌ Error generating threat analysis: {e}")
            return {}
    
    async def get_intelligence_summary(self, days_back: int = 7) -> Dict[str, Any]:
        """Get intelligence summary for recent period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Get recent intelligence
            results = self.client.scroll(
                collection_name=self.intelligence_collection,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="timestamp",
                            range=Range(gte=cutoff_date.isoformat())
                        )
                    ]
                ),
                limit=1000
            )[0]
            
            summary = {
                "total_items": len(results),
                "period_days": days_back,
                "type_distribution": {},
                "impact_analysis": {
                    "high_impact": 0,    # 8-10
                    "medium_impact": 0,  # 5-7
                    "low_impact": 0      # 1-4
                },
                "top_intelligence": [],
                "trending_topics": [],
                "competitor_activity": {}
            }
            
            for result in results:
                payload = result.payload
                intel_type = payload.get("intelligence_type", "unknown")
                impact_score = payload.get("impact_score", 0)
                competitor_id = payload.get("competitor_id", "unknown")
                
                # Type distribution
                summary["type_distribution"][intel_type] = summary["type_distribution"].get(intel_type, 0) + 1
                
                # Impact analysis
                if impact_score >= 8:
                    summary["impact_analysis"]["high_impact"] += 1
                elif impact_score >= 5:
                    summary["impact_analysis"]["medium_impact"] += 1
                else:
                    summary["impact_analysis"]["low_impact"] += 1
                
                # Top intelligence
                if impact_score >= 7:
                    summary["top_intelligence"].append({
                        "title": payload.get("title", ""),
                        "competitor_id": competitor_id,
                        "impact_score": impact_score,
                        "intelligence_type": intel_type,
                        "timestamp": payload.get("timestamp", "")
                    })
                
                # Competitor activity
                summary["competitor_activity"][competitor_id] = summary["competitor_activity"].get(competitor_id, 0) + 1
            
            # Sort top intelligence
            summary["top_intelligence"].sort(key=lambda x: x["impact_score"], reverse=True)
            
            logger.info(f"📊 Generated intelligence summary for {days_back} days: {len(results)} items")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating intelligence summary: {e}")
            return {}

# Factory function for creating service instance
def create_competitor_intelligence_service() -> CompetitorIntelligenceService:
    """Create competitor intelligence service with Qdrant client"""
    try:
        # For now, use a simple in-memory client for development
        # In production, this would use the cloud Qdrant configuration
        from qdrant_client import QdrantClient
        
        # Try to create a simple client (this will work locally)
        client = QdrantClient(":memory:")
        
        service = CompetitorIntelligenceService(client)
        
        # Note: Collection initialization will be done lazily on first use
        # to avoid asyncio event loop issues during service creation
        
        return service
        
    except Exception as e:
        logger.error(f"❌ Failed to create competitor intelligence service: {e}")
        raise 