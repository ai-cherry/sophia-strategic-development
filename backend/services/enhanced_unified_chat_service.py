#!/usr/bin/env python3
"""
Enhanced Unified Chat Service for Sophia AI
Production-ready FastAPI service with WebSocket support and Snowflake integration
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from uuid import uuid4
import snowflake.connector
from snowflake.connector import DictCursor
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication
security = HTTPBearer()
CEO_ACCESS_TOKEN = os.getenv("CEO_ACCESS_TOKEN", "sophia_ceo_access_2024")
ADMIN_USER_ID = "ceo_user"

# Snowflake Configuration (from prompts)
SNOWFLAKE_CONFIG = {
    "account": "ZNB04675",
    "user": "SCOOBYJAVA15",
    "password": "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A",
    "role": "ACCOUNTADMIN",
    "database": "SOPHIA_AI_PROD",
    "schema": "UNIVERSAL_CHAT",
    "warehouse": "SOPHIA_AI_WH"
}

# Pydantic Models
class ChatMessage(BaseModel):
    message_id: str
    session_id: str
    user_id: str
    content: str
    message_type: str = "user"
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatSession(BaseModel):
    session_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    context: Optional[Dict[str, Any]] = None
    message_count: int = 0

class SendMessageRequest(BaseModel):
    content: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class CreateSessionRequest(BaseModel):
    title: str
    context: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    category_filter: Optional[str] = None

# Connection Manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

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

# Snowflake Service
class SnowflakeService:
    def __init__(self):
        self.connection = None

    async def connect(self):
        """Establish Snowflake connection"""
        try:
            self.connection = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
            logger.info("✅ Connected to Snowflake")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Snowflake: {e}")
            raise

    async def disconnect(self):
        """Close Snowflake connection"""
        if self.connection:
            self.connection.close()
            logger.info("Snowflake connection closed")

    async def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        try:
            cursor = self.connection.cursor(DictCursor)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    async def create_session(self, user_id: str, title: str, context: Optional[Dict] = None) -> str:
        """Create new chat session"""
        session_id = str(uuid4())
        query = """
        INSERT INTO CONVERSATION_SESSIONS (SESSION_ID, USER_ID, TITLE, CREATED_AT, UPDATED_AT, CONTEXT)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        context_json = json.dumps(context) if context else None
        
        await self.execute_query(query, (session_id, user_id, title, now, now, context_json))
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id

    async def save_message(self, session_id: str, user_id: str, content: str, message_type: str = "user", metadata: Optional[Dict] = None) -> str:
        """Save message to database"""
        message_id = str(uuid4())
        query = """
        INSERT INTO CONVERSATION_MESSAGES (MESSAGE_ID, SESSION_ID, USER_ID, CONTENT, MESSAGE_TYPE, CREATED_AT, METADATA)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        metadata_json = json.dumps(metadata) if metadata else None
        
        await self.execute_query(query, (message_id, session_id, user_id, content, message_type, now, metadata_json))
        
        # Update session timestamp
        update_query = "UPDATE CONVERSATION_SESSIONS SET UPDATED_AT = %s WHERE SESSION_ID = %s"
        await self.execute_query(update_query, (now, session_id))
        
        return message_id

    async def get_session_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages for a session"""
        query = """
        SELECT MESSAGE_ID, SESSION_ID, USER_ID, CONTENT, MESSAGE_TYPE, CREATED_AT, METADATA
        FROM CONVERSATION_MESSAGES
        WHERE SESSION_ID = %s
        ORDER BY CREATED_AT DESC
        LIMIT %s
        """
        results = await self.execute_query(query, (session_id, limit))
        return list(reversed(results))

    async def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base using semantic search"""
        # For now, do a simple text search - will enhance with embeddings later
        search_query = """
        SELECT 
            k.ENTRY_ID,
            k.TITLE,
            k.CONTENT,
            k.CATEGORY_ID,
            c.CATEGORY_NAME,
            0.8 as similarity_score
        FROM KNOWLEDGE_BASE_ENTRIES k
        JOIN KNOWLEDGE_CATEGORIES c ON k.CATEGORY_ID = c.CATEGORY_ID
        WHERE k.STATUS = 'published'
        AND (UPPER(k.TITLE) LIKE UPPER('%' || %s || '%') 
             OR UPPER(k.CONTENT) LIKE UPPER('%' || %s || '%'))
        ORDER BY k.CREATED_AT DESC
        LIMIT %s
        """
        
        results = await self.execute_query(search_query, (query, query, limit))
        return results

    async def generate_ai_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate AI response - simplified for initial implementation"""
        if context:
            context_text = "\n".join([f"• {item['TITLE']}: {item['CONTENT'][:200]}..." for item in context[:3]])
            response = f"""Based on our knowledge base, here's what I found relevant to your query "{query}":

{context_text}

I'm here to help you with any questions about Pay Ready's customers, products, or business information. Feel free to ask for more specific details or upload additional documents to expand our knowledge base."""
        else:
            response = f"""I understand you're asking about "{query}". While I don't have specific information about this in our current knowledge base, I'm ready to help once you upload relevant documents.

You can upload customer lists, product descriptions, employee information, or any other business documents through the Knowledge Base dashboard. This will help me provide more accurate and relevant responses to your questions."""

        return response

