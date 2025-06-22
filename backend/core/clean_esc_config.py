"""Clean Sophia AI ESC Integration - Based on Production Patterns

This module provides clean ESC integration using proven patterns from the comprehensive setup notes.
"""

import json
import logging
import os
import subprocess
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ESCConfigError(Exception):
    """Exception raised for ESC configuration errors."""
    pass


class SophiaESCConfig:
    """Clean ESC configuration manager based on production patterns."""
    def __init__(self, pulumi_org: str = "scoobyjava-org"):
        self.pulumi_org = pulumi_org
        self.environment = f"{pulumi_org}/default/sophia-ai-production"
        self._config_cache: Optional[Dict[str, Any]] = None
        self._load_esc_config()
    
    def _load_esc_config(self):
        """Load configuration from Pulumi ESC using production patterns."""
        logger.info(f"🔍 Loading ESC config from: {self.environment}")
        
        try:
            # Use pulumi CLI to get ESC environment values
            cmd = ["pulumi", "env", "open", self.environment, "--format", "json"]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True, 
                timeout=15
            )
            
            self._config_cache = json.loads(result.stdout)
            logger.info(f"✅ ESC config loaded successfully")
            
            # Log config structure (without sensitive values)
            if self._config_cache:
                config_keys = list(self._config_cache.keys())
                logger.info(f"📋 Config sections: {config_keys}")
                
                values = self._config_cache.get("values", {})
                if values:
                    value_keys = list(values.keys())
                    logger.info(f"🔧 Value sections: {value_keys}")
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ ESC command failed: {e.stderr}")
            self._config_cache = self._get_fallback_config()
            
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ ESC command timed out")
            self._config_cache = self._get_fallback_config()
            
        except Exception as e:
            logger.error(f"❌ ESC error: {e}")
            self._config_cache = self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Fallback configuration using environment variables."""
        logger.info("📦 Using environment variable fallback")
        
        return {
            "values": {
                "sophia": {
                    "ai": {
                        "openai": {
                            "api_key": os.getenv("OPENAI_API_KEY", "")
                        },
                        "anthropic": {
                            "api_key": os.getenv("ANTHROPIC_API_KEY", "")
                        }
                    },
                    "business": {
                        "gong": {
                            "access_key": os.getenv("GONG_ACCESS_KEY", ""),
                            "client_secret": os.getenv("GONG_CLIENT_SECRET", "")
                        }
                    },
                    "data": {
                        "pinecone": {
                            "api_key": os.getenv("PINECONE_API_KEY", "")
                        }
                    }
                }
            }
        }
    
    def get_all_values(self) -> Dict[str, Any]:
        """Get all configuration values."""
        if not self._config_cache:
            return {}
        return self._config_cache.get("values", {})
    
    def get_sophia_config(self) -> Dict[str, Any]:
        """Get Sophia-specific configuration."""
        values = self.get_all_values()
        return values.get("sophia", {})
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI service configurations."""
        sophia = self.get_sophia_config()
        return sophia.get("ai", {})
    
    def get_business_config(self) -> Dict[str, Any]:
        """Get business service configurations."""
        sophia = self.get_sophia_config()
        return sophia.get("business", {})
    
    def get_data_config(self) -> Dict[str, Any]:
        """Get data service configurations."""
        sophia = self.get_sophia_config()
        return sophia.get("data", {})
    
    def get_openai_key(self) -> str:
        """Get OpenAI API key."""
        ai_config = self.get_ai_config()
        openai_config = ai_config.get("openai", {})
        return openai_config.get("api_key", "")
    
    def get_anthropic_key(self) -> str:
        """Get Anthropic API key."""
        ai_config = self.get_ai_config()
        anthropic_config = ai_config.get("anthropic", {})
        return anthropic_config.get("api_key", "")
    
    def get_gong_credentials(self) -> Dict[str, str]:
        """Get Gong API credentials."""
        business_config = self.get_business_config()
        gong_config = business_config.get("gong", {})
        return {
            "access_key": gong_config.get("access_key", ""),
            "client_secret": gong_config.get("client_secret", "")
        }
    
    def get_pinecone_key(self) -> str:
        """Get Pinecone API key."""
        data_config = self.get_data_config()
        pinecone_config = data_config.get("pinecone", {})
        return pinecone_config.get("api_key", "")
    
    def is_configured(self) -> bool:
        """Check if ESC configuration is properly loaded."""
        return self._config_cache is not None and len(self.get_all_values()) > 0
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of configuration status."""
        ai_config = self.get_ai_config()
        business_config = self.get_business_config()
        data_config = self.get_data_config()
        
        return {
            "esc_loaded": self.is_configured(),
            "environment": self.environment,
            "services": {
                "openai": bool(ai_config.get("openai", {}).get("api_key")),
                "anthropic": bool(ai_config.get("anthropic", {}).get("api_key")),
                "gong": bool(business_config.get("gong", {}).get("access_key")),
                "pinecone": bool(data_config.get("pinecone", {}).get("api_key"))
            },
            "total_services": len([
                s for s in [
                    ai_config.get("openai", {}).get("api_key"),
                    ai_config.get("anthropic", {}).get("api_key"),
                    business_config.get("gong", {}).get("access_key"),
                    data_config.get("pinecone", {}).get("api_key")
                ] if s
            ])
        }
    
    # Async methods for enhanced backend compatibility
    async def initialize(self):
        """Async initialization method."""
        self._load_esc_config()
    
    async def get_status(self) -> Dict[str, Any]:
        """Get async configuration status."""
        return self.get_config_summary()
    
    async def get_openai_api_key(self) -> str:
        """Get OpenAI API key async."""
        return self.get_openai_key()
    
    async def get_anthropic_api_key(self) -> str:
        """Get Anthropic API key async."""
        return self.get_anthropic_key()
    
    async def get_gong_access_key(self) -> str:
        """Get Gong access key async."""
        gong_creds = self.get_gong_credentials()
        return gong_creds.get("access_key", "")
    
    async def get_gong_secret_key(self) -> str:
        """Get Gong secret key async."""
        gong_creds = self.get_gong_credentials()
        return gong_creds.get("client_secret", "")
    
    async def get_pinecone_api_key(self) -> str:
        """Get Pinecone API key async."""
        return self.get_pinecone_key()
    
    async def test_service_access(self) -> Dict[str, str]:
        """Test access to all services async."""
        tests = {}
        
        # Test OpenAI
        openai_key = self.get_openai_key()
        tests["openai"] = "configured" if openai_key and len(openai_key) > 10 else "missing"
        
        # Test Anthropic  
        anthropic_key = self.get_anthropic_key()
        tests["anthropic"] = "configured" if anthropic_key and len(anthropic_key) > 10 else "missing"
        
        # Test Gong
        gong_creds = self.get_gong_credentials()
        tests["gong"] = "configured" if (gong_creds["access_key"] and gong_creds["client_secret"]) else "missing"
        
        # Test Pinecone
        pinecone_key = self.get_pinecone_key()
        tests["pinecone"] = "configured" if pinecone_key and len(pinecone_key) > 10 else "missing"
        
        return tests


# Global instance
esc_config = SophiaESCConfig()

# Export the main config instance
config = esc_config

# Backward compatibility interface
class LegacyConfigAdapter:
    """Adapter to maintain backward compatibility with existing code."""
    def __init__(self, esc_config: SophiaESCConfig):
        self.esc = esc_config
        self.pulumi_org = esc_config.pulumi_org
        self.environment = esc_config.environment
    
    def get_all_values(self) -> Dict[str, Any]:
        return self.esc.get_all_values()


# Create legacy adapter for backward compatibility if needed
legacy_config = LegacyConfigAdapter(esc_config) 