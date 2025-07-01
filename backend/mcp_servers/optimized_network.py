"""
Optimized MCP Network Layer for Sophia AI Platform.

This module provides high-performance networking capabilities for MCP servers
with connection pooling, keepalive, compression, and advanced retry strategies.
"""

import asyncio
import gzip
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import aiohttp
import orjson
from aiohttp import ClientSession, TCPConnector
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class CompressionType(str, Enum):
    """Compression types for network optimization."""

    NONE = "none"
    GZIP = "gzip"
    BROTLI = "br"  # If brotli library is available


class RetryStrategy(str, Enum):
    """Retry strategies for network resilience."""

    NONE = "none"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"


@dataclass
class NetworkStats:
    """Network statistics for monitoring and optimization."""

    bytes_sent: int = 0
    bytes_received: int = 0
    requests_sent: int = 0
    requests_received: int = 0
    failed_requests: int = 0
    retried_requests: int = 0
    avg_latency_ms: float = 0.0
    compression_ratio: float = 1.0  # 1.0 means no compression benefit
    connection_errors: int = 0
    timeout_errors: int = 0


@dataclass
class MCPNetworkConfig:
    """Configuration for the optimized MCP network layer."""

    # Connection settings
    max_connections: int = 100
    max_connections_per_host: int = 20
    connection_timeout_seconds: float = 30.0
    keepalive_timeout_seconds: float = 60.0

    # Performance settings
    enable_connection_pooling: bool = True
    enable_keepalive: bool = True
    enable_compression: bool = True
    compression_type: CompressionType = CompressionType.GZIP
    compression_threshold_bytes: int = 1024  # Only compress if larger than this

    # Retry settings
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    max_retries: int = 3
    retry_delay_base_seconds: float = 0.5
    retry_max_delay_seconds: float = 10.0

    # Advanced settings
    use_orjson: bool = True  # Use faster JSON serialization/deserialization
    tcp_nodelay: bool = True  # Disable Nagle's algorithm
    enable_dns_cache: bool = True
    dns_cache_ttl_seconds: int = 300  # 5 minutes

    # Metrics
    enable_metrics: bool = True
    metrics_prefix: str = "mcp_network"


