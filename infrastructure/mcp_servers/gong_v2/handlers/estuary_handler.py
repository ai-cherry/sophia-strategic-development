"""
Estuary Flow webhook handler for Gong V2 MCP server
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, Field
import redis.asyncio as redis

from ..config import settings
from ..models.data_models import CallInfo, TranscriptSegment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/estuary", tags=["estuary"])

# Redis client for caching
redis_client: Optional[redis.Redis] = None

async def get_redis_client():
    """Get or create Redis client"""
    global redis_client
    if not redis_client:
        redis_client = await redis.from_url(
            f"redis://146.235.200.1:6379",
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client

# Estuary Event Models
class EstuaryEvent(BaseModel):
    """Estuary Flow event structure"""
    id: str = Field(..., description="Event ID")
    type: str = Field(..., description="Event type")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event payload")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EstuaryWebhookResponse(BaseModel):
    """Response for Estuary webhook"""
    status: str
    event_id: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)

# Expected schema for Gong events
GONG_SCHEMA = {
    "call_completed": {
        "required": ["call_id", "transcript", "duration", "participants"],
        "properties": {
            "call_id": {"type": "string"},
            "transcript": {"type": "string"},
            "duration": {"type": "number"},
            "participants": {"type": "array"},
            "sentiment": {"type": "number"},
            "topics": {"type": "array"}
        }
    },
    "call_updated": {
        "required": ["call_id"],
        "properties": {
            "call_id": {"type": "string"},
            "sentiment": {"type": "number"},
            "topics": {"type": "array"},
            "action_items": {"type": "array"}
        }
    }
}

def validate_schema(event: EstuaryEvent, schema: Dict[str, Any]) -> bool:
    """Validate event data against expected schema"""
    if event.type not in schema:
        return False
    
    event_schema = schema[event.type]
    
    # Check required fields
    for field in event_schema.get("required", []):
        if field not in event.data:
            logger.error(f"Missing required field: {field}")
            return False
    
    # Validate field types (simplified)
    for field, spec in event_schema.get("properties", {}).items():
        if field in event.data:
            expected_type = spec["type"]
            actual_value = event.data[field]
            
            if expected_type == "string" and not isinstance(actual_value, str):
                return False
            elif expected_type == "number" and not isinstance(actual_value, (int, float)):
                return False
            elif expected_type == "array" and not isinstance(actual_value, list):
                return False
    
    return True

@router.post("/webhook", response_model=EstuaryWebhookResponse)
async def handle_estuary_webhook(
    event: EstuaryEvent,
    authorization: str = Header(None),
    request: Request = None
):
    """
    Handle incoming Estuary Flow events
    
    This endpoint receives real-time updates from Estuary Flow
    for Gong call data and processes them accordingly.
    """
    
    # Verify webhook token
    expected_token = f"Bearer {settings.ESTUARY_WEBHOOK_TOKEN}"
    if authorization != expected_token:
        logger.warning(f"Invalid webhook token from {request.client.host}")
        raise HTTPException(401, "Invalid authorization")
    
    # Validate event schema
    if not validate_schema(event, GONG_SCHEMA):
        logger.error(f"Invalid event schema for type: {event.type}")
        raise HTTPException(400, f"Invalid schema for event type: {event.type}")
    
    try:
        # Process based on event type
        if event.type == "call_completed":
            await process_call_completed(event.data)
        elif event.type == "call_updated":
            await process_call_updated(event.data)
        else:
            logger.warning(f"Unknown event type: {event.type}")
            raise HTTPException(400, f"Unknown event type: {event.type}")
        
        # Store in Redis for quick access
        redis = await get_redis_client()
        cache_key = f"gong:call:{event.data.get('call_id', event.id)}"
        cache_data = {
            **event.data,
            "event_type": event.type,
            "processed_at": datetime.utcnow().isoformat(),
            "event_id": event.id
        }
        
        await redis.setex(
            cache_key,
            7200,  # 2 hour TTL
            json.dumps(cache_data)
        )
        
        # Also store in event stream for processing
        stream_key = "gong:events:stream"
        await redis.xadd(
            stream_key,
            {"event": json.dumps(event.dict())},
            maxlen=10000  # Keep last 10k events
        )
        
        logger.info(f"Processed Estuary event: {event.id} (type: {event.type})")
        
        return EstuaryWebhookResponse(
            status="processed",
            event_id=event.id
        )
        
    except Exception as e:
        logger.error(f"Error processing Estuary event: {e}")
        raise HTTPException(500, f"Processing error: {str(e)}")

async def process_call_completed(data: Dict[str, Any]):
    """Process completed call event"""
    call_id = data["call_id"]
    
    # Extract and process transcript segments
    transcript_text = data.get("transcript", "")
    segments = parse_transcript_segments(transcript_text)
    
    # Calculate metrics
    metrics = {
        "total_duration": data.get("duration", 0),
        "participant_count": len(data.get("participants", [])),
        "sentiment_score": data.get("sentiment", 0),
        "topic_count": len(data.get("topics", [])),
        "has_action_items": bool(data.get("action_items", []))
    }
    
    # Store processed data
    redis = await get_redis_client()
    
    # Store call info
    await redis.hset(
        f"gong:calls:{call_id}",
        mapping={
            "status": "completed",
            "duration": data.get("duration", 0),
            "sentiment": data.get("sentiment", 0),
            "topics": json.dumps(data.get("topics", [])),
            "metrics": json.dumps(metrics),
            "processed_at": datetime.utcnow().isoformat()
        }
    )
    
    # Store transcript segments for analysis
    for i, segment in enumerate(segments):
        await redis.hset(
            f"gong:transcripts:{call_id}:{i}",
            mapping={
                "speaker": segment.get("speaker", "Unknown"),
                "text": segment.get("text", ""),
                "sentiment": segment.get("sentiment", "neutral")
            }
        )
    
    logger.info(f"Processed completed call: {call_id}")

async def process_call_updated(data: Dict[str, Any]):
    """Process call update event"""
    call_id = data["call_id"]
    
    # Update only changed fields
    redis = await get_redis_client()
    
    updates = {}
    if "sentiment" in data:
        updates["sentiment"] = data["sentiment"]
    if "topics" in data:
        updates["topics"] = json.dumps(data["topics"])
    if "action_items" in data:
        updates["action_items"] = json.dumps(data["action_items"])
    
    updates["updated_at"] = datetime.utcnow().isoformat()
    
    if updates:
        await redis.hset(
            f"gong:calls:{call_id}",
            mapping=updates
        )
    
    logger.info(f"Updated call: {call_id}")

def parse_transcript_segments(transcript: str) -> list[Dict[str, Any]]:
    """Parse transcript text into segments"""
    # Simple parsing - in production, this would be more sophisticated
    segments = []
    
    # Split by speaker pattern (e.g., "Speaker Name: text")
    import re
    pattern = r'([^:]+):\s*([^:]+?)(?=\n[^:]+:|$)'
    matches = re.findall(pattern, transcript, re.MULTILINE | re.DOTALL)
    
    for speaker, text in matches:
        segments.append({
            "speaker": speaker.strip(),
            "text": text.strip(),
            "sentiment": analyze_simple_sentiment(text)
        })
    
    return segments

def analyze_simple_sentiment(text: str) -> str:
    """Simple sentiment analysis"""
    positive_words = ["great", "excellent", "love", "perfect", "amazing", "wonderful"]
    negative_words = ["problem", "issue", "concern", "difficult", "challenge", "bad"]
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

@router.get("/status")
async def estuary_status():
    """Check Estuary integration status"""
    try:
        redis = await get_redis_client()
        
        # Get recent events count
        stream_key = "gong:events:stream"
        stream_info = await redis.xinfo_stream(stream_key)
        
        # Get processed calls count
        call_keys = await redis.keys("gong:calls:*")
        
        return {
            "status": "healthy",
            "integration": "estuary_flow",
            "recent_events": stream_info.get("length", 0),
            "processed_calls": len(call_keys),
            "last_check": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }

@router.get("/schema")
async def get_expected_schema():
    """Return expected event schema for Estuary configuration"""
    return {
        "webhook_endpoint": "/estuary/webhook",
        "auth_type": "bearer_token",
        "event_types": list(GONG_SCHEMA.keys()),
        "schemas": GONG_SCHEMA,
        "metadata": {
            "version": "1.0.0",
            "server": "gong_v2_mcp"
        }
    } 