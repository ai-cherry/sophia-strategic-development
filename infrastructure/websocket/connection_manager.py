from __future__ import annotations

import asyncio
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, set[WebSocket]] = defaultdict(set)
        self.logger = logger.bind(component="WebSocketConnectionManager")

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id].add(websocket)
        self.logger.info(f"New WebSocket connection for client_id='{client_id}'")

    def disconnect(self, websocket: WebSocket, client_id: str):
        """Disconnect a WebSocket."""
        if websocket in self.active_connections.get(client_id, set()):
            self.active_connections[client_id].remove(websocket)
            self.logger.info(f"WebSocket connection closed for client_id='{client_id}'")
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]

    async def send_to_client(self, message: str | dict, client_id: str):
        """Send a message to all connections for a specific client."""
        disconnected_sockets = []
        for websocket in self.active_connections.get(client_id, set()):
            try:
                if isinstance(message, dict):
                    await websocket.send_json(message)
                else:
                    await websocket.send_text(message)
            except (WebSocketDisconnect, RuntimeError):
                disconnected_sockets.append(websocket)

        for websocket in disconnected_sockets:
            self.disconnect(websocket, client_id)

    async def broadcast(self, message: str | dict):
        """Send a message to all connected clients."""
        all_sockets = [
            ws for ws_set in self.active_connections.values() for ws in ws_set
        ]
        tasks = []
        for websocket in all_sockets:
            try:
                if isinstance(message, dict):
                    tasks.append(websocket.send_json(message))
                else:
                    tasks.append(websocket.send_text(message))
            except (WebSocketDisconnect, RuntimeError):
                # Handle disconnection during broadcast, though less common
                pass
        await asyncio.gather(*tasks, return_exceptions=True)

    def get_active_clients(self) -> list[str]:
        """Get a list of all active client IDs."""
        return list(self.active_connections.keys())

# Singleton instance
manager = ConnectionManager()
