"""Data models for github_v2 MCP server."""
from pydantic import BaseModel, Field
from datetime import datetime

class Github_V2Record(BaseModel):
    """Base model for github_v2 records."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    # TODO: Add github_v2-specific fields
