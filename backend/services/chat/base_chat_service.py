"""
Base Chat Service - Phase 2B Implementation
Abstract base class for all chat services with common functionality
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import logging
import time
from datetime import datetime

from ...models.chat_models import (
    ChatRequest, ChatResponse, ChatMode, ChatProvider, 
    ChatMetadata, ChatUsage, ChatStatus
)

logger = logging.getLogger(__name__)

class BaseChatService(ABC):
    """
    Abstract base class for all chat services
    Provides common functionality and enforces interface consistency
    """
    
    def __init__(self, mode: ChatMode, default_provider: ChatProvider):
        self.mode = mode
        self.default_provider = default_provider
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
    @abstractmethod
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request and return a response
        Must be implemented by all concrete chat services
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get the system prompt for this chat mode
        Must be implemented by all concrete chat services
        """
        pass
    
    @abstractmethod
    def get_suggested_questions(self, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Get suggested follow-up questions for this chat mode
        Must be implemented by all concrete chat services
        """
        pass
    
    def validate_request(self, request: ChatRequest) -> None:
        """
        Validate chat request
        Raises ValueError if request is invalid
        """
        if not request.message or not request.message.strip():
            raise ValueError("Message cannot be empty")
        
        if len(request.message) > 10000:
            raise ValueError("Message too long (max 10,000 characters)")
        
        if request.configuration:
            if request.configuration.temperature < 0 or request.configuration.temperature > 2:
                raise ValueError("Temperature must be between 0 and 2")
            
            if request.configuration.max_tokens < 1 or request.configuration.max_tokens > 8000:
                raise ValueError("Max tokens must be between 1 and 8000")
    
    def create_metadata(self, 
                       response_type: str,
                       features: List[str],
                       model_used: Optional[str] = None,
                       processing_time_ms: Optional[int] = None,
                       **kwargs) -> ChatMetadata:
        """Create standardized metadata for responses"""
        return ChatMetadata(
            response_type=response_type,
            features=features,
            model_used=model_used,
            processing_time_ms=processing_time_ms,
            provider_info=kwargs.get('provider_info'),
            confidence_score=kwargs.get('confidence_score')
        )
    
    def create_usage(self,
                    prompt_tokens: int = 0,
                    completion_tokens: int = 0,
                    estimated_cost: float = 0.0) -> ChatUsage:
        """Create standardized usage information"""
        return ChatUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost=estimated_cost,
            cost_currency="USD"
        )
    
    def create_response(self,
                       request: ChatRequest,
                       response_text: str,
                       metadata: ChatMetadata,
                       usage: Optional[ChatUsage] = None,
                       suggestions: Optional[List[str]] = None,
                       status: ChatStatus = ChatStatus.COMPLETED) -> ChatResponse:
        """Create standardized chat response"""
        return ChatResponse(
            response=response_text,
            session_id=request.session_id,
            mode=self.mode,
            provider=request.configuration.provider if request.configuration else self.default_provider,
            status=status,
            metadata=metadata,
            suggestions=suggestions or self.get_suggested_questions(),
            usage=usage
        )
    
    async def process_with_timing(self, request: ChatRequest) -> ChatResponse:
        """
        Process chat request with timing and error handling
        Template method that calls the abstract process_chat method
        """
        start_time = time.time()
        
        try:
            # Validate request
            self.validate_request(request)
            
            # Log request
            self.logger.info(f"Processing {self.mode.value} chat: {request.message[:50]}...")
            
            # Process the chat
            response = await self.process_chat(request)
            
            # Add processing time to metadata
            processing_time_ms = int((time.time() - start_time) * 1000)
            if response.metadata:
                response.metadata.processing_time_ms = processing_time_ms
            
            self.logger.info(f"Chat processed successfully in {processing_time_ms}ms")
            return response
            
        except ValueError as e:
            self.logger.warning(f"Invalid request: {str(e)}")
            raise
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            self.logger.error(f"Chat processing failed after {processing_time_ms}ms: {str(e)}")
            
            # Return error response
            error_metadata = self.create_metadata(
                response_type="error",
                features=[],
                processing_time_ms=processing_time_ms
            )
            
            return self.create_response(
                request=request,
                response_text=f"I apologize, but I encountered an error processing your request: {str(e)}",
                metadata=error_metadata,
                status=ChatStatus.FAILED
            )
    
    def get_default_configuration(self) -> Dict[str, Any]:
        """Get default configuration for this chat service"""
        return {
            "mode": self.mode.value,
            "provider": self.default_provider.value,
            "temperature": 0.7,
            "max_tokens": 1000
        }
    
    def supports_streaming(self) -> bool:
        """Check if this service supports streaming responses"""
        return False  # Override in subclasses that support streaming
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities for this chat service"""
        return ["basic_chat"]  # Override in subclasses
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mode={self.mode.value}, provider={self.default_provider.value})"
    
    def __repr__(self) -> str:
        return self.__str__()

