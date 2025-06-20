"""Comprehensive Integration Tests for Sophia AI Backend
Tests all integration components and configurations
"""

import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

# Import modules to test
from backend.core.integration_config import IntegrationConfig, ServiceConfig
from backend.core.integration_registry import IntegrationRegistry
from backend.core.pulumi_esc import ESCClient
from backend.integrations.gong_integration import GongIntegration
from backend.integrations.lambda_labs_integration import LambdaLabsIntegration
from backend.integrations.vercel_integration import VercelIntegration


class TestIntegrationConfig:
    """Test the integration configuration system"""

    @pytest.fixture
    async def config_manager(self):
        """Create a test configuration manager"""
        config = IntegrationConfig()
        await config.initialize()
        return config

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test configuration manager initialization"""
        config = IntegrationConfig()
        result = await config.initialize()
        assert result is True
        assert config.initialized is True

    @pytest.mark.asyncio
    async def test_service_registry_loading(self, config_manager):
        """Test service registry loading"""
        services = await config_manager.list_services()
        assert isinstance(services, list)
        assert len(services) > 0

        # Check for expected services
        expected_services = [
            "snowflake",
            "gong",
            "vercel",
            "estuary",
            "pinecone",
            "openai",
        ]
        for service in expected_services:
            assert service in services

    @pytest.mark.asyncio
    async def test_service_config_retrieval(self, config_manager):
        """Test service configuration retrieval"""
        # Test with a known service
        config = await config_manager.get_service_config("gong")
        assert config is not None
        assert isinstance(config, ServiceConfig)
        assert config.service_name == "gong"
        assert isinstance(config.config, dict)
        assert isinstance(config.secrets, dict)
        assert isinstance(config.metadata, dict)

    @pytest.mark.asyncio
    async def test_service_validation(self, config_manager):
        """Test service configuration validation"""
        # Test with a known service
        is_valid = await config_manager.validate_service("gong")
        assert isinstance(is_valid, bool)

        # Test with unknown service
        is_valid = await config_manager.validate_service("unknown_service")
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_cache_functionality(self, config_manager):
        """Test configuration caching"""
        # Get config twice to test caching
        config1 = await config_manager.get_service_config("gong")
        config2 = await config_manager.get_service_config("gong")

        assert config1 is not None
        assert config2 is not None
        assert config1.service_name == config2.service_name

        # Test cache refresh
        await config_manager.refresh_cache("gong")
        config3 = await config_manager.get_service_config("gong")
        assert config3 is not None


class TestIntegrationRegistry:
    """Test the integration registry system"""

    @pytest.fixture
    async def registry(self):
        """Create a test integration registry"""
        registry = IntegrationRegistry()
        await registry.initialize()
        return registry

    @pytest.mark.asyncio
    async def test_registry_initialization(self):
        """Test registry initialization"""
        registry = IntegrationRegistry()
        result = await registry.initialize()
        assert result is True
        assert registry.initialized is True

    @pytest.mark.asyncio
    async def test_integration_listing(self, registry):
        """Test listing integrations"""
        integrations = registry.list_integrations()
        assert isinstance(integrations, list)
        assert len(integrations) > 0

        # Check for expected integrations
        expected_integrations = ["snowflake", "pinecone", "openai", "anthropic"]
        for integration in expected_integrations:
            assert integration in integrations

    @pytest.mark.asyncio
    async def test_integration_validation(self, registry):
        """Test integration validation"""
        # Test with built-in integrations
        for integration_name in ["snowflake", "pinecone", "openai"]:
            # Note: This might fail if dependencies aren't installed, which is expected
            result = await registry.validate_integration(integration_name)
            assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_health_checks(self, registry):
        """Test health check functionality"""
        # Test health check for all integrations
        health_status = await registry.health_check_all()
        assert isinstance(health_status, dict)

        # Test individual health checks
        for service_name in registry.list_integrations():
            health = await registry.health_check(service_name)
            assert isinstance(health, bool)

    @pytest.mark.asyncio
    async def test_integration_stats(self, registry):
        """Test integration statistics"""
        stats = registry.get_integration_stats()
        assert isinstance(stats, dict)
        assert "total_registered" in stats
        assert "total_active" in stats
        assert "health_status" in stats
        assert isinstance(stats["total_registered"], int)
        assert isinstance(stats["total_active"], int)


class TestPulumiESCClient:
    """Test the Pulumi ESC client"""

    @pytest.fixture
    def esc_client(self):
        """Create a test ESC client"""
        return ESCClient(
            organization="test-org", project="test-project", stack="test-stack"
        )

    @pytest.mark.asyncio
    async def test_client_initialization(self, esc_client):
        """Test ESC client initialization"""
        assert esc_client.organization == "test-org"
        assert esc_client.project == "test-project"
        assert esc_client.stack == "test-stack"
        assert esc_client.base_url == "https://api.pulumi.com"

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_configuration_retrieval(self, mock_get, esc_client):
        """Test configuration retrieval with mocked response"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"test_key": "test_value"}
        mock_get.return_value.__aenter__.return_value = mock_response

        # Test configuration retrieval
        result = await esc_client.get_configuration("test_key")
        assert result == {"test_key": "test_value"}

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_secret_retrieval(self, mock_get, esc_client):
        """Test secret retrieval with mocked response"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"secret_value": "encrypted_secret"}
        mock_get.return_value.__aenter__.return_value = mock_response

        # Test secret retrieval
        result = await esc_client.get_secret("test_secret")
        assert result == {"secret_value": "encrypted_secret"}


class TestGongIntegration:
    """Test Gong integration"""

    @pytest.fixture
    def gong_integration(self):
        """Create a test Gong integration"""
        return GongIntegration()

    @pytest.mark.asyncio
    @patch("backend.integrations.gong_integration.aiohttp.ClientSession")
    async def test_gong_client_creation(self, mock_session, gong_integration):
        """Test Gong client creation"""
        # Mock service config
        mock_config = ServiceConfig(
            service_name="gong",
            config={"base_url": "https://api.gong.io"},
            secrets={"api_key": "test_key"},
        )

        # Test client creation
        client = await gong_integration._create_client(mock_config)
        assert client is not None

    @pytest.mark.asyncio
    @patch("backend.integrations.gong_integration.aiohttp.ClientSession.get")
    async def test_gong_health_check(self, mock_get, gong_integration):
        """Test Gong health check"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response

        # Set up client
        gong_integration.session = AsyncMock()
        gong_integration.base_url = "https://api.gong.io"

        # Test health check
        result = await gong_integration._perform_health_check()
        assert result is True


