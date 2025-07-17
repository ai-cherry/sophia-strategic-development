"""
Service Configuration Module
Individual service configuration factories
"""

from typing import Dict, Any
from .secret_manager import SecretManager


class ServiceConfigs:
    """Service-specific configuration factories"""
    
    def __init__(self, secret_manager: SecretManager = None):
        self.secret_manager = secret_manager
        
    def _get_config_value(self, key: str, default: str = None) -> str:
        """Get config value through secret manager or direct fallback"""
        if self.secret_manager:
            return self.secret_manager.get_config_value(key, default)
        else:
            # Fallback for backward compatibility
            from .secret_manager import get_config_value
            return get_config_value(key, default)
    
    def get_qdrant_config(self) -> Dict[str, str]:
        """Get Qdrant configuration"""
        return {
            "url": self._get_config_value("QDRANT_URL", "https://cloud.qdrant.io"),
            "api_key": self._get_config_value("QDRANT_API_KEY"),
            "timeout": "30",
            "pool_size": "10"
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        host = self._get_config_value("REDIS_HOST", "localhost")
        port = self._get_config_value("REDIS_PORT", "6379")
        password = self._get_config_value("REDIS_PASSWORD")
        
        config = {
            "host": host,
            "port": int(port),
            "db": 0,
            "decode_responses": True,
            "socket_timeout": 30,
            "socket_connect_timeout": 30,
            "retry_on_timeout": True,
            "health_check_interval": 30
        }
        
        if password:
            config["password"] = password
            
        return config
    
    def get_lambda_labs_config(self) -> Dict[str, Any]:
        """Get Lambda Labs configuration"""
        api_key = (
            self._get_config_value("LAMBDA_API_KEY") or
            self._get_config_value("LAMBDA_CLOUD_API_KEY") or
            self._get_config_value("lambda_api_key")
        )
        
        return {
            "api_key": api_key,
            "api_endpoint": "https://cloud.lambda.ai/api/v1/instances",
            "ssh_private_key": self._get_config_value("LAMBDA_PRIVATE_SSH_KEY"),
            "ssh_public_key": self._get_config_value("LAMBDA_SSH_KEY"),
            "ip_address": self._get_config_value("LAMBDA_IP_ADDRESS", "192.222.58.232"),
            "instances": {
                "master": {"ip": "192.222.58.232", "gpu": "GH200", "role": "master"},
                "mcp": {"ip": "104.171.202.117", "gpu": "A6000", "role": "worker"},
                "data": {"ip": "104.171.202.134", "gpu": "A100", "role": "worker"},
                "prod": {"ip": "104.171.202.103", "gpu": "RTX6000", "role": "worker"}
            }
        }
    
    def get_gong_config(self) -> Dict[str, Any]:
        """Get Gong configuration"""
        return {
            "access_key": self._get_config_value("GONG_ACCESS_KEY"),
            "access_key_secret": self._get_config_value("GONG_ACCESS_KEY_SECRET"),
            "base_url": self._get_config_value("GONG_BASE_URL", "https://api.gong.io"),
            "client_access_key": self._get_config_value("GONG_CLIENT_ACCESS_KEY"),
            "client_secret": self._get_config_value("GONG_CLIENT_SECRET")
        }
    
    def get_docker_hub_config(self) -> Dict[str, str]:
        """Get Docker Hub configuration"""
        return {
            "username": self._get_config_value("DOCKERHUB_USERNAME", "scoobyjava15"),
            "access_token": self._get_config_value("DOCKER_HUB_ACCESS_TOKEN"),
            "registry": "docker.io"
        }
    
    def get_integration_config(self) -> Dict[str, Any]:
        """Get business integration configuration"""
        return {
            "slack": {
                "bot_token": self._get_config_value("SLACK_BOT_TOKEN"),
                "user_token": self._get_config_value("SLACK_USER_TOKEN"),
                "webhook_url": self._get_config_value("SLACK_WEBHOOK_URL")
            },
            "linear": {
                "api_key": self._get_config_value("LINEAR_API_KEY"),
                "base_url": "https://api.linear.app"
            },
            "notion": {
                "api_token": self._get_config_value("NOTION_API_TOKEN"),
                "base_url": "https://api.notion.com"
            },
            "asana": {
                "access_token": self._get_config_value("ASANA_ACCESS_TOKEN"),
                "base_url": "https://app.asana.com/api/1.0"
            },
            "hubspot": {
                "access_token": self._get_config_value("HUBSPOT_ACCESS_TOKEN"),
                "base_url": "https://api.hubapi.com"
            },
            "github": {
                "token": self._get_config_value("GITHUB_TOKEN"),
                "base_url": "https://api.github.com"
            }
        }
    
    def get_salesforce_config(self) -> Dict[str, Any]:
        """Get Salesforce configuration"""
        return {
            "client_id": self._get_config_value("SALESFORCE_CLIENT_ID"),
            "client_secret": self._get_config_value("SALESFORCE_CLIENT_SECRET"),
            "username": self._get_config_value("SALESFORCE_USERNAME"),
            "password": self._get_config_value("SALESFORCE_PASSWORD"),
            "security_token": self._get_config_value("SALESFORCE_SECURITY_TOKEN"),
            "instance_url": self._get_config_value("SALESFORCE_INSTANCE_URL", "https://login.salesforce.com"),
            "api_version": self._get_config_value("SALESFORCE_API_VERSION", "v60.0"),
            "grant_type": "password",
            "sandbox": self._get_config_value("SALESFORCE_SANDBOX", "false").lower() == "true"
        }
    
    def get_hubspot_full_config(self) -> Dict[str, Any]:
        """Get full HubSpot configuration with all options"""
        return {
            "access_token": self._get_config_value("HUBSPOT_ACCESS_TOKEN"),
            "app_id": self._get_config_value("HUBSPOT_APP_ID"),
            "webhook_secret": self._get_config_value("HUBSPOT_WEBHOOK_SECRET"),
            "portal_id": self._get_config_value("HUBSPOT_PORTAL_ID"),
            "base_url": self._get_config_value("HUBSPOT_BASE_URL", "https://api.hubapi.com"),
            "rate_limit_per_second": 10,
            "rate_limit_per_day": 250000,
            "cache_ttl": 300  # 5 minutes default cache
        }
