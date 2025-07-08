"""
Gong V2 Main Handler - Sales conversation intelligence and analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import httpx

from ..config import settings
from ..models.data_models import (
    CallRequest,
    CallResponse,
    CoachingRequest,
    InsightRequest,
    SearchRequest,
    TranscriptRequest,
)

logger = logging.getLogger(__name__)


class GongHandler:
    """Enhanced Gong operations for sales intelligence"""

    def __init__(self):
        self.api_key = settings.GONG_API_KEY
        self.api_secret = settings.GONG_API_SECRET
        self.base_url = "https://api.gong.io/v2"
        self.client = httpx.AsyncClient(
            auth=(self.api_key, self.api_secret),
            headers={"Content-Type": "application/json"},
        )
        self._cache = {}
        self._cache_ttl = timedelta(minutes=15)

    async def get_recent_calls(self, request: CallRequest) -> CallResponse:
        """Get recent sales calls with insights"""
        try:
            # Build query parameters
            params = {
                "fromDateTime": (
                    request.from_date.isoformat()
                    if request.from_date
                    else (datetime.utcnow() - timedelta(days=7)).isoformat()
                ),
                "toDateTime": (
                    request.to_date.isoformat()
                    if request.to_date
                    else datetime.utcnow().isoformat()
                ),
            }

            if request.user_id:
                params["userId"] = request.user_id

            # Get calls
            response = await self.client.get(f"{self.base_url}/calls", params=params)
            response.raise_for_status()

            calls_data = response.json()

            # Process calls with insights
            calls = []
            for call in calls_data.get("calls", [])[: request.limit]:
                call_info = {
                    "id": call["id"],
                    "title": call.get("title", ""),
                    "scheduled": call.get("scheduled"),
                    "duration": call.get("duration"),
                    "participants": call.get("parties", []),
                    "url": call.get("url"),
                    "score": call.get("score"),
                    "topics": await self._get_call_topics(call["id"]),
                    "action_items": await self._get_action_items(call["id"]),
                }
                calls.append(call_info)

            return CallResponse(
                success=True,
                data={
                    "calls": calls,
                    "total": calls_data.get("totalRecords", 0),
                    "stats": await self._calculate_call_stats(calls),
                },
            )

        except Exception as e:
            logger.exception(f"Error fetching calls: {e}")
            return CallResponse(success=False, error=str(e))

    async def get_call_transcript(self, request: TranscriptRequest) -> dict[str, Any]:
        """Get call transcript with speaker separation"""
        cache_key = f"transcript:{request.call_id}"

        # Check cache
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if cached["expires"] > datetime.utcnow():
                return cached["data"]

        try:
            response = await self.client.get(
                f"{self.base_url}/calls/{request.call_id}/transcript"
            )
            response.raise_for_status()

            transcript_data = response.json()

            # Process transcript
            segments = []
            for segment in transcript_data.get("transcript", []):
                segments.append(
                    {
                        "speaker": segment.get("speakerName", "Unknown"),
                        "text": segment.get("text", ""),
                        "start_time": segment.get("start"),
                        "sentiment": await self._analyze_sentiment(
                            segment.get("text", "")
                        ),
                    }
                )

            result = {
                "success": True,
                "call_id": request.call_id,
                "segments": segments,
                "summary": await self._generate_summary(segments),
                "key_moments": await self._extract_key_moments(segments),
            }

            # Cache result
            self._cache[cache_key] = {
                "data": result,
                "expires": datetime.utcnow() + self._cache_ttl,
            }

            return result

        except Exception as e:
            logger.exception(f"Error fetching transcript: {e}")
            return {"success": False, "error": str(e)}

    async def get_sales_insights(self, request: InsightRequest) -> dict[str, Any]:
        """Get AI-powered sales insights"""
        try:
            # Get team performance data
            response = await self.client.get(
                f"{self.base_url}/stats/team",
                params={
                    "fromDateTime": request.from_date.isoformat(),
                    "toDateTime": request.to_date.isoformat(),
                },
            )
            response.raise_for_status()

            stats_data = response.json()

            # Generate insights
            insights = {
                "success": True,
                "period": {
                    "from": request.from_date.isoformat(),
                    "to": request.to_date.isoformat(),
                },
                "metrics": {
                    "total_calls": stats_data.get("totalCalls", 0),
                    "avg_call_duration": stats_data.get("avgDuration", 0),
                    "talk_ratio": stats_data.get("avgTalkRatio", 0),
                    "conversion_rate": stats_data.get("conversionRate", 0),
                },
                "insights": await self._generate_insights(stats_data),
                "recommendations": await self._generate_recommendations(stats_data),
                "trends": await self._analyze_trends(stats_data),
            }

            return insights

        except Exception as e:
            logger.exception(f"Error generating insights: {e}")
            return {"success": False, "error": str(e)}

    async def get_coaching_opportunities(
        self, request: CoachingRequest
    ) -> dict[str, Any]:
        """Identify coaching opportunities from calls"""
        try:
            # Get user's recent calls
            calls_response = await self.get_recent_calls(
                CallRequest(user_id=request.user_id, limit=20)
            )

            if not calls_response.success:
                return {"success": False, "error": "Failed to fetch calls"}

            calls = calls_response.data["calls"]

            # Analyze calls for coaching opportunities
            opportunities = []

            for call in calls:
                if call.get("score", 100) < 70:  # Low scoring calls
                    opportunities.append(
                        {
                            "type": "low_score",
                            "call_id": call["id"],
                            "title": call["title"],
                            "score": call["score"],
                            "areas": await self._identify_improvement_areas(call["id"]),
                            "suggestions": await self._generate_coaching_tips(
                                call["id"]
                            ),
                        }
                    )

            # Aggregate patterns
            patterns = await self._identify_patterns(opportunities)

            return {
                "success": True,
                "user_id": request.user_id,
                "opportunities": opportunities,
                "patterns": patterns,
                "action_plan": await self._create_action_plan(patterns),
            }

        except Exception as e:
            logger.exception(f"Error finding coaching opportunities: {e}")
            return {"success": False, "error": str(e)}

    async def search_conversations(self, request: SearchRequest) -> dict[str, Any]:
        """Search across all conversations"""
        try:
            # Search calls
            response = await self.client.post(
                f"{self.base_url}/calls/search",
                json={
                    "query": request.query,
                    "filters": {
                        "fromDateTime": (
                            request.from_date.isoformat() if request.from_date else None
                        ),
                        "toDateTime": (
                            request.to_date.isoformat() if request.to_date else None
                        ),
                    },
                },
            )
            response.raise_for_status()

            search_results = response.json()

            # Process results
            results = []
            for result in search_results.get("calls", [])[: request.limit]:
                results.append(
                    {
                        "call_id": result["id"],
                        "title": result.get("title"),
                        "date": result.get("scheduled"),
                        "relevance_score": result.get("score"),
                        "matched_segments": result.get("matchedSegments", []),
                        "context": await self._get_search_context(
                            result["id"], request.query
                        ),
                    }
                )

            return {
                "success": True,
                "query": request.query,
                "total_results": search_results.get("totalRecords", 0),
                "results": results,
            }

        except Exception as e:
            logger.exception(f"Search error: {e}")
            return {"success": False, "error": str(e)}

    # Helper methods
    async def _get_call_topics(self, call_id: str) -> list[str]:
        """Extract topics from a call"""
        try:
            response = await self.client.get(f"{self.base_url}/calls/{call_id}/topics")
            response.raise_for_status()
            topics_data = response.json()
            return [topic["name"] for topic in topics_data.get("topics", [])]
        except:
            return []

    async def _get_action_items(self, call_id: str) -> list[dict[str, Any]]:
        """Extract action items from a call"""
        try:
            response = await self.client.get(
                f"{self.base_url}/calls/{call_id}/action-items"
            )
            response.raise_for_status()
            items_data = response.json()
            return items_data.get("actionItems", [])
        except:
            return []

    async def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text segment"""
        # Simplified sentiment analysis
        positive_words = ["great", "excellent", "love", "perfect", "amazing"]
        negative_words = ["problem", "issue", "concern", "difficult", "challenge"]

        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"

    async def _generate_summary(self, segments: list[dict[str, Any]]) -> str:
        """Generate call summary from segments"""
        # Simplified summary generation
        total_segments = len(segments)
        if total_segments == 0:
            return "No transcript available"

        # Get first and last few segments for context
        preview = " ".join([s["text"] for s in segments[:3]])
        return f"Call with {total_segments} segments. Preview: {preview[:200]}..."

    async def _extract_key_moments(
        self, segments: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Extract key moments from conversation"""
        key_moments = []

        # Look for questions, objections, and decisions
        for _i, segment in enumerate(segments):
            text = segment["text"].lower()

            if "?" in text:
                key_moments.append(
                    {
                        "type": "question",
                        "text": segment["text"],
                        "speaker": segment["speaker"],
                        "timestamp": segment.get("start_time"),
                    }
                )
            elif any(word in text for word in ["concern", "worried", "problem"]):
                key_moments.append(
                    {
                        "type": "objection",
                        "text": segment["text"],
                        "speaker": segment["speaker"],
                        "timestamp": segment.get("start_time"),
                    }
                )
            elif any(word in text for word in ["agree", "deal", "yes", "confirm"]):
                key_moments.append(
                    {
                        "type": "agreement",
                        "text": segment["text"],
                        "speaker": segment["speaker"],
                        "timestamp": segment.get("start_time"),
                    }
                )

        return key_moments[:10]  # Return top 10 moments

    async def _calculate_call_stats(
        self, calls: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate statistics from calls"""
        if not calls:
            return {}

        total_duration = sum(call.get("duration", 0) for call in calls)
        avg_duration = total_duration / len(calls) if calls else 0
        avg_score = (
            sum(call.get("score", 0) for call in calls) / len(calls) if calls else 0
        )

        return {
            "total_calls": len(calls),
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "avg_score": avg_score,
        }

    async def _generate_insights(self, stats_data: dict[str, Any]) -> list[str]:
        """Generate insights from statistics"""
        insights = []

        if stats_data.get("avgTalkRatio", 0) > 0.7:
            insights.append(
                "High talk ratio detected - consider more customer engagement"
            )

        if stats_data.get("conversionRate", 0) < 0.2:
            insights.append(
                "Low conversion rate - review sales process and objection handling"
            )

        if stats_data.get("avgDuration", 0) < 600:  # Less than 10 minutes
            insights.append(
                "Short call durations - ensure adequate discovery and value demonstration"
            )

        return insights

    async def _generate_recommendations(self, stats_data: dict[str, Any]) -> list[str]:
        """Generate recommendations based on data"""
        recommendations = []

        if stats_data.get("totalCalls", 0) < 50:
            recommendations.append("Increase call volume to improve pipeline")

        if stats_data.get("avgScore", 0) < 70:
            recommendations.append("Focus on call quality improvement through coaching")

        return recommendations

    async def _analyze_trends(self, stats_data: dict[str, Any]) -> dict[str, str]:
        """Analyze trends in the data"""
        # Simplified trend analysis
        return {
            "call_volume": (
                "increasing" if stats_data.get("totalCalls", 0) > 100 else "stable"
            ),
            "quality": (
                "improving" if stats_data.get("avgScore", 0) > 80 else "needs attention"
            ),
            "engagement": "high" if stats_data.get("avgTalkRatio", 0) < 0.6 else "low",
        }

    async def _identify_improvement_areas(self, call_id: str) -> list[str]:
        """Identify areas for improvement in a call"""
        # Simplified implementation
        return ["objection handling", "discovery questions", "value articulation"]

    async def _generate_coaching_tips(self, call_id: str) -> list[str]:
        """Generate coaching tips for a call"""
        return [
            "Ask more open-ended discovery questions",
            "Pause after presenting key value propositions",
            "Summarize customer needs before proposing solutions",
        ]

    async def _identify_patterns(
        self, opportunities: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Identify patterns in coaching opportunities"""
        patterns = []

        if len(opportunities) > 3:
            patterns.append(
                {
                    "pattern": "consistent_low_scores",
                    "frequency": len(opportunities),
                    "impact": "high",
                    "recommendation": "Schedule intensive coaching session",
                }
            )

        return patterns

    async def _create_action_plan(
        self, patterns: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Create action plan based on patterns"""
        action_plan = []

        for pattern in patterns:
            action_plan.append(
                {
                    "action": f"Address {pattern['pattern']}",
                    "priority": pattern["impact"],
                    "timeline": "next_week",
                    "resources": [
                        "manager_coaching",
                        "peer_shadowing",
                        "training_materials",
                    ],
                }
            )

        return action_plan

    async def _get_search_context(self, call_id: str, query: str) -> str:
        """Get context around search match"""
        # Simplified - would normally get actual transcript context
        return f"Context for '{query}' in call {call_id}"
