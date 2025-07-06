import asyncio
import logging
from enum import Enum
from typing import Optional, Union

from backend.core.auto_esc_config import get_config_value
from backend.core.optimized_cache import OptimizedCache
from backend.services.circuit_breaker import CircuitBreaker, ConnectionError

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    SNOWFLAKE = "snowflake"
    GONG = "gong"
    HUBSPOT = "hubspot"
    SLACK = "slack"
    LINEAR = "linear"
    PINECONE = "pinecone"
    REDIS = "redis"


class DataError(Exception):
    """Base exception for data-related errors"""

    pass


class DataValidationError(DataError):
    """Raised when data validation fails"""

    pass


class EmptyResultError(DataError):
    """Raised when query returns no results"""

    pass


class DataSourceManager:
    """Centralized manager for all data sources"""

    def __init__(self):
        self.cache = OptimizedCache()
        self.feature_flags = self._load_feature_flags()
        self.circuit_breakers = {
            source: CircuitBreaker(name=source.value) for source in DataSourceType
        }
        # In a real implementation, self.sources would hold connector instances
        # self.sources = self._initialize_sources()

    def _load_feature_flags(self) -> dict[str, bool]:
        """Load feature flags from Pulumi ESC"""
        try:
            return {
                "enable_real_data": get_config_value(
                    "features.enable_real_data", False
                ),
                "enable_mock_data": get_config_value("features.enable_mock_data", True),
                "enable_caching": get_config_value("features.enable_caching", True),
                "enable_snowflake": get_config_value(
                    "data_sources.snowflake.enabled", True
                ),
                "enable_gong": get_config_value("data_sources.gong.enabled", True),
                "enable_hubspot": get_config_value(
                    "data_sources.hubspot.enabled", True
                ),
            }
        except Exception as e:
            logger.error(f"Failed to load feature flags from Pulumi ESC: {e}")
            # Return a default safe configuration
            return {
                "enable_real_data": False,
                "enable_mock_data": True,
                "enable_caching": False,
                "enable_snowflake": False,
                "enable_gong": False,
                "enable_hubspot": False,
            }

    async def fetch_data(
        self,
        source: DataSourceType,
        query: str,
        params: Optional[dict] = None,
        use_cache: bool = True,
    ) -> Union[list[dict], dict]:
        """Fetch data from specified source with caching and error handling"""

        if not self.feature_flags.get(f"enable_{source.value}", False):
            raise DataError(
                f"Data source '{source.value}' is not enabled in feature flags."
            )

        if not self.feature_flags["enable_real_data"]:
            if self.feature_flags["enable_mock_data"]:
                return self._get_mock_data(source, query)
            raise DataError("Real data disabled and no mock data available")

        cache_key = f"{source.value}:{query}:{str(params)}"
        if use_cache and self.feature_flags["enable_caching"]:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for {source.value} query.")
                return cached_data
            logger.info(f"Cache miss for {source.value} query.")

        async def _fetch_operation():
            # This is where the actual data fetching logic would go.
            # For now, it's a placeholder.
            logger.info(f"Fetching real data from {source.value}...")
            # In a real implementation, you would call the specific source's fetch method.
            # e.g., data = await self.sources[source].fetch(query, params)
            await asyncio.sleep(0.5)  # Simulate network latency

            # Placeholder data
            data = {"result": f"Real data for {source.value} with query '{query}'"}

            self._validate_data(data, source)
            return data

        try:
            breaker = self.circuit_breakers[source]
            data = await breaker.call(_fetch_operation)

            if use_cache and self.feature_flags["enable_caching"]:
                ttl = self._get_cache_ttl(source)
                await self.cache.set(cache_key, data, ttl)

            return data

        except ConnectionError as e:
            logger.error(f"Connection error for {source.value}: {e}")
            raise
        except EmptyResultError as e:
            logger.warning(f"Empty result for {source.value}: {e}")
            return []
        except DataValidationError as e:
            logger.error(f"Data validation error for {source.value}: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error fetching from {source.value}")
            raise DataError(f"Failed to fetch from {source.value}: {e}")

    def _get_mock_data(self, source: DataSourceType, query: str) -> dict:
        """Returns mock data for a given source and query."""
        logger.info(f"Returning mock data for {source.value}")
        return {
            "data": f"Mock data for {source.value} query: {query}",
            "source": "mock",
        }

    def _validate_data(self, data: any, source: DataSourceType):
        """Validates the data from a source."""
        logger.info(f"Validating data from {source.value}...")
        if data is None:
            raise DataValidationError("Data is None")
        # Add more sophisticated validation logic here.
        pass

    def _get_cache_ttl(self, source: DataSourceType) -> int:
        """Get cache time-to-live in seconds for a given source."""
        ttl_map = {
            DataSourceType.SNOWFLAKE: 3600,  # 1 hour
            DataSourceType.GONG: 3600 * 6,  # 6 hours
            DataSourceType.HUBSPOT: 900,  # 15 minutes
            DataSourceType.SLACK: 60,  # 1 minute
            DataSourceType.LINEAR: 60,  # 1 minute
            DataSourceType.PINECONE: 3600 * 24,  # 24 hours
            DataSourceType.REDIS: 300,  # 5 minutes
        }
        return ttl_map.get(source, 300)
