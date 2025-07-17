"""
Security Configuration for Sophia AI
Centralized security settings and validation
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Centralized security configuration"""
    
    # Environment settings
    environment: str = "prod"
    debug_mode: bool = False
    
    # Secret management
    secret_validation_enabled: bool = True
    secret_rotation_enabled: bool = True
    
    # API security
    api_rate_limit_enabled: bool = True
    api_rate_limit_requests: int = 100
    api_rate_limit_window: int = 60  # seconds
    
    # Session security
    session_timeout_minutes: int = 60
    secure_cookies: bool = True
    
    # Logging security
    log_sensitive_data: bool = False
    audit_logging_enabled: bool = True
    
    # File security
    allowed_file_extensions: List[str] = field(default_factory=lambda: ['.txt', '.json', '.yaml', '.py'])
    max_file_size_mb: int = 10
    
    @classmethod
    def from_environment(cls) -> 'SecurityConfig':
        """Create SecurityConfig from environment variables"""
        
        config = cls()
        
        # Environment detection
        config.environment = os.getenv("ENVIRONMENT", "prod")
        config.debug_mode = os.getenv("DEBUG", "false").lower() == "true"
        
        # Security settings based on environment
        if config.environment == "prod":
            config.secret_validation_enabled = True
            config.api_rate_limit_enabled = True
            config.secure_cookies = True
            config.log_sensitive_data = False
            config.audit_logging_enabled = True
        elif config.environment == "staging":
            config.secret_validation_enabled = True
            config.api_rate_limit_enabled = True
            config.secure_cookies = True
            config.log_sensitive_data = False
            config.audit_logging_enabled = True
        else:  # dev, test, etc.
            config.secret_validation_enabled = False
            config.api_rate_limit_enabled = False
            config.secure_cookies = False
            config.log_sensitive_data = True
            config.audit_logging_enabled = False
            
        # Override with specific environment variables
        if os.getenv("API_RATE_LIMIT_ENABLED"):
            config.api_rate_limit_enabled = os.getenv("API_RATE_LIMIT_ENABLED").lower() == "true"
            
        if os.getenv("API_RATE_LIMIT_REQUESTS"):
            try:
                config.api_rate_limit_requests = int(os.getenv("API_RATE_LIMIT_REQUESTS"))
            except ValueError:
                logger.warning("Invalid API_RATE_LIMIT_REQUESTS value, using default")
                
        if os.getenv("SESSION_TIMEOUT_MINUTES"):
            try:
                config.session_timeout_minutes = int(os.getenv("SESSION_TIMEOUT_MINUTES"))
            except ValueError:
                logger.warning("Invalid SESSION_TIMEOUT_MINUTES value, using default")
                
        logger.info(f"✅ Security config initialized for {config.environment} environment")
        return config
        
    def validate(self) -> bool:
        """Validate security configuration"""
        try:
            # Check required environment variables exist
            required_vars = []
            
            if self.environment == "prod":
                required_vars = [
                    "OPENAI_API_KEY",
                    "ANTHROPIC_API_KEY", 
                    "PULUMI_ACCESS_TOKEN"
                ]
                
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                logger.error(f"❌ Missing required environment variables: {missing_vars}")
                return False
                
            # Validate rate limiting settings
            if self.api_rate_limit_enabled:
                if self.api_rate_limit_requests <= 0:
                    logger.error("❌ API rate limit requests must be positive")
                    return False
                    
                if self.api_rate_limit_window <= 0:
                    logger.error("❌ API rate limit window must be positive") 
                    return False
                    
            # Validate session timeout
            if self.session_timeout_minutes <= 0:
                logger.error("❌ Session timeout must be positive")
                return False
                
            logger.info("✅ Security configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Security configuration validation failed: {e}")
            return False
            
    def get_secret_mappings(self) -> Dict[str, str]:
        """Get secret mappings for configuration access"""
        return {
            # AI Services
            "OPENAI_API_KEY": "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY": "ANTHROPIC_API_KEY", 
            "PORTKEY_API_KEY": "PORTKEY_API_KEY",
            "OPENROUTER_API_KEY": "OPENROUTER_API_KEY",
            
            # Business Intelligence
            "GONG_ACCESS_KEY": "GONG_ACCESS_KEY",
            "GONG_ACCESS_KEY_SECRET": "gong_access_key_secret",
            "GONG_BASE_URL": "gong_base_url",
            
            # Infrastructure
            "PULUMI_ACCESS_TOKEN": "PULUMI_ACCESS_TOKEN",
            "DOCKER_HUB_ACCESS_TOKEN": "DOCKER_HUB_ACCESS_TOKEN",
            
            # Vector Databases
            "QDRANT_URL": "QDRANT_URL",
            "QDRANT_API_KEY": "QDRANT_API_KEY",
            "PINECONE_API_KEY": "PINECONE_API_KEY",
            
            # Business Tools
            "SLACK_BOT_TOKEN": "SLACK_BOT_TOKEN",
            "LINEAR_API_KEY": "LINEAR_API_KEY",
            "NOTION_API_TOKEN": "NOTION_API_TOKEN",
            "ASANA_ACCESS_TOKEN": "ASANA_ACCESS_TOKEN",
            "HUBSPOT_ACCESS_TOKEN": "HUBSPOT_ACCESS_TOKEN",
            
            # Lambda Labs
            "LAMBDA_API_KEY": "LAMBDA_API_KEY",
            "LAMBDA_SSH_KEY": "LAMBDA_SSH_KEY",
            "LAMBDA_PRIVATE_SSH_KEY": "LAMBDA_PRIVATE_SSH_KEY"
        }
        
    def get_file_security_config(self) -> Dict[str, Any]:
        """Get file security configuration"""
        return {
            "allowed_extensions": self.allowed_file_extensions,
            "max_size_mb": self.max_file_size_mb,
            "scan_uploads": True,
            "quarantine_suspicious": True
        }
        
    def get_api_security_config(self) -> Dict[str, Any]:
        """Get API security configuration"""
        return {
            "rate_limit_enabled": self.api_rate_limit_enabled,
            "rate_limit_requests": self.api_rate_limit_requests,
            "rate_limit_window": self.api_rate_limit_window,
            "cors_enabled": True,
            "cors_origins": ["https://app.sophia-intel.ai"] if self.environment == "prod" else ["*"],
            "https_only": self.environment == "prod",
            "secure_headers": True
        }
        
    def get_session_security_config(self) -> Dict[str, Any]:
        """Get session security configuration"""
        return {
            "timeout_minutes": self.session_timeout_minutes,
            "secure_cookies": self.secure_cookies,
            "same_site": "strict" if self.environment == "prod" else "lax",
            "http_only": True,
            "regenerate_on_login": True
        }
        
    def get_logging_security_config(self) -> Dict[str, Any]:
        """Get logging security configuration"""
        return {
            "log_sensitive_data": self.log_sensitive_data,
            "audit_enabled": self.audit_logging_enabled,
            "sanitize_logs": True,
            "log_level": "INFO" if self.environment == "prod" else "DEBUG",
            "max_log_size_mb": 100,
            "log_retention_days": 30 if self.environment == "prod" else 7
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "environment": self.environment,
            "debug_mode": self.debug_mode,
            "secret_validation_enabled": self.secret_validation_enabled,
            "api_rate_limit_enabled": self.api_rate_limit_enabled,
            "session_timeout_minutes": self.session_timeout_minutes,
            "secure_cookies": self.secure_cookies,
            "audit_logging_enabled": self.audit_logging_enabled
        }


# Global security config instance
_security_config: Optional[SecurityConfig] = None


def get_security_config() -> SecurityConfig:
    """Get or create the global security configuration"""
    global _security_config
    
    if _security_config is None:
        _security_config = SecurityConfig.from_environment()
        
        # Validate configuration
        if not _security_config.validate():
            logger.warning("⚠️  Security configuration validation failed, using defaults")
            
    return _security_config


def reload_security_config() -> SecurityConfig:
    """Reload security configuration from environment"""
    global _security_config
    _security_config = None
    return get_security_config() 