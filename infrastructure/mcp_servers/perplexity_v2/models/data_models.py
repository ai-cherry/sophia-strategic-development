"""Data models for perplexity_v2 MCP server."""
from datetime import datetime

from pydantic import BaseModel, Field


class Perplexity_V2Record(BaseModel):
    """Base model for perplexity_v2 records."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    # TODO: Add perplexity_v2-specific fields
