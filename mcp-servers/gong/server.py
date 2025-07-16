#!/usr/bin/env python3
"""

# Modern stack imports
from backend.services.coding_mcp_unified_memory_service import get_coding_memory_service, CodingMCPUnifiedMemoryService
from backend.services.lambda_labs_serverless_service import LambdaLabsServerlessService
import redis.asyncio as redis
import asyncpg

Sophia AI Gong MCP Server V2
Provides sales call analytics and insights with GPU-accelerated memory storage
Using official Anthropic MCP SDK

Date: July 12, 2025
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
from backend.core.redis_connection_manager import create_redis_from_config
from backend.services.coding_mcp_unified_memory_service import CodingMCPUnifiedMemoryService

logger = logging.getLogger(__name__)

class GongMCPServer(StandardizedMCPServer):
    """Gong MCP Server for sales call analytics with GPU-accelerated memory"""

    def __init__(self):
        config = ServerConfig(
            name="gong_v2",
            version="3.0.0",
            description="Sales call analytics with GPU-accelerated memory storage",
        )
        super().__init__(config)

        # Gong configuration
        self.api_key = get_config_value("gong_api_key")
        self.base_url = "https://api.gong.io/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Initialize memory service
        try:
            self.memory_service = CodingMCPUnifiedMemoryService()
            logger.info("UnifiedMemoryService initialized for Gong")
        except Exception as e:
            logger.error(f"Failed to initialize memory service: {e}")
            self.memory_service = None

        # Initialize modern stack services
        self.memory_service = CodingMCPUnifiedMemoryService()
        self.lambda_gpu = LambdaLabsServerlessService()
        self.redis = create_redis_from_config()

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
                description="Retrieve transcript for a specific call and store in GPU-accelerated memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "call_id": {"type": "string", "description": "The call ID"},
                        "store_in_memory": {
                            "type": "boolean",
                            "description": "Store transcript in memory for future reference",
                            "default": True,
                        },
                    },
                    "required": ["call_id"],
                },
            ),
            Tool(
                name="get_call_insights",
                description="Get AI-generated insights for a call and store in memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "call_id": {"type": "string", "description": "The call ID"},
                        "store_in_memory": {
                            "type": "boolean",
                            "description": "Store insights in memory",
                            "default": True,
                        },
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
            Tool(
                name="search_call_memory",
                description="Search stored call transcripts and insights using GPU-accelerated vector search",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            ),
        ]

    async def handle_custom_tool(self, name: str, arguments: dict) -> list[TextContent]:
        """Handle custom tool calls"""
        try:
            if name == "list_calls":
                return await self._list_calls(arguments)
            elif name == "get_call_transcript":
                return await self._get_call_transcript(
                    arguments["call_id"], arguments.get("store_in_memory", True)
                )
            elif name == "get_call_insights":
                return await self._get_call_insights(
                    arguments["call_id"], arguments.get("store_in_memory", True)
                )
            elif name == "search_calls":
                return await self._search_calls(arguments)
            elif name == "get_speaker_stats":
                return await self._get_speaker_stats(arguments["call_id"])
            elif name == "get_deal_intelligence":
                return await self._get_deal_intelligence(arguments["deal_id"])
            elif name == "search_call_memory":
                return await self._search_call_memory(arguments)
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

    async def _get_call_transcript(
        self, call_id: str, store_in_memory: bool = True
    ) -> list[TextContent]:
        """Get call transcript and optionally store in GPU-accelerated memory"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calls/{call_id}/transcript", headers=self.headers
                )
                response.raise_for_status()

            transcript = response.json()

            # Get call metadata for context
            call_response = await client.get(
                f"{self.base_url}/calls/{call_id}", headers=self.headers
            )
            call_data = call_response.json() if call_response.status_code == 200 else {}

            result = f"Transcript for Call {call_id}:\n\n"
            full_transcript = ""

            for segment in transcript.get("transcript", []):
                speaker = segment.get("speakerName", "Unknown")
                text = segment.get("text", "")
                result += f"{speaker}: {text}\n\n"
                full_transcript += f"{speaker}: {text}\n"

            # Store in GPU-accelerated memory if requested
            if store_in_memory and self.memory_service and full_transcript:
                try:
                    metadata = {
                        "call_id": call_id,
                        "type": "call_transcript",
                        "title": call_data.get("title", "Unknown"),
                        "date": call_data.get("scheduled", datetime.now().isoformat()),
                        "duration": call_data.get("duration", 0),
                        "participants": [
                            p.get("email", "unknown")
                            for p in call_data.get("participants", [])
                        ],
                    }

                    memory_id = await self.memory_service.add_knowledge(
                        content=full_transcript,
                        source=f"gong/call/{call_id}",
                        metadata=metadata,
                    )

                    result += f"\n✅ Transcript stored in GPU-accelerated memory (ID: {memory_id})"
                    logger.info(f"Stored transcript for call {call_id} in memory")
                except Exception as e:
                    logger.error(f"Failed to store transcript in memory: {e}")
                    result += f"\n⚠️ Failed to store in memory: {e}"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error getting transcript: {e}")
            return [TextContent(type="text", text=f"Error getting transcript: {e!s}")]

    async def _get_call_insights(
        self, call_id: str, store_in_memory: bool = True
    ) -> list[TextContent]:
        """Get AI-generated insights and store in memory"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calls/{call_id}/highlights", headers=self.headers
                )
                response.raise_for_status()

            highlights = response.json()

            result = f"Insights for Call {call_id}:\n\n"
            insights_content = f"Call {call_id} Insights:\n"

            # Topics discussed
            topics = highlights.get("topics", [])
            if topics:
                result += "Topics Discussed:\n"
                insights_content += "Topics: "
                for topic in topics:
                    result += (
                        f"- {topic['name']} (confidence: {topic.get('score', 0):.2f})\n"
                    )
                    insights_content += f"{topic['name']}, "
                result += "\n"
                insights_content = insights_content.rstrip(", ") + "\n"

            # Key moments
            moments = highlights.get("keyMoments", [])
            if moments:
                result += "Key Moments:\n"
                insights_content += "Key Moments:\n"
                for moment in moments:
                    result += f"- {moment['text']} (at {moment['time']})\n"
                    insights_content += f"- {moment['text']}\n"
                result += "\n"

            # Action items
            actions = highlights.get("actionItems", [])
            if actions:
                result += "Action Items:\n"
                insights_content += "Action Items:\n"
                for action in actions:
                    result += f"- {action['text']} (assigned to: {action.get('assignee', 'TBD')})\n"
                    insights_content += f"- {action['text']} (assignee: {action.get('assignee', 'TBD')})\n"

            # Store insights in memory if requested
            if store_in_memory and self.memory_service and insights_content:
                try:
                    metadata = {
                        "call_id": call_id,
                        "type": "call_insights",
                        "topics": [t["name"] for t in topics],
                        "action_items": [a["text"] for a in actions],
                        "key_moments": len(moments),
                    }

                    memory_id = await self.memory_service.add_knowledge(
                        content=insights_content,
                        source=f"gong/insights/{call_id}",
                        metadata=metadata,
                    )

                    result += f"\n✅ Insights stored in GPU-accelerated memory (ID: {memory_id})"
                    logger.info(f"Stored insights for call {call_id} in memory")
                except Exception as e:
                    logger.error(f"Failed to store insights in memory: {e}")
                    result += f"\n⚠️ Failed to store in memory: {e}"

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

    async def _search_call_memory(self, params: dict) -> list[TextContent]:
        """Search stored call transcripts and insights using GPU-accelerated vector search"""
        if not self.memory_service:
            return [TextContent(type="text", text="Memory service not available")]

        try:
            # Search for Gong-related content
            results = await self.memory_service.search_knowledge(
                query=params["query"],
                limit=params.get("limit", 5),
                metadata_filter={"source": {"$contains": "gong"}},
            )

            if not results:
                return [
                    TextContent(
                        type="text",
                        text=f"No stored call data found for '{params['query']}'",
                    )
                ]

            result = f"Found {len(results)} relevant call memories:\n\n"

            for idx, res in enumerate(results, 1):
                metadata = res.get("metadata", {})
                result += f"{idx}. {metadata.get('type', 'Unknown')} - Call {metadata.get('call_id', 'Unknown')}\n"
                result += f"   Date: {metadata.get('date', 'Unknown')}\n"
                result += f"   Score: {res.get('similarity', 0):.3f}\n"
                result += f"   Content preview: {res['content'][:200]}...\n\n"

            result += f"\n⚡ Search completed in {results[0].get('latency_ms', 0)}ms using GPU acceleration"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error searching call memory: {e}")
            return [TextContent(type="text", text=f"Error searching memory: {e!s}")]

    async def on_startup(self):
        """Initialize Gong server with memory service"""
        await super().on_startup()

        if self.memory_service:
            await self.memory_service.initialize()
            logger.info("Gong server ready with GPU-accelerated memory storage")

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        if self.memory_service:
            await self.memory_service.close()

        await super().on_shutdown()

# Main entry point
async def main():
    """Main entry point"""
    server = GongMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
