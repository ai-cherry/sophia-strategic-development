"""Configuration utilities for the Sophia AI backend."""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from .auto_esc_config import AutoESCConfig


class Config(BaseModel):
    """Typed configuration loaded from Pulumi ESC."""

    openai_api_key: str | None = None
    # REMOVED: ModernStack dependency None

    @classmethod
    def from_esc(cls) -> Config:
        """Instantiate :class:`Config` using Pulumi ESC values."""

        esc_config = AutoESCConfig()
        data: dict[str, Any] = {
            field: esc_config.get(field) for field in cls.model_fields
        }
        return cls(**data)
