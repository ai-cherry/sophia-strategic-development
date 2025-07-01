"""
Sophia AI - Optimized MCP Client

High-performance client for interacting with MCP servers with advanced features:
- Connection pooling and keepalive
- Automatic compression/decompression
- Intelligent retry strategies
- Fast JSON serialization
- Comprehensive metrics collection
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import orjson

from backend.mcp_servers.optimized_network import (
    CompressionType,
    MCPNetworkConfig,
    OptimizedMCPNetwork,
    RetryStrategy,
)

logger = logging.getLogger(__name__)


class MCPClientMode(Enum):
    """MCP client operation modes."""

    STANDARD = "standard"  # Regular operation
    HIGH_THROUGHPUT = "high_throughput"  # Optimized for high throughput
    LOW_LATENCY = "low_latency"  # Optimized for low latency
    RESILIENT = "resilient"  # Optimized for reliability


@dataclass
class MCPClientConfig:
    """Configuration for optimized MCP client."""

    # Connection settings
    max_connections: int = 50
    max_connections_per_host: int = 10
    connection_timeout_seconds: float = 30.0

    # Performance settings
    enable_connection_pooling: bool = True
    enable_keepalive: bool = True
    enable_compression: bool = True
    compression_type: CompressionType = CompressionType.GZIP

    # Retry settings
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    max_retries: int = 3
    retry_delay_base_seconds: float = 0.5

    # Advanced settings
    use_orjson: bool = True
    tcp_nodelay: bool = True
    enable_dns_cache: bool = True

    # Client-specific settings
    batch_size: int = 10
    parallel_requests: int = 5
    enable_response_validation: bool = True
    enable_request_throttling: bool = False
    requests_per_second: float = 10.0


class OptimizedMCPClient:
    """
    High-performance client for interacting with MCP servers.

    Features:
    - Connection pooling with configurable limits
    - Keep-alive connections for reduced latency
    - Automatic compression/decompression
    - Intelligent retry strategies
    - Fast JSON serialization with orjson
    - Parallel request execution
    - Request batching
    - Response validation
    - Request throttling
    """

    def __init__(
        self,
        config_path: str = "mcp_config.json",
        client_mode: MCPClientMode = MCPClientMode.STANDARD,
        client_config: MCPClientConfig | None = None,
    ):
        """
        Initialize the optimized MCP client.

        Args:
            config_path: Path to the MCP configuration file
            client_mode: Operation mode for the client
            client_config: Custom client configuration
        """
        self.config = self._load_config(config_path)
        self.client_mode = client_mode

        # Use provided config or create based on mode
        if client_config:
            self.client_config = client_config
        else:
            self.client_config = self._create_config_for_mode(client_mode)

        # Initialize network layers for each server
        self.network_layers: dict[str, OptimizedMCPNetwork] = {}

        # Request throttling
        self.last_request_time = 0.0
        self.request_semaphore = asyncio.Semaphore(self.client_config.parallel_requests)

        # Statistics
        self.requests_sent = 0
        self.requests_succeeded = 0
        self.requests_failed = 0
        self.total_latency_ms = 0.0

        logger.info(f"Initialized OptimizedMCPClient in {client_mode.value} mode")

    def _create_config_for_mode(self, mode: MCPClientMode) -> MCPClientConfig:
        """Create client configuration based on operation mode."""
        if mode == MCPClientMode.HIGH_THROUGHPUT:
            return MCPClientConfig(
                max_connections=100,
                max_connections_per_host=20,
                connection_timeout_seconds=60.0,
                enable_compression=True,
                retry_strategy=RetryStrategy.LINEAR,
                max_retries=2,
                batch_size=20,
                parallel_requests=10,
                enable_response_validation=False,  # Skip validation for speed
            )

        elif mode == MCPClientMode.LOW_LATENCY:
            return MCPClientConfig(
                max_connections=50,
                max_connections_per_host=10,
                connection_timeout_seconds=10.0,
                enable_compression=False,  # Skip compression for lower latency
                retry_strategy=RetryStrategy.NONE,  # No retries for lower latency
                max_retries=0,
                batch_size=1,
                parallel_requests=5,
                tcp_nodelay=True,
            )

        elif mode == MCPClientMode.RESILIENT:
            return MCPClientConfig(
                max_connections=30,
                max_connections_per_host=5,
                connection_timeout_seconds=120.0,
                enable_compression=True,
                retry_strategy=RetryStrategy.EXPONENTIAL,
                max_retries=5,
                retry_delay_base_seconds=1.0,
                batch_size=5,
                parallel_requests=3,
                enable_response_validation=True,
            )

        # Default: STANDARD mode
        return MCPClientConfig()

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load the MCP configuration file."""
        config_file = Path(config_path)
        if not config_file.exists():
            logger.error(f"MCP config file not found at: {config_path}")
            raise FileNotFoundError(f"MCP config file not found at: {config_path}")

        try:
            with open(config_file) as f:
                if self.client_config and self.client_config.use_orjson:
                    return orjson.loads(f.read())
                else:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading MCP config: {e}")
            raise

    async def initialize(self) -> None:
        """Initialize the client and all network layers."""
        # Initialize network layers for each server
        for server_name, _server_config in self.config.get("servers", {}).items():
            network_config = MCPNetworkConfig(
                max_connections=self.client_config.max_connections,
                max_connections_per_host=self.client_config.max_connections_per_host,
                connection_timeout_seconds=self.client_config.connection_timeout_seconds,
                enable_keepalive=self.client_config.enable_keepalive,
                enable_compression=self.client_config.enable_compression,
                compression_type=self.client_config.compression_type,
                retry_strategy=self.client_config.retry_strategy,
                max_retries=self.client_config.max_retries,
                retry_delay_base_seconds=self.client_config.retry_delay_base_seconds,
                use_orjson=self.client_config.use_orjson,
                tcp_nodelay=self.client_config.tcp_nodelay,
                enable_dns_cache=self.client_config.enable_dns_cache,
            )

            network = OptimizedMCPNetwork(network_config, server_name)
            await network.initialize()
            self.network_layers[server_name] = network

        logger.info(f"Initialized network layers for {len(self.network_layers)} servers")

    async def shutdown(self) -> None:
        """Shutdown the client and all network layers."""
        for _server_name, network in self.network_layers.items():
            await network.shutdown()

        logger.info("Shut down all network layers")

    async def _throttle_request(self) -> None:
        """Throttle requests if enabled."""
        if not self.client_config.enable_request_throttling:
            return

        # Calculate time since last request
        now = time.time()
        time_since_last = now - self.last_request_time

        # Calculate minimum interval between requests
        min_interval = 1.0 / self.client_config.requests_per_second

        # Sleep if needed
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)

        # Update last request time
        self.last_request_time = time.time()

    async def _validate_response(self, response_data: Any) -> bool:
        """Validate response data."""
        if not self.client_config.enable_response_validation:
            return True

        # Basic validation
        if response_data is None:
            return False

        # Check for error field
        if isinstance(response_data, dict) and "error" in response_data:
            return False

        return True

    async def call_mcp_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any],
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """
        Call a specific tool on a specified MCP server with optimized networking.

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            timeout: Custom timeout in seconds

        Returns:
            Response data from the MCP server
        """
        start_time = time.time()

        # Check if server exists in configuration
        if server_name not in self.config.get("servers", {}):
            raise ValueError(f"MCP Server '{server_name}' not found in configuration.")

        # Check if network layer is initialized
        if server_name not in self.network_layers:
            await self.initialize()

        # Get server configuration
        server_config = self.config["servers"][server_name]
        base_url = server_config.get("baseUrl")

        if not base_url:
            raise ValueError(
                f"No baseUrl configured for MCP server '{server_name}'. Only HTTP servers are supported by this client."
            )

        # Apply throttling if enabled
        await self._throttle_request()

        # Acquire semaphore to limit parallel requests
        async with self.request_semaphore:
            try:
                # Prepare request payload
                payload = {
                    "tool_name": tool_name,
                    "arguments": arguments,
                }

                # Get network layer for this server
                network = self.network_layers[server_name]

                # Send request
                endpoint = f"{base_url}/mcp/call_tool"
                status, response_data, headers = await network.post(
                    url=endpoint,
                    data=payload,
                    timeout=timeout or self.client_config.connection_timeout_seconds,
                )

                # Check status code
                if status != 200:
                    raise Exception(f"MCP server returned status code {status}")

                # Validate response if enabled
                if not await self._validate_response(response_data):
                    raise ValueError(f"Invalid response from MCP server: {response_data}")

                # Update statistics
                self.requests_sent += 1
                self.requests_succeeded += 1
                self.total_latency_ms += (time.time() - start_time) * 1000

                return response_data

            except Exception as e:
                # Update statistics
                self.requests_sent += 1
                self.requests_failed += 1

                logger.error(f"Error calling MCP server '{server_name}': {e}")
                raise Exception(
                    f"Failed to communicate with MCP server '{server_name}'."
                ) from e

    async def batch_call_mcp_tool(
        self,
        server_name: str,
        tool_name: str,
        batch_arguments: list[dict[str, Any]],
        timeout: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        Call a specific tool on a specified MCP server with multiple sets of arguments.

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            batch_arguments: List of argument sets for the tool
            timeout: Custom timeout in seconds

        Returns:
            List of response data from the MCP server
        """
        # Split into batches
        batch_size = self.client_config.batch_size
        batches = [
            batch_arguments[i:i+batch_size]
            for i in range(0, len(batch_arguments), batch_size)
        ]

        results = []

        for batch in batches:
            # Process each batch in parallel
            tasks = [
                self.call_mcp_tool(server_name, tool_name, args, timeout)
                for args in batch
            ]

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error in batch item {i}: {result}")
                    results.append({"error": str(result)})
                else:
                    results.append(result)

        return results

    async def call_multiple_servers(
        self,
        calls: list[tuple[str, str, dict[str, Any]]],
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """
        Call multiple MCP servers in parallel.

        Args:
            calls: List of (server_name, tool_name, arguments) tuples
            timeout: Custom timeout in seconds

        Returns:
            Dictionary mapping call index to response data
        """
        tasks = [
            self.call_mcp_tool(server_name, tool_name, arguments, timeout)
            for server_name, tool_name, arguments in calls
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Create result dictionary
        return {
            i: result if not isinstance(result, Exception) else {"error": str(result)}
            for i, result in enumerate(results)
        }

    def get_statistics(self) -> dict[str, Any]:
        """Get client statistics."""
        return {
            "requests_sent": self.requests_sent,
            "requests_succeeded": self.requests_succeeded,
            "requests_failed": self.requests_failed,
            "success_rate": self.requests_succeeded / max(self.requests_sent, 1),
            "avg_latency_ms": self.total_latency_ms / max(self.requests_succeeded, 1),
            "mode": self.client_mode.value,
        }

    def reset_statistics(self) -> None:
        """Reset client statistics."""
        self.requests_sent = 0
        self.requests_succeeded = 0
        self.requests_failed = 0
        self.total_latency_ms = 0.0


# Factory function to create optimized client
def create_optimized_mcp_client(
    config_path: str = "mcp_config.json",
    mode: str = "standard",
    **config_kwargs,
) -> OptimizedMCPClient:
    """Create an optimized MCP client with custom configuration."""
    # Convert mode string to enum
    try:
        client_mode = MCPClientMode(mode.lower())
    except ValueError:
        logger.warning(f"Invalid mode '{mode}', using STANDARD mode")
        client_mode = MCPClientMode.STANDARD

    # Create custom config if kwargs provided
    client_config = MCPClientConfig(**config_kwargs) if config_kwargs else None

    return OptimizedMCPClient(config_path, client_mode, client_config)


# Example usage
async def example():
    """Example usage of the optimized MCP client."""
    client = create_optimized_mcp_client(
        mode="high_throughput",
        max_connections=50,
        enable_compression=True,
    )

    await client.initialize()

    try:
        # Single call
        result = await client.call_mcp_tool(
            server_name="example_server",
            tool_name="analyze_data",
            arguments={"data_id": "12345"},
        )
        print(f"Result: {result}")

        # Batch call
        batch_results = await client.batch_call_mcp_tool(
            server_name="example_server",
            tool_name="analyze_data",
            batch_arguments=[
                {"data_id": "12345"},
                {"data_id": "67890"},
            ],
        )
        print(f"Batch results: {batch_results}")

        # Get statistics
        stats = client.get_statistics()
        print(f"Client stats: {stats}")
    finally:
        await client.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example())

