"""Sophia AI - Complete Integration Configuration Module.

Centralized configuration management for all integrations with full implementation
"""

import asyncio
import importlib
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Dict, Generic, List, Optional, TypeVar

from .pulumi_esc import ESCClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variables for generic types
T = TypeVar("T")
ConfigType = TypeVar("ConfigType")
ClientType = TypeVar("ClientType")


@dataclass
class ServiceConfig:
    """Service configuration container."""

    service_name: str
    config: Dict[str, Any] = field(default_factory=dict)
    secrets: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with default."""return self.config.get(key, default).

    def get_secret(self, key: str, default: str = None) -> str:
        """Get secret value with default."""return self.secrets.get(key, default).

    def has_config(self, key: str) -> bool:
        """Check if configuration key exists."""return key in self.config.

    def has_secret(self, key: str) -> bool:
        """Check if secret key exists."""return key in self.secrets.

    def validate_required_config(self, required_keys: List[str]) -> bool:
        """Validate that all required configuration keys are present."""return all(key in self.config for key in required_keys).

    def validate_required_secrets(self, required_keys: List[str]) -> bool:
        """Validate that all required secret keys are present."""return all(key in self.secrets for key in required_keys).


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""pass.


class IntegrationError(Exception):
    """Exception raised for integration errors."""pass.


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed operations."""def decorator(func):.

        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {e}"
                    )
                    await asyncio.sleep(delay * (2**attempt))  # Exponential backoff
            return None

        return wrapper

    return decorator


