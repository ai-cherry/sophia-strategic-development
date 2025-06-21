"""
Sophia AI - Automatic & Comprehensive ESC Integration
This module provides a single, unified, and dynamic interface to all secrets
and configurations stored in the Pulumi ESC environment.

NO MORE MANUAL CONFIGURATION OR PROPERTY DEFINITIONS REQUIRED!
"""

import json
import logging
import os
import subprocess
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class NestedConfig:
    """A helper class to allow nested attribute access for the config."""
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def __getattr__(self, name: str) -> Any:
        value = self._data.get(name)
        if isinstance(value, dict):
            return NestedConfig(value)
        return value

    def to_dict(self) -> Dict[str, Any]:
        return self._data

class AutoESCConfig:
    """
    Automatically loads the entire configuration from Pulumi ESC and provides
    dynamic, nested access to all values.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutoESCConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.pulumi_org = os.getenv("PULUMI_ORG", "scoobyjava-org")
        self.environment = f"{self.pulumi_org}/default/sophia-ai-production"
        self._config_cache: Dict[str, Any] = {}
        self._load_esc_config()
        self._initialized = True

    def _load_esc_config(self):
        """
        Loads the entire config structure from Pulumi ESC. It first tries to
        get the values, and if that fails, it falls back to environment variables.
        """
        logger.info(f"Attempting to load configuration from Pulumi ESC: {self.environment}")
        try:
            cmd = f"pulumi env open {self.environment} --format json"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=True, timeout=15
            )
            self._config_cache = json.loads(result.stdout)
            logger.info(f"✅ Successfully loaded {len(self._config_cache.get('values', {}))} config groups from ESC.")
            
            # Also ensure environmentVariables from ESC are set for libraries that need them
            env_vars = self._config_cache.get('environmentVariables', {})
            for key, value in env_vars.items():
                if not os.getenv(key): # Don't override existing env vars
                    os.environ[key] = str(value)

        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Could not load from Pulumi ESC: {e.stderr}. This is expected if not in a CI/CD environment or logged into Pulumi.")
            logger.info("Falling back to environment variables for configuration.")
            self._config_cache = self._load_config_from_env()
        except subprocess.TimeoutExpired:
            logger.error("❌ Timed out trying to connect to Pulumi ESC.")
            logger.info("Falling back to environment variables for configuration.")
            self._config_cache = self._load_config_from_env()
        except Exception as e:
            logger.error(f"❌ An unexpected error occurred with Pulumi ESC: {e}", exc_info=True)
            logger.info("Falling back to environment variables for configuration.")
            self._config_cache = self._load_config_from_env()

    def _load_config_from_env(self) -> Dict[str, Any]:
        """Provides a basic fallback by reading known keys from env vars."""
        # This is a fallback and won't have the nested structure.
        return {
            "values": {
                "ai_services": {"openai_api_key": os.getenv("OPENAI_API_KEY")},
                "business_intelligence": {"gong_access_key": os.getenv("GONG_ACCESS_KEY")},
                "observability": {
                    "arize_api_key": os.getenv("ARIZE_API_KEY"),
                    "arize_space_id": os.getenv("ARIZE_SPACE_ID"),
                }
            }
        }
        
    def __getattr__(self, name: str) -> Any:
        """
        Dynamically provides attribute access to the nested config.
        e.g., config.ai_services.openai_api_key
        """
        # We primarily care about the 'values' block from the ESC output.
        values = self._config_cache.get("values", {})
        if name in values:
            value = values[name]
            if isinstance(value, dict):
                return NestedConfig(value)
            return value
        
        # Fallback for direct access to top-level keys if needed
        value = self._config_cache.get(name)
        if isinstance(value, dict):
            return NestedConfig(value)

        return value

    def get_all_values(self) -> Dict[str, Any]:
        """Returns the entire 'values' dictionary from the config."""
        return self._config_cache.get("values", {})

# Singleton instance for global access
config = AutoESCConfig()
