"""
Base module for Sophia AI core components.

This module contains base classes and interfaces with NO dependencies
to prevent circular imports.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseConfig(ABC):
    """Base configuration interface with no dependencies."""

    @abstractmethod
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        pass

    @abstractmethod
    def set_value(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        pass


class BaseSecurityConfig(BaseConfig):
    """Base security configuration interface."""

    @abstractmethod
    def get_secret(self, key: str) -> str | None:
        """Get a secret value."""
        pass

    @abstractmethod
    def is_secure_key(self, key: str) -> bool:
        """Check if a key should be treated as secure."""
        pass


class BaseConnectionManager(ABC):
    """Base connection manager interface."""

    @abstractmethod
    async def get_connection(self, connection_type: str) -> Any:
        """Get a connection by type."""
        pass

    @abstractmethod
    async def close_all(self) -> None:
        """Close all connections."""
        pass


class ServiceRegistry:
    """Central service registry to avoid circular imports."""

    _instance = None
    _services: dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, name: str, service: Any) -> None:
        """Register a service."""
        self._services[name] = service

    def get(self, name: str) -> Any | None:
        """Get a registered service."""
        return self._services.get(name)

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()


# Global service registry instance
service_registry = ServiceRegistry()
