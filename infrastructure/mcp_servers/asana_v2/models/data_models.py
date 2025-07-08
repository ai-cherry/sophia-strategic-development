"""Data models for asana_v2 MCP server."""

from datetime import datetime

from pydantic import BaseModel, Field


class Asana_V2Record(BaseModel):
    """Base model for asana_v2 records."""

    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    # TODO: Add asana_v2-specific fields
