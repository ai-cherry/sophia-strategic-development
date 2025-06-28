"""
Analyze Call Sentiment Use Case

This module implements the business logic for analyzing the sentiment
of a sales call.
"""

from dataclasses import dataclass
from typing import Optional
from backend.application.ports.repositories.call_repository import CallRepository
from backend.application.ports.services.ai_service import AIService
from backend.domain.entities.call import Call
from backend.domain.value_objects.sentiment import Sentiment


@dataclass
class AnalyzeCallSentimentRequest:
    """Request object for analyzing call sentiment."""
    call_id: str
    force_reanalysis: bool = False


@dataclass
class AnalyzeCallSentimentResponse:
    """Response object for call sentiment analysis."""
    call_id: str
    sentiment: Sentiment
    requires_followup: bool
    risk_indicators: list[str]
    engagement_score: float


class CallNotFoundError(Exception):
    """Raised when a call cannot be found."""
    def __init__(self, call_id: str):
        super().__init__(f"Call not found: {call_id}")
        self.call_id = call_id


class NoTranscriptError(Exception):
    """Raised when a call has no transcript to analyze."""
    def __init__(self, call_id: str):
        super().__init__(f"Call {call_id} has no transcript")
        self.call_id = call_id


class AnalyzeCallSentimentUseCase:
    """
    Use case for analyzing call sentiment.
    
    This class encapsulates the business logic for sentiment analysis,
    independent of any framework or infrastructure concerns.
    """
    
    def __init__(
        self,
        call_repository: CallRepository,
        ai_service: AIService
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            call_repository: Repository for accessing call data
            ai_service: Service for AI operations
        """
        self._call_repository = call_repository
        self._ai_service = ai_service
    
    async def execute(
        self, 
        request: AnalyzeCallSentimentRequest
    ) -> AnalyzeCallSentimentResponse:
        """
        Execute the call sentiment analysis use case.
        
        Args:
            request: The request containing call ID and options
            
        Returns:
            AnalyzeCallSentimentResponse: The analysis results
            
        Raises:
            CallNotFoundError: If the call doesn't exist
            NoTranscriptError: If the call has no transcript
        """
        # Retrieve the call
        call = await self._call_repository.get_by_id(request.call_id)
        if not call:
            raise CallNotFoundError(request.call_id)
        
        # Check if we need to analyze
        if not request.force_reanalysis and call.sentiment:
            # Already analyzed, return existing results
            return self._create_response(call)
        
        # Validate transcript exists
        if not call.transcript:
            raise NoTranscriptError(request.call_id)
        
        # Perform sentiment analysis
        sentiment = await self._ai_service.analyze_sentiment(call.transcript)
        
        # Update the call with sentiment
        call.sentiment = sentiment
        await self._call_repository.update(call)
        
        # Apply business rules and create response
        return self._create_response(call)
    
    def _create_response(self, call: Call) -> AnalyzeCallSentimentResponse:
        """
        Create response object from analyzed call.
        
        Args:
            call: The call with sentiment analysis
            
        Returns:
            AnalyzeCallSentimentResponse: The formatted response
        """
        if not call.sentiment:
            # This should not happen as we ensure sentiment exists before calling this
            raise ValueError(f"Call {call.id} has no sentiment analysis")
        
        return AnalyzeCallSentimentResponse(
            call_id=call.id,
            sentiment=call.sentiment,
            requires_followup=call.requires_followup(),
            risk_indicators=call.get_risk_indicators(),
            engagement_score=call.get_engagement_score()
        )
    
    async def analyze_multiple_calls(
        self,
        call_ids: list[str]
    ) -> list[AnalyzeCallSentimentResponse]:
        """
        Analyze sentiment for multiple calls.
        
        Args:
            call_ids: List of call IDs to analyze
            
        Returns:
            list[AnalyzeCallSentimentResponse]: Analysis results for each call
        """
        results = []
        
        for call_id in call_ids:
            try:
                request = AnalyzeCallSentimentRequest(call_id=call_id)
                response = await self.execute(request)
                results.append(response)
            except (CallNotFoundError, NoTranscriptError):
                # Skip calls that can't be analyzed
                continue
        
        return results 
