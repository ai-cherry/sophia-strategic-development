"""
Base Configuration Module
Provides core configuration without dependencies
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BaseConfig:
    """Core configuration with zero dependencies"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "prod")
        self.pulumi_org = os.getenv("PULUMI_ORG", "scoobyjava-org")
        self.pulumi_stack = f"{self.pulumi_org}/default/sophia-ai-production"
        self.debug_mode = self.environment != "prod"
        
        logger.info(f"✅ Base config initialized for {self.environment} environment")
        
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information"""
        return {
            "environment": self.environment,
            "pulumi_org": self.pulumi_org,
            "pulumi_stack": self.pulumi_stack,
            "debug_mode": self.debug_mode
        }
        
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "prod"
        
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment in ["dev", "development", "local"]