class TestVercelIntegration:
    """Test Vercel integration"""

    @pytest.fixture
    def vercel_integration(self):
        """Create a test Vercel integration"""
        return VercelIntegration()

    @pytest.mark.asyncio
    @patch("backend.integrations.vercel_integration.aiohttp.ClientSession")
    async def test_vercel_client_creation(self, mock_session, vercel_integration):
        """Test Vercel client creation"""
        # Mock service config
        mock_config = ServiceConfig(
            service_name="vercel",
            config={"team_id": "test_team"},
            secrets={"token": "test_token"},
        )

        # Test client creation
        client = await vercel_integration._create_client(mock_config)
        assert client is not None

    @pytest.mark.asyncio
    @patch("backend.integrations.vercel_integration.aiohttp.ClientSession.get")
    async def test_vercel_health_check(self, mock_get, vercel_integration):
        """Test Vercel health check"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response

        # Set up client
        vercel_integration.session = AsyncMock()
        vercel_integration.base_url = "https://api.vercel.com"

        # Test health check
        result = await vercel_integration._perform_health_check()
        assert result is True


class TestLambdaLabsIntegration:
    """Test Lambda Labs integration"""

    @pytest.fixture
    def lambda_labs_integration(self):
        """Create a test Lambda Labs integration"""
        return LambdaLabsIntegration()

    @pytest.mark.asyncio
    @patch("backend.integrations.lambda_labs_integration.aiohttp.ClientSession")
    async def test_lambda_labs_client_creation(
        self, mock_session, lambda_labs_integration
    ):
        """Test Lambda Labs client creation"""
        # Mock service config
        mock_config = ServiceConfig(
            service_name="lambda_labs", config={}, secrets={"api_key": "test_key"}
        )

        # Test client creation
        client = await lambda_labs_integration._create_client(mock_config)
        assert client is not None

    @pytest.mark.asyncio
    @patch("backend.integrations.lambda_labs_integration.aiohttp.ClientSession.get")
    async def test_lambda_labs_health_check(self, mock_get, lambda_labs_integration):
        """Test Lambda Labs health check"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response

        # Set up client
        lambda_labs_integration.session = AsyncMock()
        lambda_labs_integration.base_url = "https://cloud.lambdalabs.com/api/v1"

        # Test health check
        result = await lambda_labs_integration._perform_health_check()
        assert result is True


class TestEndToEndIntegration:
    """End-to-end integration tests"""

    @pytest.mark.asyncio
    async def test_full_integration_flow(self):
        """Test complete integration flow"""
        # Initialize configuration manager
        config_manager = IntegrationConfig()
        await config_manager.initialize()

        # Initialize registry
        registry = IntegrationRegistry()
        await registry.initialize()

        # Test service listing
        services = await config_manager.list_services()
        assert len(services) > 0

        # Test integration listing
        integrations = registry.list_integrations()
        assert len(integrations) > 0

        # Test health checks
        health_status = await registry.health_check_all()
        assert isinstance(health_status, dict)

        # Test statistics
        stats = registry.get_integration_stats()
        assert isinstance(stats, dict)
        assert stats["total_registered"] > 0

    @pytest.mark.asyncio
    async def test_configuration_validation_flow(self):
        """Test configuration validation flow"""
        # Initialize configuration manager
        config_manager = IntegrationConfig()
        await config_manager.initialize()

        # Test service validation for all services
        services = await config_manager.list_services()
        for service in services:
            # Get service config
            config = await config_manager.get_service_config(service)
            assert config is not None

            # Validate service
            is_valid = await config_manager.validate_service(service)
            assert isinstance(is_valid, bool)

    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test cache performance and functionality"""
        config_manager = IntegrationConfig()
        await config_manager.initialize()

        # Test multiple retrievals for caching
        service_name = "gong"

        # First retrieval (should cache)
        config1 = await config_manager.get_service_config(service_name)
        assert config1 is not None

        # Second retrieval (should use cache)
        config2 = await config_manager.get_service_config(service_name)
        assert config2 is not None
        assert config1.service_name == config2.service_name

        # Test cache refresh
        await config_manager.refresh_cache(service_name)

        # Third retrieval (should refresh cache)
        config3 = await config_manager.get_service_config(service_name)
        assert config3 is not None


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test utilities
def create_mock_service_config(
    service_name: str, config: Dict[str, Any] = None, secrets: Dict[str, str] = None
) -> ServiceConfig:
    """Create a mock service configuration for testing"""
    return ServiceConfig(
        service_name=service_name,
        config=config or {},
        secrets=secrets or {},
        metadata={"type": "test", "config_keys": [], "secret_keys": []},
    )


def create_mock_response(
    status: int = 200, json_data: Dict[str, Any] = None
) -> AsyncMock:
    """Create a mock HTTP response for testing"""
    mock_response = AsyncMock()
    mock_response.status = status
    mock_response.json.return_value = json_data or {}
    return mock_response


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
