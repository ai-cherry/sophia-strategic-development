"""Secure credential manager for Sophia AI."""

from __future__ import annotations

from .auto_esc_config import AutoESCConfig


class SecureCredentialManager:
    """
    Retrieve credentials stored in Pulumi ESC."""

    def __init__(self, esc_config: AutoESCConfig | None = None) -> None:
        self._config = esc_config or AutoESCConfig()

    async def get_openai_api_key(self) -> str | None:
        """
        Return the OpenAI API key from ESC if present."""

        return self._config.get("openai_api_key")
