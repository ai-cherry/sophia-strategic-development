"""
Unified Configuration for Sophia AI
Single source of truth for all configuration access

This module provides a centralized way to access configuration values
with clear precedence rules and type safety.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional, TypeVar, Union

from backend.core.auto_esc_config import get_config_value

T = TypeVar("T")

class UnifiedConfig:
    """
    Centralized configuration with clear precedence.

    Precedence order:
    1. Environment variable (highest priority)
    2. Pulumi ESC
    3. Configuration file
    4. Default value
    """

    # Configuration file cache
    _config_file_cache: Optional[dict] = None
    _config_file_path = Path("config/sophia_config.json")

    @classmethod
    def get(
        cls, key: str, default: Optional[T] = None, cast_type: Optional[type] = None
    ) -> Union[T, Any]:
        """
        Get configuration value with precedence handling.

        Args:
            key: Configuration key (case-insensitive for env vars)
            default: Default value if not found
            cast_type: Optional type to cast the value to

        Returns:
            Configuration value with appropriate type
        """
        # 1. Check environment variable (uppercase)
        env_key = key.upper()
        value = os.getenv(env_key)

        if value is not None:
            return cls._cast_value(value, cast_type)

        # 2. Check Pulumi ESC (lowercase)
        esc_key = key.lower()
        value = get_config_value(esc_key)

        if value is not None:
            return cls._cast_value(value, cast_type)

        # 3. Check configuration file
        if cls._config_file_cache is None:
            cls._load_config_file()

        if cls._config_file_cache:
            value = cls._config_file_cache.get(key)
            if value is not None:
                return cls._cast_value(value, cast_type)

        # 4. Return default
        return default

    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        """Get configuration value as boolean"""
        value = cls.get(key, default)

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")

        return bool(value)

    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        """Get configuration value as integer"""
        return cls.get(key, default, cast_type=int)

    @classmethod
    def get_float(cls, key: str, default: float = 0.0) -> float:
        """Get configuration value as float"""
        return cls.get(key, default, cast_type=float)

    @classmethod
    def get_list(cls, key: str, default: Optional[list] = None) -> list:
        """Get configuration value as list"""
        value = cls.get(key, default)

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            # Try to parse as JSON
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                # Split by comma as fallback
                return [item.strip() for item in value.split(",")]

        return default or []

    @classmethod
    def get_dict(cls, key: str, default: Optional[dict] = None) -> dict:
        """Get configuration value as dictionary"""
        value = cls.get(key, default)

        if isinstance(value, dict):
            return value

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass

        return default or {}

    @classmethod
    def _load_config_file(cls) -> None:
        """Load configuration from file if exists"""
        if cls._config_file_path.exists():
            try:
                with open(cls._config_file_path) as f:
                    cls._config_file_cache = json.load(f)
            except Exception as e:
                # Log error but don't fail
                print(f"Warning: Failed to load config file: {e}")
                cls._config_file_cache = {}
        else:
            cls._config_file_cache = {}

    @classmethod
    def _cast_value(cls, value: Any, cast_type: Optional[type]) -> Any:
        """Cast value to specified type"""
        if cast_type is None or value is None:
            return value

        try:
            if cast_type == bool:
                return cls.get_bool("_dummy", value)
            else:
                return cast_type(value)
        except (ValueError, TypeError):
            return value

    @classmethod
    def get_required(cls, key: str, cast_type: Optional[type] = None) -> Any:
        """
        Get required configuration value.

        Raises:
            ValueError: If configuration value is not found
        """
        value = cls.get(key, cast_type=cast_type)

        if value is None:
            raise ValueError(f"Required configuration '{key}' not found")

        return value

    @classmethod
    def get_current_config(cls) -> dict:
        """Get legacy configuration (deprecated)"""
        return {
            "host": cls.get("postgres_host", "localhost"),
            "user": cls.get("postgres_user", "postgres"),
            "password": cls.get("postgres_password"),
            "database": cls.get("postgres_database", "sophia_ai"),
            "schema": cls.get("postgres_schema", "public"),
        }

    @classmethod
    def get_redis_config(cls) -> dict:
        """Get complete Redis configuration"""
        return {
            "host": cls.get("redis_host", "localhost"),
            "port": cls.get_int("redis_port", 6379),
            "password": cls.get("redis_password"),
            "db": cls.get_int("redis_db", 0),
        }

    @classmethod
    def get_postgres_config(cls) -> dict:
        """Get complete PostgreSQL configuration"""
        return {
            "host": cls.get("postgres_host", "localhost"),
            "port": cls.get_int("postgres_port", 5432),
            "database": cls.get("postgres_database", "sophia_ai"),
            "user": cls.get("postgres_user", "postgres"),
            "password": cls.get("postgres_password"),
        }

    @classmethod
    def get_mcp_config(cls) -> dict:
        """Get MCP server configuration"""
        return {
            "gateway_url": cls.get("mcp_gateway_url", "http://localhost:8000"),
            "timeout": cls.get_int("mcp_timeout", 30),
            "max_retries": cls.get_int("mcp_max_retries", 3),
            "servers": cls.get_dict("mcp_servers", {}),
        }

    @classmethod
    def dump_config(cls, mask_secrets: bool = True) -> dict:
        """
        Dump current configuration for debugging.

        Args:
            mask_secrets: Whether to mask sensitive values

        Returns:
            Dictionary of all configuration values
        """
        sensitive_keys = {"password", "token", "key", "secret", "credential", "pat"}

        config = {}

        # Common configuration keys to check
        keys = [
            "environment",
            "debug",
            "log_level",
            "postgres_host",
            "QDRANT_user",
            "postgres_password",
            "postgres_database",
            "postgres_database",
            "postgres_schema",
            "redis_host",
            "redis_port",
            "postgres_host",
            "postgres_port",
            "openai_api_key",
            "anthropic_api_key",
            "pulumi_org",
        ]

        for key in keys:
            value = cls.get(key)
            if value is not None:
                if mask_secrets and any(s in key.lower() for s in sensitive_keys):
                    config[key] = "***MASKED***"
                else:
                    config[key] = value

        return config

# Convenience functions
def get_config(key: str, default: Optional[Any] = None) -> Any:
    """Shorthand for UnifiedConfig.get()"""
    return UnifiedConfig.get(key, default)

def get_required_config(key: str) -> Any:
    """Shorthand for UnifiedConfig.get_required()"""
    return UnifiedConfig.get_required(key)

def config_bool(key: str, default: bool = False) -> bool:
    """Shorthand for UnifiedConfig.get_bool()"""
    return UnifiedConfig.get_bool(key, default)

def config_int(key: str, default: int = 0) -> int:
    """Shorthand for UnifiedConfig.get_int()"""
    return UnifiedConfig.get_int(key, default)
