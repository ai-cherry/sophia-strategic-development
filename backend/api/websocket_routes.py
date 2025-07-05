from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from backend.services.unified_chat_service import (
    AccessLevel,
    ChatContext,
    ChatRequest,
    UnifiedChatService,
    get_unified_chat_service,
)
from backend.websocket.connection_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    chat_service: UnifiedChatService = Depends(get_unified_chat_service),
):
    """
    Main WebSocket endpoint for unified chat.
    Handles all real-time chat communication.
    """
    await manager.connect(websocket, client_id)
    logger.info(f"WebSocket connected for client_id='{client_id}'")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                logger.debug(f"Received payload from '{client_id}': {payload}")

                # --- Default values for graceful handling ---
                message = payload.get("message", "")
                context_str = payload.get("search_context", "blended_intelligence")
                access_level_str = payload.get("access_level", "employee")
                session_id = payload.get("session_id")  # Can be None

                # --- Enum conversion with fallbacks ---
                try:
                    context = ChatContext(context_str)
                except ValueError:
                    logger.warning(
                        f"Invalid chat context '{context_str}', falling back to default."
                    )
                    context = ChatContext.BLENDED_INTELLIGENCE

                try:
                    access_level = AccessLevel(access_level_str)
                except ValueError:
                    logger.warning(
                        f"Invalid access level '{access_level_str}', falling back to default."
                    )
                    access_level = AccessLevel.EMPLOYEE

                # --- Create and Process Chat Request ---
                chat_request = ChatRequest(
                    message=message,
                    user_id=client_id,
                    session_id=session_id,
                    context=context,
                    access_level=access_level,
                    metadata={"source": "websocket"},
                )

                response = await chat_service.process_chat(chat_request)

                # --- Send response back to client ---
                await manager.send_to_client(
                    {
                        "type": "response",
                        "data": {
                            "response": response.response,
                            "sources": response.sources,
                            "suggestions": response.suggestions,
                            "timestamp": response.timestamp,
                        },
                    },
                    client_id,
                )

            except json.JSONDecodeError:
                logger.error("Received invalid JSON from WebSocket.")
                await manager.send_to_client(
                    {"type": "error", "message": "Invalid JSON format."}, client_id
                )
            except Exception as e:
                logger.exception(f"Error processing WebSocket message: {e}")
                await manager.send_to_client(
                    {
                        "type": "error",
                        "message": f"An unexpected error occurred: {str(e)}",
                    },
                    client_id,
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client_id='{client_id}'")
    finally:
        manager.disconnect(websocket, client_id)
