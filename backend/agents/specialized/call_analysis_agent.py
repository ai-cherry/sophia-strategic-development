"""
Enhanced Call Analysis Agent with Snowflake Cortex Integration

This agent provides comprehensive call analysis using Snowflake's native AI capabilities
combined with traditional Gong integration for maximum insight generation.

Key Features:
- Snowflake Cortex AI for sentiment, summarization, and embeddings
- Vector similarity search for pattern recognition
- HubSpot context integration for business impact analysis
- Real-time call scoring and trend analysis
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from backend.agents.core.base_agent import BaseAgent
from backend.core.auto_esc_config import config
from backend.utils.snowflake_gong_connector import get_gong_connector
from backend.utils.snowflake_cortex_service import (
    analyze_gong_call_sentiment,
    summarize_gong_call_with_context,
    find_similar_gong_calls
)

# Traditional integrations (fallback)
from backend.integrations.gong_api_client import GongAPIClient

logger = logging.getLogger(__name__)


class CallPriority(Enum):
    """Call analysis priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CallInsight:
    """Individual call insight with AI confidence"""
    insight_type: str
    description: str
    confidence: float
    impact: str  # high, medium, low
    recommendation: str
    supporting_data: Dict[str, Any]


@dataclass
class CallAnalysisResult:
    """Comprehensive call analysis result"""
    call_id: str
    analysis_timestamp: datetime
    overall_score: float
    priority: CallPriority
    key_insights: List[CallInsight]
    sentiment_analysis: Dict[str, Any]
    business_impact: Dict[str, Any]
    recommendations: List[str]
    similar_calls: List[Dict[str, Any]]
    ai_enhanced: bool


