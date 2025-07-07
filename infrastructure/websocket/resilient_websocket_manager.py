from datetime import UTC, datetime

#!/usr/bin/env python3
"""
Resilient WebSocket Manager for Sophia AI
Production-grade WebSocket management with auto-reconnection and message queuing
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketState(Enum):
    """WebSocket connection states"""

    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"


@dataclass
class WebSocketConnection:
    """WebSocket connection information"""

    websocket: WebSocket
    client_id: str
    connected_at: datetime
    last_ping: datetime
    message_count: int = 0
    state: WebSocketState = WebSocketState.CONNECTED


class MessageQueue:
    """Message queue for offline clients"""

    def __init__(self):
        self.queues: dict[str, list[dict[str, Any]]] = {}
        self.max_queue_size = 100

    async def enqueue(self, client_id: str, message: dict[str, Any]):
        """Enqueue message for client"""
        if client_id not in self.queues:
            self.queues[client_id] = []

        # Add message with timestamp
        queued_message = {
            "message": message,
            "queued_at": datetime.now(UTC).isoformat(),
            "attempts": 0,
        }

        self.queues[client_id].append(queued_message)

        # Limit queue size
        if len(self.queues[client_id]) > self.max_queue_size:
            self.queues[client_id] = self.queues[client_id][-self.max_queue_size :]

        logger.debug(
            f"Queued message for {client_id}, queue size: {len(self.queues[client_id])}"
        )

    async def dequeue_all(self, client_id: str) -> list[dict[str, Any]]:
        """Get all queued messages for client"""
        messages = self.queues.get(client_id, [])
        if client_id in self.queues:
            del self.queues[client_id]
        return messages


class ResilientWebSocketManager:
    """Production-grade WebSocket management with auto-reconnection"""

    def __init__(self):
        self.connections: dict[str, WebSocketConnection] = {}
        self.message_queue = MessageQueue()
        self.monitoring_tasks: dict[str, asyncio.Task] = {}
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_queued": 0,
            "reconnections": 0,
        }

    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect WebSocket with comprehensive error handling"""
        try:
            await websocket.accept()

            connection_info = WebSocketConnection(
                websocket=websocket,
                client_id=client_id,
                connected_at=datetime.now(UTC),
                last_ping=datetime.now(UTC),
                state=WebSocketState.CONNECTED,
            )

            self.connections[client_id] = connection_info
            self.stats["total_connections"] += 1
            self.stats["active_connections"] = len(self.connections)

            # Start connection monitoring
            monitor_task = asyncio.create_task(self._monitor_connection(client_id))
            self.monitoring_tasks[client_id] = monitor_task

            # Send queued messages
            await self._send_queued_messages(client_id)

            logger.info(f"✅ WebSocket connected: {client_id}")

        except Exception as e:
            logger.error(f"❌ WebSocket connection failed for {client_id}: {e}")
            await self.disconnect(websocket, client_id)

    async def disconnect(self, websocket: WebSocket, client_id: str):
        """Disconnect WebSocket with cleanup"""
        try:
            if client_id in self.connections:
                del self.connections[client_id]
                self.stats["active_connections"] = len(self.connections)

            # Cancel monitoring task
            if client_id in self.monitoring_tasks:
                self.monitoring_tasks[client_id].cancel()
                del self.monitoring_tasks[client_id]

            # Close WebSocket if still open
            try:
                await websocket.close()
            except Exception:
                pass  # Already closed

            logger.info(f"🔌 WebSocket disconnected: {client_id}")

        except Exception as e:
            logger.error(f"Error during WebSocket disconnect for {client_id}: {e}")

    async def send_message(self, client_id: str, message: dict[str, Any]) -> bool:
        """Send message with automatic queuing on failure"""
        connection = self.connections.get(client_id)

        if not connection or connection.state == WebSocketState.DISCONNECTED:
            # Queue message for when client reconnects
            await self.message_queue.enqueue(client_id, message)
            self.stats["messages_queued"] += 1
            return False

        try:
            await connection.websocket.send_json(message)
            connection.message_count += 1
            connection.last_ping = datetime.now(UTC)
            self.stats["messages_sent"] += 1
            return True

        except WebSocketDisconnect:
            await self.disconnect(connection.websocket, client_id)
            await self.message_queue.enqueue(client_id, message)
            self.stats["messages_queued"] += 1
            return False
        except Exception as e:
            logger.error(f"WebSocket send error for {client_id}: {e}")
            await self.message_queue.enqueue(client_id, message)
            self.stats["messages_queued"] += 1
            return False

    async def broadcast_message(
        self, message: dict[str, Any], exclude_clients: list[str] = None
    ):
        """Broadcast message to all connected clients"""
        exclude_clients = exclude_clients or []

        tasks = []
        for client_id in self.connections:
            if client_id not in exclude_clients:
                task = asyncio.create_task(self.send_message(client_id, message))
                tasks.append(task)

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful_sends = sum(1 for result in results if result is True)
            logger.info(
                f"Broadcast message sent to {successful_sends}/{len(tasks)} clients"
            )

    async def _monitor_connection(self, client_id: str):
        """Monitor connection health with automatic recovery"""
        while client_id in self.connections:
            try:
                connection = self.connections[client_id]

                # Send ping to check connection
                ping_message = {
                    "type": "ping",
                    "timestamp": datetime.now(UTC).isoformat(),
                }

                try:
                    await connection.websocket.send_json(ping_message)
                    connection.last_ping = datetime.now(UTC)
                except Exception:
                    # Connection is dead, remove it
                    await self.disconnect(connection.websocket, client_id)
                    break

                # Check for stale connections (5 minutes without activity)
                if (datetime.now(UTC) - connection.last_ping).seconds > 300:
                    logger.warning(f"Stale WebSocket connection detected: {client_id}")
                    await self.disconnect(connection.websocket, client_id)
                    break

                # Wait for next check (30 seconds)
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Connection monitoring error for {client_id}: {e}")
                await self.disconnect(self.connections[client_id].websocket, client_id)
                break

    async def _send_queued_messages(self, client_id: str):
        """Send all queued messages to reconnected client"""
        queued_messages = await self.message_queue.dequeue_all(client_id)

        if queued_messages:
            logger.info(
                f"Sending {len(queued_messages)} queued messages to {client_id}"
            )

            for queued_msg in queued_messages:
                message = queued_msg["message"]
                message["_queued_at"] = queued_msg["queued_at"]
                message["_delivery_attempt"] = queued_msg["attempts"] + 1

                success = await self.send_message(client_id, message)
                if not success:
                    # If sending fails, re-queue remaining messages
                    remaining_messages = queued_messages[
                        queued_messages.index(queued_msg) :
                    ]
                    for remaining_msg in remaining_messages:
                        await self.message_queue.enqueue(
                            client_id, remaining_msg["message"]
                        )
                    break

    async def get_connection_stats(self) -> dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "stats": self.stats,
            "active_connections": {
                client_id: {
                    "connected_at": conn.connected_at.isoformat(),
                    "last_ping": conn.last_ping.isoformat(),
                    "message_count": conn.message_count,
                    "state": conn.state.value,
                }
                for client_id, conn in self.connections.items()
            },
            "queue_status": {
                "clients_with_queued_messages": len(self.message_queue.queues),
                "total_queued_messages": sum(
                    len(queue) for queue in self.message_queue.queues.values()
                ),
            },
        }


# Global instance
resilient_websocket_manager = ResilientWebSocketManager()
