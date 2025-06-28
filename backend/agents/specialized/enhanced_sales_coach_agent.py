#!/usr/bin/env python3
"""
Enhanced Sales Coach Agent - First Layer Implementation
Integrates Microsoft emails via Gong.io with advanced coaching capabilities
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from backend.agents.core.base_agent import BaseAgent
from backend.integrations.enhanced_microsoft_gong_integration import (
    EnhancedMicrosoftGongIntegration,
    RealTimeCoachingInsight,
    CoachingPriority
)
from backend.mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer

logger = logging.getLogger(__name__)


@dataclass
class CoachingSession:
    """Coaching session data"""
    sales_rep: str
    session_id: str
    timestamp: datetime
    insights: List[RealTimeCoachingInsight]
    action_items: List[Dict[str, Any]]
    performance_score: float
    improvement_plan: Dict[str, Any]


class EnhancedSalesCoachAgent(BaseAgent):
    """
    Enhanced Sales Coach Agent with Microsoft email intelligence via Gong
    Implements first layer of advanced coaching capabilities
    """
    
    def __init__(self):
        super().__init__()
        self.microsoft_gong_integration = EnhancedMicrosoftGongIntegration()
        self.ai_memory = EnhancedAiMemoryMCPServer()
        self.coaching_sessions = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize all components"""
        if not self.initialized:
            await self.microsoft_gong_integration.initialize()
            await self.ai_memory.initialize()
            self.initialized = True
            logger.info("✅ Enhanced Sales Coach Agent initialized")
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coaching task"""
        if not self.initialized:
            await self.initialize()
        
        task_type = task.get("type", "analyze_performance")
        
        if task_type == "analyze_performance":
            return await self._analyze_sales_rep_performance(task)
        elif task_type == "generate_coaching_report":
            return await self._generate_coaching_report(task)
        elif task_type == "real_time_coaching":
            return await self._provide_real_time_coaching(task)
        elif task_type == "track_improvement":
            return await self._track_improvement_progress(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _analyze_sales_rep_performance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sales rep performance with Microsoft email intelligence
        """
        sales_rep = task.get("sales_rep")
        days = task.get("days", 7)
        
        if not sales_rep:
            return {"error": "sales_rep is required"}
        
        try:
            # Get comprehensive analysis from Microsoft+Gong integration
            analysis = await self.microsoft_gong_integration.analyze_sales_rep_performance(
                sales_rep=sales_rep,
                days=days
            )
            
            if "error" in analysis:
                return analysis
            
            # Create coaching session
            session = CoachingSession(
                sales_rep=sales_rep,
                session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                insights=analysis.get("coaching_insights", []),
                action_items=analysis.get("improvement_recommendations", {}).get("action_items", []),
                performance_score=analysis.get("overall_score", 0.0),
                improvement_plan=analysis.get("improvement_recommendations", {})
            )
            
            # Store session
            self.coaching_sessions[session.session_id] = session
            
            # Store insights in AI Memory
            await self._store_coaching_insights(session, analysis)
            
            # Generate friendly but stern coaching message
            coaching_message = await self._generate_coaching_message(session, analysis)
            
            return {
                "success": True,
                "session_id": session.session_id,
                "sales_rep": sales_rep,
                "analysis_period_days": days,
                "performance_score": session.performance_score,
                "coaching_message": coaching_message,
                "insights": [
                    {
                        "type": insight.insight_type,
                        "priority": insight.priority.value,
                        "message": insight.message,
                        "action_required": insight.action_required
                    } for insight in session.insights
                ],
                "action_items": session.action_items,
                "email_intelligence": analysis.get("email_intelligence", {}),
                "call_performance": analysis.get("call_performance", {}),
                "competitive_intelligence": analysis.get("competitive_intelligence", {}),
                "next_review": session.improvement_plan.get("next_review"),
                "timestamp": session.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sales rep performance: {e}")
            return {"error": str(e)}
    
    async def _generate_coaching_message(
        self, 
        session: CoachingSession, 
        analysis: Dict[str, Any]
    ) -> str:
        """Generate friendly but stern coaching message"""
        
        sales_rep = session.sales_rep
        score = session.performance_score
        critical_insights = [i for i in session.insights if i.priority == CoachingPriority.CRITICAL]
        high_insights = [i for i in session.insights if i.priority == CoachingPriority.HIGH]
        
        # Get email and call summaries
        email_summary = analysis.get("email_intelligence", {}).get("summary", {})
        call_summary = analysis.get("call_performance", {}).get("summary", {})
        
        response_rate = email_summary.get("response_rate", 0)
        personalization = email_summary.get("avg_personalization_score", 0)
        avg_sentiment = call_summary.get("avg_sentiment", 0)
        avg_talk_ratio = call_summary.get("avg_talk_ratio", 0)
        
        # Build coaching message
        message_parts = []
        
        # Opening - friendly but direct
        message_parts.append(f"Hey {sales_rep}!")
        message_parts.append(
            "I've been analyzing your performance this week, and I need to have a frank conversation with you. "
            "You clearly have talent - I can see that in your technical knowledge and your ability to connect with prospects. "
            "But there are some patterns emerging that we need to address **immediately** before they impact your numbers."
        )
        
        # Critical issues
        if critical_insights:
            message_parts.append("\n## 🚨 **CRITICAL FINDINGS - Immediate Action Required**")
            for insight in critical_insights:
                if insight.insight_type == "call_sentiment":
                    message_parts.append(
                        f"### **Call Sentiment Declining** ⚠️\n"
                        f"**Current Score:** {avg_sentiment:.2f}\n\n"
                        f"{sales_rep}, you're letting prospect pushback get under your skin. I can hear it in your voice. "
                        f"When prospects push back, that's not rejection - that's engagement. They're telling you what they need to hear."
                    )
        
        # High priority issues
        if high_insights:
            message_parts.append("\n## 📧 **EMAIL PERFORMANCE ISSUES**")
            for insight in high_insights:
                if insight.insight_type == "email_response_rate":
                    message_parts.append(
                        f"**Response Rate:** {response_rate:.1f}% (down from target 40%)\n"
                        f"**Personalization Score:** {personalization:.2f} (target 0.7+)\n\n"
                        f"{sales_rep}, your emails are reading like templates. Prospects can tell when you haven't done your homework. "
                        f"Every email should feel like it was written specifically for them, because it should be."
                    )
                elif insight.insight_type == "talk_ratio":
                    message_parts.append(
                        f"**Talk Ratio:** {avg_talk_ratio:.1%} (target 60% or less)\n\n"
                        f"This is discovery 101, {sales_rep}. You can't sell if you don't know their pain. "
                        f"Every minute you're talking is a minute you're not learning about their business."
                    )
        
        # Positive reinforcement
        message_parts.append(f"\n## 🔥 **THE TRUTH, {sales_rep.upper()}**")
        message_parts.append(
            f"You have **massive potential**. When you're in the zone, you're unstoppable. "
            f"But right now, you're working harder, not smarter."
        )
        
        # What's happening
        issues = []
        if avg_sentiment < 0.5:
            issues.append("You're letting frustration show in your voice")
        if response_rate < 35:
            issues.append("Your emails sound like everyone else's")
        if avg_talk_ratio > 0.7:
            issues.append("You're talking too much because you're nervous about silence")
        
        if issues:
            message_parts.append("**Here's what's happening:**")
            for i, issue in enumerate(issues, 1):
                message_parts.append(f"{i}. {issue}")
        
        # Commitment request
        message_parts.append(f"\n## 🎯 **YOUR COMMITMENT**")
        message_parts.append(
            f"{sales_rep}, I need you to commit to these changes **this week**. "
            f"Not next month, not when you feel like it. This week."
        )
        
        # Action items
        if session.action_items:
            message_parts.append("**Your homework:**")
            for i, action in enumerate(session.action_items, 1):
                timeline = action.get("timeline", "This week")
                action_text = action.get("action", "")
                message_parts.append(f"{i}. **{timeline}:** {action_text}")
        
        # Closing
        message_parts.append(
            f"\n**Remember:** Every top performer went through this. The difference is they listened to coaching and made the adjustments."
        )
        message_parts.append(f"You've got this, {sales_rep}, but only if you're willing to change. Are you in?")
        
        return "\n\n".join(message_parts)
    
    async def _store_coaching_insights(self, session: CoachingSession, analysis: Dict[str, Any]):
        """Store coaching insights in AI Memory"""
        
        try:
            # Store comprehensive coaching session
            await self.ai_memory.store_coaching_insight(
                sales_rep=session.sales_rep,
                insight_type="comprehensive_performance_analysis",
                content=f"Performance analysis for {session.sales_rep}: "
                       f"Score {session.performance_score:.2f}, "
                       f"{len(session.insights)} insights identified, "
                       f"{len(session.action_items)} action items assigned",
                tags=[
                    "performance_analysis",
                    "email_intelligence", 
                    "call_analysis",
                    f"score_{int(session.performance_score * 100)}"
                ] + [insight.insight_type for insight in session.insights],
                confidence_score=0.95,
                use_cortex_analysis=True
            )
            
            # Store specific insights
            for insight in session.insights:
                await self.ai_memory.store_coaching_insight(
                    sales_rep=session.sales_rep,
                    insight_type=insight.insight_type,
                    content=insight.message,
                    tags=[
                        insight.priority.value,
                        insight.insight_type,
                        "action_required" if insight.action_required else "observation"
                    ],
                    confidence_score=0.9
                )
            
            logger.info(f"Stored coaching insights for {session.sales_rep} in AI Memory")
            
        except Exception as e:
            logger.error(f"Error storing coaching insights: {e}")
    
    async def _provide_real_time_coaching(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Provide real-time coaching during calls"""
        
        call_id = task.get("call_id")
        sales_rep = task.get("sales_rep")
        current_metrics = task.get("current_metrics", {})
        
        if not call_id or not sales_rep:
            return {"error": "call_id and sales_rep are required"}
        
        try:
            real_time_insights = []
            
            # Check talk ratio
            current_talk_ratio = current_metrics.get("talk_ratio", 0)
            if current_talk_ratio > 0.75:
                real_time_insights.append({
                    "type": "talk_ratio_alert",
                    "priority": "high",
                    "message": "You've been talking for too long - ask a question",
                    "action": "Ask: 'What's your biggest challenge with your current solution?'"
                })
            
            # Check sentiment
            current_sentiment = current_metrics.get("sentiment", 0)
            if current_sentiment < 0.4:
                real_time_insights.append({
                    "type": "sentiment_drop",
                    "priority": "critical",
                    "message": "Prospect tone shifted negative - acknowledge their concern",
                    "action": "Say: 'I can hear some concern in your voice. What specifically worries you about this?'"
                })
            
            # Check for buying signals
            transcript_snippet = current_metrics.get("recent_transcript", "").lower()
            buying_signals = ["budget", "timeline", "decision", "approval", "next steps"]
            
            for signal in buying_signals:
                if signal in transcript_snippet:
                    real_time_insights.append({
                        "type": "buying_signal",
                        "priority": "high",
                        "message": f"They mentioned '{signal}' - this is a buying signal!",
                        "action": f"Dig deeper: 'Tell me more about your {signal} process...'"
                    })
                    break
            
            return {
                "success": True,
                "call_id": call_id,
                "sales_rep": sales_rep,
                "real_time_insights": real_time_insights,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error providing real-time coaching: {e}")
            return {"error": str(e)}
    
    async def _track_improvement_progress(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Track improvement progress over time"""
        
        sales_rep = task.get("sales_rep")
        days_back = task.get("days_back", 30)
        
        if not sales_rep:
            return {"error": "sales_rep is required"}
        
        try:
            # Get historical coaching insights from AI Memory
            historical_insights = await self.ai_memory.recall_coaching_insights(
                query=f"performance_analysis {sales_rep}",
                limit=10
            )
            
            # Analyze improvement trends
            improvement_trends = self._analyze_improvement_trends(historical_insights)
            
            # Get current performance
            current_analysis = await self.microsoft_gong_integration.analyze_sales_rep_performance(
                sales_rep=sales_rep,
                days=7
            )
            
            current_score = current_analysis.get("overall_score", 0)
            
            return {
                "success": True,
                "sales_rep": sales_rep,
                "current_score": current_score,
                "improvement_trends": improvement_trends,
                "coaching_effectiveness": self._calculate_coaching_effectiveness(improvement_trends),
                "recommendations": self._generate_improvement_recommendations(improvement_trends),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error tracking improvement progress: {e}")
            return {"error": str(e)}
    
    def _analyze_improvement_trends(self, historical_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze improvement trends from historical data"""
        
        if not historical_insights:
            return {"trend": "insufficient_data", "insights": []}
        
        # Extract performance scores over time
        scores = []
        dates = []
        
        for insight in historical_insights:
            if "score_" in str(insight.get("tags", [])):
                # Extract score from tags
                for tag in insight.get("tags", []):
                    if tag.startswith("score_"):
                        try:
                            score = int(tag.split("_")[1]) / 100.0
                            scores.append(score)
                            dates.append(insight.get("timestamp", ""))
                            break
                        except:
                            pass
        
        if len(scores) < 2:
            return {"trend": "insufficient_data", "scores": scores}
        
        # Calculate trend
        recent_scores = scores[:3]  # Last 3 scores
        earlier_scores = scores[3:6] if len(scores) > 3 else scores
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        earlier_avg = sum(earlier_scores) / len(earlier_scores)
        
        if recent_avg > earlier_avg + 0.1:
            trend = "improving"
        elif recent_avg < earlier_avg - 0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "recent_average": recent_avg,
            "earlier_average": earlier_avg,
            "improvement_rate": recent_avg - earlier_avg,
            "total_sessions": len(scores),
            "scores": scores
        }
    
    def _calculate_coaching_effectiveness(self, improvement_trends: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate coaching effectiveness metrics"""
        
        trend = improvement_trends.get("trend", "insufficient_data")
        improvement_rate = improvement_trends.get("improvement_rate", 0)
        
        if trend == "improving":
            effectiveness = min(0.9, 0.5 + improvement_rate * 2)
        elif trend == "declining":
            effectiveness = max(0.1, 0.5 + improvement_rate * 2)
        else:
            effectiveness = 0.5
        
        return {
            "effectiveness_score": effectiveness,
            "trend": trend,
            "coaching_impact": "positive" if improvement_rate > 0 else "negative" if improvement_rate < 0 else "neutral",
            "recommendation": self._get_effectiveness_recommendation(effectiveness, trend)
        }
    
    def _get_effectiveness_recommendation(self, effectiveness: float, trend: str) -> str:
        """Get recommendation based on coaching effectiveness"""
        
        if effectiveness > 0.7:
            return "Coaching is highly effective - continue current approach"
        elif effectiveness > 0.5:
            return "Coaching is moderately effective - consider adjusting approach"
        else:
            return "Coaching effectiveness is low - major approach change needed"
    
    def _generate_improvement_recommendations(self, improvement_trends: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on improvement trends"""
        
        trend = improvement_trends.get("trend", "insufficient_data")
        recommendations = []
        
        if trend == "improving":
            recommendations.extend([
                "Continue current coaching approach - it's working",
                "Gradually increase performance targets",
                "Share success patterns with other team members"
            ])
        elif trend == "declining":
            recommendations.extend([
                "Increase coaching frequency and intensity",
                "Review and adjust coaching methods",
                "Consider additional training or support"
            ])
        else:
            recommendations.extend([
                "Maintain consistent coaching schedule",
                "Try new coaching techniques to drive improvement",
                "Set clearer, more specific goals"
            ])
        
        return recommendations


# Global instance
enhanced_sales_coach_agent = EnhancedSalesCoachAgent()