class IntegrationConfig:
    """Enhanced centralized configuration manager for all integrations."""def __init__(self):.

        self.configs = {}
        self.secrets = {}
        self.esc_client = None
        self.initialized = False
        self.environment = os.environ.get("SOPHIA_ENVIRONMENT", "production")
        self.config_cache = {}
        self.secret_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_refresh = {}
        self._lock = asyncio.Lock()

    @retry_on_failure(max_retries=3)
    async def initialize(self) -> bool:
        """Initialize the configuration manager with retry logic."""if self.initialized:.

            return True

        async with self._lock:
            if self.initialized:  # Double-check after acquiring lock
                return True

            try:
                # Initialize Pulumi ESC client
                self.esc_client = ESCClient(
                    organization=os.environ.get("PULUMI_ORGANIZATION", "ai-cherry"),
                    project=os.environ.get("PULUMI_PROJECT", "sophia"),
                    stack=self.environment,
                )

                # Test ESC connection
                await self.esc_client._ensure_session()

                # Load service registry
                await self._load_service_registry()

                self.initialized = True
                logger.info(
                    "Integration configuration manager initialized successfully"
                )
                return True
            except Exception as e:
                logger.error(
                    f"Failed to initialize integration configuration manager: {e}"
                )
                # Initialize with fallback mode
                await self._initialize_fallback_mode()
                return False

    async def _initialize_fallback_mode(self) -> None:
        """Initialize in fallback mode using environment variables."""logger.warning(.

            "Initializing integration configuration manager in fallback mode"
        )
        self.esc_client = None
        await self._load_service_registry()
        self.initialized = True

    async def _load_service_registry(self) -> None:
        """Load service registry from Pulumi ESC or local file with validation."""try:.

            # Try to load from Pulumi ESC first
            if self.esc_client:
                try:
                    registry = await self.esc_client.get_configuration(
                        "service_registry"
                    )
                    if registry and self._validate_service_registry(registry):
                        self.configs = registry
                        logger.info(
                            f"Loaded service registry from Pulumi ESC with {len(self.configs)} services"
                        )
                        return
                except Exception as e:
                    logger.warning(f"Failed to load from Pulumi ESC: {e}")

            # Fall back to local file
            registry_path = os.environ.get(
                "SERVICE_REGISTRY_PATH",
                "/home/ubuntu/github/sophia-main/infrastructure/service_registry.json",
            )

            if os.path.exists(registry_path):
                with open(registry_path, "r") as f:
                    registry = json.load(f)
                    if self._validate_service_registry(registry):
                        self.configs = registry
                        logger.info(
                            f"Loaded service registry from local file with {len(self.configs)} services"
                        )
                        return

            # Create default registry with validation
            self.configs = self._create_default_registry()
            logger.info(
                f"Created default service registry with {len(self.configs)} services"
            )

        except Exception as e:
            logger.error(f"Failed to load service registry: {e}")
            self.configs = {}

    def _validate_service_registry(self, registry: Dict[str, Any]) -> bool:
        """Validate service registry structure."""if not isinstance(registry, dict):.

            logger.error("Service registry must be a dictionary")
            return False

        required_fields = ["type", "config_keys", "secret_keys"]
        for service_name, config in registry.items():
            if not isinstance(config, dict):
                logger.error(
                    f"Service {service_name} configuration must be a dictionary"
                )
                return False

            for field in required_fields:
                if field not in config:
                    logger.error(
                        f"Service {service_name} missing required field: {field}"
                    )
                    return False

        return True

    def _create_default_registry(self) -> Dict[str, Any]:
        """Create default service registry with comprehensive service definitions."""return {.

            "snowflake": {
                "type": "database",
                "config_keys": ["account", "warehouse", "database", "schema", "role"],
                "secret_keys": ["user", "password"],
                "rotation_schedule": "30d",
                "health_check": "SELECT 1",
                "timeout": 30,
                "required_packages": ["snowflake-connector-python"],
            },
            "gong": {
                "type": "api",
                "config_keys": ["base_url"],
                "secret_keys": ["api_key", "api_secret", "client_secret"],
                "rotation_schedule": "60d",
                "health_check": "/health",
                "timeout": 10,
                "required_packages": ["requests"],
            },
            "vercel": {
                "type": "api",
                "config_keys": ["team_id", "project_id", "org_id"],
                "secret_keys": ["token"],
                "rotation_schedule": "90d",
                "health_check": "/v1/user",
                "timeout": 10,
                "required_packages": ["requests"],
            },
            "estuary": {
                "type": "api",
                "config_keys": ["api_url"],
                "secret_keys": ["api_key"],
                "rotation_schedule": "60d",
                "health_check": "/health",
                "timeout": 15,
                "required_packages": ["aiohttp"],
            },
            "lambda_labs": {
                "type": "infrastructure",
                "config_keys": [],
                "secret_keys": [
                    "api_key",
                    "jupyter_password",
                    "ssh_public_key",
                    "ssh_private_key",
                ],
                "rotation_schedule": "90d",
                "health_check": "/instances",
                "timeout": 20,
                "required_packages": ["requests"],
            },
            "airbyte": {
                "type": "api",
                "config_keys": ["base_url"],
                "secret_keys": ["api_key", "password"],
                "rotation_schedule": "60d",
                "health_check": "/health",
                "timeout": 15,
                "required_packages": ["requests"],
            },
            "pinecone": {
                "type": "api",
                "config_keys": ["environment"],
                "secret_keys": ["api_key"],
                "rotation_schedule": "90d",
                "health_check": "/describe_index_stats",
                "timeout": 10,
                "required_packages": ["pinecone-client"],
            },
            "weaviate": {
                "type": "api",
                "config_keys": ["url"],
                "secret_keys": ["api_key"],
                "rotation_schedule": "90d",
                "health_check": "/v1/.well-known/ready",
                "timeout": 10,
                "required_packages": ["weaviate-client"],
            },
            "openai": {
                "type": "api",
                "config_keys": [],
                "secret_keys": ["api_key"],
                "rotation_schedule": "30d",
                "health_check": "/models",
                "timeout": 10,
                "required_packages": ["openai"],
            },
            "anthropic": {
                "type": "api",
                "config_keys": [],
                "secret_keys": ["api_key"],
                "rotation_schedule": "30d",
                "health_check": "/messages",
                "timeout": 10,
                "required_packages": ["anthropic"],
            },
            "github": {
                "type": "api",
                "config_keys": ["org"],
                "secret_keys": ["token"],
                "rotation_schedule": "90d",
                "health_check": "/user",
                "timeout": 10,
                "required_packages": ["PyGithub"],
            },
        }

    @retry_on_failure(max_retries=2)
    async def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """Get configuration for a specific service with enhanced error handling."""if not self.initialized:.

            await self.initialize()

        if service_name not in self.configs:
            logger.error(f"Unknown service: {service_name}")
            return None

        try:
            # Check if we need to refresh the cache
            if (
                service_name not in self.last_refresh
                or (time.time() - self.last_refresh[service_name]) > self.cache_ttl
            ):
                # Get service configuration
                config = {}
                secrets = {}

                # Get configuration values with validation
                for key in self.configs[service_name].get("config_keys", []):
                    value = await self._get_config_value(service_name, key)
                    if value is not None:
                        config[key] = value

                # Get secret values with validation
                for key in self.configs[service_name].get("secret_keys", []):
                    value = await self._get_secret_value(service_name, key)
                    if value is not None:
                        secrets[key] = value

                # Validate required configurations
                if not self._validate_service_config(service_name, config, secrets):
                    logger.error(f"Invalid configuration for service {service_name}")
                    return None

                # Cache the results
                self.config_cache[service_name] = config
                self.secret_cache[service_name] = secrets
                self.last_refresh[service_name] = time.time()

            # Return service configuration
            return ServiceConfig(
                service_name=service_name,
                config=self.config_cache.get(service_name, {}),
                secrets=self.secret_cache.get(service_name, {}),
                metadata=self.configs[service_name],
            )
        except Exception as e:
            logger.error(f"Failed to get configuration for {service_name}: {e}")
            return None

    async def _get_config_value(self, service_name: str, key: str) -> Optional[Any]:
        """Get a configuration value from ESC or environment."""config_key = f"{service_name}_{key}".

        # Try Pulumi ESC first
        if self.esc_client:
            try:
                value = await self.esc_client.get_configuration(config_key)
                if value is not None:
                    return value
            except Exception as e:
                logger.warning(f"Failed to get config from ESC for {config_key}: {e}")

        # Fall back to environment variables
        env_key = f"{service_name.upper()}_{key.upper()}"
        return os.environ.get(env_key)

    async def _get_secret_value(self, service_name: str, key: str) -> Optional[str]:
        """Get a secret value from ESC or environment."""secret_key = f"{service_name}_{key}".

        # Try Pulumi ESC first
        if self.esc_client:
            try:
                value = await self.esc_client.get_secret(secret_key)
                if value is not None:
                    return value
            except Exception as e:
                logger.warning(f"Failed to get secret from ESC for {secret_key}: {e}")

        # Fall back to environment variables
        env_key = f"{service_name.upper()}_{key.upper()}"
        return os.environ.get(env_key)

    def _validate_service_config(
        self, service_name: str, config: Dict[str, Any], secrets: Dict[str, str]
    ) -> bool:
        """Validate service configuration completeness."""service_meta = self.configs[service_name].

        # Check required config keys
        for key in service_meta.get("config_keys", []):
            if key not in config:
                logger.warning(f"Missing config key {key} for service {service_name}")

        # Check required secret keys
        for key in service_meta.get("secret_keys", []):
            if key not in secrets:
                logger.warning(f"Missing secret key {key} for service {service_name}")
                return False  # Secrets are critical

        return True

    async def get_config_value(self, service_name: str, key: str) -> Optional[Any]:
        """Get a specific configuration value."""service_config = await self.get_service_config(service_name).

        if not service_config:
            return None

        return service_config.get_config(key)

    async def get_secret_value(self, service_name: str, key: str) -> Optional[str]:
        """Get a specific secret value."""service_config = await self.get_service_config(service_name).

        if not service_config:
            return None

        return service_config.get_secret(key)

    async def get_connection_string(self, service_name: str) -> Optional[str]:
        """Get connection string for a service with enhanced validation."""service_config = await self.get_service_config(service_name).

        if not service_config:
            return None

        try:
            if service_name == "snowflake":
                required_keys = [
                    "user",
                    "password",
                    "account",
                    "database",
                    "schema",
                    "warehouse",
                    "role",
                ]
                if not all(
                    service_config.has_secret(key) or service_config.has_config(key)
                    for key in required_keys
                ):
                    logger.error("Missing required keys for Snowflake connection")
                    return None

                return f"snowflake://{service_config.get_secret('user')}:{service_config.get_secret('password')}@{service_config.get_config('account')}/{service_config.get_config('database')}/{service_config.get_config('schema')}?warehouse={service_config.get_config('warehouse')}&role={service_config.get_config('role')}"

            elif service_name == "postgres":
                required_keys = ["user", "password", "host", "port", "database"]
                if not all(
                    service_config.has_secret(key) or service_config.has_config(key)
                    for key in required_keys
                ):
                    logger.error("Missing required keys for PostgreSQL connection")
                    return None

                return f"postgresql://{service_config.get_secret('user')}:{service_config.get_secret('password')}@{service_config.get_config('host')}:{service_config.get_config('port')}/{service_config.get_config('database')}"

            else:
                logger.warning(
                    f"No connection string template for service {service_name}"
                )
                return None

        except Exception as e:
            logger.error(
                f"Failed to generate connection string for {service_name}: {e}"
            )
            return None

    async def list_services(self) -> List[str]:
        """List all registered services."""if not self.initialized:.

            await self.initialize()

        return list(self.configs.keys())

    async def get_service_metadata(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific service."""if not self.initialized:.

            await self.initialize()

        if service_name not in self.configs:
            logger.error(f"Unknown service: {service_name}")
            return None

        return self.configs[service_name]

    async def refresh_cache(self, service_name: str = None) -> None:
        """Refresh configuration cache for a service or all services."""if service_name:.

            if service_name in self.last_refresh:
                del self.last_refresh[service_name]
            if service_name in self.config_cache:
                del self.config_cache[service_name]
            if service_name in self.secret_cache:
                del self.secret_cache[service_name]
        else:
            self.last_refresh.clear()
            self.config_cache.clear()
            self.secret_cache.clear()

        logger.info(f"Cache refreshed for {service_name or 'all services'}")

    async def validate_service(self, service_name: str) -> bool:
        """Validate a service configuration."""service_config = await self.get_service_config(service_name).

        if not service_config:
            return False

        service_meta = self.configs[service_name]

        # Check required packages
        required_packages = service_meta.get("required_packages", [])
        for package in required_packages:
            try:
                importlib.import_module(package.replace("-", "_"))
            except ImportError:
                logger.error(
                    f"Required package {package} not installed for {service_name}"
                )
                return False

        # Check required configuration
        required_config = service_meta.get("config_keys", [])
        if not service_config.validate_required_config(required_config):
            logger.error(f"Missing required configuration for {service_name}")
            return False

        # Check required secrets
        required_secrets = service_meta.get("secret_keys", [])
        if not service_config.validate_required_secrets(required_secrets):
            logger.error(f"Missing required secrets for {service_name}")
            return False

        return True


class Integration(ABC, Generic[ConfigType, ClientType]):
    """Abstract base class for all integrations."""def __init__(self, service_name: str):.

        self.service_name = service_name
        self.config_manager = IntegrationConfig()
        self.client = None
        self.initialized = False
        self.service_config = None

    async def initialize(self) -> bool:
        """Initialize the integration."""if self.initialized:.

            return True

        try:
            # Initialize config manager
            if not self.config_manager.initialized:
                await self.config_manager.initialize()

            # Get service configuration
            self.service_config = await self.config_manager.get_service_config(
                self.service_name
            )
            if not self.service_config:
                logger.error(f"Failed to get configuration for {self.service_name}")
                return False

            # Validate service configuration
            if not await self.config_manager.validate_service(self.service_name):
                logger.error(f"Invalid configuration for {self.service_name}")
                return False

            # Initialize client
            self.client = await self._create_client(self.service_config)
            if not self.client:
                logger.error(f"Failed to create client for {self.service_name}")
                return False

            self.initialized = True
            logger.info(f"Initialized {self.service_name} integration")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize {self.service_name} integration: {e}")
            return False

    @abstractmethod
    async def _create_client(self, config: ServiceConfig) -> Optional[ClientType]:
        """Create a client for the integration."""pass.

    async def get_client(self) -> Optional[ClientType]:
        """Get the client for the integration."""if not self.initialized:.

            await self.initialize()

        return self.client

    async def health_check(self) -> bool:
        """Perform health check for the integration."""if not self.initialized:.

            await self.initialize()

        if not self.client:
            return False

        try:
            return await self._perform_health_check()
        except Exception as e:
            logger.error(f"Health check failed for {self.service_name}: {e}")
            return False

    @abstractmethod
    async def _perform_health_check(self) -> bool:
        """Perform service-specific health check."""pass.

    async def get_config(self) -> Optional[ServiceConfig]:
        """Get service configuration."""if not self.service_config:.

            self.service_config = await self.config_manager.get_service_config(
                self.service_name
            )

        return self.service_config

    async def refresh_config(self) -> None:
        """Refresh service configuration."""await self.config_manager.refresh_cache(self.service_name).

        self.service_config = None


# Create singleton instance
integration_config = IntegrationConfig()


# Convenience functions
async def get_config(service_name: str) -> Optional[ServiceConfig]:
    """Get configuration for a service."""return await integration_config.get_service_config(service_name).


async def get_secret(service_name: str, key: str) -> Optional[str]:
    """Get a secret value."""return await integration_config.get_secret_value(service_name, key).


async def get_connection_string(service_name: str) -> Optional[str]:
    """Get connection string for a service."""return await integration_config.get_connection_string(service_name).


async def list_services() -> List[str]:
    """List all registered services."""return await integration_config.list_services().


async def validate_service(service_name: str) -> bool:
    """Validate a service configuration."""return await integration_config.validate_service(service_name).


async def refresh_cache(service_name: str = None) -> None:
    """Refresh configuration cache."""
    return await integration_config.refresh_cache(service_name)
