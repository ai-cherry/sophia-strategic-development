"""
Application Use Cases

This module contains the business use cases that orchestrate
the application's behavior.
"""

from .analyze_call_sentiment import (
    AnalyzeCallRequest,
    AnalyzeCallResponse,
    AnalyzeCallSentimentUseCase,
    CallNotFoundError,
    NoTranscriptError,
)
from .qualify_deal import (
    DealNotFoundError,
    QualificationCriteria,
    QualifyDealRequest,
    QualifyDealResponse,
    QualifyDealUseCase,
)

__all__ = [
    "AnalyzeCallRequest",
    "AnalyzeCallResponse",
    "AnalyzeCallSentimentUseCase",
    "CallNotFoundError",
    "DealNotFoundError",
    "NoTranscriptError",
    "QualificationCriteria",
    "QualifyDealRequest",
    "QualifyDealResponse",
    "QualifyDealUseCase",
]