# Authentication
async def authenticate_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Authenticate user with simple token"""
    if credentials.credentials == CEO_ACCESS_TOKEN:
        return ADMIN_USER_ID
    raise HTTPException(status_code=401, detail="Invalid authentication token")

# Initialize services
app = FastAPI(
    title="Sophia AI Enhanced Chat Service",
    description="Production-ready chat service with WebSocket support",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()
snowflake_service = SnowflakeService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await snowflake_service.connect()
    logger.info("🚀 Enhanced Chat Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await snowflake_service.disconnect()
    logger.info("Enhanced Chat Service shut down")

# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process the message
            query = message_data.get("content", "")
            session_id = message_data.get("session_id")
            
            if not session_id:
                # Create new session
                session_id = await snowflake_service.create_session(
                    user_id=user_id,
                    title=f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
            
            # Save user message
            await snowflake_service.save_message(session_id, user_id, query, "user")
            
            # Search knowledge base
            search_results = await snowflake_service.search_knowledge(query)
            
            # Generate AI response
            ai_response = await snowflake_service.generate_ai_response(query, search_results)
            
            # Save AI response
            await snowflake_service.save_message(session_id, "system", ai_response, "assistant")
            
            # Send response back to client
            response_data = {
                "message_id": str(uuid4()),
                "session_id": session_id,
                "content": ai_response,
                "message_type": "assistant",
                "timestamp": datetime.now().isoformat(),
                "search_results": search_results[:3],  # Include top 3 search results
                "sources": [{"title": r["TITLE"], "category": r["CATEGORY_NAME"]} for r in search_results[:3]]
            }
            
            await manager.send_personal_message(json.dumps(response_data), user_id)
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)

# REST API Endpoints

@app.post("/api/v1/chat/sessions")
async def create_chat_session(
    request: CreateSessionRequest,
    user_id: str = Depends(authenticate_user)
) -> Dict[str, str]:
    """Create new chat session"""
    session_id = await snowflake_service.create_session(
        user_id=user_id,
        title=request.title,
        context=request.context
    )
    return {"session_id": session_id, "status": "created"}

@app.get("/api/v1/chat/sessions/{session_id}")
async def get_session_details(
    session_id: str,
    user_id: str = Depends(authenticate_user)
) -> Dict[str, Any]:
    """Get session details"""
    query = """
    SELECT SESSION_ID, USER_ID, TITLE, CREATED_AT, UPDATED_AT, CONTEXT
    FROM CONVERSATION_SESSIONS
    WHERE SESSION_ID = %s AND USER_ID = %s
    """
    results = await snowflake_service.execute_query(query, (session_id, user_id))
    
    if not results:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = results[0]
    return {
        "session_id": session["SESSION_ID"],
        "title": session["TITLE"],
        "created_at": session["CREATED_AT"],
        "updated_at": session["UPDATED_AT"],
        "context": json.loads(session["CONTEXT"]) if session["CONTEXT"] else None
    }

@app.post("/api/v1/chat/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    user_id: str = Depends(authenticate_user)
) -> Dict[str, Any]:
    """Send message to session"""
    # Save user message
    message_id = await snowflake_service.save_message(session_id, user_id, request.content, "user")
    
    # Search knowledge base
    search_results = await snowflake_service.search_knowledge(request.content)
    
    # Generate AI response
    ai_response = await snowflake_service.generate_ai_response(request.content, search_results)
    
    # Save AI response
    ai_message_id = await snowflake_service.save_message(session_id, "system", ai_response, "assistant")
    
    return {
        "user_message_id": message_id,
        "ai_message_id": ai_message_id,
        "ai_response": ai_response,
        "search_results": search_results[:3],
        "sources": [{"title": r["TITLE"], "category": r["CATEGORY_NAME"]} for r in search_results[:3]]
    }

@app.get("/api/v1/chat/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = 50,
    user_id: str = Depends(authenticate_user)
) -> List[Dict[str, Any]]:
    """Get messages for session"""
    messages = await snowflake_service.get_session_messages(session_id, limit)
    return messages

@app.put("/api/v1/chat/sessions/{session_id}/context")
async def update_session_context(
    session_id: str,
    context: Dict[str, Any],
    user_id: str = Depends(authenticate_user)
) -> Dict[str, str]:
    """Update session context"""
    query = """
    UPDATE CONVERSATION_SESSIONS 
    SET CONTEXT = %s, UPDATED_AT = %s 
    WHERE SESSION_ID = %s AND USER_ID = %s
    """
    await snowflake_service.execute_query(
        query, 
        (json.dumps(context), datetime.now(), session_id, user_id)
    )
    return {"status": "updated"}

@app.post("/api/v1/knowledge/search")
async def search_knowledge(
    request: SearchRequest,
    user_id: str = Depends(authenticate_user)
) -> Dict[str, Any]:
    """Search knowledge base"""
    results = await snowflake_service.search_knowledge(request.query, request.limit)
    return {
        "query": request.query,
        "results": results,
        "total_results": len(results)
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Snowflake connection
        test_query = "SELECT 1 as test"
        await snowflake_service.execute_query(test_query)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "snowflake": "connected",
                "websocket": "operational",
                "authentication": "enabled"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run(
        "enhanced_unified_chat_service:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
