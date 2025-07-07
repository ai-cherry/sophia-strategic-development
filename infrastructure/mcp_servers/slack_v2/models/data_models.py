"""Data models for slack_v2 MCP server."""
from pydantic import BaseModel, Field
from datetime import datetime

class Slack_V2Record(BaseModel):
    """Base model for slack_v2 records."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    # TODO: Add slack_v2-specific fields
