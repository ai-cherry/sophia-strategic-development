#!/usr/bin/env python3
from backend.core.auto_esc_config import get_config_value

"""
Sophia AI Standalone Server for Live Testing
Bypasses existing backend import conflicts by running as standalone service
"""

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any
from uuid import uuid4

import snowflake.connector
import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from snowflake.connector import DictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CEO_ACCESS_TOKEN = os.getenv(
    "CEO_ACCESS_TOKEN",
    get_config_value(
        "ceo_access_token",
        get_config_value("ceo_access_token", "sophia_ceo_access_2024"),
    ),
)
ADMIN_USER_ID = "ceo_user"

# Snowflake Configuration
SNOWFLAKE_CONFIG = {
    "account": "ZNB04675",
    "user": "SCOOBYJAVA15",
    "password": os.getenv("SNOWFLAKE_PASSWORD", ""),
    "role": "ACCOUNTADMIN",
    "database": "SOPHIA_AI_PROD",
    "schema": "UNIVERSAL_CHAT",
    "warehouse": "SOPHIA_AI_WH",
}


# Models
class UploadResponse(BaseModel):
    entry_id: str
    title: str
    status: str
    message: str
    processing_time: float


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    category_filter: str | None = None


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    use_knowledge: bool = True


# Authentication
security = HTTPBearer()


async def authenticate_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if credentials.credentials == CEO_ACCESS_TOKEN:
        return ADMIN_USER_ID
    raise HTTPException(status_code=401, detail="Invalid authentication token")


# Database Service
class SnowflakeService:
    def __init__(self):
        self.connection = None

    async def connect(self):
        try:
            self.connection = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
            logger.info("✅ Connected to Snowflake")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Snowflake: {e}")
            raise

    async def disconnect(self):
        if self.connection:
            self.connection.close()

    async def execute_query(
        self, query: str, params: tuple | None = None
    ) -> list[dict[str, Any]]:
        try:
            cursor = self.connection.cursor(DictCursor)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    async def upload_knowledge_entry(
        self, title: str, content: str, category_id: str = "general"
    ) -> str:
        entry_id = str(uuid4())

        # Ensure category exists
        check_query = (
            "SELECT CATEGORY_ID FROM KNOWLEDGE_CATEGORIES WHERE CATEGORY_ID = %s"
        )
        existing = await self.execute_query(check_query, (category_id,))

        if not existing:
            create_cat_query = """
            INSERT INTO KNOWLEDGE_CATEGORIES (CATEGORY_ID, CATEGORY_NAME, DESCRIPTION, CREATED_AT)
            VALUES (%s, %s, %s, %s)
            """
            await self.execute_query(
                create_cat_query,
                (
                    category_id,
                    category_id.title(),
                    "Auto-created category",
                    datetime.now(),
                ),
            )

        # Insert knowledge entry
        insert_query = """
        INSERT INTO KNOWLEDGE_BASE_ENTRIES
        (ENTRY_ID, TITLE, CONTENT, CATEGORY_ID, STATUS, METADATA, CREATED_AT, UPDATED_AT)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        metadata = {"auto_created": True, "source": "standalone_server"}
        now = datetime.now()

        await self.execute_query(
            insert_query,
            (
                entry_id,
                title,
                content,
                category_id,
                "published",
                json.dumps(metadata),
                now,
                now,
            ),
        )

        return entry_id

    async def search_knowledge(
        self, query: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        search_query = """
        SELECT
            k.ENTRY_ID, k.TITLE, k.CONTENT, k.CATEGORY_ID, c.CATEGORY_NAME,
            k.CREATED_AT, k.UPDATED_AT
        FROM KNOWLEDGE_BASE_ENTRIES k
        JOIN KNOWLEDGE_CATEGORIES c ON k.CATEGORY_ID = c.CATEGORY_ID
        WHERE k.STATUS = 'published'
        AND (UPPER(k.TITLE) LIKE UPPER('%' || %s || '%')
             OR UPPER(k.CONTENT) LIKE UPPER('%' || %s || '%'))
        ORDER BY k.UPDATED_AT DESC
        LIMIT %s
        """

        results = await self.execute_query(search_query, (query, query, limit))
        return results

    async def create_session(self, user_id: str, title: str) -> str:
        session_id = str(uuid4())
        query = """
        INSERT INTO CONVERSATION_SESSIONS (SESSION_ID, USER_ID, TITLE, CREATED_AT, UPDATED_AT)
        VALUES (%s, %s, %s, %s, %s)
        """
        now = datetime.now()
        await self.execute_query(query, (session_id, user_id, title, now, now))
        return session_id

    async def save_message(
        self, session_id: str, user_id: str, content: str, message_type: str
    ) -> str:
        message_id = str(uuid4())
        query = """
        INSERT INTO CONVERSATION_MESSAGES (MESSAGE_ID, SESSION_ID, USER_ID, CONTENT, MESSAGE_TYPE, CREATED_AT)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        await self.execute_query(
            query,
            (message_id, session_id, user_id, content, message_type, datetime.now()),
        )
        return message_id

    async def generate_ai_response(
        self, query: str, context: list[dict[str, Any]]
    ) -> str:
        if context:
            context_text = "\n".join(
                [
                    f"• {item['TITLE']}: {item['CONTENT'][:200]}..."
                    for item in context[:3]
                ]
            )
            response = f"""Based on our knowledge base, here's what I found relevant to your query "{query}":

{context_text}

I'm here to help you with any questions about Pay Ready's business information. Feel free to ask for more specific details or upload additional documents to expand our knowledge base."""
        else:
            response = f"""I understand you're asking about "{query}". While I don't have specific information about this in our current knowledge base, I'm ready to help once you upload relevant documents.

You can upload customer lists, product descriptions, employee information, or any other business documents through the API endpoints. This will help me provide more accurate and relevant responses to your questions."""

        return response


# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected")

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)


# Initialize services
snowflake_service = SnowflakeService()
manager = ConnectionManager()


# Lifespan manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await snowflake_service.connect()
    logger.info("🚀 Sophia AI Standalone Server started successfully")
    yield
    # Shutdown
    await snowflake_service.disconnect()
    logger.info("Sophia AI Standalone Server shut down")


# Create FastAPI app
app = FastAPI(
    title="Sophia AI Standalone Server",
    description="Live testing server for Sophia AI knowledge management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/")
async def root():
    return {
        "message": "Sophia AI Standalone Server - Live Testing Ready",
        "version": "1.0.0",
        "services": {
            "knowledge_upload": "/upload",
            "knowledge_search": "/search",
            "chat": "/chat",
            "websocket": "/ws/chat/{user_id}",
            "health": "/health",
        },
        "documentation": "/docs",
    }


@app.get("/health")
async def health_check():
    try:
        await snowflake_service.execute_query("SELECT 1 as test")
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {"snowflake": "connected", "websocket": "operational"},
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@app.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    category_id: str = Form("general"),
    user_id: str = Depends(authenticate_user),
):
    start_time = datetime.now()

    try:
        # Read file content
        file_content = await file.read()
        content = file_content.decode("utf-8", errors="ignore")

        # Add file info to content
        full_content = f"File: {file.filename}\nType: {file.content_type}\nSize: {len(file_content)} bytes\n\nContent:\n{content}"

        # Upload to knowledge base
        entry_id = await snowflake_service.upload_knowledge_entry(
            title, full_content, category_id
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        return UploadResponse(
            entry_id=entry_id,
            title=title,
            status="success",
            message=f"File '{file.filename}' uploaded successfully",
            processing_time=processing_time,
        )

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"Upload failed: {e}")
        return UploadResponse(
            entry_id="",
            title=title,
            status="error",
            message=f"Upload failed: {str(e)}",
            processing_time=processing_time,
        )


@app.post("/search")
async def search_knowledge(
    request: SearchRequest, user_id: str = Depends(authenticate_user)
):
    try:
        results = await snowflake_service.search_knowledge(request.query, request.limit)

        return {
            "query": request.query,
            "results": [
                {
                    "entry_id": row["ENTRY_ID"],
                    "title": row["TITLE"],
                    "content": (
                        row["CONTENT"][:500] + "..."
                        if len(row["CONTENT"]) > 500
                        else row["CONTENT"]
                    ),
                    "category_id": row["CATEGORY_ID"],
                    "category_name": row["CATEGORY_NAME"],
                    "created_at": (
                        row["CREATED_AT"].isoformat() if row["CREATED_AT"] else None
                    ),
                }
                for row in results
            ],
            "total_results": len(results),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/chat")
async def chat_with_knowledge(
    request: ChatRequest, user_id: str = Depends(authenticate_user)
):
    try:
        session_id = request.session_id

        # Create session if not provided
        if not session_id:
            session_id = await snowflake_service.create_session(
                user_id=user_id,
                title=f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            )

        # Save user message
        user_message_id = await snowflake_service.save_message(
            session_id, user_id, request.message, "user"
        )

        # Search knowledge if requested
        knowledge_results = []
        if request.use_knowledge:
            knowledge_results = await snowflake_service.search_knowledge(
                request.message, 5
            )

        # Generate AI response
        ai_response = await snowflake_service.generate_ai_response(
            request.message, knowledge_results
        )

        # Save AI response
        ai_message_id = await snowflake_service.save_message(
            session_id, "system", ai_response, "assistant"
        )

        return {
            "session_id": session_id,
            "user_message_id": user_message_id,
            "ai_message_id": ai_message_id,
            "response": ai_response,
            "knowledge_sources": [
                {"title": row["TITLE"], "category": row["CATEGORY_NAME"]}
                for row in knowledge_results[:3]
            ],
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            query = message_data.get("content", "")
            session_id = message_data.get("session_id")

            if not session_id:
                session_id = await snowflake_service.create_session(
                    user_id=user_id,
                    title=f"WebSocket Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                )

            # Save user message
            await snowflake_service.save_message(session_id, user_id, query, "user")

            # Search knowledge
            search_results = await snowflake_service.search_knowledge(query, 3)

            # Generate response
            ai_response = await snowflake_service.generate_ai_response(
                query, search_results
            )

            # Save AI response
            await snowflake_service.save_message(
                session_id, "system", ai_response, "assistant"
            )

            # Send response
            response_data = {
                "message_id": str(uuid4()),
                "session_id": session_id,
                "content": ai_response,
                "message_type": "assistant",
                "timestamp": datetime.now().isoformat(),
                "sources": [
                    {"title": r["TITLE"], "category": r["CATEGORY_NAME"]}
                    for r in search_results
                ],
            }

            await manager.send_personal_message(json.dumps(response_data), user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)


if __name__ == "__main__":
    logger.info("🚀 Starting Sophia AI Standalone Server...")
    logger.info("📍 Main API: http://localhost:8000")
    logger.info("📍 Documentation: http://localhost:8000/docs")
    logger.info("🔑 CEO Access Token: sophia_ceo_access_2024")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=False)
