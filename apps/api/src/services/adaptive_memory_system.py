"""
🧠 ADAPTIVE MEMORY SYSTEM
Memory system that learns from usage patterns and improves over time

Created: July 14, 2025
Phase: 2.1 - Advanced Memory Intelligence
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from collections import defaultdict, deque

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, UpdateStatus

from ..core.truthful_config import get_real_QDRANT_config
from .advanced_hybrid_search_service import SearchResult, SearchContext, BusinessInsights

logger = logging.getLogger(__name__)

class FeedbackType(Enum):
    CLICK = "click"
    RATING = "rating"
    BOOKMARK = "bookmark"
    SHARE = "share"
    DISMISS = "dismiss"
    NEGATIVE_FEEDBACK = "negative_feedback"

class LearningPattern(Enum):
    USER_PREFERENCE = "user_preference"
    QUERY_REFINEMENT = "query_refinement"
    CONTENT_RELEVANCE = "content_relevance"
    TEMPORAL_PATTERN = "temporal_pattern"
    BUSINESS_CONTEXT = "business_context"

@dataclass
class UserFeedback:
    """User feedback on search results"""
    user_id: str
    query: str
    result_id: str
    feedback_type: FeedbackType
    rating: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

@dataclass
class UserProfile:
    """User profile with learned preferences"""
    user_id: str
    preferred_topics: List[str] = field(default_factory=list)
    search_patterns: Dict[str, float] = field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    business_focus_areas: List[str] = field(default_factory=list)
    personalization_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    learning_velocity: float = 0.1  # How quickly to adapt

@dataclass
class LearningInsight:
    """Insight learned from user interactions"""
    pattern_type: LearningPattern
    description: str
    confidence: float
    impact_score: float
    evidence: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None

class AdaptiveMemorySystem:
    """
    Memory system that improves over time by learning from:
    - User interaction patterns
    - Search success/failure rates
    - Business context relevance
    - Temporal usage patterns
    """
    
    def __init__(self):
        self.QDRANT_config = get_real_QDRANT_config()
        self.client = None
        self.user_profiles: Dict[str, UserProfile] = {}
        self.learning_insights: List[LearningInsight] = []
        self.interaction_buffer: deque = deque(maxlen=10000)
        self.learning_cache: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        # Learning parameters
        self.min_interactions_for_learning = 5
        self.confidence_threshold = 0.7
        self.learning_rate = 0.1
        
    async def initialize(self):
        """Initialize the adaptive memory system"""
        try:
            self.client = QdrantClient(
                url=self.QDRANT_config["url"],
                api_key=self.QDRANT_config["api_key"],
                timeout=self.QDRANT_config["timeout"]
            )
            
            # Load existing user profiles
            await self._load_user_profiles()
            
            # Load learning insights
            await self._load_learning_insights()
            
            # Start background learning process
            asyncio.create_task(self._continuous_learning_loop())
            
            self.logger.info("✅ Adaptive Memory System initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Adaptive Memory System: {e}")
            raise

    async def learn_from_interaction(self, query: str, results: List[SearchResult], 
                                   user_feedback: UserFeedback):
        """
        Learn from user interaction to improve future searches
        """
        try:
            # 1. Update relevance scores based on user feedback
            await self._update_relevance_scores(results, user_feedback)
            
            # 2. Learn user preferences for future personalization
            await self._update_user_profile(query, user_feedback)
            
            # 3. Improve collection routing
            await self._optimize_collection_routing(query, results, user_feedback)
            
            # 4. Update semantic understanding
            await self._refine_semantic_embeddings(query, user_feedback)
            
            # 5. Store interaction for future learning
            await self._store_interaction(query, results, user_feedback)
            
            self.logger.info(f"✅ Learned from interaction: {user_feedback.feedback_type.value}")
            
        except Exception as e:
            self.logger.error(f"❌ Learning from interaction failed: {e}")
            raise

    async def _update_relevance_scores(self, results: List[SearchResult], 
                                     user_feedback: UserFeedback):
        """Update relevance scores based on user feedback"""
        try:
            # Calculate relevance adjustment based on feedback
            relevance_adjustment = self._calculate_relevance_adjustment(user_feedback)
            
            # Find the result that received feedback
            target_result = None
            for result in results:
                if result.id == user_feedback.result_id:
                    target_result = result
                    break
            
            if not target_result:
                return
            
            # Update the result's metadata with new relevance score
            updated_payload = target_result.metadata.copy()
            current_relevance = updated_payload.get("relevance_score", 0.5)
            new_relevance = current_relevance + relevance_adjustment
            updated_payload["relevance_score"] = max(0.0, min(1.0, new_relevance))
            
            # Update user-specific relevance
            user_relevance_key = f"user_relevance_{user_feedback.user_id}"
            user_relevance = updated_payload.get(user_relevance_key, 0.5)
            updated_payload[user_relevance_key] = user_relevance + relevance_adjustment
            
            # Update feedback count
            feedback_count = updated_payload.get("feedback_count", 0) + 1
            updated_payload["feedback_count"] = feedback_count
            
            # Update in Qdrant
            await self._update_point_payload(target_result.id, updated_payload)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update relevance scores: {e}")

    async def _update_user_profile(self, query: str, user_feedback: UserFeedback):
        """Update user profile based on interaction"""
        try:
            user_id = user_feedback.user_id
            
            # Get or create user profile
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = UserProfile(user_id=user_id)
            
            profile = self.user_profiles[user_id]
            
            # Extract topics from query
            query_topics = await self._extract_topics(query)
            
            # Update preferred topics based on feedback
            if user_feedback.feedback_type in [FeedbackType.CLICK, FeedbackType.RATING, FeedbackType.BOOKMARK]:
                for topic in query_topics:
                    if topic in profile.preferred_topics:
                        # Increase preference strength
                        topic_index = profile.preferred_topics.index(topic)
                        # Move to front (most preferred)
                        profile.preferred_topics.pop(topic_index)
                        profile.preferred_topics.insert(0, topic)
                    else:
                        # Add new preferred topic
                        profile.preferred_topics.append(topic)
                        
                    # Keep only top 20 topics
                    profile.preferred_topics = profile.preferred_topics[:20]
            
            # Update search patterns
            query_pattern = await self._extract_query_pattern(query)
            if query_pattern in profile.search_patterns:
                profile.search_patterns[query_pattern] += 0.1
            else:
                profile.search_patterns[query_pattern] = 0.1
            
            # Update interaction history
            interaction = {
                "query": query,
                "feedback_type": user_feedback.feedback_type.value,
                "rating": user_feedback.rating,
                "timestamp": user_feedback.timestamp.isoformat(),
                "context": user_feedback.context
            }
            profile.interaction_history.append(interaction)
            
            # Keep only last 100 interactions
            profile.interaction_history = profile.interaction_history[-100:]
            
            # Update business focus areas
            business_areas = await self._extract_business_areas(query)
            for area in business_areas:
                if area not in profile.business_focus_areas:
                    profile.business_focus_areas.append(area)
            
            # Update personalization score
            profile.personalization_score = await self._calculate_personalization_score(profile)
            profile.last_updated = datetime.now()
            
            # Save updated profile
            await self._save_user_profile(profile)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update user profile: {e}")

    async def _optimize_collection_routing(self, query: str, results: List[SearchResult], 
                                         user_feedback: UserFeedback):
        """Optimize which collections are most useful for different query types"""
        try:
            # Analyze which collections provided the most useful results
            collection_performance = defaultdict(list)
            
            for result in results:
                collection = result.source
                if result.id == user_feedback.result_id:
                    # This result received feedback
                    score = self._calculate_relevance_adjustment(user_feedback)
                    collection_performance[collection].append(score)
                else:
                    # No feedback, neutral score
                    collection_performance[collection].append(0.0)
            
            # Update collection routing preferences
            query_type = await self._classify_query_type(query)
            routing_key = f"collection_routing_{query_type}"
            
            if routing_key not in self.learning_cache:
                self.learning_cache[routing_key] = {}
            
            for collection, scores in collection_performance.items():
                avg_score = sum(scores) / len(scores) if scores else 0.0
                
                if collection in self.learning_cache[routing_key]:
                    # Update with learning rate
                    current_score = self.learning_cache[routing_key][collection]
                    new_score = current_score + self.learning_rate * (avg_score - current_score)
                    self.learning_cache[routing_key][collection] = new_score
                else:
                    self.learning_cache[routing_key][collection] = avg_score
            
        except Exception as e:
            self.logger.error(f"❌ Failed to optimize collection routing: {e}")

    async def _refine_semantic_embeddings(self, query: str, user_feedback: UserFeedback):
        """Refine semantic understanding based on user feedback"""
        try:
            # This would integrate with your embedding service to improve embeddings
            # For now, we'll store the feedback for future embedding model training
            
            embedding_feedback = {
                "query": query,
                "result_id": user_feedback.result_id,
                "feedback_type": user_feedback.feedback_type.value,
                "rating": user_feedback.rating,
                "timestamp": user_feedback.timestamp.isoformat(),
                "user_id": user_feedback.user_id
            }
            
            # Store in learning cache for future embedding model updates
            if "embedding_feedback" not in self.learning_cache:
                self.learning_cache["embedding_feedback"] = []
            
            self.learning_cache["embedding_feedback"].append(embedding_feedback)
            
            # Keep only recent feedback for embedding training
            if len(self.learning_cache["embedding_feedback"]) > 1000:
                self.learning_cache["embedding_feedback"] = self.learning_cache["embedding_feedback"][-1000:]
            
        except Exception as e:
            self.logger.error(f"❌ Failed to refine semantic embeddings: {e}")

    async def _store_interaction(self, query: str, results: List[SearchResult], 
                               user_feedback: UserFeedback):
        """Store interaction for future learning"""
        try:
            interaction = {
                "query": query,
                "num_results": len(results),
                "feedback": {
                    "user_id": user_feedback.user_id,
                    "result_id": user_feedback.result_id,
                    "feedback_type": user_feedback.feedback_type.value,
                    "rating": user_feedback.rating,
                    "timestamp": user_feedback.timestamp.isoformat()
                },
                "context": user_feedback.context,
                "session_id": user_feedback.session_id
            }
            
            self.interaction_buffer.append(interaction)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store interaction: {e}")

    async def get_personalized_search_context(self, user_id: str, query: str) -> SearchContext:
        """Get personalized search context based on user profile"""
        try:
            # Get user profile
            profile = self.user_profiles.get(user_id)
            if not profile:
                # Return default context for new users
                return SearchContext(
                    user_id=user_id,
                    session_id=f"session_{datetime.now().timestamp()}",
                    business_domain="general"
                )
            
            # Determine business domain based on user's focus areas
            business_domain = "general"
            if profile.business_focus_areas:
                business_domain = profile.business_focus_areas[0]  # Primary focus
            
            # Adjust parameters based on user profile
            max_results = 50
            confidence_threshold = 0.7
            
            # Adjust based on user's interaction patterns
            if profile.personalization_score > 0.8:
                # Highly personalized user - can use lower confidence threshold
                confidence_threshold = 0.6
                max_results = 60
            
            return SearchContext(
                user_id=user_id,
                session_id=f"session_{datetime.now().timestamp()}",
                business_domain=business_domain,
                max_results=max_results,
                confidence_threshold=confidence_threshold,
                personalization_enabled=True
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get personalized search context: {e}")
            # Return default context on error
            return SearchContext(
                user_id=user_id,
                session_id=f"session_{datetime.now().timestamp()}",
                business_domain="general"
            )

    async def generate_learning_insights(self) -> List[LearningInsight]:
        """Generate insights about learned patterns"""
        try:
            insights = []
            
            # Analyze user preference patterns
            preference_insights = await self._analyze_user_preferences()
            insights.extend(preference_insights)
            
            # Analyze query patterns
            query_insights = await self._analyze_query_patterns()
            insights.extend(query_insights)
            
            # Analyze content relevance patterns
            content_insights = await self._analyze_content_relevance()
            insights.extend(content_insights)
            
            # Analyze temporal patterns
            temporal_insights = await self._analyze_temporal_patterns()
            insights.extend(temporal_insights)
            
            # Store insights
            self.learning_insights.extend(insights)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate learning insights: {e}")
            return []

    async def _continuous_learning_loop(self):
        """Continuous learning background process"""
        while True:
            try:
                # Wait for sufficient interactions
                await asyncio.sleep(300)  # Check every 5 minutes
                
                if len(self.interaction_buffer) < self.min_interactions_for_learning:
                    continue
                
                # Generate learning insights
                await self.generate_learning_insights()
                
                # Update collection routing optimization
                await self._update_collection_routing_optimization()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                self.logger.info("✅ Continuous learning cycle completed")
                
            except Exception as e:
                self.logger.error(f"❌ Continuous learning loop error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    # Helper methods
    async def _calculate_relevance_adjustment(self, feedback: UserFeedback) -> float:
        """Calculate relevance score adjustment based on feedback"""
        adjustments = {
            FeedbackType.CLICK: 0.1,
            FeedbackType.RATING: feedback.rating * 0.2 if feedback.rating else 0.1,
            FeedbackType.BOOKMARK: 0.3,
            FeedbackType.SHARE: 0.2,
            FeedbackType.DISMISS: -0.1,
            FeedbackType.NEGATIVE_FEEDBACK: -0.3
        }
        return adjustments.get(feedback.feedback_type, 0.0)

    async def _extract_topics(self, query: str) -> List[str]:
        """Extract topics from query"""
        # Simple topic extraction (would use NLP in production)
        import re
        words = re.findall(r'\b\w+\b', query.lower())
        return [word for word in words if len(word) > 3]

    async def _extract_query_pattern(self, query: str) -> str:
        """Extract query pattern for categorization"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["how", "what", "why", "when", "where"]):
            return "question"
        elif any(word in query_lower for word in ["find", "search", "show", "get"]):
            return "search"
        elif any(word in query_lower for word in ["compare", "versus", "vs"]):
            return "comparison"
        else:
            return "general"

    async def _extract_business_areas(self, query: str) -> List[str]:
        """Extract business areas from query"""
        query_lower = query.lower()
        areas = []
        
        if any(word in query_lower for word in ["customer", "client", "account"]):
            areas.append("customer_management")
        if any(word in query_lower for word in ["sales", "revenue", "deal"]):
            areas.append("sales")
        if any(word in query_lower for word in ["market", "competition"]):
            areas.append("market_intelligence")
        if any(word in query_lower for word in ["finance", "budget", "cost"]):
            areas.append("finance")
        
        return areas

    async def _calculate_personalization_score(self, profile: UserProfile) -> float:
        """Calculate personalization score based on profile data"""
        score = 0.0
        
        # Score based on number of interactions
        score += min(len(profile.interaction_history) * 0.01, 0.3)
        
        # Score based on topic preferences
        score += min(len(profile.preferred_topics) * 0.02, 0.3)
        
        # Score based on search patterns
        score += min(len(profile.search_patterns) * 0.05, 0.4)
        
        return min(score, 1.0)

    async def _classify_query_type(self, query: str) -> str:
        """Classify query type for routing optimization"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["customer", "client"]):
            return "customer"
        elif any(word in query_lower for word in ["sales", "revenue"]):
            return "sales"
        elif any(word in query_lower for word in ["market", "competition"]):
            return "market"
        elif any(word in query_lower for word in ["code", "development"]):
            return "technical"
        else:
            return "general"

    async def _update_point_payload(self, point_id: str, payload: Dict[str, Any]):
        """Update point payload in Qdrant"""
        try:
            # This would update the point in the appropriate collection
            # For now, we'll log the update
            self.logger.info(f"Updating point {point_id} with new payload")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update point payload: {e}")

    async def _load_user_profiles(self):
        """Load existing user profiles from storage"""
        # This would load from persistent storage
        # For now, start with empty profiles
        pass

    async def _save_user_profile(self, profile: UserProfile):
        """Save user profile to persistent storage"""
        # This would save to persistent storage
        # For now, keep in memory
        pass

    async def _load_learning_insights(self):
        """Load existing learning insights from storage"""
        # This would load from persistent storage
        # For now, start with empty insights
        pass

    async def _analyze_user_preferences(self) -> List[LearningInsight]:
        """Analyze user preference patterns"""
        insights = []
        
        # Analyze common preferred topics across users
        all_topics = []
        for profile in self.user_profiles.values():
            all_topics.extend(profile.preferred_topics)
        
        if all_topics:
            from collections import Counter
            topic_counts = Counter(all_topics)
            most_common = topic_counts.most_common(5)
            
            insight = LearningInsight(
                pattern_type=LearningPattern.USER_PREFERENCE,
                description=f"Most popular topics: {', '.join([t[0] for t in most_common])}",
                confidence=0.8,
                impact_score=0.7,
                evidence=[{"topic_counts": dict(most_common)}]
            )
            insights.append(insight)
        
        return insights

    async def _analyze_query_patterns(self) -> List[LearningInsight]:
        """Analyze query patterns"""
        insights = []
        
        # Analyze query patterns from interaction buffer
        query_patterns = defaultdict(int)
        for interaction in self.interaction_buffer:
            pattern = await self._extract_query_pattern(interaction["query"])
            query_patterns[pattern] += 1
        
        if query_patterns:
            most_common_pattern = max(query_patterns, key=query_patterns.get)
            insight = LearningInsight(
                pattern_type=LearningPattern.QUERY_REFINEMENT,
                description=f"Most common query pattern: {most_common_pattern}",
                confidence=0.75,
                impact_score=0.6,
                evidence=[{"pattern_counts": dict(query_patterns)}]
            )
            insights.append(insight)
        
        return insights

    async def _analyze_content_relevance(self) -> List[LearningInsight]:
        """Analyze content relevance patterns"""
        insights = []
        
        # Analyze feedback patterns
        positive_feedback = 0
        negative_feedback = 0
        
        for interaction in self.interaction_buffer:
            feedback_type = interaction["feedback"]["feedback_type"]
            if feedback_type in ["click", "rating", "bookmark", "share"]:
                positive_feedback += 1
            elif feedback_type in ["dismiss", "negative_feedback"]:
                negative_feedback += 1
        
        if positive_feedback + negative_feedback > 0:
            satisfaction_rate = positive_feedback / (positive_feedback + negative_feedback)
            insight = LearningInsight(
                pattern_type=LearningPattern.CONTENT_RELEVANCE,
                description=f"Content satisfaction rate: {satisfaction_rate:.2%}",
                confidence=0.8,
                impact_score=0.9,
                evidence=[{"positive": positive_feedback, "negative": negative_feedback}]
            )
            insights.append(insight)
        
        return insights

    async def _analyze_temporal_patterns(self) -> List[LearningInsight]:
        """Analyze temporal usage patterns"""
        insights = []
        
        # Analyze usage by time of day
        hour_usage = defaultdict(int)
        for interaction in self.interaction_buffer:
            timestamp = datetime.fromisoformat(interaction["feedback"]["timestamp"])
            hour_usage[timestamp.hour] += 1
        
        if hour_usage:
            peak_hour = max(hour_usage, key=hour_usage.get)
            insight = LearningInsight(
                pattern_type=LearningPattern.TEMPORAL_PATTERN,
                description=f"Peak usage hour: {peak_hour}:00",
                confidence=0.7,
                impact_score=0.5,
                evidence=[{"hour_usage": dict(hour_usage)}]
            )
            insights.append(insight)
        
        return insights

    async def _update_collection_routing_optimization(self):
        """Update collection routing based on learned patterns"""
        # This would optimize collection routing based on learned patterns
        pass

    async def _cleanup_old_data(self):
        """Clean up old data to prevent memory bloat"""
        # Clean up old interactions
        cutoff_time = datetime.now() - timedelta(days=30)
        
        # Clean up old learning insights
        self.learning_insights = [
            insight for insight in self.learning_insights 
            if insight.created_at > cutoff_time
        ]
        
        # Clean up old user profile interactions
        for profile in self.user_profiles.values():
            profile.interaction_history = [
                interaction for interaction in profile.interaction_history
                if datetime.fromisoformat(interaction["timestamp"]) > cutoff_time
            ] 