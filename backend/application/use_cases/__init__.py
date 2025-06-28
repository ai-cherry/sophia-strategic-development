"""
Application Use Cases

This module contains the business use cases that orchestrate
the application's behavior.
"""

from .analyze_call_sentiment import (
    AnalyzeCallSentimentUseCase,
    AnalyzeCallRequest,
    AnalyzeCallResponse,
    CallNotFoundError,
    NoTranscriptError
)

from .qualify_deal import (
    QualifyDealUseCase,
    QualifyDealRequest,
    QualifyDealResponse,
    QualificationCriteria,
    DealNotFoundError
)

__all__ = [
    'AnalyzeCallSentimentUseCase',
    'AnalyzeCallRequest',
    'AnalyzeCallResponse',
    'CallNotFoundError',
    'NoTranscriptError',
    'QualifyDealUseCase',
    'QualifyDealRequest',
    'QualifyDealResponse',
    'QualificationCriteria',
    'DealNotFoundError'
]
