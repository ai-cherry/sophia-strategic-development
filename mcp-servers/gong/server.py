#!/usr/bin/env python3
"""
Sophia AI Gong MCP Server
Provides sales call analytics and insights
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

import httpx
from base.unified_standardized_base import (
    ServerConfig,
)
from base.unified_standardized_base import (
    UnifiedStandardizedMCPServer as StandardizedMCPServer,
)
from mcp.types import TextContent, Tool

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


class GongMCPServer(StandardizedMCPServer):
    """Gong MCP Server for sales call analytics"""

    def __init__(self):
        config = ServerConfig(
            name="gong_v2",
            version="2.0.0",
            description="Sales call analytics and insights",
        )
        super().__init__(config)

        # Gong configuration
        self.api_key = get_config_value("gong_api_key")
        self.base_url = "https://api.gong.io/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def get_custom_tools(self) -> list[Tool]:
        """Define custom tools for Gong operations"""
        return [
            Tool(
                name="list_calls",
                description="List recent calls with filters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "from_date": {
                            "type": "string",
                            "description": "Start date (ISO format)",
                        },
                        "to_date": {
                            "type": "string",
                            "description": "End date (ISO format)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of calls to return",
                            "default": 10,
                        },
                    },
                },
            ),
            Tool(
                name="get_call_transcript",
                description="Retrieve transcript for a specific call",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "call_id": {"type": "string", "description": "The call ID"}
                    },
                    "required": ["call_id"],
                },
            ),
            Tool(
                name="get_call_insights",
                description="Get AI-generated insights for a call",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "call_id": {"type": "string", "description": "The call ID"}
                    },
                    "required": ["call_id"],
                },
            ),
            Tool(
                name="search_calls",
                description="Search calls by content or participant",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "participant_email": {
                            "type": "string",
                            "description": "Filter by participant email",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="get_speaker_stats",
                description="Get speaker talk time analytics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "call_id": {"type": "string", "description": "The call ID"}
                    },
                    "required": ["call_id"],
                },
            ),
            Tool(
                name="get_deal_intelligence",
                description="Get deal-specific insights from calls",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "deal_id": {"type": "string", "description": "CRM deal ID"}
                    },
                    "required": ["deal_id"],
                },
            ),
        ]

    async def handle_custom_tool(self, name: str, arguments: dict) -> list[TextContent]:
        """Handle custom tool calls"""
        try:
            if name == "list_calls":
                return await self._list_calls(arguments)
            elif name == "get_call_transcript":
                return await self._get_call_transcript(arguments["call_id"])
            elif name == "get_call_insights":
                return await self._get_call_insights(arguments["call_id"])
            elif name == "search_calls":
                return await self._search_calls(arguments)
            elif name == "get_speaker_stats":
                return await self._get_speaker_stats(arguments["call_id"])
            elif name == "get_deal_intelligence":
                return await self._get_deal_intelligence(arguments["deal_id"])
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Error handling tool {name}: {e}")
            return [TextContent(type="text", text=f"Error: {e!s}")]

    async def _list_calls(self, params: dict) -> list[TextContent]:
        """List recent calls"""
        try:
            # Default date range if not provided
            if "from_date" not in params:
                params["from_date"] = (datetime.now() - timedelta(days=7)).isoformat()
            if "to_date" not in params:
                params["to_date"] = datetime.now().isoformat()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calls",
                    headers=self.headers,
                    params={
                        "fromDateTime": params["from_date"],
                        "toDateTime": params["to_date"],
                        "limit": params.get("limit", 10),
                    },
                )
                response.raise_for_status()

            calls = response.json().get("calls", [])

            result = f"Found {len(calls)} calls:\n\n"
            for call in calls:
                result += f"- Call ID: {call['id']}\n"
                result += f"  Title: {call.get('title', 'N/A')}\n"
                result += f"  Date: {call.get('scheduled', 'N/A')}\n"
                result += f"  Duration: {call.get('duration', 0)} minutes\n"
                result += f"  Participants: {len(call.get('participants', []))}\n\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error listing calls: {e}")
            return [TextContent(type="text", text=f"Error listing calls: {e!s}")]

    async def _get_call_transcript(self, call_id: str) -> list[TextContent]:
        """Get call transcript"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calls/{call_id}/transcript", headers=self.headers
                )
                response.raise_for_status()

            transcript = response.json()

            result = f"Transcript for Call {call_id}:\n\n"
            for segment in transcript.get("transcript", []):
                speaker = segment.get("speakerName", "Unknown")
                text = segment.get("text", "")
                result += f"{speaker}: {text}\n\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error getting transcript: {e}")
            return [TextContent(type="text", text=f"Error getting transcript: {e!s}")]

    async def _get_call_insights(self, call_id: str) -> list[TextContent]:
        """Get AI-generated insights"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calls/{call_id}/highlights", headers=self.headers
                )
                response.raise_for_status()

            highlights = response.json()

            result = f"Insights for Call {call_id}:\n\n"

            # Topics discussed
            topics = highlights.get("topics", [])
            if topics:
                result += "Topics Discussed:\n"
                for topic in topics:
                    result += (
                        f"- {topic['name']} (confidence: {topic.get('score', 0):.2f})\n"
                    )
                result += "\n"

            # Key moments
            moments = highlights.get("keyMoments", [])
            if moments:
                result += "Key Moments:\n"
                for moment in moments:
                    result += f"- {moment['text']} (at {moment['time']})\n"
                result += "\n"

            # Action items
            actions = highlights.get("actionItems", [])
            if actions:
                result += "Action Items:\n"
                for action in actions:
                    result += f"- {action['text']} (assigned to: {action.get('assignee', 'TBD')})\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return [TextContent(type="text", text=f"Error getting insights: {e!s}")]

    async def _search_calls(self, params: dict) -> list[TextContent]:
        """Search calls by content"""
        try:
            search_params = {"q": params["query"]}
            if "participant_email" in params:
                search_params["participantEmail"] = params["participant_email"]

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calls/search",
                    headers=self.headers,
                    params=search_params,
                )
                response.raise_for_status()

            results = response.json().get("calls", [])

            result = f"Found {len(results)} calls matching '{params['query']}':\n\n"
            for call in results:
                result += f"- Call ID: {call['id']}\n"
                result += f"  Title: {call.get('title', 'N/A')}\n"
                result += f"  Date: {call.get('scheduled', 'N/A')}\n"
                result += f"  Relevance: {call.get('relevanceScore', 0):.2f}\n\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error searching calls: {e}")
            return [TextContent(type="text", text=f"Error searching calls: {e!s}")]

    async def _get_speaker_stats(self, call_id: str) -> list[TextContent]:
        """Get speaker statistics"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calls/{call_id}/stats", headers=self.headers
                )
                response.raise_for_status()

            stats = response.json()

            result = f"Speaker Statistics for Call {call_id}:\n\n"

            # Talk time distribution
            speakers = stats.get("speakers", [])
            total_time = sum(s.get("talkTime", 0) for s in speakers)

            for speaker in speakers:
                name = speaker.get("name", "Unknown")
                talk_time = speaker.get("talkTime", 0)
                percentage = (talk_time / total_time * 100) if total_time > 0 else 0
                result += f"{name}:\n"
                result += f"  Talk time: {talk_time}s ({percentage:.1f}%)\n"
                result += f"  Pace: {speaker.get('pace', 'N/A')} words/min\n"
                result += f"  Questions asked: {speaker.get('questionsAsked', 0)}\n\n"

            # Interaction metrics
            result += f"Total speakers: {len(speakers)}\n"
            result += f"Longest monologue: {stats.get('longestMonologue', 0)}s\n"
            result += f"Interactivity score: {stats.get('interactivity', 0):.2f}\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error getting speaker stats: {e}")
            return [
                TextContent(type="text", text=f"Error getting speaker stats: {e!s}")
            ]

    async def _get_deal_intelligence(self, deal_id: str) -> list[TextContent]:
        """Get deal-specific intelligence"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/deals/{deal_id}/intelligence",
                    headers=self.headers,
                )
                response.raise_for_status()

            intelligence = response.json()

            result = f"Deal Intelligence for {deal_id}:\n\n"

            # Deal health score
            result += f"Health Score: {intelligence.get('healthScore', 'N/A')}/100\n"
            result += f"Risk Level: {intelligence.get('riskLevel', 'Unknown')}\n\n"

            # Key indicators
            indicators = intelligence.get("indicators", {})
            result += "Key Indicators:\n"
            result += f"- Engagement level: {indicators.get('engagement', 'N/A')}\n"
            result += f"- Decision maker involvement: {indicators.get('decisionMaker', 'N/A')}\n"
            result += (
                f"- Competition mentioned: {indicators.get('competition', 'No')}\n"
            )
            result += f"- Budget discussed: {indicators.get('budget', 'No')}\n\n"

            # Recent interactions
            interactions = intelligence.get("recentInteractions", [])
            if interactions:
                result += "Recent Interactions:\n"
                for interaction in interactions[:5]:
                    result += f"- {interaction['date']}: {interaction['summary']}\n"

            # Recommendations
            recommendations = intelligence.get("recommendations", [])
            if recommendations:
                result += "\nRecommendations:\n"
                for rec in recommendations:
                    result += f"- {rec['action']} (priority: {rec['priority']})\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error getting deal intelligence: {e}")
            return [
                TextContent(type="text", text=f"Error getting deal intelligence: {e!s}")
            ]


# Main entry point
async def main():
    """Main entry point"""
    server = GongMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
