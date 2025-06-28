#!/usr/bin/env python3
"""
Enhanced Slack Integration Service
CRITICAL: Migrates from deprecated RTM API to Events API/Socket Mode
Addresses: Critical Priority Item - Prevent service disruption
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.async_client import AsyncSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

logger = logging.getLogger(__name__)

@dataclass
class SlackMessage:
    """Enhanced Slack message structure"""
    channel_id: str
    user_id: str
    text: str
    timestamp: str
    thread_ts: Optional[str] = None
    message_type: str = "message"
    subtype: Optional[str] = None
    attachments: List[Dict] = None
    blocks: List[Dict] = None
    metadata: Dict[str, Any] = None

@dataclass
class SlackAnalytics:
    """Slack analytics data structure"""
    channel_id: str
    channel_name: str
    message_count: int
    user_count: int
    sentiment_score: float
    topics: List[str]
    action_items: List[str]
    decisions: List[str]
    business_impact_score: float
    engagement_score: float

class EnhancedSlackIntegrationService:
    """
    Enhanced Slack Integration Service with Events API/Socket Mode
    REPLACES deprecated RTM API to prevent service disruption
    """
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.bot_token = config.get("SLACK_BOT_TOKEN")
        self.app_token = config.get("SLACK_APP_TOKEN")  # For Socket Mode
        self.signing_secret = config.get("SLACK_SIGNING_SECRET")
        
        # Initialize clients with modern APIs
        self.web_client = AsyncWebClient(token=self.bot_token)
        self.socket_client = None
        
        # Event handlers
        self.message_handlers: List[Callable] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Analytics and monitoring
        self.analytics_buffer: List[SlackAnalytics] = []
        self.is_connected = False
        self.connection_health = {"status": "disconnected", "last_ping": None}
        
        # Real-time processing queues
        self.message_queue = asyncio.Queue()
        self.analytics_queue = asyncio.Queue()
        
        logger.info("✅ Enhanced Slack Integration Service initialized with Events API/Socket Mode")

    async def initialize(self):
        """Initialize Socket Mode connection (replaces RTM API)"""
        try:
            if not self.app_token:
                raise ValueError("SLACK_APP_TOKEN required for Socket Mode")
            
            # Initialize Socket Mode client
            self.socket_client = AsyncSocketModeClient(
                app_token=self.app_token,
                web_client=self.web_client
            )
            
            # Register event handlers
            self._register_socket_mode_handlers()
            
            # Test connection
            auth_response = await self.web_client.auth_test()
            if not auth_response["ok"]:
                raise Exception(f"Slack auth failed: {auth_response.get('error')}")
            
            logger.info(f"✅ Authenticated as {auth_response['user']} in team {auth_response['team']}")
            
            # Start background processors
            asyncio.create_task(self._process_message_queue())
            asyncio.create_task(self._process_analytics_queue())
            asyncio.create_task(self._health_monitor())
            
            self.is_connected = True
            logger.info("✅ Enhanced Slack service initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Slack service: {e}")
            raise

    def _register_socket_mode_handlers(self):
        """Register Socket Mode event handlers (replaces RTM handlers)"""
        
        @self.socket_client.socket_mode_request_listeners.append
        async def handle_socket_mode_request(client: AsyncSocketModeClient, req: SocketModeRequest):
            """Handle all Socket Mode requests"""
            try:
                # Acknowledge the request immediately
                response = SocketModeResponse(envelope_id=req.envelope_id)
                await client.send_socket_mode_response(response)
                
                # Process the event
                if req.type == "events_api":
                    await self._handle_events_api_event(req.payload)
                elif req.type == "interactive":
                    await self._handle_interactive_event(req.payload)
                elif req.type == "slash_commands":
                    await self._handle_slash_command(req.payload)
                
            except Exception as e:
                logger.error(f"Error handling socket mode request: {e}")

    async def _handle_events_api_event(self, payload: Dict[str, Any]):
        """Handle Events API events (modern replacement for RTM)"""
        event = payload.get("event", {})
        event_type = event.get("type")
        
        if event_type == "message":
            await self._handle_message_event(event)
        elif event_type == "channel_created":
            await self._handle_channel_event(event)
        elif event_type == "member_joined_channel":
            await self._handle_member_event(event)
        elif event_type == "reaction_added":
            await self._handle_reaction_event(event)
        
        # Call registered event handlers
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")

    async def _handle_message_event(self, event: Dict[str, Any]):
        """Enhanced message handling with analytics"""
        try:
            # Skip bot messages and message changes
            if event.get("subtype") in ["bot_message", "message_changed", "message_deleted"]:
                return
            
            # Create enhanced message object
            message = SlackMessage(
                channel_id=event.get("channel"),
                user_id=event.get("user"),
                text=event.get("text", ""),
                timestamp=event.get("ts"),
                thread_ts=event.get("thread_ts"),
                message_type=event.get("type", "message"),
                subtype=event.get("subtype"),
                attachments=event.get("attachments", []),
                blocks=event.get("blocks", []),
                metadata={
                    "event_ts": event.get("event_ts"),
                    "team": event.get("team"),
                    "channel_type": event.get("channel_type")
                }
            )
            
            # Add to processing queue
            await self.message_queue.put(message)
            
            # Call registered message handlers
            for handler in self.message_handlers:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Message handler error: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling message event: {e}")

    async def _process_message_queue(self):
        """Process messages for analytics and intelligence"""
        while True:
            try:
                # Wait for messages with timeout
                try:
                    message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Enhanced message processing
                await self._analyze_message(message)
                await self._extract_business_intelligence(message)
                await self._update_user_analytics(message)
                
                # Mark task as done
                self.message_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in message queue processing: {e}")
                await asyncio.sleep(1)

    async def _analyze_message(self, message: SlackMessage):
        """Analyze message for sentiment, topics, and business intelligence"""
        try:
            # Get channel info for context
            channel_info = await self._get_channel_info(message.channel_id)
            
            # Sentiment analysis (placeholder - would integrate with AI service)
            sentiment_score = await self._calculate_sentiment(message.text)
            
            # Topic extraction
            topics = await self._extract_topics(message.text)
            
            # Action item detection
            action_items = await self._detect_action_items(message.text)
            
            # Decision tracking
            decisions = await self._detect_decisions(message.text)
            
            # Business impact assessment
            business_impact = await self._assess_business_impact(message, channel_info)
            
            # Store analytics
            analytics = SlackAnalytics(
                channel_id=message.channel_id,
                channel_name=channel_info.get("name", "unknown"),
                message_count=1,
                user_count=1,
                sentiment_score=sentiment_score,
                topics=topics,
                action_items=action_items,
                decisions=decisions,
                business_impact_score=business_impact,
                engagement_score=1.0
            )
            
            await self.analytics_queue.put(analytics)
            
        except Exception as e:
            logger.error(f"Error analyzing message: {e}")

    async def _extract_business_intelligence(self, message: SlackMessage):
        """Extract business intelligence from messages"""
        try:
            text = message.text.lower()
            
            # Customer mentions
            customer_keywords = ["customer", "client", "prospect", "lead"]
            if any(keyword in text for keyword in customer_keywords):
                await self._track_customer_mention(message)
            
            # Product discussions
            product_keywords = ["product", "feature", "release", "roadmap"]
            if any(keyword in text for keyword in product_keywords):
                await self._track_product_discussion(message)
            
            # Sales activities
            sales_keywords = ["deal", "contract", "proposal", "revenue", "sales"]
            if any(keyword in text for keyword in sales_keywords):
                await self._track_sales_activity(message)
            
            # Support issues
            support_keywords = ["bug", "issue", "problem", "error", "fix"]
            if any(keyword in text for keyword in support_keywords):
                await self._track_support_issue(message)
                
        except Exception as e:
            logger.error(f"Error extracting business intelligence: {e}")

    async def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score (-1 to 1)"""
        # Placeholder implementation - would integrate with AI service
        positive_words = ["great", "excellent", "awesome", "good", "love", "happy"]
        negative_words = ["bad", "terrible", "awful", "hate", "angry", "frustrated"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)

    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from message text"""
        # Placeholder implementation - would use NLP service
        business_topics = {
            "sales": ["sales", "revenue", "deal", "contract", "proposal"],
            "product": ["product", "feature", "development", "roadmap", "release"],
            "support": ["support", "bug", "issue", "problem", "customer service"],
            "marketing": ["marketing", "campaign", "brand", "promotion", "advertising"],
            "finance": ["finance", "budget", "cost", "pricing", "investment"]
        }
        
        text_lower = text.lower()
        detected_topics = []
        
        for topic, keywords in business_topics.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics

    async def _detect_action_items(self, text: str) -> List[str]:
        """Detect action items in messages"""
        action_patterns = [
            "todo:", "action:", "need to", "should", "will", "plan to",
            "follow up", "next steps", "deliverable", "deadline"
        ]
        
        text_lower = text.lower()
        actions = []
        
        for pattern in action_patterns:
            if pattern in text_lower:
                # Extract the sentence containing the action
                sentences = text.split('.')
                for sentence in sentences:
                    if pattern in sentence.lower():
                        actions.append(sentence.strip())
                        break
        
        return actions

    async def _detect_decisions(self, text: str) -> List[str]:
        """Detect decisions made in messages"""
        decision_patterns = [
            "decided", "decision", "agreed", "approved", "rejected",
            "go with", "choose", "selected", "final answer"
        ]
        
        text_lower = text.lower()
        decisions = []
        
        for pattern in decision_patterns:
            if pattern in text_lower:
                sentences = text.split('.')
                for sentence in sentences:
                    if pattern in sentence.lower():
                        decisions.append(sentence.strip())
                        break
        
        return decisions

    async def _assess_business_impact(self, message: SlackMessage, channel_info: Dict) -> float:
        """Assess business impact of message content"""
        impact_score = 0.0
        text_lower = message.text.lower()
        
        # Channel importance
        important_channels = ["general", "leadership", "sales", "product", "executives"]
        if any(channel in channel_info.get("name", "").lower() for channel in important_channels):
            impact_score += 0.3
        
        # Content importance
        high_impact_keywords = [
            "revenue", "customer", "deal", "contract", "crisis", "urgent",
            "launch", "release", "partnership", "acquisition", "strategy"
        ]
        keyword_count = sum(1 for keyword in high_impact_keywords if keyword in text_lower)
        impact_score += min(keyword_count * 0.2, 0.7)
        
        return min(impact_score, 1.0)

    async def start_socket_connection(self):
        """Start Socket Mode connection (replaces RTM connection)"""
        try:
            if not self.socket_client:
                raise Exception("Socket client not initialized")
            
            logger.info("🔌 Starting Socket Mode connection...")
            await self.socket_client.connect()
            
            self.is_connected = True
            self.connection_health["status"] = "connected"
            self.connection_health["last_ping"] = datetime.now()
            
            logger.info("✅ Socket Mode connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Socket Mode connection: {e}")
            self.is_connected = False
            raise

    async def stop_connection(self):
        """Stop Socket Mode connection"""
        try:
            if self.socket_client:
                await self.socket_client.disconnect()
            
            self.is_connected = False
            self.connection_health["status"] = "disconnected"
            
            logger.info("🔌 Socket Mode connection stopped")
            
        except Exception as e:
            logger.error(f"Error stopping connection: {e}")

    async def _health_monitor(self):
        """Monitor connection health and reconnect if needed"""
        while True:
            try:
                if self.is_connected:
                    # Ping to test connection
                    try:
                        await self.web_client.api_test()
                        self.connection_health["last_ping"] = datetime.now()
                        self.connection_health["status"] = "healthy"
                    except Exception as e:
                        logger.warning(f"Health check failed: {e}")
                        self.connection_health["status"] = "unhealthy"
                        
                        # Attempt reconnection
                        try:
                            await self.stop_connection()
                            await asyncio.sleep(5)
                            await self.start_socket_connection()
                        except Exception as reconnect_error:
                            logger.error(f"Reconnection failed: {reconnect_error}")
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(60)

    async def send_message(self, channel_id: str, text: str, **kwargs) -> Dict[str, Any]:
        """Send message using Web API"""
        try:
            response = await self.web_client.chat_postMessage(
                channel=channel_id,
                text=text,
                **kwargs
            )
            
            if response["ok"]:
                logger.info(f"✅ Message sent to {channel_id}")
                return response
            else:
                logger.error(f"❌ Failed to send message: {response.get('error')}")
                return response
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    async def get_channel_analytics(self, channel_id: str, days_back: int = 7) -> SlackAnalytics:
        """Get comprehensive channel analytics"""
        try:
            # Get channel info
            channel_info = await self._get_channel_info(channel_id)
            
            # Get channel history
            oldest = (datetime.now() - timedelta(days=days_back)).timestamp()
            history = await self.web_client.conversations_history(
                channel=channel_id,
                oldest=oldest,
                limit=1000
            )
            
            if not history["ok"]:
                raise Exception(f"Failed to get channel history: {history.get('error')}")
            
            messages = history["messages"]
            
            # Analyze messages
            total_messages = len(messages)
            unique_users = len(set(msg.get("user") for msg in messages if msg.get("user")))
            
            # Calculate metrics
            sentiments = []
            all_topics = []
            all_actions = []
            all_decisions = []
            
            for msg in messages:
                text = msg.get("text", "")
                if text:
                    sentiments.append(await self._calculate_sentiment(text))
                    all_topics.extend(await self._extract_topics(text))
                    all_actions.extend(await self._detect_action_items(text))
                    all_decisions.extend(await self._detect_decisions(text))
            
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
            engagement_score = min(total_messages / (days_back * 10), 1.0)  # Normalize
            
            return SlackAnalytics(
                channel_id=channel_id,
                channel_name=channel_info.get("name", "unknown"),
                message_count=total_messages,
                user_count=unique_users,
                sentiment_score=avg_sentiment,
                topics=list(set(all_topics)),
                action_items=all_actions,
                decisions=all_decisions,
                business_impact_score=await self._calculate_channel_business_impact(messages),
                engagement_score=engagement_score
            )
            
        except Exception as e:
            logger.error(f"Error getting channel analytics: {e}")
            raise

    async def _get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Get channel information"""
        try:
            response = await self.web_client.conversations_info(channel=channel_id)
            if response["ok"]:
                return response["channel"]
            else:
                logger.warning(f"Could not get channel info for {channel_id}")
                return {"name": "unknown", "id": channel_id}
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return {"name": "unknown", "id": channel_id}

    async def _calculate_channel_business_impact(self, messages: List[Dict]) -> float:
        """Calculate overall business impact for channel"""
        if not messages:
            return 0.0
        
        total_impact = 0.0
        for msg in messages:
            text = msg.get("text", "")
            if text:
                # Simplified business impact calculation
                impact_keywords = ["revenue", "customer", "deal", "launch", "crisis", "urgent"]
                keyword_count = sum(1 for keyword in impact_keywords if keyword.lower() in text.lower())
                total_impact += min(keyword_count * 0.1, 0.5)
        
        return min(total_impact / len(messages), 1.0)

    def register_message_handler(self, handler: Callable):
        """Register a message handler"""
        self.message_handlers.append(handler)

    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            "is_connected": self.is_connected,
            "health": self.connection_health,
            "api_type": "Events API + Socket Mode",
            "deprecated_api": "RTM API (migrated)",
            "message_queue_size": self.message_queue.qsize(),
            "analytics_queue_size": self.analytics_queue.qsize()
        }

# Factory function for easy initialization
async def create_enhanced_slack_service(config: Dict[str, str]) -> EnhancedSlackIntegrationService:
    """Create and initialize enhanced Slack service"""
    service = EnhancedSlackIntegrationService(config)
    await service.initialize()
    return service 
