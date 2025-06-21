"""Sophia AI - Complete Integration Registry.

Registry for all integrations with the Sophia AI platform with full implementation
"""

import asyncio
import importlib
import inspect
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from .integration_config import (
    Integration,
    IntegrationConfig,
    IntegrationError,
    ServiceConfig,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class IntegrationMetadata:
    """Metadata for an integration."""

    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    secret_schema: Dict[str, Any] = field(default_factory=dict)
    health_check_interval: int = 300  # 5 minutes
    retry_attempts: int = 3
    timeout: int = 30
    tags: List[str] = field(default_factory=list)


class IntegrationRegistry:
    """Comprehensive registry for all integrations with the Sophia AI platform."""def __init__(self):.

        self.integrations: Dict[str, Type[Integration]] = {}
        self.instances: Dict[str, Integration] = {}
        self.metadata: Dict[str, IntegrationMetadata] = {}
        self.config_manager = IntegrationConfig()
        self.initialized = False
        self._lock = asyncio.Lock()
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self.health_status: Dict[str, bool] = {}

    async def initialize(self) -> bool:
        """Initialize the integration registry."""if self.initialized:.

            return True

        async with self._lock:
            if self.initialized:  # Double-check after acquiring lock
                return True

            try:
                # Initialize config manager
                await self.config_manager.initialize()

                # Auto-discover and register integrations
                await self._auto_discover_integrations()

                # Start health monitoring
                await self._start_health_monitoring()

                self.initialized = True
                logger.info(
                    f"Integration registry initialized with {len(self.integrations)} integrations"
                )
                return True
            except Exception as e:
                logger.error(f"Failed to initialize integration registry: {e}")
                return False

    def register(
        self,
        service_name: str,
        integration_class: Type[Integration],
        metadata: IntegrationMetadata = None,
    ) -> None:
        """Register an integration with optional metadata."""if not issubclass(integration_class, Integration):.

            raise IntegrationError(
                "Integration class must inherit from Integration base class"
            )

        self.integrations[service_name] = integration_class

        if metadata:
            self.metadata[service_name] = metadata
        else:
            # Create default metadata
            self.metadata[service_name] = IntegrationMetadata(
                name=service_name,
                version="1.0.0",
                description=f"Integration for {service_name}",
                author="Sophia AI",
                dependencies=[],
                config_schema={},
                secret_schema={},
            )

        logger.info(f"Registered integration for {service_name}")

    def unregister(self, service_name: str) -> bool:
        """Unregister an integration."""if service_name not in self.integrations:.

            logger.warning(f"Integration {service_name} not found for unregistration")
            return False

        # Stop health monitoring
        if service_name in self.health_check_tasks:
            self.health_check_tasks[service_name].cancel()
            del self.health_check_tasks[service_name]

        # Remove instance if exists
        if service_name in self.instances:
            del self.instances[service_name]

        # Remove from registry
        del self.integrations[service_name]
        if service_name in self.metadata:
            del self.metadata[service_name]
        if service_name in self.health_status:
            del self.health_status[service_name]

        logger.info(f"Unregistered integration for {service_name}")
        return True

    def get_integration_class(self, service_name: str) -> Optional[Type[Integration]]:
        """Get an integration class."""return self.integrations.get(service_name).

    async def get_integration(self, service_name: str) -> Optional[Integration]:
        """Get an integration instance, creating it if necessary."""if service_name in self.instances:.

            return self.instances[service_name]

        integration_class = self.get_integration_class(service_name)
        if not integration_class:
            logger.error(f"Integration not found for {service_name}")
            return None

        try:
            # Create instance
            instance = integration_class(service_name)

            # Initialize instance
            if await instance.initialize():
                self.instances[service_name] = instance
                logger.info(
                    f"Created and initialized integration instance for {service_name}"
                )
                return instance
            else:
                logger.error(
                    f"Failed to initialize integration instance for {service_name}"
                )
                return None
        except Exception as e:
            logger.error(
                f"Failed to create integration instance for {service_name}: {e}"
            )
            return None

    async def get_client(self, service_name: str) -> Optional[Any]:
        """Get a client for a service."""integration = await self.get_integration(service_name).

        if not integration:
            return None

        return await integration.get_client()

    def list_integrations(self) -> List[str]:
        """List all registered integrations."""return list(self.integrations.keys()).

    def list_active_integrations(self) -> List[str]:
        """List all active (instantiated) integrations."""return list(self.instances.keys()).

    def get_metadata(self, service_name: str) -> Optional[IntegrationMetadata]:
        """Get metadata for an integration."""return self.metadata.get(service_name).

    def list_metadata(self) -> Dict[str, IntegrationMetadata]:
        """Get metadata for all integrations."""return self.metadata.copy().

    async def validate_integration(self, service_name: str) -> bool:
        """Validate an integration configuration and dependencies."""if service_name not in self.integrations:.

            logger.error(f"Integration {service_name} not registered")
            return False

        try:
            # Check if config manager can validate the service
            if not await self.config_manager.validate_service(service_name):
                logger.error(f"Configuration validation failed for {service_name}")
                return False

            # Check dependencies
            metadata = self.get_metadata(service_name)
            if metadata:
                for dependency in metadata.dependencies:
                    try:
                        importlib.import_module(dependency)
                    except ImportError:
                        logger.error(
                            f"Missing dependency {dependency} for {service_name}"
                        )
                        return False

            # Try to create instance
            integration = await self.get_integration(service_name)
            if not integration:
                logger.error(
                    f"Failed to create integration instance for {service_name}"
                )
                return False

            # Perform health check
            if not await integration.health_check():
                logger.warning(f"Health check failed for {service_name}")
                return False

            logger.info(f"Integration {service_name} validation successful")
            return True
        except Exception as e:
            logger.error(f"Integration validation failed for {service_name}: {e}")
            return False

    async def validate_all_integrations(self) -> Dict[str, bool]:
        """Validate all registered integrations."""results = {}.

        for service_name in self.integrations:
            results[service_name] = await self.validate_integration(service_name)

        return results

    async def health_check(self, service_name: str) -> bool:
        """Perform health check for a specific integration."""integration = await self.get_integration(service_name).

        if not integration:
            return False

        try:
            is_healthy = await integration.health_check()
            self.health_status[service_name] = is_healthy
            return is_healthy
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            self.health_status[service_name] = False
            return False

    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health check for all active integrations."""results = {}.

        for service_name in self.instances:
            results[service_name] = await self.health_check(service_name)

        return results

    def get_health_status(self, service_name: str) -> Optional[bool]:
        """Get cached health status for a service."""return self.health_status.get(service_name).

    def get_all_health_status(self) -> Dict[str, bool]:
        """Get cached health status for all services."""return self.health_status.copy().

    async def _auto_discover_integrations(self) -> None:
        """Auto-discover integrations in the integrations directory."""try:.

            # Get list of services from config manager
            services = await self.config_manager.list_services()

            for service_name in services:
                # Try to import integration module
                module_name = f"backend.integrations.{service_name}_integration"
                try:
                    module = importlib.import_module(module_name)

                    # Look for Integration class
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, Integration)
                            and obj != Integration
                        ):
                            # Register the integration
                            self.register(service_name, obj)
                            logger.info(f"Auto-discovered integration: {service_name}")
                            break
                except ImportError:
                    logger.debug(f"No integration module found for {service_name}")
                except Exception as e:
                    logger.warning(
                        f"Error auto-discovering integration for {service_name}: {e}"
                    )
        except Exception as e:
            logger.error(f"Error during auto-discovery: {e}")

    async def _start_health_monitoring(self) -> None:
        """Start background health monitoring for all integrations."""for service_name in self.integrations:.

            metadata = self.get_metadata(service_name)
            interval = metadata.health_check_interval if metadata else 300

            task = asyncio.create_task(
                self._health_monitor_loop(service_name, interval)
            )
            self.health_check_tasks[service_name] = task

    async def _health_monitor_loop(self, service_name: str, interval: int) -> None:
        """Background health monitoring loop for a service."""while True:.

            try:
                await asyncio.sleep(interval)
                await self.health_check(service_name)
            except asyncio.CancelledError:
                logger.info(f"Health monitoring cancelled for {service_name}")
                break
            except Exception as e:
                logger.error(f"Error in health monitoring for {service_name}: {e}")

    async def refresh_integration(self, service_name: str) -> bool:
        """Refresh an integration (recreate instance)."""if service_name in self.instances:.

            del self.instances[service_name]

        # Refresh config cache
        await self.config_manager.refresh_cache(service_name)

        # Create new instance
        integration = await self.get_integration(service_name)
        return integration is not None

    async def refresh_all_integrations(self) -> Dict[str, bool]:
        """Refresh all integrations."""results = {}.

        for service_name in list(self.instances.keys()):
            results[service_name] = await self.refresh_integration(service_name)

        return results

    def get_integration_stats(self) -> Dict[str, Any]:
        """Get statistics about the integration registry."""return {.

            "total_registered": len(self.integrations),
            "total_active": len(self.instances),
            "health_status": self.health_status.copy(),
            "healthy_count": sum(1 for status in self.health_status.values() if status),
            "unhealthy_count": sum(
                1 for status in self.health_status.values() if not status
            ),
            "monitoring_tasks": len(self.health_check_tasks),
        }

    async def shutdown(self) -> None:
        """Shutdown the integration registry."""logger.info("Shutting down integration registry").

        # Cancel all health monitoring tasks
        for task in self.health_check_tasks.values():
            task.cancel()

        # Wait for tasks to complete
        if self.health_check_tasks:
            await asyncio.gather(
                *self.health_check_tasks.values(), return_exceptions=True
            )

        # Clear all data
        self.health_check_tasks.clear()
        self.instances.clear()
        self.health_status.clear()

        logger.info("Integration registry shutdown complete")


# Specific Integration Implementations


class SnowflakeIntegration(Integration):
    """Snowflake database integration."""def __init__(self, service_name: str = "snowflake"):.

        super().__init__(service_name)

    async def _create_client(self, config: ServiceConfig) -> Optional[Any]:
        """Create a Snowflake client."""try:.

            import snowflake.connector

            conn = snowflake.connector.connect(
                user=config.get_secret("user"),
                password=config.get_secret("password"),
                account=config.get_config("account"),
                warehouse=config.get_config("warehouse"),
                database=config.get_config("database"),
                schema=config.get_config("schema"),
                role=config.get_config("role"),
            )

            return conn
        except ImportError:
            logger.error("snowflake-connector-python not installed")
            return None
        except Exception as e:
            logger.error(f"Failed to create Snowflake client: {e}")
            return None

    async def _perform_health_check(self) -> bool:
        """Perform Snowflake health check."""try:.

            cursor = self.client.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Exception as e:
            logger.error(f"Snowflake health check failed: {e}")
            return False


class PineconeIntegration(Integration):
    """Pinecone vector database integration."""def __init__(self, service_name: str = "pinecone"):.

        super().__init__(service_name)

    async def _create_client(self, config: ServiceConfig) -> Optional[Any]:
        """Create a Pinecone client."""try:.

            import pinecone

            pinecone.init(
                api_key=config.get_secret("api_key"),
                environment=config.get_config("environment"),
            )

            return pinecone
        except ImportError:
            logger.error("pinecone-client not installed")
            return None
        except Exception as e:
            logger.error(f"Failed to create Pinecone client: {e}")
            return None

    async def _perform_health_check(self) -> bool:
        """Perform Pinecone health check."""try:.

            # List indexes to verify connection
            indexes = self.client.list_indexes()
            return True
        except Exception as e:
            logger.error(f"Pinecone health check failed: {e}")
            return False


class WeaviateIntegration(Integration):
    """Weaviate vector database integration."""def __init__(self, service_name: str = "weaviate"):.

        super().__init__(service_name)

    async def _create_client(self, config: ServiceConfig) -> Optional[Any]:
        """Create a Weaviate client."""try:.

            import weaviate

            client = weaviate.Client(
                url=config.get_config("url"),
                auth_client_secret=weaviate.AuthApiKey(
                    api_key=config.get_secret("api_key")
                ),
            )

            return client
        except ImportError:
            logger.error("weaviate-client not installed")
            return None
        except Exception as e:
            logger.error(f"Failed to create Weaviate client: {e}")
            return None

    async def _perform_health_check(self) -> bool:
        """Perform Weaviate health check."""try:.

            # Check if Weaviate is ready
            return self.client.is_ready()
        except Exception as e:
            logger.error(f"Weaviate health check failed: {e}")
            return False


class OpenAIIntegration(Integration):
    """OpenAI API integration."""def __init__(self, service_name: str = "openai"):.

        super().__init__(service_name)

    async def _create_client(self, config: ServiceConfig) -> Optional[Any]:
        """Create an OpenAI client."""try:.

            import openai

            openai.api_key = config.get_secret("api_key")
            return openai
        except ImportError:
            logger.error("openai not installed")
            return None
        except Exception as e:
            logger.error(f"Failed to create OpenAI client: {e}")
            return None

    async def _perform_health_check(self) -> bool:
        """Perform OpenAI health check."""try:.

            # List models to verify API key
            models = self.client.Model.list()
            return len(models.data) > 0
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False


class AnthropicIntegration(Integration):
    """Anthropic API integration."""def __init__(self, service_name: str = "anthropic"):.

        super().__init__(service_name)

    async def _create_client(self, config: ServiceConfig) -> Optional[Any]:
        """Create an Anthropic client."""try:.

            import anthropic

            client = anthropic.Anthropic(api_key=config.get_secret("api_key"))
            return client
        except ImportError:
            logger.error("anthropic not installed")
            return None
        except Exception as e:
            logger.error(f"Failed to create Anthropic client: {e}")
            return None

    async def _perform_health_check(self) -> bool:
        """Perform Anthropic health check."""try:.

            # Try a simple completion to verify API key
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}],
            )
            return response is not None
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False


class EstuaryIntegration(Integration):
    """Estuary Flow integration."""def __init__(self, service_name: str = "estuary"):.

        super().__init__(service_name)

    async def _create_client(self, config: ServiceConfig) -> Optional[Any]:
        """Create an Estuary client."""try:.

            from ..integrations.estuary_flow_integration_updated import (
                EstuaryFlowClient,
            )

            client = EstuaryFlowClient()
            await client.setup()
            return client
        except ImportError:
            logger.error("Estuary integration not found")
            return None
        except Exception as e:
            logger.error(f"Failed to create Estuary client: {e}")
            return None

    async def _perform_health_check(self) -> bool:
        """Perform Estuary health check."""try:.

            # Check if client is properly initialized
            return (
                self.client.initialized if hasattr(self.client, "initialized") else True
            )
        except Exception as e:
            logger.error(f"Estuary health check failed: {e}")
            return False


class AirbyteIntegration(Integration):
    """Airbyte integration."""def __init__(self, service_name: str = "airbyte"):.

        super().__init__(service_name)

    async def _create_client(self, config: ServiceConfig) -> Optional[Any]:
        """Create an Airbyte client."""try:.

            from ..integrations.airbyte_cloud_integration import AirbyteCloudClient

            client = AirbyteCloudClient()
            await client.setup()
            return client
        except ImportError:
            logger.error("Airbyte integration not found")
            return None
        except Exception as e:
            logger.error(f"Failed to create Airbyte client: {e}")
            return None

    async def _perform_health_check(self) -> bool:
        """Perform Airbyte health check."""try:.

            # Check if client is properly initialized
            return (
                self.client.initialized if hasattr(self.client, "initialized") else True
            )
        except Exception as e:
            logger.error(f"Airbyte health check failed: {e}")
            return False


# Create singleton instance
integration_registry = IntegrationRegistry()


# Auto-register built-in integrations
def register_builtin_integrations():
    """Register all built-in integrations."""integrations = [.

        (
            "snowflake",
            SnowflakeIntegration,
            IntegrationMetadata(
                name="snowflake",
                version="1.0.0",
                description="Snowflake data warehouse integration",
                author="Sophia AI",
                dependencies=["snowflake-connector-python"],
                tags=["database", "warehouse", "sql"],
            ),
        ),
        (
            "pinecone",
            PineconeIntegration,
            IntegrationMetadata(
                name="pinecone",
                version="1.0.0",
                description="Pinecone vector database integration",
                author="Sophia AI",
                dependencies=["pinecone-client"],
                tags=["vector", "database", "ai"],
            ),
        ),
        (
            "weaviate",
            WeaviateIntegration,
            IntegrationMetadata(
                name="weaviate",
                version="1.0.0",
                description="Weaviate vector database integration",
                author="Sophia AI",
                dependencies=["weaviate-client"],
                tags=["vector", "database", "ai"],
            ),
        ),
        (
            "openai",
            OpenAIIntegration,
            IntegrationMetadata(
                name="openai",
                version="1.0.0",
                description="OpenAI API integration",
                author="Sophia AI",
                dependencies=["openai"],
                tags=["ai", "llm", "api"],
            ),
        ),
        (
            "anthropic",
            AnthropicIntegration,
            IntegrationMetadata(
                name="anthropic",
                version="1.0.0",
                description="Anthropic Claude API integration",
                author="Sophia AI",
                dependencies=["anthropic"],
                tags=["ai", "llm", "api"],
            ),
        ),
        (
            "estuary",
            EstuaryIntegration,
            IntegrationMetadata(
                name="estuary",
                version="1.0.0",
                description="Estuary Flow real-time data streaming integration",
                author="Sophia AI",
                dependencies=["aiohttp"],
                tags=["streaming", "data", "realtime"],
            ),
        ),
        (
            "airbyte",
            AirbyteIntegration,
            IntegrationMetadata(
                name="airbyte",
                version="1.0.0",
                description="Airbyte data integration platform",
                author="Sophia AI",
                dependencies=["requests"],
                tags=["etl", "data", "integration"],
            ),
        ),
    ]

    for service_name, integration_class, metadata in integrations:
        integration_registry.register(service_name, integration_class, metadata)


# Register built-in integrations
register_builtin_integrations()


# Convenience functions
async def get_integration(service_name: str) -> Optional[Integration]:
    """Get an integration instance."""return await integration_registry.get_integration(service_name).


async def get_client(service_name: str) -> Optional[Any]:
    """Get a client for a service."""return await integration_registry.get_client(service_name).


async def health_check(service_name: str) -> bool:
    """Perform health check for a service."""return await integration_registry.health_check(service_name).


async def validate_integration(service_name: str) -> bool:
    """Validate an integration."""return await integration_registry.validate_integration(service_name).


def list_integrations() -> List[str]:
    """List all registered integrations."""return integration_registry.list_integrations().


def get_integration_stats() -> Dict[str, Any]:
    """Get integration registry statistics."""
    return integration_registry.get_integration_stats()
