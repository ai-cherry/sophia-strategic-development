"""
Sophia AI - Automatic ESC Integration
Backend automatically pulls configuration from Pulumi ESC
NO MORE MANUAL CONFIGURATION!
"""

import os
import subprocess
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AutoESCConfig:
    """Automatically loads configuration from Pulumi ESC"""
    
    def __init__(self):
        self.pulumi_org = os.getenv("PULUMI_ORG", "scoobyjava-org")
        self.environment = f"{self.pulumi_org}/default/sophia-ai-production"
        self._config_cache = {}
        self._load_esc_config()
    
    def _load_esc_config(self):
        """Load configuration from Pulumi ESC"""
        try:
            # Run pulumi env open to get environment variables
            cmd = f"pulumi env open {self.environment} --format json"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=True
            )
            
            config = json.loads(result.stdout)
            
            # Set environment variables from ESC
            if "environmentVariables" in config:
                for key, value in config["environmentVariables"].items():
                    os.environ[key] = str(value)
                    self._config_cache[key] = value
            
            logger.info(f"✅ Loaded {len(self._config_cache)} config values from ESC")
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Could not load ESC config: {e}")
            logger.info("📋 Using environment variables as fallback")
        except Exception as e:
            logger.error(f"❌ ESC integration error: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return os.getenv(key, default)
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get secret value"""
        return os.getenv(key)
    
    @property
    def openai_api_key(self) -> Optional[str]:
        return self.get_secret("OPENAI_API_KEY")
    
    @property
    def gong_access_key(self) -> Optional[str]:
        return self.get_secret("GONG_ACCESS_KEY")
    
    @property
    def gong_client_secret(self) -> Optional[str]:
        return self.get_secret("GONG_CLIENT_SECRET")
    
    @property
    def slack_bot_token(self) -> Optional[str]:
        return self.get_secret("SLACK_BOT_TOKEN")

# Global configuration instance
config = AutoESCConfig()
