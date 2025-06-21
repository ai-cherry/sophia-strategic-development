"""Sophia AI - Enhanced Configuration Manager.

Centralized configuration management for all integrations with improved error handling and validation
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Dict, List, Optional

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Service configuration container."""

    service_name: str
    config: Dict[str, Any]
    secrets: Dict[str, str]
    metadata: Dict[str, Any]


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


class ConfigManager:
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
                from .pulumi_esc import ESCClient

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
                logger.info("Configuration manager initialized successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize configuration manager: {e}")
                # Initialize with fallback mode
                await self._initialize_fallback_mode()
                return False

    async def _initialize_fallback_mode(self) -> None:
        """Initialize in fallback mode using environment variables."""logger.warning("Initializing configuration manager in fallback mode").

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
            },
            "gong": {
                "type": "api",
                "config_keys": ["base_url"],
                "secret_keys": ["api_key", "api_secret", "client_secret"],
                "rotation_schedule": "60d",
                "health_check": "/health",
                "timeout": 10,
            },
            "vercel": {
                "type": "api",
                "config_keys": ["team_id", "project_id", "org_id"],
                "secret_keys": ["token"],
                "rotation_schedule": "90d",
                "health_check": "/v1/user",
                "timeout": 10,
            },
            "estuary": {
                "type": "api",
                "config_keys": ["api_url"],
                "secret_keys": ["api_key"],
                "rotation_schedule": "60d",
                "health_check": "/health",
                "timeout": 15,
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
            },
            "airbyte": {
                "type": "api",
                "config_keys": ["base_url"],
                "secret_keys": ["api_key", "password"],
                "rotation_schedule": "60d",
                "health_check": "/health",
                "timeout": 15,
            },
            "pinecone": {
                "type": "api",
                "config_keys": ["environment"],
                "secret_keys": ["api_key"],
                "rotation_schedule": "90d",
                "health_check": "/describe_index_stats",
                "timeout": 10,
            },
            "weaviate": {
                "type": "api",
                "config_keys": ["url"],
                "secret_keys": ["api_key"],
                "rotation_schedule": "90d",
                "health_check": "/v1/.well-known/ready",
                "timeout": 10,
            },
            "openai": {
                "type": "api",
                "config_keys": [],
                "secret_keys": ["api_key"],
                "rotation_schedule": "30d",
                "health_check": "/models",
                "timeout": 10,
            },
            "anthropic": {
                "type": "api",
                "config_keys": [],
                "secret_keys": ["api_key"],
                "rotation_schedule": "30d",
                "health_check": "/messages",
                "timeout": 10,
            },
            "github": {
                "type": "api",
                "config_keys": ["org"],
                "secret_keys": ["token"],
                "rotation_schedule": "90d",
                "health_check": "/user",
                "timeout": 10,
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

        return service_config.config.get(key)

    async def get_secret_value(self, service_name: str, key: str) -> Optional[str]:
        """Get a specific secret value."""service_config = await self.get_service_config(service_name).

        if not service_config:
            return None

        return service_config.secrets.get(key)

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
                    key in service_config.secrets or key in service_config.config
                    for key in required_keys
                ):
                    logger.error("Missing required keys for Snowflake connection")
                    return None

                return f"snowflake://{service_config.secrets['user']}:{service_config.secrets['password']}@{service_config.config['account']}/{service_config.config['database']}/{service_config.config['schema']}?warehouse={service_config.config['warehouse']}&role={service_config.config['role']}"

            elif service_name == "postgres":
                required_keys = ["user", "password", "host", "port", "database"]
                if not all(
                    key in service_config.secrets or key in service_config.config
                    for key in required_keys
                ):
                    logger.error("Missing required keys for PostgreSQL connection")
                    return None

                return f"postgresql://{service_config.secrets['user']}:{service_config.secrets['password']}@{service_config.config['host']}:{service_config.config['port']}/{service_config.config['database']}"

            else:
                logger.warning(
                    f"No connection string template for service {service_name}"
                )
                return None

        except KeyError as e:
            logger.error(f"Missing configuration for connection string: {e}")
            return None

    async def get_api_client(self, service_name: str) -> Optional[Any]:
        """Get API client for a service with enhanced error handling."""service_config = await self.get_service_config(service_name).

        if not service_config:
            return None

        try:
            if service_name == "pinecone":
                import pinecone

                pinecone.init(
                    api_key=service_config.secrets["api_key"],
                    environment=service_config.config["environment"],
                )
                return pinecone

            elif service_name == "openai":
                import openai

                openai.api_key = service_config.secrets["api_key"]
                return openai

            elif service_name == "anthropic":
                import anthropic

                client = anthropic.Anthropic(api_key=service_config.secrets["api_key"])
                return client

            elif service_name == "weaviate":
                import weaviate

                client = weaviate.Client(
                    url=service_config.config["url"],
                    auth_client_secret=weaviate.AuthApiKey(
                        api_key=service_config.secrets["api_key"]
                    ),
                )
                return client

            else:
                logger.warning(
                    f"No API client implementation for service {service_name}"
                )
                return None

        except ImportError as e:
            logger.error(f"Failed to import module for {service_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create API client for {service_name}: {e}")
            return None

    async def health_check(self, service_name: str) -> bool:
        """Perform health check for a service."""service_config = await self.get_service_config(service_name).

        if not service_config:
            return False

        try:
            health_endpoint = service_config.metadata.get("health_check")
            timeout = service_config.metadata.get("timeout", 10)

            if not health_endpoint:
                logger.warning(f"No health check endpoint defined for {service_name}")
                return True  # Assume healthy if no check defined

            if service_name in ["snowflake"]:
                # Database health check
                connection_string = await self.get_connection_string(service_name)
                if not connection_string:
                    return False

                # Implement database connection test
                if service_name == "snowflake":
                    try:
                        import snowflake.connector

                        conn = snowflake.connector.connect(
                            user=service_config.secrets["user"],
                            password=service_config.secrets["password"],
                            account=service_config.config["account"],
                            warehouse=service_config.config["warehouse"],
                            database=service_config.config["database"],
                            schema=service_config.config["schema"],
                            role=service_config.config["role"],
                        )
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        result = cursor.fetchone()
                        conn.close()
                        return result is not None
                    except Exception as e:
                        logger.error(f"Snowflake connection test failed: {e}")
                        return False

                elif service_name == "postgres":
                    try:
                        import psycopg2

                        conn = psycopg2.connect(connection_string)
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        result = cursor.fetchone()
                        conn.close()
                        return result is not None
                    except Exception as e:
                        logger.error(f"PostgreSQL connection test failed: {e}")
                        return False
                return True

            else:
                # API health check
                base_url = service_config.config.get(
                    "base_url"
                ) or service_config.config.get("url")
                if not base_url:
                    logger.warning(f"No base URL configured for {service_name}")
                    return False

                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as session:
                    headers = {}
                    if "api_key" in service_config.secrets:
                        headers["Authorization"] = (
                            f"Bearer {service_config.secrets['api_key']}"
                        )

                    async with session.get(
                        f"{base_url}{health_endpoint}", headers=headers
                    ) as response:
                        return response.status < 400

        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return False

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


# Create singleton instance
config_manager = ConfigManager()


async def get_config(service_name: str) -> Optional[ServiceConfig]:
    """Get configuration for a service."""return await config_manager.get_service_config(service_name).


async def get_secret(service_name: str, key: str) -> Optional[str]:
    """Get a secret value."""return await config_manager.get_secret_value(service_name, key).


async def get_connection_string(service_name: str) -> Optional[str]:
    """Get connection string for a service."""return await config_manager.get_connection_string(service_name).


async def get_api_client(service_name: str) -> Optional[Any]:
    """Get API client for a service."""return await config_manager.get_api_client(service_name).


async def health_check(service_name: str) -> bool:
    """Perform health check for a service."""return await config_manager.health_check(service_name).


async def list_services() -> List[str]:
    """List all registered services."""return await config_manager.list_services().


async def refresh_cache(service_name: str = None) -> None:
    """Refresh configuration cache."""
    return await config_manager.refresh_cache(service_name)
