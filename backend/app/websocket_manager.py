"""WebSocket Manager for Real-Time Dashboard Updates
Implements WebSocket connections for live data streaming to dashboards.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from backend.core.auto_esc_config import config
from backend.core.hierarchical_cache import hierarchical_cache
from backend.monitoring.observability import logger


class WebSocketClient(BaseModel):
    """WebSocket client connection"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    websocket: WebSocket
    subscriptions: Set[str] = Field(default_factory=set)
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_ping: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, any] = {}


class DashboardUpdate(BaseModel):
    """Dashboard update message"""

    type: str  # metric, alert, notification, data
    dashboard_id: Optional[str] = None
    widget_id: Optional[str] = None
    data: Dict[str, any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: str = "normal"  # low, normal, high, critical


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocketClient] = {}
        self.subscription_map: Dict[str, Set[str]] = {}  # subscription -> client_ids
        self._initialized = False
        self._redis_client = None
        self._update_queue: asyncio.Queue = asyncio.Queue()

    async def initialize(self):
        """Initialize WebSocket manager"""
        if self._initialized:
            return

        # Initialize Redis for pub/sub
        import aioredis

        self._redis_client = await aioredis.create_redis_pool(
            config.redis_url or "redis://localhost:6379", encoding="utf-8"
        )

        # Start background tasks
        asyncio.create_task(self._process_updates())
        asyncio.create_task(self._monitor_connections())
        asyncio.create_task(self._subscribe_to_streams())

        self._initialized = True
        logger.info("WebSocket manager initialized")

    async def connect(
        self, websocket: WebSocket, metadata: Optional[Dict] = None
    ) -> str:
        """Accept WebSocket connection"""
        await self.initialize()
        await websocket.accept()

        # Create client
        client = WebSocketClient(websocket=websocket, metadata=metadata or {})

        self.active_connections[client.id] = client

        # Send welcome message
        await self._send_to_client(
            client.id,
            {
                "type": "connection",
                "status": "connected",
                "client_id": client.id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        logger.info(f"WebSocket client connected: {client.id}")
        return client.id

    async def disconnect(self, client_id: str):
        """Handle WebSocket disconnection"""
        if client_id in self.active_connections:
            client = self.active_connections[client_id]

            # Remove from all subscriptions
            for subscription in list(client.subscriptions):
                await self.unsubscribe(client_id, subscription)

            # Remove client
            del self.active_connections[client_id]

            logger.info(f"WebSocket client disconnected: {client_id}")

    async def subscribe(self, client_id: str, subscription: str):
        """Subscribe client to updates"""
        if client_id not in self.active_connections:
            return

        client = self.active_connections[client_id]
        client.subscriptions.add(subscription)

        if subscription not in self.subscription_map:
            self.subscription_map[subscription] = set()
        self.subscription_map[subscription].add(client_id)

        # Send confirmation
        await self._send_to_client(
            client_id,
            {
                "type": "subscription",
                "action": "subscribed",
                "subscription": subscription,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        logger.info(f"Client {client_id} subscribed to {subscription}")

    async def unsubscribe(self, client_id: str, subscription: str):
        """Unsubscribe client from updates"""
        if client_id not in self.active_connections:
            return

        client = self.active_connections[client_id]
        client.subscriptions.discard(subscription)

        if subscription in self.subscription_map:
            self.subscription_map[subscription].discard(client_id)
            if not self.subscription_map[subscription]:
                del self.subscription_map[subscription]

        # Send confirmation
        await self._send_to_client(
            client_id,
            {
                "type": "subscription",
                "action": "unsubscribed",
                "subscription": subscription,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def broadcast_update(self, update: DashboardUpdate):
        """Broadcast update to relevant clients"""
        await self._update_queue.put(update)

    async def send_metric_update(
        self,
        metric_name: str,
        value: any,
        dashboard_id: Optional[str] = None,
        widget_id: Optional[str] = None,
    ):
        """Send metric update to dashboards"""
        update = DashboardUpdate(
            type="metric",
            dashboard_id=dashboard_id,
            widget_id=widget_id,
            data={
                "metric": metric_name,
                "value": value,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        await self.broadcast_update(update)

    async def send_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warning",
        data: Optional[Dict] = None,
    ):
        """Send alert to dashboards"""
        update = DashboardUpdate(
            type="alert",
            data={
                "alert_type": alert_type,
                "message": message,
                "severity": severity,
                "details": data or {},
                "timestamp": datetime.utcnow().isoformat(),
            },
            priority="high" if severity in ["error", "critical"] else "normal",
        )
        await self.broadcast_update(update)

    async def send_notification(
        self,
        title: str,
        message: str,
        notification_type: str = "info",
        actions: Optional[List[Dict]] = None,
    ):
        """Send notification to dashboards"""
        update = DashboardUpdate(
            type="notification",
            data={
                "title": title,
                "message": message,
                "type": notification_type,
                "actions": actions or [],
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        await self.broadcast_update(update)

    async def send_data_update(
        self,
        data_type: str,
        data: Dict,
        dashboard_id: Optional[str] = None,
        widget_id: Optional[str] = None,
    ):
        """Send data update to dashboards"""
        update = DashboardUpdate(
            type="data",
            dashboard_id=dashboard_id,
            widget_id=widget_id,
            data={
                "data_type": data_type,
                "payload": data,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        await self.broadcast_update(update)

    async def handle_client_message(self, client_id: str, message: Dict):
        """Handle incoming message from client"""
        if client_id not in self.active_connections:
            return

        message_type = message.get("type")

        if message_type == "ping":
            # Update last ping
            self.active_connections[client_id].last_ping = datetime.utcnow()
            await self._send_to_client(client_id, {"type": "pong"})

        elif message_type == "subscribe":
            subscriptions = message.get("subscriptions", [])
            for sub in subscriptions:
                await self.subscribe(client_id, sub)

        elif message_type == "unsubscribe":
            subscriptions = message.get("subscriptions", [])
            for sub in subscriptions:
                await self.unsubscribe(client_id, sub)

        elif message_type == "request":
            # Handle data requests
            await self._handle_data_request(client_id, message)

    async def _send_to_client(self, client_id: str, message: Dict):
        """Send message to specific client"""
        if client_id not in self.active_connections:
            return

        client = self.active_connections[client_id]
        try:
            await client.websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")
            await self.disconnect(client_id)

    async def _broadcast_to_subscription(self, subscription: str, message: Dict):
        """Broadcast message to all clients with subscription"""
        if subscription not in self.subscription_map:
            return

        # Get all client IDs with this subscription
        client_ids = list(self.subscription_map[subscription])

        # Send to each client
        tasks = []
        for client_id in client_ids:
            tasks.append(self._send_to_client(client_id, message))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_updates(self):
        """Process update queue"""
        while True:
            try:
                update = await self._update_queue.get()

                # Determine subscriptions to notify
                subscriptions = set()

                # Add type-based subscription
                subscriptions.add(f"updates:{update.type}")

                # Add dashboard-specific subscription
                if update.dashboard_id:
                    subscriptions.add(f"dashboard:{update.dashboard_id}")

                # Add widget-specific subscription
                if update.widget_id:
                    subscriptions.add(f"widget:{update.widget_id}")

                # Add priority-based subscription
                if update.priority in ["high", "critical"]:
                    subscriptions.add("updates:priority")

                # Broadcast to all relevant subscriptions
                message = update.dict()
                tasks = []
                for subscription in subscriptions:
                    tasks.append(self._broadcast_to_subscription(subscription, message))

                await asyncio.gather(*tasks)

            except Exception as e:
                logger.error(f"Error processing update: {e}")

    async def _monitor_connections(self):
        """Monitor WebSocket connections health"""
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds

            now = datetime.utcnow()
            disconnected = []

            for client_id, client in self.active_connections.items():
                # Check if client is still alive
                time_since_ping = (now - client.last_ping).total_seconds()

                if time_since_ping > 60:  # No ping for 60 seconds
                    disconnected.append(client_id)
                    continue

                # Send heartbeat
                try:
                    await client.websocket.send_json(
                        {"type": "heartbeat", "timestamp": now.isoformat()}
                    )
                except:
                    disconnected.append(client_id)

            # Disconnect dead clients
            for client_id in disconnected:
                await self.disconnect(client_id)

            # Log stats
            logger.info(
                f"WebSocket connections: {len(self.active_connections)} active, {len(disconnected)} disconnected"
            )

    async def _subscribe_to_streams(self):
        """Subscribe to real-time data streams"""
        if not self._redis_client:
            return

        # Subscribe to dashboard updates channel
        channel = await self._redis_client.subscribe("dashboard:updates")

        async for message in channel[0].iter():
            try:
                data = json.loads(message)

                # Convert to DashboardUpdate
                update = DashboardUpdate(type="data", data=data)

                await self.broadcast_update(update)

            except Exception as e:
                logger.error(f"Error processing stream message: {e}")

    async def _handle_data_request(self, client_id: str, message: Dict):
        """Handle data request from client"""
        request_type = message.get("request_type")
        request_id = message.get("request_id", str(uuid4()))

        try:
            if request_type == "metrics":
                # Get current metrics
                metrics = await self._get_current_metrics(message.get("metrics", []))
                await self._send_to_client(
                    client_id,
                    {"type": "response", "request_id": request_id, "data": metrics},
                )

            elif request_type == "historical":
                # Get historical data
                data = await self._get_historical_data(
                    message.get("metric"),
                    message.get("start_time"),
                    message.get("end_time"),
                )
                await self._send_to_client(
                    client_id,
                    {"type": "response", "request_id": request_id, "data": data},
                )

        except Exception as e:
            await self._send_to_client(
                client_id, {"type": "error", "request_id": request_id, "error": str(e)}
            )

    async def _get_current_metrics(self, metric_names: List[str]) -> Dict:
        """Get current metric values"""
        metrics = {}

        for metric in metric_names:
            # Try to get from cache first
            value = await hierarchical_cache.get(f"metric:{metric}")
            if value is not None:
                metrics[metric] = value

        return metrics

    async def _get_historical_data(
        self, metric: str, start_time: Optional[str], end_time: Optional[str]
    ) -> List[Dict]:
        """Get historical data for metric"""
        # This would query time-series database
        # Placeholder implementation
        return []

    async def get_connection_stats(self) -> Dict:
        """Get WebSocket connection statistics"""
        total_subscriptions = sum(
            len(client.subscriptions) for client in self.active_connections.values()
        )

        return {
            "active_connections": len(self.active_connections),
            "total_subscriptions": total_subscriptions,
            "subscription_topics": list(self.subscription_map.keys()),
            "clients": [
                {
                    "id": client_id,
                    "connected_at": client.connected_at.isoformat(),
                    "subscriptions": list(client.subscriptions),
                    "metadata": client.metadata,
                }
                for client_id, client in self.active_connections.items()
            ],
        }


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


# WebSocket endpoint handler
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for dashboard connections"""
    client_id = await websocket_manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            await websocket_manager.handle_client_message(client_id, data)

    except WebSocketDisconnect:
        await websocket_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket_manager.disconnect(client_id)
