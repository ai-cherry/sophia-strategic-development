"""Pulumi ESC configuration loader for Sophia AI."""

from __future__ import annotations

import json
import logging
import os
import subprocess
from typing import Any, Optional

from pydantic import BaseModel, ValidationError

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


class Settings(BaseModel):
    """Typed settings loaded from Pulumi ESC."""

    openai_api_key: Optional[str] = None
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    slack_bot_token: Optional[str] = None


class AutoESCConfig:
    """Singleton loader for Pulumi ESC secrets."""

    _instance: Optional["AutoESCConfig"] = None
    _config: dict[str, Any] | None = None

    def __new__(cls) -> "AutoESCConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._config is None:
            self._load_config()

    def _load_config(self) -> None:
        """Load configuration from Pulumi ESC."""
        org = os.getenv("PULUMI_ORG", "scoobyjava-org")
        stack = os.getenv("PULUMI_STACK", "sophia-ai-production")
        cmd = [
            "pulumi",
            "env",
            "open",
            f"{org}/default/{stack}",
            "--format",
            "json",
        ]
        logging.debug("Loading ESC config via: %s", " ".join(cmd))
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                logging.error("pulumi env open failed: %s", result.stderr.strip())
                self._config = {}
                return
            self._config = json.loads(result.stdout)
            logging.info(
                "Loaded ESC configuration with %d keys", len(self._config or {})
            )
        except json.JSONDecodeError as exc:
            logging.exception("Failed to parse ESC output: %s", exc)
            self._config = {}
        except Exception as exc:  # pragma: no cover - defensive
            logging.exception("Unexpected error loading ESC config: %s", exc)
            self._config = {}

    def get(self, key: str, default: Any | None = None) -> Any | None:
        """Retrieve a config value."""

        if self._config is None:
            return default
        return self._config.get(key, default)

    def as_settings(self) -> Settings:
        """Return config as typed :class:`Settings`."""

        try:
            return Settings(**(self._config or {}))
        except ValidationError as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Invalid ESC configuration: {exc}") from exc


config = AutoESCConfig()
