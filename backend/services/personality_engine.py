"""
Personality Engine - Phase 2
Refined personality modes with sass 0.9 tied to user profiles
Contextual business intelligence responses with adaptive tone
"""

import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2
from backend.services.portkey_gateway import PortkeyGateway
from backend.core.auto_esc_config import get_config_value
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PersonalityMode(Enum):
    NEUTRAL = "neutral"           # sass: 0.2, professional tone
    PROFESSIONAL = "professional" # sass: 0.4, business-focused
    CONFIDENT = "confident"       # sass: 0.6, assertive insights
    SNARKY = "snarky"            # sass: 0.8, witty and sharp
    CEO_SAVAGE = "ceo_savage"     # sass: 0.9, no-nonsense executive


class ResponseContext(Enum):
    FINANCIAL_ANALYSIS = "financial_analysis"
    SALES_PERFORMANCE = "sales_performance"
    MARKET_TRENDS = "market_trends"
    TEAM_PRODUCTIVITY = "team_productivity"
    CUSTOMER_INSIGHTS = "customer_insights"
    STRATEGIC_PLANNING = "strategic_planning"
    OPERATIONAL_METRICS = "operational_metrics"


@dataclass
class UserPersonalityProfile:
    """User's personality preferences and context"""
    user_id: str
    preferred_mode: PersonalityMode
    sass_tolerance: float  # 0.0 to 1.0
    communication_style: str
    role: str  # CEO, Manager, Analyst, etc.
    domain_expertise: List[str]
    interaction_history: List[Dict[str, Any]]
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "preferred_mode": self.preferred_mode.value,
            "sass_tolerance": self.sass_tolerance,
            "communication_style": self.communication_style,
            "role": self.role,
            "domain_expertise": self.domain_expertise,
            "interaction_count": len(self.interaction_history),
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class PersonalityResponse:
    """Response with personality context"""
    content: str
    personality_mode: PersonalityMode
    sass_level: float
    context: ResponseContext
    confidence: float
    tone_adjustments: List[str]
    generated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "personality_mode": self.personality_mode.value,
            "sass_level": self.sass_level,
            "context": self.context.value,
            "confidence": self.confidence,
            "tone_adjustments": self.tone_adjustments,
            "generated_at": self.generated_at.isoformat()
        }


