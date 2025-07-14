"""
Enhanced Project Intelligence API Routes

Integrates Gong conversation intelligence with existing project management
to provide comprehensive project insights from both formal tools and conversations.

Date: July 9, 2025
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.services.gong_multi_purpose_intelligence import (
    GongMultiPurposeIntelligence,
)
from backend.services.project_management_service import ProjectManagementService
from backend.services.sophia_ai_unified_orchestrator import SophiaAIUnifiedOrchestrator as SophiaUnifiedOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/project-intelligence", tags=["project-intelligence"])


@router.get("/gong-insights")
async def get_gong_project_insights(
    timeframe_days: int = Query(default=7, description="Number of days to analyze"),
    category: str | None = Query(
        default=None, description="Specific category to filter"
    ),
):
    """Get project intelligence insights from Gong conversations"""

    try:
        gong_intelligence = GongMultiPurposeIntelligence()

        if category:
            # Get specific category insights
            all_insights = await gong_intelligence.extract_multi_purpose_insights(
                timeframe_days
            )
            insights = all_insights.get(category, [])
        else:
            # Get project management specific insights
            project_insights = (
                await gong_intelligence.get_project_management_intelligence(
                    timeframe_days
                )
            )
            insights = {
                "project_references": project_insights.project_references,
                "timeline_discussions": project_insights.timeline_discussions,
                "risk_indicators": project_insights.risk_indicators,
                "technical_decisions": project_insights.technical_decisions,
                "blockers_identified": project_insights.blockers_identified,
            }

        return {
            "success": True,
            "timeframe_days": timeframe_days,
            "category": category or "project_management",
            "insights": insights,
            "current_date": "July 9, 2025",
            "total_insights": (
                len(insights)
                if isinstance(insights, list)
                else sum(len(v) for v in insights.values())
            ),
        }

    except Exception as e:
        logger.error(f"Error getting Gong project insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unified-project-status")
async def get_unified_project_status():
    """Get unified project status combining formal tools and conversation intelligence"""

    try:
        # Get existing project management data
        project_service = ProjectManagementService()
        formal_data = await project_service.get_unified_summary()

        # Get conversation intelligence
        gong_intelligence = GongMultiPurposeIntelligence()
        conversation_insights = (
            await gong_intelligence.get_project_management_intelligence(14)
        )

        # Combine and correlate data
        unified_status = {
            "formal_projects": formal_data,
            "conversation_intelligence": {
                "project_discussions": len(conversation_insights.project_references),
                "risks_identified": len(conversation_insights.risk_indicators),
                "technical_decisions": len(conversation_insights.technical_decisions),
                "timeline_discussions": len(conversation_insights.timeline_discussions),
                "recent_risks": conversation_insights.risk_indicators[
                    :5
                ],  # Top 5 recent risks
                "recent_decisions": conversation_insights.technical_decisions[
                    :3
                ],  # Top 3 recent decisions
            },
            "correlation_analysis": await _correlate_formal_and_conversation_data(
                formal_data, conversation_insights
            ),
            "current_date": "July 9, 2025",
            "last_updated": datetime.now().isoformat(),
        }

        return unified_status

    except Exception as e:
        logger.error(f"Error getting unified project status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/natural-language-query")
async def process_natural_language_query(request: dict[str, Any]):
    """Process natural language queries about project intelligence"""

    try:
        query = request.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        # Route query to appropriate service
        if any(
            keyword in query.lower()
            for keyword in ["conversation", "call", "discussion", "meeting"]
        ):
            # Gong conversation intelligence
            gong_intelligence = GongMultiPurposeIntelligence()
            result = await gong_intelligence.get_natural_language_insights(query)
        else:
            # Unified chat service for general project queries
            chat_service = SophiaUnifiedOrchestrator()
            result = await chat_service.process_enhanced_query(
                query,
                {
                    "context_type": "project_intelligence",
                    "current_date": "July 9, 2025",
                },
            )

        return {
            "success": True,
            "query": query,
            "response": result,
            "current_date": "July 9, 2025",
            "processing_time": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error processing natural language query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-dashboard")
async def get_project_risk_dashboard():
    """Get comprehensive project risk dashboard with conversation intelligence"""

    try:
        gong_intelligence = GongMultiPurposeIntelligence()
        project_service = ProjectManagementService()

        # Get risks from conversations
        conversation_insights = (
            await gong_intelligence.get_project_management_intelligence(30)
        )
        conversation_risks = conversation_insights.risk_indicators

        # Get formal project health data
        formal_projects = await project_service.get_unified_summary()
        formal_risks = [
            project
            for project in formal_projects.get("active_projects", [])
            if project.get("status") == "At Risk"
            or project.get("health_score", 100) < 70
        ]

        # Categorize and prioritize risks
        risk_dashboard = {
            "conversation_risks": {
                "total": len(conversation_risks),
                "critical": [
                    r for r in conversation_risks if r.get("severity") == "critical"
                ],
                "high": [r for r in conversation_risks if r.get("severity") == "high"],
                "medium": [
                    r for r in conversation_risks if r.get("severity") == "medium"
                ],
                "recent": sorted(
                    conversation_risks,
                    key=lambda x: x.get("call_date", ""),
                    reverse=True,
                )[:10],
            },
            "formal_project_risks": {
                "total": len(formal_risks),
                "at_risk_projects": formal_risks,
                "health_distribution": _calculate_health_distribution(
                    formal_projects.get("active_projects", [])
                ),
            },
            "risk_correlation": await _correlate_conversation_and_formal_risks(
                conversation_risks, formal_risks
            ),
            "recommendations": await _generate_risk_recommendations(
                conversation_risks, formal_risks
            ),
            "current_date": "July 9, 2025",
            "last_updated": datetime.now().isoformat(),
        }

        return risk_dashboard

    except Exception as e:
        logger.error(f"Error getting project risk dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team-intelligence")
async def get_team_intelligence_from_conversations():
    """Get team performance and communication insights from conversations"""

    try:
        gong_intelligence = GongMultiPurposeIntelligence()

        # Get team performance insights
        all_insights = await gong_intelligence.extract_multi_purpose_insights(14)
        team_insights = all_insights.get("team_performance", [])

        # Analyze team communication patterns
        team_intelligence = {
            "communication_effectiveness": await _analyze_communication_patterns(
                team_insights
            ),
            "meeting_effectiveness": await _analyze_meeting_effectiveness(
                team_insights
            ),
            "coaching_opportunities": [
                insight
                for insight in team_insights
                if "coaching" in insight.insight.lower()
                or "improvement" in insight.insight.lower()
            ],
            "collaboration_patterns": await _analyze_collaboration_patterns(
                team_insights
            ),
            "process_improvements": [
                insight
                for insight in team_insights
                if "process" in insight.insight.lower()
                or "workflow" in insight.insight.lower()
            ],
            "insights_summary": {
                "total_insights": len(team_insights),
                "high_priority": [
                    i for i in team_insights if i.urgency_level == "urgent"
                ],
                "positive_feedback": [
                    i for i in team_insights if i.sentiment_score > 0.5
                ],
                "areas_of_concern": [
                    i for i in team_insights if i.sentiment_score < -0.3
                ],
            },
            "current_date": "July 9, 2025",
            "analysis_period": "Last 14 days",
        }

        return team_intelligence

    except Exception as e:
        logger.error(f"Error getting team intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions


async def _correlate_formal_and_conversation_data(
    formal_data: dict[str, Any], conversation_insights
) -> dict[str, Any]:
    """Correlate formal project data with conversation insights"""

    correlations = {
        "project_mentions": [],
        "risk_alignment": [],
        "timeline_discrepancies": [],
        "confidence_score": 0.0,
    }

    try:
        # Extract project names from formal data
        formal_projects = [
            p.get("name", "") for p in formal_data.get("active_projects", [])
        ]

        # Check for project mentions in conversations
        for project_ref in conversation_insights.project_references:
            content = project_ref.get("content", "").lower()
            matching_projects = [p for p in formal_projects if p.lower() in content]

            if matching_projects:
                correlations["project_mentions"].append(
                    {
                        "formal_project": matching_projects[0],
                        "conversation_reference": project_ref,
                        "alignment": "mentioned",
                    }
                )

        # Calculate confidence score
        total_formal_projects = len(formal_projects)
        mentioned_projects = len(correlations["project_mentions"])
        correlations["confidence_score"] = (
            mentioned_projects / total_formal_projects
            if total_formal_projects > 0
            else 0
        )

    except Exception as e:
        logger.error(f"Error correlating data: {e}")

    return correlations


async def _correlate_conversation_and_formal_risks(
    conversation_risks: list[dict], formal_risks: list[dict]
) -> dict[str, Any]:
    """Correlate risks identified in conversations with formal project risks"""

    correlation = {
        "aligned_risks": [],
        "conversation_only_risks": [],
        "formal_only_risks": [],
        "risk_coverage": 0.0,
    }

    try:
        # Simple keyword matching for risk correlation
        formal_project_names = [r.get("name", "").lower() for r in formal_risks]

        for conv_risk in conversation_risks:
            risk_content = conv_risk.get("content", "").lower()
            matching_formal = [
                name for name in formal_project_names if name in risk_content
            ]

            if matching_formal:
                correlation["aligned_risks"].append(
                    {
                        "conversation_risk": conv_risk,
                        "formal_project": matching_formal[0],
                        "alignment_type": "project_name_match",
                    }
                )
            else:
                correlation["conversation_only_risks"].append(conv_risk)

        # Calculate risk coverage
        total_risks = len(conversation_risks) + len(formal_risks)
        aligned_risks = len(correlation["aligned_risks"])
        correlation["risk_coverage"] = (
            aligned_risks / total_risks if total_risks > 0 else 0
        )

    except Exception as e:
        logger.error(f"Error correlating risks: {e}")

    return correlation


async def _generate_risk_recommendations(
    conversation_risks: list[dict], formal_risks: list[dict]
) -> list[str]:
    """Generate actionable risk recommendations"""

    recommendations = []

    try:
        # High-severity conversation risks
        critical_conv_risks = [
            r for r in conversation_risks if r.get("severity") == "critical"
        ]
        if critical_conv_risks:
            recommendations.append(
                f"Address {len(critical_conv_risks)} critical risks identified in recent conversations"
            )

        # Formal project risks
        if formal_risks:
            recommendations.append(
                f"Review {len(formal_risks)} at-risk projects in formal project management tools"
            )

        # General recommendations
        if len(conversation_risks) > len(formal_risks):
            recommendations.append(
                "Consider updating formal project risk tracking based on conversation insights"
            )

        recommendations.append(
            "Schedule risk review meeting to align conversation and formal risk data"
        )

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")

    return recommendations


def _calculate_health_distribution(projects: list[dict]) -> dict[str, int]:
    """Calculate health score distribution for projects"""

    distribution = {"healthy": 0, "warning": 0, "at_risk": 0}

    for project in projects:
        health_score = project.get("health_score", 100)
        if health_score >= 80:
            distribution["healthy"] += 1
        elif health_score >= 60:
            distribution["warning"] += 1
        else:
            distribution["at_risk"] += 1

    return distribution


async def _analyze_communication_patterns(team_insights: list) -> dict[str, Any]:
    """Analyze team communication patterns from insights"""

    patterns = {
        "meeting_frequency": 0,
        "communication_quality": "good",
        "participation_levels": "balanced",
        "key_themes": [],
    }

    # Simple analysis based on available insights
    patterns["meeting_frequency"] = len(team_insights)

    # Analyze sentiment for communication quality
    if team_insights:
        avg_sentiment = sum(i.sentiment_score for i in team_insights) / len(
            team_insights
        )
        if avg_sentiment > 0.3:
            patterns["communication_quality"] = "excellent"
        elif avg_sentiment > 0:
            patterns["communication_quality"] = "good"
        else:
            patterns["communication_quality"] = "needs_improvement"

    return patterns


async def _analyze_meeting_effectiveness(team_insights: list) -> dict[str, Any]:
    """Analyze meeting effectiveness from team insights"""

    effectiveness = {
        "total_meetings_analyzed": len(team_insights),
        "effective_meetings": 0,
        "improvement_opportunities": [],
        "average_sentiment": 0.0,
    }

    if team_insights:
        # Calculate effectiveness based on sentiment and urgency
        effective_count = sum(
            1
            for insight in team_insights
            if insight.sentiment_score > 0 and insight.urgency_level != "urgent"
        )
        effectiveness["effective_meetings"] = effective_count
        effectiveness["average_sentiment"] = sum(
            i.sentiment_score for i in team_insights
        ) / len(team_insights)

        # Identify improvement opportunities
        low_sentiment_insights = [i for i in team_insights if i.sentiment_score < 0]
        effectiveness["improvement_opportunities"] = [
            i.insight for i in low_sentiment_insights[:3]
        ]

    return effectiveness


async def _analyze_collaboration_patterns(team_insights: list) -> dict[str, Any]:
    """Analyze team collaboration patterns"""

    collaboration = {
        "cross_team_interactions": 0,
        "collaboration_quality": "good",
        "common_participants": [],
        "collaboration_themes": [],
    }

    if team_insights:
        # Analyze participant patterns
        all_participants = []
        for insight in team_insights:
            all_participants.extend(insight.participants)

        # Find common participants
        from collections import Counter

        participant_counts = Counter(all_participants)
        collaboration["common_participants"] = [
            {"name": name, "frequency": count}
            for name, count in participant_counts.most_common(5)
        ]

        # Assess collaboration quality based on participant diversity and sentiment
        unique_participants = len(set(all_participants))
        avg_sentiment = sum(i.sentiment_score for i in team_insights) / len(
            team_insights
        )

        if unique_participants > 10 and avg_sentiment > 0.2:
            collaboration["collaboration_quality"] = "excellent"
        elif unique_participants > 5 and avg_sentiment > 0:
            collaboration["collaboration_quality"] = "good"
        else:
            collaboration["collaboration_quality"] = "needs_improvement"

    return collaboration