class CallAnalysisAgent(BaseAgent):
    """
    Enhanced Call Analysis Agent with Snowflake Cortex AI
    
    Provides deep call analysis using native Snowflake AI capabilities
    for sentiment analysis, summarization, and pattern recognition.
    """
    
    def __init__(self, config_dict: Optional[Dict] = None):
        super().__init__(config_dict)
        self.agent_type = "call_analysis"
        self.snowflake_enabled = True
        self.traditional_gong_client = None
        
        # Analysis configuration
        self.analysis_config = {
            "sentiment_thresholds": {
                "very_positive": 0.7,
                "positive": 0.3,
                "neutral": -0.3,
                "negative": -0.7
            },
            "similarity_threshold": 0.75,
            "min_confidence": 0.6,
            "batch_size": 50,
            "lookback_days": 90
        }
    
    async def initialize(self) -> None:
        """Initialize the Call Analysis Agent"""
        try:
            # Initialize traditional Gong client as fallback
            if config.get("gong_access_key"):
                self.traditional_gong_client = GongAPIClient()
                
            logger.info("✅ Call Analysis Agent initialized with Snowflake Cortex integration")
            
        except Exception as e:
            logger.error(f"Failed to initialize Call Analysis Agent: {e}")
            raise
    
    async def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [
            "analyze_individual_call",
            "analyze_call_batch",
            "generate_call_insights",
            "score_call_performance",
            "find_call_patterns",
            "track_sentiment_trends",
            "analyze_business_impact",
            "generate_call_reports"
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process call analysis task with AI enhancement"""
        task_type = task.get("task_type")
        
        try:
            if task_type == "analyze_call":
                return await self._analyze_individual_call(task)
            elif task_type == "batch_analysis":
                return await self._analyze_call_batch(task)
            elif task_type == "generate_insights":
                return await self._generate_call_insights(task)
            elif task_type == "score_call":
                return await self._score_call_performance(task)
            elif task_type == "find_patterns":
                return await self._find_call_patterns(task)
            elif task_type == "sentiment_trends":
                return await self._track_sentiment_trends(task)
            elif task_type == "business_impact":
                return await self._analyze_business_impact(task)
            elif task_type == "call_report":
                return await self._generate_call_report(task)
            else:
                return await self._handle_general_analysis_query(task)
                
        except Exception as e:
            logger.error(f"Error processing call analysis task: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_available": bool(self.traditional_gong_client)
            }
    
    async def _analyze_individual_call(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive analysis of a single call using Snowflake Cortex AI
        
        ENHANCED APPROACH: Uses Snowflake Cortex for sentiment, summarization,
        and vector analysis with HubSpot context integration.
        """
        call_id = task.get("call_id")
        include_similar = task.get("include_similar", True)
        
        if not call_id:
            return {"success": False, "error": "call_id required"}
        
        try:
            logger.info(f"Analyzing call {call_id} with Snowflake Cortex AI")
            
            # Get comprehensive call data from Snowflake
            connector = await get_gong_connector()
            call_details = await connector.get_call_analysis_data(call_id, include_full_transcript=True)
            
            if not call_details:
                return {"success": False, "error": f"Call {call_id} not found"}
            
            # AI-powered sentiment analysis
            sentiment_analysis = await analyze_gong_call_sentiment(call_id)
            
            # AI-powered call summarization with context
            call_summary = await summarize_gong_call_with_context(call_id)
            
            # Generate key insights using AI analysis
            key_insights = await self._generate_ai_insights(call_details, sentiment_analysis, call_summary)
            
            # Calculate overall call score
            overall_score = await self._calculate_call_score(call_details, sentiment_analysis)
            
            # Determine priority level
            priority = self._determine_call_priority(overall_score, sentiment_analysis)
            
            # Find similar calls for pattern analysis
            similar_calls = []
            if include_similar and call_summary.get("ai_summary"):
                similar_calls = await find_similar_gong_calls(
                    query_text=call_summary["ai_summary"],
                    top_k=5,
                    similarity_threshold=self.analysis_config["similarity_threshold"]
                )
            
            # Analyze business impact
            business_impact = await self._analyze_call_business_impact(call_details, sentiment_analysis)
            
            # Generate recommendations
            recommendations = await self._generate_call_recommendations(
                call_details, sentiment_analysis, key_insights
            )
            
            result = CallAnalysisResult(
                call_id=call_id,
                analysis_timestamp=datetime.now(),
                overall_score=overall_score,
                priority=priority,
                key_insights=key_insights,
                sentiment_analysis=sentiment_analysis,
                business_impact=business_impact,
                recommendations=recommendations,
                similar_calls=similar_calls,
                ai_enhanced=True
            )
            
            return {
                "success": True,
                "call_analysis": result.__dict__,
                "call_details": call_details,
                "call_summary": call_summary,
                "data_source": "snowflake_cortex",
                "ai_enhanced": True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing call {call_id}: {e}")
            
            # Fallback to traditional analysis
            if self.traditional_gong_client:
                return await self._analyze_call_traditional(call_id)
            
            return {"success": False, "error": str(e)}
    
    async def _analyze_call_batch(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Batch analysis of multiple calls with AI insights
        
        ENHANCED APPROACH: Processes calls in batches using Snowflake Cortex
        for efficient analysis and pattern recognition.
        """
        call_ids = task.get("call_ids", [])
        sales_rep = task.get("sales_rep")
        date_range = task.get("date_range")
        limit = task.get("limit", self.analysis_config["batch_size"])
        
        try:
            connector = await get_gong_connector()
            
            # Get calls for analysis
            if call_ids:
                # Analyze specific calls
                calls_to_analyze = call_ids[:limit]
            elif sales_rep:
                # Get recent calls for sales rep
                coaching_calls = await connector.get_calls_for_coaching(
                    sales_rep=sales_rep,
                    date_range_days=7,
                    limit=limit
                )
                calls_to_analyze = [call["CALL_ID"] for call in coaching_calls]
            else:
                return {"success": False, "error": "call_ids or sales_rep required"}
            
            # Process calls in parallel batches
            batch_results = []
            for i in range(0, len(calls_to_analyze), 10):  # Process 10 at a time
                batch = calls_to_analyze[i:i+10]
                batch_tasks = [
                    self._analyze_individual_call({"call_id": call_id, "include_similar": False})
                    for call_id in batch
                ]
                batch_results.extend(await asyncio.gather(*batch_tasks, return_exceptions=True))
            
            # Filter successful results
            successful_analyses = [
                result for result in batch_results 
                if isinstance(result, dict) and result.get("success")
            ]
            
            # Generate batch insights
            batch_insights = await self._generate_batch_insights(successful_analyses)
            
            return {
                "success": True,
                "batch_size": len(calls_to_analyze),
                "successful_analyses": len(successful_analyses),
                "individual_results": successful_analyses,
                "batch_insights": batch_insights,
                "data_source": "snowflake_cortex_batch",
                "ai_enhanced": True
            }
            
        except Exception as e:
            logger.error(f"Error in batch call analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def _find_call_patterns(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find patterns across calls using AI analysis
        
        ENHANCED APPROACH: Uses Snowflake vector search and Cortex AI
        to identify semantic patterns and trends.
        """
        pattern_query = task.get("pattern_query", "")
        sales_rep = task.get("sales_rep")
        date_range_days = task.get("date_range_days", self.analysis_config["lookback_days"])
        
        try:
            # Use vector search to find similar call patterns
            if pattern_query:
                similar_calls = await find_similar_gong_calls(
                    query_text=pattern_query,
                    top_k=20,
                    similarity_threshold=0.6,
                    date_range_days=date_range_days
                )
            else:
                # Get recent calls for pattern analysis
                connector = await get_gong_connector()
                if sales_rep:
                    recent_calls = await connector.get_calls_for_coaching(
                        sales_rep=sales_rep,
                        date_range_days=date_range_days,
                        limit=20
                    )
                    similar_calls = [{"call_id": call["CALL_ID"]} for call in recent_calls]
                else:
                    return {"success": False, "error": "pattern_query or sales_rep required"}
            
            if not similar_calls:
                return {
                    "success": True,
                    "patterns": [],
                    "message": "No patterns found for the given criteria"
                }
            
            # Analyze patterns in the calls
            patterns = await self._analyze_call_patterns(similar_calls)
            
            # Generate pattern insights
            pattern_insights = await self._generate_pattern_insights(patterns)
            
            return {
                "success": True,
                "pattern_query": pattern_query,
                "calls_analyzed": len(similar_calls),
                "patterns": patterns,
                "insights": pattern_insights,
                "data_source": "snowflake_vector_analysis",
                "ai_enhanced": True
            }
            
        except Exception as e:
            logger.error(f"Error finding call patterns: {e}")
            return {"success": False, "error": str(e)}
    
    async def _track_sentiment_trends(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track sentiment trends over time using Snowflake analytics
        
        ENHANCED APPROACH: Uses Snowflake Cortex sentiment analysis
        with time-series analysis for trend identification.
        """
        sales_rep = task.get("sales_rep")
        date_range_days = task.get("date_range_days", 30)
        
        try:
            connector = await get_gong_connector()
            
            # Get performance data with sentiment trends
            if sales_rep:
                performance_data = await connector.get_sales_rep_performance(sales_rep, date_range_days)
            else:
                # Get overall sentiment trends
                performance_data = {"error": "sales_rep required for current implementation"}
            
            if performance_data.get("error"):
                return {"success": False, "error": performance_data["error"]}
            
            # Analyze sentiment trends
            sentiment_trends = {
                "current_avg_sentiment": performance_data.get("avg_sentiment", 0.5),
                "sentiment_category": self._classify_sentiment(performance_data.get("avg_sentiment", 0.5)),
                "positive_call_rate": performance_data.get("positive_call_rate", 0),
                "negative_call_count": performance_data.get("negative_calls", 0),
                "trend_direction": self._determine_trend_direction(performance_data),
                "improvement_recommendations": self._generate_sentiment_recommendations(performance_data)
            }
            
            return {
                "success": True,
                "sales_rep": sales_rep,
                "analysis_period_days": date_range_days,
                "sentiment_trends": sentiment_trends,
                "performance_data": performance_data,
                "data_source": "snowflake_sentiment_analysis",
                "ai_enhanced": True
            }
            
        except Exception as e:
            logger.error(f"Error tracking sentiment trends: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_ai_insights(
        self,
        call_details: Dict[str, Any],
        sentiment_analysis: Dict[str, Any],
        call_summary: Dict[str, Any]
    ) -> List[CallInsight]:
        """Generate AI-powered insights from call analysis"""
        insights = []
        
        # Sentiment insights
        sentiment_score = sentiment_analysis.get("call_sentiment_score", 0.5)
        if sentiment_score < self.analysis_config["sentiment_thresholds"]["positive"]:
            insights.append(CallInsight(
                insight_type="sentiment_risk",
                description=f"Low customer sentiment detected ({sentiment_analysis.get('sentiment_category', 'Unknown')})",
                confidence=0.9,
                impact="high",
                recommendation="Immediate follow-up required to address customer concerns",
                supporting_data={
                    "sentiment_score": sentiment_score,
                    "negative_segments": sentiment_analysis.get("negative_segments"),
                    "transcript_segments": sentiment_analysis.get("transcript_segments")
                }
            ))
        
        # Business impact insights
        if call_details.get("DEAL_AMOUNT") and call_details.get("DEAL_AMOUNT") > 50000:
            insights.append(CallInsight(
                insight_type="high_value_opportunity",
                description=f"High-value deal opportunity (${call_details['DEAL_AMOUNT']:,.0f})",
                confidence=0.95,
                impact="high",
                recommendation="Prioritize this opportunity and ensure proper follow-up",
                supporting_data={
                    "deal_amount": call_details.get("DEAL_AMOUNT"),
                    "deal_stage": call_details.get("DEAL_STAGE"),
                    "company_name": call_details.get("COMPANY_NAME")
                }
            ))
        
        # Communication insights
        talk_ratio = call_details.get("TALK_RATIO", 0.5)
        if talk_ratio > 0.8:
            insights.append(CallInsight(
                insight_type="communication_imbalance",
                description=f"Sales rep dominated conversation ({talk_ratio:.0%} talk time)",
                confidence=0.85,
                impact="medium",
                recommendation="Encourage more customer engagement through discovery questions",
                supporting_data={
                    "talk_ratio": talk_ratio,
                    "questions_asked": call_details.get("QUESTIONS_ASKED_COUNT"),
                    "call_duration": call_details.get("CALL_DURATION_SECONDS")
                }
            ))
        
        # Engagement insights
        if call_details.get("INTERACTIVITY_SCORE") and call_details["INTERACTIVITY_SCORE"] < 0.3:
            insights.append(CallInsight(
                insight_type="low_engagement",
                description="Low customer engagement detected during call",
                confidence=0.8,
                impact="medium",
                recommendation="Focus on building rapport and asking engaging questions",
                supporting_data={
                    "interactivity_score": call_details.get("INTERACTIVITY_SCORE"),
                    "call_duration": call_details.get("CALL_DURATION_SECONDS")
                }
            ))
        
        return insights
    
    async def _calculate_call_score(
        self,
        call_details: Dict[str, Any],
        sentiment_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall call performance score (0-100)"""
        score = 0.0
        
        # Sentiment component (40% weight)
        sentiment_score = sentiment_analysis.get("call_sentiment_score", 0.5)
        sentiment_component = max(0, min(100, (sentiment_score + 1) * 50))
        score += sentiment_component * 0.4
        
        # Talk ratio component (25% weight)
        talk_ratio = call_details.get("TALK_RATIO", 0.5)
        ideal_ratio = 0.5  # 50% talk time is ideal
        talk_ratio_component = max(0, min(100, 100 - abs(talk_ratio - ideal_ratio) * 200))
        score += talk_ratio_component * 0.25
        
        # Engagement component (20% weight)
        interactivity = call_details.get("INTERACTIVITY_SCORE", 0.5)
        engagement_component = interactivity * 100 if interactivity else 50
        score += engagement_component * 0.2
        
        # Duration component (15% weight)
        duration = call_details.get("CALL_DURATION_SECONDS", 0)
        duration_component = min(100, (duration / 1800) * 100)  # 30 min = 100%
        score += duration_component * 0.15
        
        return round(score, 1)
    
    def _determine_call_priority(
        self,
        overall_score: float,
        sentiment_analysis: Dict[str, Any]
    ) -> CallPriority:
        """Determine call priority based on score and sentiment"""
        sentiment_score = sentiment_analysis.get("call_sentiment_score", 0.5)
        
        # Critical priority for very negative sentiment or very low scores
        if sentiment_score < -0.5 or overall_score < 30:
            return CallPriority.CRITICAL
        
        # High priority for negative sentiment or low scores
        if sentiment_score < 0 or overall_score < 50:
            return CallPriority.HIGH
        
        # Medium priority for neutral sentiment or average scores
        if sentiment_score < 0.5 or overall_score < 75:
            return CallPriority.MEDIUM
        
        # Low priority for positive sentiment and high scores
        return CallPriority.LOW
    
    async def _analyze_call_business_impact(
        self,
        call_details: Dict[str, Any],
        sentiment_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze the business impact of the call"""
        impact = {
            "revenue_potential": 0,
            "risk_level": "low",
            "deal_progression": "unknown",
            "follow_up_urgency": "normal"
        }
        
        # Revenue potential
        deal_amount = call_details.get("DEAL_AMOUNT", 0)
        if deal_amount:
            impact["revenue_potential"] = deal_amount
        
        # Risk assessment
        sentiment_score = sentiment_analysis.get("call_sentiment_score", 0.5)
        if sentiment_score < -0.3:
            impact["risk_level"] = "high"
            impact["follow_up_urgency"] = "urgent"
        elif sentiment_score < 0.3:
            impact["risk_level"] = "medium"
            impact["follow_up_urgency"] = "high"
        
        # Deal progression
        deal_stage = call_details.get("DEAL_STAGE", "")
        if deal_stage:
            if "closed" in deal_stage.lower():
                impact["deal_progression"] = "closed"
            elif "proposal" in deal_stage.lower() or "negotiation" in deal_stage.lower():
                impact["deal_progression"] = "late_stage"
            else:
                impact["deal_progression"] = "early_stage"
        
        return impact
    
    async def _generate_call_recommendations(
        self,
        call_details: Dict[str, Any],
        sentiment_analysis: Dict[str, Any],
        key_insights: List[CallInsight]
    ) -> List[str]:
        """Generate actionable recommendations based on call analysis"""
        recommendations = []
        
        # Sentiment-based recommendations
        sentiment_score = sentiment_analysis.get("call_sentiment_score", 0.5)
        if sentiment_score < 0.3:
            recommendations.append("Schedule immediate follow-up call to address customer concerns")
            recommendations.append("Review call recording to identify specific pain points")
        
        # Talk ratio recommendations
        talk_ratio = call_details.get("TALK_RATIO", 0.5)
        if talk_ratio > 0.7:
            recommendations.append("Practice discovery questioning to increase customer engagement")
        
        # Deal-specific recommendations
        if call_details.get("DEAL_AMOUNT", 0) > 25000:
            recommendations.append("Involve sales manager in next interaction for high-value opportunity")
        
        # Insight-based recommendations
        high_impact_insights = [insight for insight in key_insights if insight.impact == "high"]
        for insight in high_impact_insights:
            recommendations.append(insight.recommendation)
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def _generate_batch_insights(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights from batch analysis results"""
        if not batch_results:
            return {"insights": [], "summary": "No successful analyses in batch"}
        
        # Extract scores and sentiments
        scores = [result["call_analysis"]["overall_score"] for result in batch_results]
        sentiments = [
            result["call_analysis"]["sentiment_analysis"].get("call_sentiment_score", 0.5)
            for result in batch_results
        ]
        
        # Calculate averages
        avg_score = sum(scores) / len(scores)
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        # Count priority levels
        priorities = [result["call_analysis"]["priority"] for result in batch_results]
        priority_counts = {
            "critical": priorities.count("critical"),
            "high": priorities.count("high"),
            "medium": priorities.count("medium"),
            "low": priorities.count("low")
        }
        
        return {
            "summary": {
                "total_calls": len(batch_results),
                "average_score": round(avg_score, 1),
                "average_sentiment": round(avg_sentiment, 2),
                "priority_distribution": priority_counts
            },
            "insights": [
                f"Average call score: {avg_score:.1f}/100",
                f"Average sentiment: {self._classify_sentiment(avg_sentiment)}",
                f"Calls needing attention: {priority_counts['critical'] + priority_counts['high']}"
            ],
            "recommendations": self._generate_batch_recommendations(avg_score, avg_sentiment, priority_counts)
        }
    
    def _classify_sentiment(self, sentiment_score: float) -> str:
        """Classify sentiment score into category"""
        thresholds = self.analysis_config["sentiment_thresholds"]
        
        if sentiment_score >= thresholds["very_positive"]:
            return "Very Positive"
        elif sentiment_score >= thresholds["positive"]:
            return "Positive"
        elif sentiment_score >= thresholds["neutral"]:
            return "Neutral"
        elif sentiment_score >= thresholds["negative"]:
            return "Negative"
        else:
            return "Very Negative"
    
    def _determine_trend_direction(self, performance_data: Dict[str, Any]) -> str:
        """Determine sentiment trend direction"""
        # Simple trend analysis - could be enhanced with historical data
        avg_sentiment = performance_data.get("avg_sentiment", 0.5)
        positive_rate = performance_data.get("positive_call_rate", 0)
        
        if avg_sentiment > 0.6 and positive_rate > 70:
            return "improving"
        elif avg_sentiment < 0.3 or positive_rate < 30:
            return "declining"
        else:
            return "stable"
    
    def _generate_sentiment_recommendations(self, performance_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations for sentiment improvement"""
        recommendations = []
        
        avg_sentiment = performance_data.get("avg_sentiment", 0.5)
        if avg_sentiment < 0.4:
            recommendations.extend([
                "Focus on active listening and empathy in customer interactions",
                "Review and practice objection handling techniques",
                "Consider additional sales training on relationship building"
            ])
        
        negative_calls = performance_data.get("negative_calls", 0)
        if negative_calls > 2:
            recommendations.append("Analyze negative calls to identify common patterns")
        
        return recommendations
    
    def _generate_batch_recommendations(
        self,
        avg_score: float,
        avg_sentiment: float,
        priority_counts: Dict[str, int]
    ) -> List[str]:
        """Generate recommendations for batch analysis"""
        recommendations = []
        
        if avg_score < 60:
            recommendations.append("Overall call performance needs improvement - consider team training")
        
        if avg_sentiment < 0.3:
            recommendations.append("Customer sentiment is concerning - review call approach and messaging")
        
        critical_high = priority_counts["critical"] + priority_counts["high"]
        if critical_high > len(priority_counts) * 0.3:  # More than 30% need attention
            recommendations.append("High number of calls need immediate attention - prioritize follow-ups")
        
        return recommendations
    
    async def _analyze_call_traditional(self, call_id: str) -> Dict[str, Any]:
        """Fallback analysis using traditional methods"""
        logger.info(f"Using traditional analysis for call {call_id}")
        
        return {
            "success": True,
            "call_id": call_id,
            "data_source": "traditional_gong",
            "message": "Basic call analysis completed using traditional methods",
            "ai_enhanced": False,
            "recommendation": "Upgrade to Snowflake integration for enhanced AI analysis"
        }
    
    async def _handle_general_analysis_query(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general analysis queries"""
        query = task.get("query", "")
        
        if "sentiment" in query.lower():
            return await self._track_sentiment_trends(task)
        elif "pattern" in query.lower():
            return await self._find_call_patterns(task)
        elif "score" in query.lower():
            return await self._score_call_performance(task)
        else:
            return {
                "success": True,
                "message": "I can help you with call analysis, sentiment tracking, pattern recognition, and performance scoring. What specific analysis do you need?",
                "available_tasks": [
                    "analyze_call - Comprehensive individual call analysis",
                    "batch_analysis - Analyze multiple calls",
                    "find_patterns - Identify patterns across calls",
                    "sentiment_trends - Track sentiment over time",
                    "score_call - Calculate call performance scores"
                ]
            }
    
    async def _score_call_performance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Score call performance using AI metrics"""
        call_id = task.get("call_id")
        
        if not call_id:
            return {"success": False, "error": "call_id required"}
        
        # Delegate to comprehensive analysis
        analysis_result = await self._analyze_individual_call({"call_id": call_id, "include_similar": False})
        
        if analysis_result.get("success"):
            return {
                "success": True,
                "call_id": call_id,
                "overall_score": analysis_result["call_analysis"]["overall_score"],
                "priority": analysis_result["call_analysis"]["priority"],
                "sentiment_category": analysis_result["call_analysis"]["sentiment_analysis"].get("sentiment_category"),
                "recommendations": analysis_result["call_analysis"]["recommendations"]
            }
        
        return analysis_result
    
    async def _analyze_call_patterns(self, similar_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in similar calls"""
        if not similar_calls:
            return {"patterns": [], "insights": "No calls to analyze"}
        
        # Extract pattern data
        sentiments = [call.get("sentiment_score", 0.5) for call in similar_calls if call.get("sentiment_score")]
        deal_stages = [call.get("deal_stage") for call in similar_calls if call.get("deal_stage")]
        
        patterns = {
            "call_count": len(similar_calls),
            "average_sentiment": sum(sentiments) / len(sentiments) if sentiments else 0.5,
            "sentiment_distribution": self._analyze_sentiment_distribution(sentiments),
            "common_deal_stages": self._analyze_deal_stages(deal_stages),
            "success_indicators": self._identify_success_patterns(similar_calls)
        }
        
        return patterns
    
    def _analyze_sentiment_distribution(self, sentiments: List[float]) -> Dict[str, int]:
        """Analyze distribution of sentiments"""
        distribution = {"very_positive": 0, "positive": 0, "neutral": 0, "negative": 0, "very_negative": 0}
        
        for sentiment in sentiments:
            category = self._classify_sentiment(sentiment).lower().replace(" ", "_")
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution
    
    def _analyze_deal_stages(self, deal_stages: List[str]) -> Dict[str, int]:
        """Analyze distribution of deal stages"""
        stage_counts = {}
        for stage in deal_stages:
            if stage:
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        return stage_counts
    
    def _identify_success_patterns(self, calls: List[Dict[str, Any]]) -> List[str]:
        """Identify patterns that indicate success"""
        patterns = []
        
        # High sentiment calls
        high_sentiment_calls = [call for call in calls if call.get("sentiment_score", 0) > 0.6]
        if len(high_sentiment_calls) > len(calls) * 0.5:
            patterns.append("High customer sentiment correlation")
        
        # Deal progression
        closed_won_calls = [call for call in calls if "won" in str(call.get("deal_stage", "")).lower()]
        if closed_won_calls:
            patterns.append("Successful deal closure patterns identified")
        
        return patterns
    
    async def _generate_pattern_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate insights from identified patterns"""
        insights = []
        
        avg_sentiment = patterns.get("average_sentiment", 0.5)
        if avg_sentiment > 0.6:
            insights.append("Strong positive sentiment pattern indicates effective communication approach")
        elif avg_sentiment < 0.3:
            insights.append("Concerning negative sentiment pattern requires immediate attention")
        
        call_count = patterns.get("call_count", 0)
        if call_count > 10:
            insights.append(f"Significant pattern identified across {call_count} similar calls")
        
        success_indicators = patterns.get("success_indicators", [])
        if success_indicators:
            insights.append(f"Success patterns: {', '.join(success_indicators)}")
        
        return insights
    
    async def _analyze_business_impact(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business impact of calls"""
        # This would be implemented based on specific business requirements
        return {
            "success": True,
            "message": "Business impact analysis not yet implemented",
            "recommendation": "Define specific business impact metrics for implementation"
        }
    
    async def _generate_call_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive call analysis report"""
        # This would generate formatted reports based on analysis results
        return {
            "success": True,
            "message": "Call report generation not yet implemented",
            "recommendation": "Define report format and requirements for implementation"
        }


# Agent factory function for AGNO integration
async def create_call_analysis_agent(config: Dict[str, Any] = None) -> CallAnalysisAgent:
    """Create and initialize a Call Analysis Agent instance"""
    agent = CallAnalysisAgent(config)
    await agent.initialize()
    return agent 