class OptimizedMCPNetwork:
    """
    High-performance network layer for MCP servers with advanced optimization features.

    Features:
    - Connection pooling with configurable limits
    - Keep-alive connections for reduced latency
    - Automatic compression/decompression
    - Intelligent retry strategies
    - Fast JSON serialization with orjson
    - Comprehensive metrics collection
    - TCP optimizations (TCP_NODELAY)
    - DNS caching
    """

    def __init__(self, config: MCPNetworkConfig, server_name: str):
        """Initialize the optimized network layer."""
        self.config = config
        self.server_name = server_name
        self.session: ClientSession | None = None
        self.stats = NetworkStats()

        # Initialize metrics if enabled
        if config.enable_metrics:
            self._initialize_metrics()

        logger.info(f"Initialized OptimizedMCPNetwork for {server_name}")

    def _initialize_metrics(self) -> None:
        """Initialize Prometheus metrics for monitoring."""
        prefix = f"{self.config.metrics_prefix}_{self.server_name}"

        # Network throughput metrics
        self.bytes_sent_counter = Counter(
            f"{prefix}_bytes_sent_total",
            "Total bytes sent over the network",
        )
        self.bytes_received_counter = Counter(
            f"{prefix}_bytes_received_total",
            "Total bytes received over the network",
        )

        # Request metrics
        self.requests_counter = Counter(
            f"{prefix}_requests_total", "Total network requests", ["method", "status"]
        )
        self.request_latency = Histogram(
            f"{prefix}_request_latency_seconds",
            "Request latency in seconds",
            ["method"],
        )

        # Retry metrics
        self.retry_counter = Counter(
            f"{prefix}_retries_total", "Total retry attempts", ["reason"]
        )

        # Connection metrics
        self.active_connections_gauge = Gauge(
            f"{prefix}_active_connections", "Number of active connections"
        )
        self.connection_errors_counter = Counter(
            f"{prefix}_connection_errors_total",
            "Total connection errors",
            ["error_type"],
        )

        # Compression metrics
        self.compression_ratio_gauge = Gauge(
            f"{prefix}_compression_ratio",
            "Compression ratio (uncompressed / compressed)",
        )

        logger.info(f"Metrics initialized for {self.server_name} network layer")

    async def initialize(self) -> None:
        """Initialize the network layer and create the aiohttp session."""
        # Configure TCP connector with optimized settings
        connector = TCPConnector(
            limit=self.config.max_connections,
            limit_per_host=self.config.max_connections_per_host,
            enable_cleanup_closed=True,
            force_close=not self.config.enable_keepalive,
            tcp_nodelay=self.config.tcp_nodelay,
            ttl_dns_cache=(
                self.config.dns_cache_ttl_seconds
                if self.config.enable_dns_cache
                else None
            ),
        )

        # Configure timeout
        timeout = aiohttp.ClientTimeout(
            total=self.config.connection_timeout_seconds,
            connect=min(5.0, self.config.connection_timeout_seconds / 2),
            sock_connect=min(5.0, self.config.connection_timeout_seconds / 2),
            sock_read=self.config.connection_timeout_seconds,
        )

        # Create session with optimized settings
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            json_serialize=orjson.dumps if self.config.use_orjson else json.dumps,
            headers={
                "User-Agent": f"SophiaAI-MCP/{self.server_name}",
                "Connection": "keep-alive" if self.config.enable_keepalive else "close",
                "Accept-Encoding": (
                    self.config.compression_type.value
                    if self.config.enable_compression
                    else "identity"
                ),
            },
        )

        logger.info(f"Network layer initialized for {self.server_name}")

    async def shutdown(self) -> None:
        """Shutdown the network layer and close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info(f"Network layer shut down for {self.server_name}")

    async def _compress_data(
        self, data: str | bytes | dict[str, Any]
    ) -> tuple[bytes, bool]:
        """Compress data if it exceeds the threshold size."""
        # Convert to bytes if needed
        if isinstance(data, dict):
            data_bytes = (
                orjson.dumps(data)
                if self.config.use_orjson
                else json.dumps(data).encode("utf-8")
            )
        elif isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = data

        # Check if compression is needed
        if (
            not self.config.enable_compression
            or len(data_bytes) < self.config.compression_threshold_bytes
        ):
            return data_bytes, False

        # Compress based on selected algorithm
        if self.config.compression_type == CompressionType.GZIP:
            compressed = gzip.compress(data_bytes)
            compression_ratio = len(data_bytes) / max(len(compressed), 1)

            # Update metrics
            if self.config.enable_metrics:
                self.compression_ratio_gauge.set(compression_ratio)

            # Update stats
            self.stats.compression_ratio = compression_ratio

            return compressed, True

        # Default: no compression
        return data_bytes, False

    async def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay for retry based on the configured strategy."""
        if self.config.retry_strategy == RetryStrategy.NONE or attempt <= 0:
            return 0

        base_delay = self.config.retry_delay_base_seconds

        if self.config.retry_strategy == RetryStrategy.LINEAR:
            delay = base_delay * attempt
        elif self.config.retry_strategy == RetryStrategy.EXPONENTIAL:
            delay = base_delay * (2 ** (attempt - 1))
        elif self.config.retry_strategy == RetryStrategy.FIBONACCI:
            # Calculate Fibonacci number (simplified)
            a, b = 1, 1
            for _ in range(attempt - 1):
                a, b = b, a + b
            delay = base_delay * a
        else:
            delay = base_delay

        # Add jitter (±20%) to prevent thundering herd
        jitter = delay * 0.2 * (2 * asyncio.get_event_loop().time() % 1 - 0.5)
        delay += jitter

        # Cap at max delay
        return min(delay, self.config.retry_max_delay_seconds)

    async def request(
        self,
        method: str,
        url: str,
        data: dict[str, Any] | str | bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        retry_for_statuses: list[int] | None = None,
    ) -> tuple[int, Any, dict[str, str]]:
        """
        Send an HTTP request with optimized networking.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL
            data: Request data (dict, string, or bytes)
            headers: Additional headers
            timeout: Custom timeout in seconds
            retry_for_statuses: List of HTTP status codes that should trigger a retry

        Returns:
            Tuple of (status_code, response_data, response_headers)
        """
        if not self.session:
            await self.initialize()

        if not self.session or self.session.closed:
            raise RuntimeError("Network session is not initialized or closed")

        # Prepare headers
        request_headers = headers or {}

        # Prepare data and handle compression
        compressed_data = None
        if data is not None:
            compressed_data, is_compressed = await self._compress_data(data)
            if is_compressed:
                request_headers["Content-Encoding"] = self.config.compression_type.value

        # Set custom timeout if provided
        request_timeout = aiohttp.ClientTimeout(total=timeout) if timeout else None

        # Initialize metrics
        start_time = time.time()
        attempt = 0
        max_attempts = self.config.max_retries + 1  # +1 for the initial attempt

        # Default retry statuses if not specified
        if retry_for_statuses is None:
            retry_for_statuses = [408, 429, 500, 502, 503, 504]

        while attempt < max_attempts:
            attempt += 1

            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    data=compressed_data,
                    headers=request_headers,
                    timeout=request_timeout,
                    allow_redirects=True,
                ) as response:
                    # Read response data
                    response_data = await response.read()

                    # Update metrics
                    request_duration = time.time() - start_time
                    if self.config.enable_metrics:
                        self.requests_counter.labels(
                            method=method, status=response.status
                        ).inc()
                        self.request_latency.labels(method=method).observe(
                            request_duration
                        )
                        self.bytes_sent_counter.inc(
                            len(compressed_data) if compressed_data else 0
                        )
                        self.bytes_received_counter.inc(len(response_data))

                    # Update stats
                    self.stats.requests_sent += 1
                    self.stats.requests_received += 1
                    self.stats.bytes_sent += (
                        len(compressed_data) if compressed_data else 0
                    )
                    self.stats.bytes_received += len(response_data)
                    self.stats.avg_latency_ms = (
                        self.stats.avg_latency_ms * (self.stats.requests_received - 1)
                        + request_duration * 1000
                    ) / self.stats.requests_received

                    # Check if we need to retry based on status code
                    if response.status in retry_for_statuses and attempt < max_attempts:
                        logger.warning(
                            f"Request to {url} failed with status {response.status}, "
                            f"retrying ({attempt}/{max_attempts-1})"
                        )

                        # Update retry metrics
                        if self.config.enable_metrics:
                            self.retry_counter.labels(
                                reason=f"status_{response.status}"
                            ).inc()

                        self.stats.retried_requests += 1

                        # Calculate and wait for retry delay
                        retry_delay = await self._calculate_retry_delay(attempt)
                        await asyncio.sleep(retry_delay)
                        continue

                    # Parse JSON response if content type is application/json
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        try:
                            if self.config.use_orjson:
                                response_body = orjson.loads(response_data)
                            else:
                                response_body = json.loads(response_data)
                        except (json.JSONDecodeError, ValueError):
                            # If JSON parsing fails, return raw data
                            response_body = response_data
                    else:
                        # For non-JSON responses, return raw data
                        response_body = response_data

                    return response.status, response_body, dict(response.headers)

            except (TimeoutError, aiohttp.ClientError) as e:
                # Update error metrics
                if self.config.enable_metrics:
                    error_type = (
                        "timeout"
                        if isinstance(e, asyncio.TimeoutError)
                        else "connection"
                    )
                    self.connection_errors_counter.labels(error_type=error_type).inc()

                # Update stats
                self.stats.connection_errors += 1
                if isinstance(e, asyncio.TimeoutError):
                    self.stats.timeout_errors += 1

                # Check if we should retry
                if attempt < max_attempts:
                    logger.warning(
                        f"Request to {url} failed with error: {str(e)}, "
                        f"retrying ({attempt}/{max_attempts-1})"
                    )

                    # Update retry metrics
                    if self.config.enable_metrics:
                        self.retry_counter.labels(reason=type(e).__name__).inc()

                    self.stats.retried_requests += 1

                    # Calculate and wait for retry delay
                    retry_delay = await self._calculate_retry_delay(attempt)
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    # Max retries reached, raise the exception
                    logger.error(
                        f"Request to {url} failed after {max_attempts} attempts: {str(e)}"
                    )
                    self.stats.failed_requests += 1
                    raise

        # This should not be reached due to the raise in the except block
        raise RuntimeError("Unexpected end of request method")

    async def get(self, url: str, **kwargs) -> tuple[int, Any, dict[str, str]]:
        """Send a GET request."""
        return await self.request("GET", url, **kwargs)

    async def post(
        self, url: str, data: dict[str, Any] | str | bytes | None = None, **kwargs
    ) -> tuple[int, Any, dict[str, str]]:
        """Send a POST request."""
        return await self.request("POST", url, data=data, **kwargs)

    async def put(
        self, url: str, data: dict[str, Any] | str | bytes | None = None, **kwargs
    ) -> tuple[int, Any, dict[str, str]]:
        """Send a PUT request."""
        return await self.request("PUT", url, data=data, **kwargs)

    async def delete(self, url: str, **kwargs) -> tuple[int, Any, dict[str, str]]:
        """Send a DELETE request."""
        return await self.request("DELETE", url, **kwargs)

    async def head(self, url: str, **kwargs) -> tuple[int, Any, dict[str, str]]:
        """Send a HEAD request."""
        return await self.request("HEAD", url, **kwargs)

    async def options(self, url: str, **kwargs) -> tuple[int, Any, dict[str, str]]:
        """Send an OPTIONS request."""
        return await self.request("OPTIONS", url, **kwargs)

    async def patch(
        self, url: str, data: dict[str, Any] | str | bytes | None = None, **kwargs
    ) -> tuple[int, Any, dict[str, str]]:
        """Send a PATCH request."""
        return await self.request("PATCH", url, data=data, **kwargs)

    def get_stats(self) -> NetworkStats:
        """Get current network statistics."""
        return self.stats

    def reset_stats(self) -> None:
        """Reset network statistics."""
        self.stats = NetworkStats()


# Factory function to create optimized network layer
def create_optimized_network(server_name: str, **config_kwargs) -> OptimizedMCPNetwork:
    """Create an optimized network layer with custom configuration."""
    config = MCPNetworkConfig(**config_kwargs)
    return OptimizedMCPNetwork(config, server_name)


# Example usage
async def example():
    """Example usage of the optimized network layer."""
    network = create_optimized_network(
        "example_server",
        max_connections=50,
        enable_compression=True,
        retry_strategy=RetryStrategy.EXPONENTIAL,
    )

    await network.initialize()

    try:
        status, data, headers = await network.get("https://api.example.com/data")
        print(f"Status: {status}")
        print(f"Data: {data}")
        print(f"Headers: {headers}")

        stats = network.get_stats()
        print(f"Network stats: {stats}")
    finally:
        await network.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example())
