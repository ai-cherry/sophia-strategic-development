"""Data models for notion_v2 MCP server."""

from datetime import datetime

from pydantic import BaseModel, Field


class Notion_V2Record(BaseModel):
    """Base model for notion_v2 records."""

    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    # TODO: Add notion_v2-specific fields
