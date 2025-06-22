"""Unified Gong integration."""
from ..enhanced_gong_api_integration import EnhancedGongIntegration

class GongConfig:
    """Minimal configuration placeholder."""
    def __init__(self, **kwargs):
        self.options = kwargs

GongIntegration = EnhancedGongIntegration
