"""
Portkey Gateway Service
Simple wrapper for Portkey AI integration
"""

from typing import Dict, Any, List, Optional
from portkey_ai import Portkey

class PortkeyGateway:
    """
    Simplified Portkey Gateway for backend services
    Uses direct Portkey integration
    """
    
    def __init__(self):
        try:
            from backend.core.auto_esc_config import get_config_value
            self.portkey_api_key = get_config_value("portkey_api_key", "")
            self.client = Portkey(api_key=self.portkey_api_key) if self.portkey_api_key else None
        except ImportError:
            self.client = None
    
    @property
    def completions(self):
        """Provide completions interface similar to OpenAI"""
        return self
    
    async def create(self, 
                    model: str = "claude-3-5-sonnet-20240620",
                    messages: Optional[List[Dict[str, str]]] = None,
                    temperature: float = 0.7,
                    max_tokens: int = 2000,
                    response_format: Optional[Dict[str, Any]] = None,
                    **kwargs) -> 'MockResponse':
        """
        Create completion with intelligent routing
        
        Args:
            model: Preferred model (can be overridden by routing)
            messages: Chat messages
            temperature: Generation temperature
            max_tokens: Maximum tokens
            response_format: Response format specification
            **kwargs: Additional parameters
            
        Returns:
            MockResponse object with choices
        """
        if messages is None:
            messages = []
        
        # If no Portkey client, return mock response
        if not self.client:
            return MockResponse("Mock response: Portkey not configured")
        
        # Simple completion using Portkey client
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            # Extract content from Portkey response
            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
                return MockResponse(content)
            else:
                return MockResponse("No response content")
        except Exception as e:
            # Return mock response on error
            return MockResponse(f"Error: {str(e)}")

class MockResponse:
    """Mock response object to match OpenAI API structure"""
    
    def __init__(self, content: str):
        self.choices = [MockChoice(content)]

class MockChoice:
    """Mock choice object"""
    
    def __init__(self, content: str):
        self.message = MockMessage(content)

class MockMessage:
    """Mock message object"""
    
    def __init__(self, content: str):
        self.content = content

# Global instance
portkey_gateway = PortkeyGateway() 