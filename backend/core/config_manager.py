"""
Configuration Manager for Sophia AI
Implements base configuration interfaces with no circular dependencies
"""

import json
import logging
import os
import subprocess
from typing import Any, Dict, Optional

from backend.core.base import BaseConfig, service_registry

logger = logging.getLogger(__name__)


class ConfigManager(BaseConfig):
    """
    Main configuration manager that implements BaseConfig
    with no dependencies on other modules
    """
    
    def __init__(self):
        self._config_cache: Dict[str, Any] = {}
        self._esc_cache: Optional[Dict[str, Any]] = None
        self._esc_org = os.getenv("PULUMI_ORG", "scoobyjava-org")
        self._esc_env = os.getenv("PULUMI_ENV", "default/sophia-ai-production")
        
        # Register self with service registry
        service_registry.register('config_manager', self)
        
        # Initialize configuration
        self._initialize_defaults()
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        # Check cache first
        if key in self._config_cache:
            return self._config_cache[key]
        
        # Check environment variables (highest priority)
        env_value = os.getenv(key.upper())
        if env_value is not None:
            self._config_cache[key] = env_value
            return env_value
        
        # Check with original case
        env_value = os.getenv(key)
        if env_value is not None:
            self._config_cache[key] = env_value
            return env_value
        
        # Try to load from Pulumi ESC
        esc_value = self._get_from_esc(key)
        if esc_value is not None:
            self._config_cache[key] = esc_value
            return esc_value
        
        # Return default
        self._config_cache[key] = default
        return default
    
    def set_value(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self._config_cache[key] = value
    
    def _get_from_esc(self, key: str) -> Optional[Any]:
        """Get value from Pulumi ESC"""
        if self._esc_cache is None:
            self._load_esc_environment()
        
        if self._esc_cache:
            # Try direct key
            value = self._esc_cache.get(key)
            if value and value != "[secret]":
                return value
            
            # Try with quotes
            quoted_key = f'"{key}"'
            value = self._esc_cache.get(quoted_key)
            if value and value != "[secret]":
                return value
            
            # If it's a secret, try to get it with --show-secrets
            if value == "[secret]":
                return self._get_secret_from_esc(key)
        
        return None
    
    def _load_esc_environment(self) -> None:
        """Load configuration from Pulumi ESC"""
        try:
            result = subprocess.run(
                ["pulumi", "env", "get", f"{self._esc_org}/{self._esc_env}"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                self._esc_cache = self._parse_esc_output(result.stdout)
                logger.info(f"Loaded {len(self._esc_cache)} items from Pulumi ESC")
            else:
                logger.warning(f"Failed to load Pulumi ESC: {result.stderr}")
                self._esc_cache = {}
                
        except subprocess.TimeoutExpired:
            logger.warning("Timeout loading Pulumi ESC environment")
            self._esc_cache = {}
        except FileNotFoundError:
            logger.warning("Pulumi CLI not found")
            self._esc_cache = {}
        except Exception as e:
            logger.warning(f"Failed to load Pulumi ESC: {e}")
            self._esc_cache = {}
    
    def _parse_esc_output(self, output: str) -> Dict[str, Any]:
        """Parse Pulumi ESC output"""
        esc_data = {}
        
        for line in output.strip().split("\n"):
            if ":" in line and not line.strip().startswith("#"):
                if "[secret]" in line:
                    key = line.split(":")[0].strip()
                    esc_data[key] = "[secret]"
                else:
                    try:
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            esc_data[key] = value
                    except Exception:
                        continue
        
        return esc_data
    
    def _get_secret_from_esc(self, key: str) -> Optional[str]:
        """Get secret value from ESC with --show-secrets"""
        try:
            result = subprocess.run(
                [
                    "pulumi", "env", "get", 
                    f"{self._esc_org}/{self._esc_env}",
                    "--show-secrets"
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                # Try JSON parsing first
                try:
                    secrets = json.loads(result.stdout)
                    return secrets.get(key)
                except json.JSONDecodeError:
                    # Fallback to line parsing
                    for line in result.stdout.split("\n"):
                        if f'"{key}":' in line and "PLACEHOLDER" not in line:
                            try:
                                value_part = line.split(":", 1)[1].strip()
                                if value_part.endswith(","):
                                    value_part = value_part[:-1]
                                return value_part.strip('"')
                            except Exception:
                                continue
        except Exception as e:
            logger.debug(f"Failed to get secret {key}: {e}")
        
        return None
    
    def _initialize_defaults(self) -> None:
        """Initialize default configuration values"""
        # Snowflake defaults
        defaults = {
            "snowflake_account": "ZNB04675.us-east-1.us-east-1",
            "snowflake_user": "SCOOBYJAVA15",
            "snowflake_role": "ACCOUNTADMIN",
            "snowflake_warehouse": "SOPHIA_AI_WH",
            "snowflake_database": "SOPHIA_AI",
            "snowflake_schema": "PROCESSED_AI",
            # Estuary defaults
            "estuary_tenant": "Pay_Ready",
            "estuary_endpoint": "https://api.estuary.dev",
            # JWT defaults
            "jwt_secret": "sophia-ai-cortex-secret-key-2025",
            "jwt_algorithm": "HS256",
            "jwt_expiration_hours": "24",
        }
        
        # Only set if not already available
        for key, value in defaults.items():
            if not self.get_value(key):
                self.set_value(key, value)
    
    def get_snowflake_config(self) -> Dict[str, Any]:
        """Get Snowflake configuration"""
        return {
            "account": self.get_value("snowflake_account"),
            "user": self.get_value("snowflake_user"),
            "password": self.get_value("snowflake_password"),
            "role": self.get_value("snowflake_role"),
            "warehouse": self.get_value("snowflake_warehouse"),
            "database": self.get_value("snowflake_database"),
            "schema": self.get_value("snowflake_schema"),
        }
    
    def get_integration_config(self) -> Dict[str, Any]:
        """Get integration configuration"""
        return {
            "gong": {
                "access_key": self.get_value("gong_access_key"),
                "access_key_secret": self.get_value("gong_access_key_secret"),
                "endpoint": self.get_value("gong_endpoint", "https://api.gong.io"),
            },
            "slack": {
                "bot_token": self.get_value("slack_bot_token"),
                "app_token": self.get_value("slack_app_token"),
                "signing_secret": self.get_value("slack_signing_secret"),
            },
            "hubspot": {
                "access_token": self.get_value("hubspot_access_token"),
                "portal_id": self.get_value("hubspot_portal_id"),
                "endpoint": self.get_value("hubspot_endpoint", "https://api.hubapi.com"),
            },
        }


# Create global instance
_config_manager = ConfigManager()


# Export convenience functions that match the old interface
def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value (backward compatibility)"""
    return _config_manager.get_value(key, default)


def set_config_value(key: str, value: Any) -> None:
    """Set configuration value (backward compatibility)"""
    _config_manager.set_value(key, value)


def get_snowflake_config() -> Dict[str, Any]:
    """Get Snowflake configuration (backward compatibility)"""
    return _config_manager.get_snowflake_config()


def get_integration_config() -> Dict[str, Any]:
    """Get integration configuration (backward compatibility)"""
    return _config_manager.get_integration_config()


# Enhanced Snowflake connection optimization config
SNOWFLAKE_OPTIMIZATION_CONFIG = {
    "connection_pool_size": 10,
    "connection_timeout": 30,
    "query_timeout": 300,
    "retry_attempts": 3,
    "auto_commit": True,
    "warehouse_auto_suspend": 60,
    "warehouse_auto_resume": True,
} 