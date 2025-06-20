from fastapi import WebSocket, WebSocketDisconnect

from backend.app.routes import (executive_routes, retool_api_routes,
                                system_intel_routes)
from backend.app.websockets import manager

app.include_router(executive_routes.router, prefix="/executive", tags=["Executive Intelligence"])
app.include_router(retool_api_routes.router, prefix="/api", tags=["Retool API - Simplified Auth"])
app.include_router(system_intel_routes.router, prefix="/api", tags=["System Intelligence"])

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # The server can listen for messages from the client if needed
            data = await websocket.receive_text()
            # For now, we just echo it back or handle it
            await manager.send_personal_message(f"Message text was: {data}", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

@app.get("/", tags=["Root"])
# ... existing code ... 