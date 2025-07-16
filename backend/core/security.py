"""
Security utilities for Sophia AI backend
"""

import os
import logging

logger = logging.getLogger(__name__)

def check_security_health() -> dict:
    """Check security configuration health"""
    try:
        # Basic security health checks
        checks = {
            "environment_vars": bool(os.getenv("OPENAI_API_KEY")),
            "debug_mode": os.getenv("DEBUG", "false").lower() != "true",
            "secure_mode": True
        }
        
        status = "healthy" if all(checks.values()) else "warning"
        
        return {
            "status": status,
            "checks": checks,
            "message": "Security configuration checked"
        }
    except Exception as e:
        logger.error(f"Security health check failed: {e}")
        return {
            "status": "error",
            "checks": {},
            "message": f"Security check error: {e}"
        }

def get_api_key(service: str) -> str:
    """Get API key for a service"""
    key_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "portkey": "PORTKEY_API_KEY"
    }
    
    env_var = key_map.get(service.lower())
    if not env_var:
        raise ValueError(f"Unknown service: {service}")
    
    key = os.getenv(env_var)
    if not key:
        raise ValueError(f"Missing API key for {service}")
    
    return key 