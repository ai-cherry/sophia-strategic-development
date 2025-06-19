"""
Unit Tests for Sophia AI Backend Core Components
Tests individual components in isolation
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from backend.core.integration_config import (
    IntegrationConfig, 
    ServiceConfig, 
    ConfigurationError,
    retry_on_failure
)
from backend.core.integration_registry import (
    IntegrationRegistry,
    IntegrationMetadata,
    Integration
)
from backend.core.pulumi_esc import ESCClient


class TestServiceConfig:
    """Test ServiceConfig class"""
    
    def test_service_config_creation(self):
        """Test ServiceConfig creation"""
        config = ServiceConfig(
            service_name="test_service",
            config={"key1": "value1"},
            secrets={"secret1": "secret_value"},
            metadata={"type": "test"}
        )
        
        assert config.service_name == "test_service"
        assert config.config["key1"] == "value1"
        assert config.secrets["secret1"] == "secret_value"
        assert config.metadata["type"] == "test"
    
    def test_service_config_methods(self):
        """Test ServiceConfig helper methods"""
        config = ServiceConfig(
            service_name="test_service",
            config={"key1": "value1", "key2": "value2"},
            secrets={"secret1": "secret_value"}
        )
        
        # Test get_config
        assert config.get_config("key1") == "value1"
        assert config.get_config("nonexistent", "default") == "default"
        
        # Test get_secret
        assert config.get_secret("secret1") == "secret_value"
        assert config.get_secret("nonexistent", "default") == "default"
        
        # Test has_config
        assert config.has_config("key1") is True
        assert config.has_config("nonexistent") is False
        
        # Test has_secret
        assert config.has_secret("secret1") is True
        assert config.has_secret("nonexistent") is False
        
        # Test validation methods
        assert config.validate_required_config(["key1", "key2"]) is True
        assert config.validate_required_config(["key1", "nonexistent"]) is False
        assert config.validate_required_secrets(["secret1"]) is True
        assert config.validate_required_secrets(["nonexistent"]) is False


class TestRetryDecorator:
    """Test retry decorator functionality"""
    
    @pytest.mark.asyncio
    async def test_retry_success(self):
        """Test retry decorator with successful function"""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.1)
        async def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await successful_function()
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_with_failures(self):
        """Test retry decorator with initial failures"""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.1)
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await failing_function()
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_max_retries_exceeded(self):
        """Test retry decorator when max retries exceeded"""
        call_count = 0
        
        @retry_on_failure(max_retries=2, delay=0.1)
        async def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Always fails")
        
        with pytest.raises(Exception, match="Always fails"):
            await always_failing_function()
        
        assert call_count == 2


class TestIntegrationConfigUnit:
    """Unit tests for IntegrationConfig class"""
    
    @pytest.fixture
    def integration_config(self):
        """Create IntegrationConfig instance for testing"""
        return IntegrationConfig()
    
    def test_integration_config_initialization(self, integration_config):
        """Test IntegrationConfig initialization"""
        assert integration_config.configs == {}
        assert integration_config.secrets == {}
        assert integration_config.esc_client is None
        assert integration_config.initialized is False
        assert integration_config.environment == "production"
        assert integration_config.cache_ttl == 300
    
    def test_validate_service_registry(self, integration_config):
        """Test service registry validation"""
        # Valid registry
        valid_registry = {
            "service1": {
                "type": "api",
                "config_keys": ["key1"],
                "secret_keys": ["secret1"]
            }
        }
        assert integration_config._validate_service_registry(valid_registry) is True
        
        # Invalid registry (missing required fields)
        invalid_registry = {
            "service1": {
                "type": "api"
                # Missing config_keys and secret_keys
            }
        }
        assert integration_config._validate_service_registry(invalid_registry) is False
        
        # Invalid registry (not a dict)
        assert integration_config._validate_service_registry("not_a_dict") is False
    
    def test_create_default_registry(self, integration_config):
        """Test default registry creation"""
        registry = integration_config._create_default_registry()
        
        assert isinstance(registry, dict)
        assert len(registry) > 0
        
        # Check for expected services
        expected_services = ["snowflake", "gong", "vercel", "estuary", "pinecone"]
        for service in expected_services:
            assert service in registry
            assert "type" in registry[service]
            assert "config_keys" in registry[service]
            assert "secret_keys" in registry[service]
    
    def test_validate_service_config(self, integration_config):
        """Test service configuration validation"""
        # Set up test registry
        integration_config.configs = {
            "test_service": {
                "type": "test",
                "config_keys": ["required_config"],
                "secret_keys": ["required_secret"]
            }
        }
        
        # Valid configuration
        config = {"required_config": "value"}
        secrets = {"required_secret": "secret"}
        assert integration_config._validate_service_config("test_service", config, secrets) is True
        
        # Missing secret (should fail)
        config = {"required_config": "value"}
        secrets = {}
        assert integration_config._validate_service_config("test_service", config, secrets) is False


class TestIntegrationMetadata:
    """Test IntegrationMetadata class"""
    
    def test_integration_metadata_creation(self):
        """Test IntegrationMetadata creation"""
        metadata = IntegrationMetadata(
            name="test_integration",
            version="1.0.0",
            description="Test integration",
            author="Test Author",
            dependencies=["requests"],
            config_schema={"type": "object"},
            secret_schema={"type": "object"},
            health_check_interval=300,
            retry_attempts=3,
            timeout=30,
            tags=["test", "api"]
        )
        
        assert metadata.name == "test_integration"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test integration"
        assert metadata.author == "Test Author"
        assert metadata.dependencies == ["requests"]
        assert metadata.health_check_interval == 300
        assert metadata.retry_attempts == 3
        assert metadata.timeout == 30
        assert metadata.tags == ["test", "api"]
    
    def test_integration_metadata_defaults(self):
        """Test IntegrationMetadata default values"""
        metadata = IntegrationMetadata(
            name="test_integration",
            version="1.0.0",
            description="Test integration",
            author="Test Author"
        )
        
        assert metadata.dependencies == []
        assert metadata.config_schema == {}
        assert metadata.secret_schema == {}
        assert metadata.health_check_interval == 300
        assert metadata.retry_attempts == 3
        assert metadata.timeout == 30
        assert metadata.tags == []


class TestIntegrationRegistryUnit:
    """Unit tests for IntegrationRegistry class"""
    
    @pytest.fixture
    def integration_registry(self):
        """Create IntegrationRegistry instance for testing"""
        return IntegrationRegistry()
    
    def test_integration_registry_initialization(self, integration_registry):
        """Test IntegrationRegistry initialization"""
        assert integration_registry.integrations == {}
        assert integration_registry.instances == {}
        assert integration_registry.metadata == {}
        assert integration_registry.initialized is False
        assert integration_registry.health_check_tasks == {}
        assert integration_registry.health_status == {}
    
    def test_register_integration(self, integration_registry):
        """Test integration registration"""
        # Create mock integration class
        class MockIntegration(Integration):
            async def _create_client(self, config):
                return MagicMock()
            
            async def _perform_health_check(self):
                return True
        
        # Create metadata
        metadata = IntegrationMetadata(
            name="mock_integration",
            version="1.0.0",
            description="Mock integration",
            author="Test"
        )
        
        # Register integration
        integration_registry.register("mock_service", MockIntegration, metadata)
        
        assert "mock_service" in integration_registry.integrations
        assert integration_registry.integrations["mock_service"] == MockIntegration
        assert "mock_service" in integration_registry.metadata
        assert integration_registry.metadata["mock_service"] == metadata
    
    def test_unregister_integration(self, integration_registry):
        """Test integration unregistration"""
        # Create and register mock integration
        class MockIntegration(Integration):
            async def _create_client(self, config):
                return MagicMock()
            
            async def _perform_health_check(self):
                return True
        
        integration_registry.register("mock_service", MockIntegration)
        
        # Verify registration
        assert "mock_service" in integration_registry.integrations
        
        # Unregister
        result = integration_registry.unregister("mock_service")
        assert result is True
        assert "mock_service" not in integration_registry.integrations
        assert "mock_service" not in integration_registry.metadata
        
        # Try to unregister non-existent integration
        result = integration_registry.unregister("non_existent")
        assert result is False
    
    def test_list_integrations(self, integration_registry):
        """Test listing integrations"""
        # Initially empty
        assert integration_registry.list_integrations() == []
        
        # Add mock integrations
        class MockIntegration(Integration):
            async def _create_client(self, config):
                return MagicMock()
            
            async def _perform_health_check(self):
                return True
        
        integration_registry.register("service1", MockIntegration)
        integration_registry.register("service2", MockIntegration)
        
        integrations = integration_registry.list_integrations()
        assert len(integrations) == 2
        assert "service1" in integrations
        assert "service2" in integrations
    
    def test_get_integration_stats(self, integration_registry):
        """Test integration statistics"""
        stats = integration_registry.get_integration_stats()
        
        assert isinstance(stats, dict)
        assert "total_registered" in stats
        assert "total_active" in stats
        assert "health_status" in stats
        assert "healthy_count" in stats
        assert "unhealthy_count" in stats
        assert "monitoring_tasks" in stats
        
        assert stats["total_registered"] == 0
        assert stats["total_active"] == 0
        assert stats["healthy_count"] == 0
        assert stats["unhealthy_count"] == 0


class TestESCClientUnit:
    """Unit tests for ESCClient class"""
    
    @pytest.fixture
    def esc_client(self):
        """Create ESCClient instance for testing"""
        return ESCClient(
            organization="test-org",
            project="test-project",
            stack="test-stack"
        )
    
    def test_esc_client_initialization(self, esc_client):
        """Test ESCClient initialization"""
        assert esc_client.organization == "test-org"
        assert esc_client.project == "test-project"
        assert esc_client.stack == "test-stack"
        assert esc_client.base_url == "https://api.pulumi.com"
        assert esc_client.session is None
        assert esc_client.cache == {}
        assert esc_client.cache_ttl == 300
    
    def test_build_url(self, esc_client):
        """Test URL building"""
        url = esc_client._build_url("test-endpoint")
        expected = "https://api.pulumi.com/api/esc/environments/test-org/test-project/test-stack/test-endpoint"
        assert url == expected
    
    def test_cache_key_generation(self, esc_client):
        """Test cache key generation"""
        key = esc_client._get_cache_key("test-key")
        expected = "test-org:test-project:test-stack:test-key"
        assert key == expected
    
    def test_cache_operations(self, esc_client):
        """Test cache operations"""
        # Test cache set and get
        esc_client._set_cache("test-key", "test-value")
        assert esc_client._get_cache("test-key") == "test-value"
        
        # Test cache expiration
        import time
        esc_client.cache_ttl = 0.1  # Very short TTL
        esc_client._set_cache("expire-key", "expire-value")
        time.sleep(0.2)
        assert esc_client._get_cache("expire-key") is None
    
    def test_cache_statistics(self, esc_client):
        """Test cache statistics"""
        # Initially empty
        stats = esc_client.get_cache_stats()
        assert stats["total_keys"] == 0
        assert stats["hit_rate"] == 0.0
        
        # Add some cache entries
        esc_client._set_cache("key1", "value1")
        esc_client._set_cache("key2", "value2")
        
        stats = esc_client.get_cache_stats()
        assert stats["total_keys"] == 2


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

