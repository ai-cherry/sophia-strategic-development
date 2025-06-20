"""Sophia AI - Comprehensive Slack Bot Implementation
Replaces admin website with intelligent Slack interface integrated with MCP architecture
"""

import asyncio
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

import aiohttp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp
from slack_sdk.socket_mode.async_client import AsyncSocketModeClient
from slack_sdk.web.async_client import AsyncWebClient

from ..core.integration_registry import integration_registry

logger = logging.getLogger(__name__)


class SlackCommandType(Enum):
    """Types of Slack commands supported"""

    DASHBOARD = "dashboard"
    QUERY = "query"
    SEARCH = "search"
    HEALTH = "health"
    DEPLOY = "deploy"
    STATS = "stats"
    HELP = "help"


@dataclass
class SlackCommand:
    """Structured Slack command"""

    command: str
    user_id: str
    channel_id: str
    text: str
    response_url: str
    trigger_id: str
    team_id: str
    timestamp: datetime


class SophiaSlackBot:
    """Comprehensive Slack bot that replaces the admin website
    Integrates with MCP architecture for natural language processing
    """

    def __init__(self):
        self.app = AsyncApp(
            token=os.getenv("SLACK_BOT_TOKEN"),
            signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
        )
        self.client = AsyncWebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.socket_client = None
        self.admin_api_base = "http://localhost:5000/api"
        self.mcp_integration = True

        # Setup command handlers
        self._setup_command_handlers()
        self._setup_event_handlers()
        self._setup_message_handlers()

    def _setup_command_handlers(self):
        """Setup Slack slash command handlers"""

        @self.app.command("/sophia")
        async def handle_sophia_command(ack, command, client, logger):
            await ack()
            await self._process_sophia_command(command, client)

        @self.app.command("/sophia-dashboard")
        async def handle_dashboard_command(ack, command, client):
            await ack()
            await self._handle_dashboard_command(command, client)

        @self.app.command("/sophia-query")
        async def handle_query_command(ack, command, client):
            await ack()
            await self._handle_query_command(command, client)

        @self.app.command("/sophia-search")
        async def handle_search_command(ack, command, client):
            await ack()
            await self._handle_search_command(command, client)

        @self.app.command("/sophia-health")
        async def handle_health_command(ack, command, client):
            await ack()
            await self._handle_health_command(command, client)

        @self.app.command("/sophia-deploy")
        async def handle_deploy_command(ack, command, client):
            await ack()
            await self._handle_deploy_command(command, client)

    def _setup_event_handlers(self):
        """Setup Slack event handlers"""

        @self.app.event("app_mention")
        async def handle_app_mention(event, client, logger):
            await self._handle_mention(event, client)

        @self.app.event("message")
        async def handle_message(event, client, logger):
            # Only process direct messages to the bot
            if event.get("channel_type") == "im":
                await self._handle_direct_message(event, client)

    def _setup_message_handlers(self):
        """Setup interactive message handlers"""

        @self.app.action("dashboard_refresh")
        async def handle_dashboard_refresh(ack, action, client):
            await ack()
            await self._refresh_dashboard(action, client)

        @self.app.action("search_filter")
        async def handle_search_filter(ack, action, client):
            await ack()
            await self._apply_search_filter(action, client)

        @self.app.action("deploy_confirm")
        async def handle_deploy_confirm(ack, action, client):
            await ack()
            await self._confirm_deployment(action, client)

    async def _process_sophia_command(
        self, command: Dict[str, Any], client: AsyncWebClient
    ):
        """Process main /sophia command with subcommands"""
        text = command.get("text", "").strip()
        channel_id = command["channel_id"]
        user_id = command["user_id"]

        if not text:
            await self._send_help_message(channel_id, client)
            return

        parts = text.split()
        subcommand = parts[0].lower()
        args = " ".join(parts[1:]) if len(parts) > 1 else ""

        if subcommand == "dashboard":
            await self._handle_dashboard_request(channel_id, client, user_id)
        elif subcommand == "query":
            await self._handle_natural_language_query(channel_id, client, args, user_id)
        elif subcommand == "search":
            await self._handle_conversation_search(channel_id, client, args, user_id)
        elif subcommand == "health":
            await self._handle_system_health(channel_id, client, user_id)
        elif subcommand == "deploy":
            await self._handle_deployment_request(channel_id, client, args, user_id)
        elif subcommand == "stats":
            await self._handle_integration_stats(channel_id, client, user_id)
        elif subcommand == "help":
            await self._send_help_message(channel_id, client)
        else:
            # Treat as natural language query
            await self._handle_natural_language_query(channel_id, client, text, user_id)

    async def _handle_dashboard_command(
        self, command: Dict[str, Any], client: AsyncWebClient
    ):
        """Handle dedicated dashboard command"""
        await self._handle_dashboard_request(
            command["channel_id"], client, command["user_id"]
        )

    async def _handle_query_command(
        self, command: Dict[str, Any], client: AsyncWebClient
    ):
        """Handle dedicated query command"""
        query = command.get("text", "").strip()
        await self._handle_natural_language_query(
            command["channel_id"], client, query, command["user_id"]
        )

    async def _handle_search_command(
        self, command: Dict[str, Any], client: AsyncWebClient
    ):
        """Handle dedicated search command"""
        search_params = command.get("text", "").strip()
        await self._handle_conversation_search(
            command["channel_id"], client, search_params, command["user_id"]
        )

    async def _handle_health_command(
        self, command: Dict[str, Any], client: AsyncWebClient
    ):
        """Handle dedicated health command"""
        await self._handle_system_health(
            command["channel_id"], client, command["user_id"]
        )

    async def _handle_deploy_command(
        self, command: Dict[str, Any], client: AsyncWebClient
    ):
        """Handle dedicated deploy command"""
        deploy_params = command.get("text", "").strip()
        await self._handle_deployment_request(
            command["channel_id"], client, deploy_params, command["user_id"]
        )

    async def _handle_dashboard_request(
        self, channel_id: str, client: AsyncWebClient, user_id: str
    ):
        """Handle dashboard statistics request"""
        try:
            # Fetch dashboard stats from admin API
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.admin_api_base}/dashboard/stats"
                ) as response:
                    if response.status == 200:
                        stats = await response.json()
                        blocks = self._create_dashboard_blocks(stats)

                        await client.chat_postMessage(
                            channel=channel_id,
                            text="📊 Sophia AI Dashboard",
                            blocks=blocks,
                            user=user_id,
                        )
                    else:
                        await client.chat_postMessage(
                            channel=channel_id,
                            text="❌ Failed to fetch dashboard statistics. Please try again later.",
                            user=user_id,
                        )
        except Exception as e:
            logger.error(f"Error handling dashboard request: {e}")
            await client.chat_postMessage(
                channel=channel_id,
                text="❌ An error occurred while fetching dashboard data.",
                user=user_id,
            )

    async def _handle_natural_language_query(
        self, channel_id: str, client: AsyncWebClient, query: str, user_id: str
    ):
        """Handle natural language queries via MCP integration"""
        if not query:
            await client.chat_postMessage(
                channel=channel_id,
                text="Please provide a query. Example: `/sophia query show me recent apartment deals`",
                user=user_id,
            )
            return

        try:
            # Use MCP server for natural language processing if available
            if self.mcp_integration:
                result = await self._process_query_via_mcp(query)
            else:
                # Fallback to direct API call
                result = await self._process_query_via_api(query)

            blocks = self._create_query_result_blocks(query, result)

            await client.chat_postMessage(
                channel=channel_id,
                text=f"🔍 Query Results for: {query}",
                blocks=blocks,
                user=user_id,
            )

        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            await client.chat_postMessage(
                channel=channel_id,
                text="❌ An error occurred while processing your query. Please try again.",
                user=user_id,
            )

    async def _handle_conversation_search(
        self, channel_id: str, client: AsyncWebClient, search_params: str, user_id: str
    ):
        """Handle conversation search requests"""
        try:
            # Parse search parameters
            params = self._parse_search_params(search_params)

            # Make API call to search endpoint
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.admin_api_base}/conversations/search", params=params
                ) as response:
                    if response.status == 200:
                        results = await response.json()
                        blocks = self._create_search_result_blocks(
                            results, search_params
                        )

                        await client.chat_postMessage(
                            channel=channel_id,
                            text=f"🔍 Search Results: {search_params}",
                            blocks=blocks,
                            user=user_id,
                        )
                    else:
                        await client.chat_postMessage(
                            channel=channel_id,
                            text="❌ Failed to search conversations. Please check your parameters.",
                            user=user_id,
                        )
        except Exception as e:
            logger.error(f"Error handling conversation search: {e}")
            await client.chat_postMessage(
                channel=channel_id,
                text="❌ An error occurred during search. Please try again.",
                user=user_id,
            )

    async def _handle_system_health(
        self, channel_id: str, client: AsyncWebClient, user_id: str
    ):
        """Handle system health check requests"""
        try:
            # Get health status from integration registry
            health_status = await integration_registry.health_check_all()
            stats = integration_registry.get_integration_stats()

            blocks = self._create_health_status_blocks(health_status, stats)

            await client.chat_postMessage(
                channel=channel_id,
                text="🏥 System Health Status",
                blocks=blocks,
                user=user_id,
            )

        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            await client.chat_postMessage(
                channel=channel_id,
                text="❌ An error occurred while checking system health.",
                user=user_id,
            )

    async def _handle_deployment_request(
        self, channel_id: str, client: AsyncWebClient, deploy_params: str, user_id: str
    ):
        """Handle deployment requests"""
        try:
            # Parse deployment parameters
            if not deploy_params:
                await client.chat_postMessage(
                    channel=channel_id,
                    text="Please specify deployment target. Example: `/sophia deploy vercel` or `/sophia deploy lambda-labs`",
                    user=user_id,
                )
                return

            # Create confirmation blocks
            blocks = self._create_deployment_confirmation_blocks(deploy_params)

            await client.chat_postMessage(
                channel=channel_id,
                text=f"🚀 Deployment Request: {deploy_params}",
                blocks=blocks,
                user=user_id,
            )

        except Exception as e:
            logger.error(f"Error handling deployment request: {e}")
            await client.chat_postMessage(
                channel=channel_id,
                text="❌ An error occurred while processing deployment request.",
                user=user_id,
            )

    async def _handle_integration_stats(
        self, channel_id: str, client: AsyncWebClient, user_id: str
    ):
        """Handle integration statistics requests"""
        try:
            stats = integration_registry.get_integration_stats()
            blocks = self._create_integration_stats_blocks(stats)

            await client.chat_postMessage(
                channel=channel_id,
                text="📈 Integration Statistics",
                blocks=blocks,
                user=user_id,
            )

        except Exception as e:
            logger.error(f"Error getting integration stats: {e}")
            await client.chat_postMessage(
                channel=channel_id,
                text="❌ An error occurred while fetching integration statistics.",
                user=user_id,
            )

    async def _handle_mention(self, event: Dict[str, Any], client: AsyncWebClient):
        """Handle app mentions"""
        text = event.get("text", "")
        channel = event["channel"]
        user = event["user"]

        # Remove bot mention from text
        clean_text = re.sub(r"<@[A-Z0-9]+>", "", text).strip()

        if clean_text:
            await self._handle_natural_language_query(channel, client, clean_text, user)
        else:
            await self._send_help_message(channel, client)

    async def _handle_direct_message(
        self, event: Dict[str, Any], client: AsyncWebClient
    ):
        """Handle direct messages to the bot"""
        text = event.get("text", "")
        channel = event["channel"]
        user = event["user"]

        if text:
            await self._handle_natural_language_query(channel, client, text, user)

    async def _process_query_via_mcp(self, query: str) -> Dict[str, Any]:
        """Process query via MCP server"""
        try:
            # Use MCP server's natural language processing
            # This would integrate with the sophia_mcp_server
            result = {
                "method": "mcp",
                "query": query,
                "results": [],
                "processed_via": "MCP Server",
            }
            return result
        except Exception as e:
            logger.error(f"MCP processing failed: {e}")
            return await self._process_query_via_api(query)

    async def _process_query_via_api(self, query: str) -> Dict[str, Any]:
        """Process query via direct API call"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.admin_api_base}/natural-query", json={"query": query}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": "Failed to process query", "query": query}

    def _parse_search_params(self, search_params: str) -> Dict[str, str]:
        """Parse search parameters from text"""
        params = {}

        # Simple parameter parsing
        if "from:" in search_params:
            match = re.search(r"from:(\S+)", search_params)
            if match:
                params["date_from"] = match.group(1)

        if "to:" in search_params:
            match = re.search(r"to:(\S+)", search_params)
            if match:
                params["date_to"] = match.group(1)

        if "company:" in search_params:
            match = re.search(r"company:(\S+)", search_params)
            if match:
                params["company"] = match.group(1)

        # Extract main query (remove parameter syntax)
        query = re.sub(r"\w+:\S+", "", search_params).strip()
        if query:
            params["q"] = query

        return params

    def _create_dashboard_blocks(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create Slack blocks for dashboard display"""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📊 Sophia AI Dashboard"},
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Calls:*\n{stats.get('total_calls', 'N/A')}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Emails:*\n{stats.get('total_emails', 'N/A')}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*High Relevance:*\n{stats.get('high_relevance_count', 'N/A')}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Active Deals:*\n{stats.get('active_deals', 'N/A')}",
                    },
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🔄 Refresh"},
                        "action_id": "dashboard_refresh",
                        "style": "primary",
                    }
                ],
            },
        ]
        return blocks

    def _create_query_result_blocks(
        self, query: str, result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create Slack blocks for query results"""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🔍 Query: {query[:50]}..."},
            }
        ]

        if "error" in result:
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"❌ *Error:* {result['error']}"},
                }
            )
        else:
            # Add result summary
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Results found:* {len(result.get('results', []))}",
                    },
                }
            )

            # Add top results
            for i, item in enumerate(result.get("results", [])[:5]):
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{i+1}.* {item.get('summary', 'No summary available')}",
                        },
                    }
                )

        return blocks

    def _create_search_result_blocks(
        self, results: Dict[str, Any], search_params: str
    ) -> List[Dict[str, Any]]:
        """Create Slack blocks for search results"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔍 Search: {search_params[:50]}...",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Found:* {results.get('total_count', 0)} conversations",
                },
            },
        ]

        # Add conversation results
        for conv in results.get("conversations", [])[:5]:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{conv.get('title', 'Untitled')}*\n{conv.get('summary', 'No summary')[:100]}...",
                    },
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View"},
                        "action_id": f"view_conversation_{conv.get('id')}",
                    },
                }
            )

        return blocks

    def _create_health_status_blocks(
        self, health_status: Dict[str, bool], stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create Slack blocks for health status"""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🏥 System Health Status"},
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Integrations:*\n{stats.get('total_registered', 0)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Active:*\n{stats.get('total_active', 0)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Healthy:*\n{stats.get('healthy_count', 0)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Unhealthy:*\n{stats.get('unhealthy_count', 0)}",
                    },
                ],
            },
        ]

        # Add individual service status
        for service, is_healthy in health_status.items():
            status_emoji = "✅" if is_healthy else "❌"
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{status_emoji} *{service.title()}*",
                    },
                }
            )

        return blocks

    def _create_deployment_confirmation_blocks(
        self, deploy_params: str
    ) -> List[Dict[str, Any]]:
        """Create Slack blocks for deployment confirmation"""
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚀 Deploy to {deploy_params.title()}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Are you sure you want to deploy to *{deploy_params}*?",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Confirm"},
                        "action_id": "deploy_confirm",
                        "style": "primary",
                        "value": deploy_params,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Cancel"},
                        "action_id": "deploy_cancel",
                    },
                ],
            },
        ]

    def _create_integration_stats_blocks(
        self, stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create Slack blocks for integration statistics"""
        return [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📈 Integration Statistics"},
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Registered:*\n{stats.get('total_registered', 0)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Active:*\n{stats.get('total_active', 0)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Healthy Services:*\n{stats.get('healthy_count', 0)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Monitoring Tasks:*\n{stats.get('monitoring_tasks', 0)}",
                    },
                ],
            },
        ]

    async def _send_help_message(self, channel_id: str, client: AsyncWebClient):
        """Send help message with available commands"""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🤖 Sophia AI Bot Help"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Available Commands:*"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "• `/sophia dashboard` - View system dashboard\n• `/sophia query <question>` - Ask natural language questions\n• `/sophia search <params>` - Search conversations\n• `/sophia health` - Check system health\n• `/sophia deploy <target>` - Deploy to environment\n• `/sophia stats` - View integration statistics\n• `/sophia help` - Show this help message",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Examples:*\n• `/sophia query show me recent apartment deals`\n• `/sophia search company:PayReady from:2024-01-01`\n• `/sophia deploy vercel`",
                },
            },
        ]

        await client.chat_postMessage(
            channel=channel_id, text="🤖 Sophia AI Bot Help", blocks=blocks
        )

    async def start(self):
        """Start the Slack bot"""
        try:
            # Initialize integrations
            await integration_registry.initialize()

            # Start socket mode client
            self.socket_client = AsyncSocketModeClient(
                app_token=os.getenv("SLACK_APP_TOKEN"), web_client=self.client
            )

            handler = AsyncSocketModeHandler(self.app)
            await self.socket_client.socket_mode_request_listeners.append(
                handler.handle
            )

            logger.info("Starting Sophia Slack Bot...")
            await self.socket_client.connect()

            # Keep the bot running
            while True:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error starting Slack bot: {e}")
            raise

    async def stop(self):
        """Stop the Slack bot"""
        if self.socket_client:
            await self.socket_client.disconnect()
        logger.info("Sophia Slack Bot stopped")


# Bot instance
sophia_slack_bot = SophiaSlackBot()


async def main():
    """Main entry point"""
    await sophia_slack_bot.start()


if __name__ == "__main__":
    asyncio.run(main())
