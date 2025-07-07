"""Data models for github MCP server."""
from datetime import datetime

from pydantic import BaseModel, Field


class GithubRecord(BaseModel):
    """Base model for github records."""

    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    # TODO: Add github-specific fields
