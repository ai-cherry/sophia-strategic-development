"""
Secret Manager Module  
Handles all secret operations with circuit breaker protection
"""

import os
import subprocess
import logging
from functools import lru_cache
from typing import Dict, Any, Optional
from .base_config import BaseConfig

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Simple circuit breaker to prevent infinite recursion"""
    
    def __init__(self, max_failures: int = 3):
        self.max_failures = max_failures
        self.failure_count = 0
        self.is_open = False
        
    def call(self, func, *args, **kwargs):
        """Call function with circuit breaker protection"""
        if self.is_open:
            raise Exception("Circuit breaker is open")
            
        try:
            result = func(*args, **kwargs)
            self.failure_count = 0  # Reset on success
            return result
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.max_failures:
                self.is_open = True
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")
            raise


class SecretManager:
    """Centralized secret management with circuit breaker"""
    
    def __init__(self, base_config: BaseConfig):
        self.base_config = base_config
        self._esc_cache: Optional[Dict[str, Any]] = None
        self._circuit_breaker = CircuitBreaker()
        
        # Secret mappings from original file
        self.secret_mappings = {
            # AI Services
            "OPENAI_API_KEY": "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY": "ANTHROPIC_API_KEY", 
            "PORTKEY_API_KEY": "PORTKEY_API_KEY",
            "OPENROUTER_API_KEY": "OPENROUTER_API_KEY",
            
            # Business Intelligence
            "GONG_ACCESS_KEY": "GONG_ACCESS_KEY",
            "GONG_ACCESS_KEY_SECRET": "gong_access_key_secret",
            "GONG_BASE_URL": "gong_base_url",
            "GONG_CLIENT_ACCESS_KEY": "gong_api_key",
            "GONG_CLIENT_SECRET": "gong_client_secret",
            
            # Infrastructure
            "PULUMI_ACCESS_TOKEN": "PULUMI_ACCESS_TOKEN",
            "DOCKER_HUB_ACCESS_TOKEN": "DOCKER_HUB_ACCESS_TOKEN", 
            "DOCKERHUB_USERNAME": "DOCKERHUB_USERNAME",
            
            # Vector Databases
            "QDRANT_URL": "QDRANT_URL",
            "QDRANT_API_KEY": "QDRANT_API_KEY",
            "PINECONE_API_KEY": "PINECONE_API_KEY",
            "PINECONE_ENVIRONMENT": "PINECONE_ENVIRONMENT",
            
            # Redis
            "REDIS_PASSWORD": "REDIS_PASSWORD",
            "REDIS_HOST": "REDIS_HOST",
            "REDIS_PORT": "REDIS_PORT",
            "REDIS_URL": "REDIS_URL",
            
            # Business Tools
            "SLACK_BOT_TOKEN": "SLACK_BOT_TOKEN",
            "SLACK_USER_TOKEN": "SLACK_USER_TOKEN", 
            "LINEAR_API_KEY": "LINEAR_API_KEY",
            "NOTION_API_TOKEN": "NOTION_API_TOKEN",
            "ASANA_ACCESS_TOKEN": "ASANA_ACCESS_TOKEN",
            "GITHUB_TOKEN": "GITHUB_TOKEN",
            "HUBSPOT_ACCESS_TOKEN": "HUBSPOT_ACCESS_TOKEN",
            
            # Lambda Labs
            "LAMBDA_API_KEY": "LAMBDA_API_KEY",
            "LAMBDA_SSH_KEY": "LAMBDA_SSH_KEY",
            "LAMBDA_PRIVATE_SSH_KEY": "LAMBDA_PRIVATE_SSH_KEY",
            "LAMBDA_API_ENDPOINT": "LAMBDA_API_ENDPOINT"
        }
        
    def get_config_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value with circuit breaker protection"""
        try:
            return self._circuit_breaker.call(self._get_config_value_internal, key, default)
        except Exception as e:
            logger.warning(f"Failed to get config value {key}: {e}")
            return default
            
    def _get_config_value_internal(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Internal config value retrieval"""
        
        # 1. Check environment variables first (direct access)
        env_value = os.getenv(key)
        if env_value:
            return env_value
        
        # 2. Check secret mappings for alternative names
        mapped_key = self.secret_mappings.get(key, key)
        if mapped_key != key:
            env_value = os.getenv(mapped_key)
            if env_value:
                return env_value
        
        # 3. Load from Pulumi ESC (with caching)
        try:
            esc_data = self._load_esc_environment()
            if esc_data and key in esc_data:
                value = esc_data[key]
                if value and value != "[secret]" and not value.startswith("PLACEHOLDER"):
                    return value
        except Exception as e:
            logger.debug(f"Failed to get {key} from Pulumi ESC: {e}")

        # 4. Return default value
        return default
        
    @lru_cache(maxsize=1)
    def _load_esc_environment(self) -> Dict[str, Any]:
        """Load configuration from Pulumi ESC environment"""
        if self._esc_cache is not None:
            return self._esc_cache

        try:
            result = subprocess.run(
                ["pulumi", "env", "get", self.base_config.pulumi_stack],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                esc_data = {}
                for line in result.stdout.strip().split("\n"):
                    if ":" in line and not line.strip().startswith("#"):
                        try:
                            parts = line.split(":", 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip()
                                esc_data[key] = value
                        except Exception:
                            continue

                self._esc_cache = esc_data
                logger.info(f"✅ Loaded {len(esc_data)} configuration items from Pulumi ESC")
                return esc_data
            else:
                logger.error(f"❌ Failed to load Pulumi ESC: {result.stderr}")
                return {}

        except Exception as e:
            logger.error(f"❌ Error loading Pulumi ESC: {e}")
            return {}


# Global instances (for backward compatibility)
_base_config: Optional[BaseConfig] = None
_secret_manager: Optional[SecretManager] = None


def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Backward compatible get_config_value function"""
    global _base_config, _secret_manager
    
    if _base_config is None:
        _base_config = BaseConfig()
        
    if _secret_manager is None:
        _secret_manager = SecretManager(_base_config)
        
    return _secret_manager.get_config_value(key, default)
