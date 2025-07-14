"""
Router Service Integration
"""
from backend.core.enhanced_router import EnhancedIntelligentRouter
from backend.core.auto_esc_config import get_config_value

class RouterService:
    def __init__(self):
        self.router = EnhancedIntelligentRouter()
        self.portkey_key = get_config_value("portkey_api_key")
        self.openrouter_key = get_config_value("openrouter_api_key")
        
    async def route_and_execute(self, prompt: str, context: dict = None):
        """Route request and execute with selected model"""
        if context is None:
            context = {}
            
        decision = await self.router.route_request(prompt, context)
        
        # Execute with selected model
        response = await self.execute_with_model(
            prompt, decision.selected_model, decision
        )
        
        return {
            "response": response,
            "routing_decision": decision,
            "model_used": decision.selected_model,
            "cost": decision.estimated_cost
        }
        
    async def execute_with_model(self, prompt: str, model: str, decision):
        """Execute request with selected model"""
        # This would integrate with actual Portkey/OpenRouter APIs
        return f"Response from {model}: {prompt[:50]}..."