class PersonalityEngine:
    """
    Refined personality engine for contextual business intelligence
    Adapts tone and sass level based on user profiles and query context
    """
    
    def __init__(self):
        self.memory_service = UnifiedMemoryServiceV2()
        self.portkey = PortkeyGateway()
        
        # User profiles cache
        self.user_profiles: Dict[str, UserPersonalityProfile] = {}
        
        # Personality templates
        self.personality_templates = self._load_personality_templates()
        
        # Context detection patterns
        self.context_patterns = self._load_context_patterns()
        
        # Performance tracking
        self.stats = {
            "responses_generated": 0,
            "avg_sass_level": 0.0,
            "personality_adjustments": 0,
            "user_profiles_created": 0
        }
    
    def _load_personality_templates(self) -> Dict[PersonalityMode, Dict[str, str]]:
        """Load personality templates for different modes"""
        return {
            PersonalityMode.NEUTRAL: {
                "prefix": "Based on the data analysis,",
                "tone": "professional and straightforward",
                "style": "Clear, factual presentation with minimal interpretation",
                "sass_multiplier": 0.2
            },
            PersonalityMode.PROFESSIONAL: {
                "prefix": "The analysis indicates",
                "tone": "business-focused with mild confidence",
                "style": "Professional insights with strategic implications",
                "sass_multiplier": 0.4
            },
            PersonalityMode.CONFIDENT: {
                "prefix": "The data clearly shows",
                "tone": "assertive and decisive",
                "style": "Strong opinions backed by data, actionable recommendations",
                "sass_multiplier": 0.6
            },
            PersonalityMode.SNARKY: {
                "prefix": "Well, well, well... the numbers don't lie:",
                "tone": "witty with strategic edge",
                "style": "Sharp observations with humor, calls out obvious issues",
                "sass_multiplier": 0.8
            },
            PersonalityMode.CEO_SAVAGE: {
                "prefix": "Let me break this down for you:",
                "tone": "brutally honest executive",
                "style": "No-nonsense, direct impact assessment, cuts through BS",
                "sass_multiplier": 0.9
            }
        }
    
    def _load_context_patterns(self) -> Dict[ResponseContext, Dict[str, Any]]:
        """Load context detection patterns"""
        return {
            ResponseContext.FINANCIAL_ANALYSIS: {
                "keywords": ["revenue", "profit", "cost", "margin", "ROI", "budget", "financial", "earnings"],
                "sass_boost": 0.1,  # Financial data deserves sharp analysis
                "tone_adjustments": ["data-driven", "bottom-line focused"]
            },
            ResponseContext.SALES_PERFORMANCE: {
                "keywords": ["sales", "pipeline", "conversion", "leads", "deals", "quota", "targets"],
                "sass_boost": 0.15,  # Sales performance needs honest feedback
                "tone_adjustments": ["results-oriented", "performance-focused"]
            },
            ResponseContext.MARKET_TRENDS: {
                "keywords": ["market", "trends", "competition", "industry", "growth", "share"],
                "sass_boost": 0.05,  # Market analysis benefits from measured confidence
                "tone_adjustments": ["strategic", "forward-looking"]
            },
            ResponseContext.TEAM_PRODUCTIVITY: {
                "keywords": ["team", "productivity", "efficiency", "performance", "collaboration"],
                "sass_boost": 0.2,   # Team issues often need direct feedback
                "tone_adjustments": ["actionable", "improvement-focused"]
            },
            ResponseContext.CUSTOMER_INSIGHTS: {
                "keywords": ["customer", "satisfaction", "retention", "churn", "NPS", "feedback"],
                "sass_boost": 0.1,   # Customer data needs balanced perspective
                "tone_adjustments": ["customer-centric", "empathetic"]
            },
            ResponseContext.STRATEGIC_PLANNING: {
                "keywords": ["strategy", "planning", "goals", "objectives", "roadmap", "vision"],
                "sass_boost": 0.05,  # Strategic content benefits from measured confidence
                "tone_adjustments": ["visionary", "long-term focused"]
            },
            ResponseContext.OPERATIONAL_METRICS: {
                "keywords": ["operations", "metrics", "KPI", "efficiency", "process", "workflow"],
                "sass_boost": 0.1,   # Operational data needs practical insights
                "tone_adjustments": ["practical", "optimization-focused"]
            }
        }
    
    async def get_user_profile(self, user_id: str) -> UserPersonalityProfile:
        """Get or create user personality profile"""
        
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # Try to load from memory service
        try:
            profile_results = await self.memory_service.search_knowledge_personalized(
                query="user personality communication preferences",
                user_id=user_id,
                limit=5
            )
            
            # Extract profile data from results
            if profile_results:
                # Analyze interaction history to determine preferences
                sass_tolerance = self._analyze_sass_tolerance(profile_results)
                role = self._extract_user_role(profile_results)
                communication_style = self._extract_communication_style(profile_results)
                domain_expertise = self._extract_domain_expertise(profile_results)
            else:
                # Default profile for new users
                sass_tolerance = 0.5
                role = "Analyst"
                communication_style = "professional"
                domain_expertise = ["business"]
            
            # Determine preferred mode based on tolerance and role
            preferred_mode = self._determine_preferred_mode(sass_tolerance, role)
            
            profile = UserPersonalityProfile(
                user_id=user_id,
                preferred_mode=preferred_mode,
                sass_tolerance=sass_tolerance,
                communication_style=communication_style,
                role=role,
                domain_expertise=domain_expertise,
                interaction_history=profile_results[:10],  # Keep recent interactions
                last_updated=datetime.utcnow()
            )
            
            self.user_profiles[user_id] = profile
            self.stats["user_profiles_created"] += 1
            
            logger.info(f"Created personality profile for {user_id}: {preferred_mode.value} (sass: {sass_tolerance:.2f})")
            
        except Exception as e:
            logger.warning(f"Failed to load user profile for {user_id}: {e}, using defaults")
            profile = self._get_default_profile(user_id)
            self.user_profiles[user_id] = profile
        
        return profile
    
    def _analyze_sass_tolerance(self, interactions: List[Dict[str, Any]]) -> float:
        """Analyze user's sass tolerance from interaction history"""
        
        # Look for indicators in interaction content
        sass_indicators = {
            "high_tolerance": ["direct", "honest", "blunt", "straight", "no nonsense", "cut through"],
            "low_tolerance": ["polite", "gentle", "diplomatic", "careful", "considerate"]
        }
        
        high_score = 0
        low_score = 0
        
        for interaction in interactions:
            content = interaction.get("content", "").lower()
            
            for indicator in sass_indicators["high_tolerance"]:
                if indicator in content:
                    high_score += 1
            
            for indicator in sass_indicators["low_tolerance"]:
                if indicator in content:
                    low_score += 1
        
        # Calculate tolerance (0.3 to 0.9 range)
        if high_score > low_score:
            return min(0.9, 0.6 + (high_score - low_score) * 0.1)
        elif low_score > high_score:
            return max(0.3, 0.6 - (low_score - high_score) * 0.1)
        else:
            return 0.6  # Default moderate tolerance
    
    def _extract_user_role(self, interactions: List[Dict[str, Any]]) -> str:
        """Extract user role from interaction patterns"""
        
        role_indicators = {
            "CEO": ["strategy", "vision", "leadership", "board", "shareholders"],
            "Manager": ["team", "reports", "management", "oversight", "coordination"],
            "Analyst": ["data", "analysis", "metrics", "reports", "insights"],
            "Sales": ["deals", "pipeline", "customers", "revenue", "targets"],
            "Marketing": ["campaigns", "leads", "brand", "content", "engagement"]
        }
        
        role_scores = {role: 0 for role in role_indicators.keys()}
        
        for interaction in interactions:
            content = interaction.get("content", "").lower()
            
            for role, indicators in role_indicators.items():
                for indicator in indicators:
                    if indicator in content:
                        role_scores[role] += 1
        
        # Return role with highest score, default to Analyst
                 best_role = max(role_scores.items(), key=lambda x: x[1])[0]
         return best_role if role_scores[best_role] > 0 else "Analyst"
    
    def _extract_communication_style(self, interactions: List[Dict[str, Any]]) -> str:
        """Extract communication style preferences"""
        
        style_indicators = {
            "executive": ["bottom line", "impact", "results", "ROI", "efficiency"],
            "analytical": ["data", "metrics", "analysis", "details", "breakdown"],
            "collaborative": ["team", "together", "input", "feedback", "discussion"],
            "direct": ["straight", "honest", "clear", "simple", "direct"]
        }
        
        style_scores = {style: 0 for style in style_indicators.keys()}
        
        for interaction in interactions:
            content = interaction.get("content", "").lower()
            
            for style, indicators in style_indicators.items():
                for indicator in indicators:
                    if indicator in content:
                        style_scores[style] += 1
        
        best_style = max(style_scores, key=style_scores.get)
        return best_style if style_scores[best_style] > 0 else "professional"
    
    def _extract_domain_expertise(self, interactions: List[Dict[str, Any]]) -> List[str]:
        """Extract domain expertise from interactions"""
        
        domains = {
            "finance": ["financial", "budget", "revenue", "profit", "cost"],
            "sales": ["sales", "deals", "pipeline", "customers", "leads"],
            "marketing": ["marketing", "campaigns", "brand", "content"],
            "operations": ["operations", "process", "workflow", "efficiency"],
            "analytics": ["analytics", "data", "metrics", "insights", "reports"],
            "strategy": ["strategy", "planning", "vision", "goals", "roadmap"]
        }
        
        domain_scores = {domain: 0 for domain in domains.keys()}
        
        for interaction in interactions:
            content = interaction.get("content", "").lower()
            
            for domain, keywords in domains.items():
                for keyword in keywords:
                    if keyword in content:
                        domain_scores[domain] += 1
        
        # Return domains with score > 0, sorted by score
        expertise = [domain for domain, score in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True) if score > 0]
        return expertise[:3] if expertise else ["business"]  # Top 3 or default
    
    def _determine_preferred_mode(self, sass_tolerance: float, role: str) -> PersonalityMode:
        """Determine preferred personality mode based on tolerance and role"""
        
        # Role-based adjustments
        role_adjustments = {
            "CEO": 0.2,      # CEOs typically prefer more direct communication
            "Manager": 0.1,   # Managers prefer confident but measured tone
            "Analyst": 0.0,   # Analysts prefer balanced approach
            "Sales": 0.15,    # Sales prefers confident, results-oriented
            "Marketing": 0.05 # Marketing prefers creative but professional
        }
        
        adjusted_tolerance = sass_tolerance + role_adjustments.get(role, 0.0)
        
        if adjusted_tolerance >= 0.85:
            return PersonalityMode.CEO_SAVAGE
        elif adjusted_tolerance >= 0.7:
            return PersonalityMode.SNARKY
        elif adjusted_tolerance >= 0.55:
            return PersonalityMode.CONFIDENT
        elif adjusted_tolerance >= 0.4:
            return PersonalityMode.PROFESSIONAL
        else:
            return PersonalityMode.NEUTRAL
    
    def _get_default_profile(self, user_id: str) -> UserPersonalityProfile:
        """Get default personality profile for new users"""
        return UserPersonalityProfile(
            user_id=user_id,
            preferred_mode=PersonalityMode.PROFESSIONAL,
            sass_tolerance=0.6,
            communication_style="professional",
            role="Analyst",
            domain_expertise=["business"],
            interaction_history=[],
            last_updated=datetime.utcnow()
        )
    
    def detect_response_context(self, query: str) -> ResponseContext:
        """Detect the context of the query for appropriate tone adjustment"""
        
        query_lower = query.lower()
        
        # Score each context based on keyword matches
        context_scores = {}
        for context, config in self.context_patterns.items():
            score = sum(1 for keyword in config["keywords"] if keyword in query_lower)
            if score > 0:
                context_scores[context] = score
        
        # Return context with highest score, default to operational metrics
        if context_scores:
            return max(context_scores, key=context_scores.get)
        else:
            return ResponseContext.OPERATIONAL_METRICS
    
    async def generate_personalized_response(self, 
                                           query: str, 
                                           data_context: Dict[str, Any],
                                           user_id: str = "default_user") -> PersonalityResponse:
        """Generate personalized response with appropriate personality"""
        
        start_time = time.time()
        
        # Get user profile
        user_profile = await self.get_user_profile(user_id)
        
        # Detect response context
        response_context = self.detect_response_context(query)
        
        # Calculate dynamic sass level
        base_sass = user_profile.sass_tolerance
        context_boost = self.context_patterns[response_context]["sass_boost"]
        dynamic_sass = min(0.9, base_sass + context_boost)
        
        # Adjust personality mode if needed
        if dynamic_sass > 0.85 and user_profile.preferred_mode != PersonalityMode.CEO_SAVAGE:
            active_mode = PersonalityMode.CEO_SAVAGE
            self.stats["personality_adjustments"] += 1
        elif dynamic_sass > 0.7 and user_profile.preferred_mode in [PersonalityMode.NEUTRAL, PersonalityMode.PROFESSIONAL]:
            active_mode = PersonalityMode.SNARKY
            self.stats["personality_adjustments"] += 1
        else:
            active_mode = user_profile.preferred_mode
        
        # Get personality template
        template = self.personality_templates[active_mode]
        context_config = self.context_patterns[response_context]
        
        # Build personality prompt
        personality_prompt = self._build_personality_prompt(
            query, data_context, template, context_config, dynamic_sass, user_profile
        )
        
        # Generate response
        response = await self.portkey.completions.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": personality_prompt}],
            temperature=0.6 if dynamic_sass > 0.7 else 0.4,
            max_tokens=300
        )
        
        content = response.choices[0].message.content
        
        # Calculate confidence based on data quality and context match
        confidence = self._calculate_response_confidence(data_context, response_context)
        
        # Track stats
        self.stats["responses_generated"] += 1
        self.stats["avg_sass_level"] = (
            (self.stats["avg_sass_level"] * (self.stats["responses_generated"] - 1) + dynamic_sass) /
            self.stats["responses_generated"]
        )
        
        execution_time = (time.time() - start_time) * 1000
        logger.info(f"Generated {active_mode.value} response for {user_id} "
                   f"(sass: {dynamic_sass:.2f}, context: {response_context.value}, {execution_time:.1f}ms)")
        
        return PersonalityResponse(
            content=content,
            personality_mode=active_mode,
            sass_level=dynamic_sass,
            context=response_context,
            confidence=confidence,
            tone_adjustments=context_config["tone_adjustments"],
            generated_at=datetime.utcnow()
        )
    
    def _build_personality_prompt(self, 
                                query: str,
                                data_context: Dict[str, Any],
                                template: Dict[str, str],
                                context_config: Dict[str, Any],
                                sass_level: float,
                                user_profile: UserPersonalityProfile) -> str:
        """Build personality-aware prompt"""
        
        return f"""You are a business intelligence assistant with a specific personality.

PERSONALITY CONFIGURATION:
- Mode: {template['tone']}
- Style: {template['style']}
- Sass Level: {sass_level:.1f}/1.0
- Context: {context_config['tone_adjustments']}
- User Role: {user_profile.role}
- User Expertise: {', '.join(user_profile.domain_expertise)}

RESPONSE GUIDELINES:
1. Start with: "{template['prefix']}"
2. Use {template['tone']} throughout
3. Apply sass level {sass_level:.1f} - be {'brutally honest' if sass_level > 0.8 else 'confident but measured' if sass_level > 0.6 else 'professional with edge' if sass_level > 0.4 else 'straightforward'}
4. Focus on {', '.join(context_config['tone_adjustments'])} insights
5. Tailor complexity for {user_profile.role} role
6. Keep response under 200 words
7. Include specific numbers and actionable insights

QUERY: {query}

DATA CONTEXT: {json.dumps(data_context, indent=2)}

Generate a response that matches the personality configuration while providing valuable business insights."""
    
    def _calculate_response_confidence(self, data_context: Dict[str, Any], response_context: ResponseContext) -> float:
        """Calculate confidence score for the response"""
        
        base_confidence = 0.7
        
        # Boost confidence if we have rich data
        if isinstance(data_context, dict) and len(data_context) > 3:
            base_confidence += 0.1
        
        # Boost confidence for contexts we handle well
        context_confidence_boost = {
            ResponseContext.FINANCIAL_ANALYSIS: 0.15,
            ResponseContext.SALES_PERFORMANCE: 0.1,
            ResponseContext.OPERATIONAL_METRICS: 0.1,
            ResponseContext.CUSTOMER_INSIGHTS: 0.05,
            ResponseContext.MARKET_TRENDS: 0.05,
            ResponseContext.TEAM_PRODUCTIVITY: 0.05,
            ResponseContext.STRATEGIC_PLANNING: 0.0
        }
        
        confidence = base_confidence + context_confidence_boost.get(response_context, 0.0)
        return min(0.95, max(0.5, confidence))
    
    async def update_user_profile(self, user_id: str, interaction_feedback: Dict[str, Any]) -> None:
        """Update user profile based on interaction feedback"""
        
        if user_id not in self.user_profiles:
            return
        
        profile = self.user_profiles[user_id]
        
        # Adjust sass tolerance based on feedback
        if interaction_feedback.get("too_sassy", False):
            profile.sass_tolerance = max(0.2, profile.sass_tolerance - 0.1)
        elif interaction_feedback.get("too_mild", False):
            profile.sass_tolerance = min(0.9, profile.sass_tolerance + 0.1)
        
        # Update preferred mode if needed
        profile.preferred_mode = self._determine_preferred_mode(profile.sass_tolerance, profile.role)
        profile.last_updated = datetime.utcnow()
        
        # Store updated profile in memory service
        try:
            await self.memory_service.add_knowledge(
                content=f"User {user_id} personality update: {json.dumps(profile.to_dict())}",
                source="personality_engine",
                metadata={
                    "user_id": user_id,
                    "type": "personality_profile",
                    "sass_tolerance": profile.sass_tolerance,
                    "preferred_mode": profile.preferred_mode.value
                }
            )
        except Exception as e:
            logger.warning(f"Failed to store updated profile for {user_id}: {e}")
    
    async def get_personality_stats(self) -> Dict[str, Any]:
        """Get personality engine performance statistics"""
        
        # Calculate mode distribution
        mode_counts = {}
        for profile in self.user_profiles.values():
            mode = profile.preferred_mode.value
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        return {
            "performance_stats": self.stats,
            "user_profiles_count": len(self.user_profiles),
            "personality_mode_distribution": mode_counts,
            "avg_sass_tolerance": sum(p.sass_tolerance for p in self.user_profiles.values()) / max(1, len(self.user_profiles)),
            "role_distribution": {},  # Could add role counting
            "generated_at": datetime.utcnow().isoformat()
        }


# Global instance for service injection
personality_engine = PersonalityEngine()
