"""
Sentiment Value Object

This module defines the Sentiment value object which represents
sentiment analysis results in the domain layer.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Sentiment:
    """
    Value object representing sentiment analysis.
    
    This is an immutable object that encapsulates sentiment score
    and confidence level.
    """
    score: float  # -1.0 to 1.0 where -1 is most negative, 1 is most positive
    confidence: float  # 0.0 to 1.0 representing confidence in the analysis
    
    def __post_init__(self):
        """Validate sentiment values."""
        if not -1.0 <= self.score <= 1.0:
            raise ValueError(f"Sentiment score must be between -1 and 1, got {self.score}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
    
    def is_positive(self) -> bool:
        """
        Check if sentiment is positive.
        
        Returns:
            bool: True if sentiment score is positive (> 0.1)
        """
        return self.score > 0.1
    
    def is_negative(self) -> bool:
        """
        Check if sentiment is negative.
        
        Returns:
            bool: True if sentiment score is negative (< -0.1)
        """
        return self.score < -0.1
    
    def is_neutral(self) -> bool:
        """
        Check if sentiment is neutral.
        
        Returns:
            bool: True if sentiment is neutral (-0.1 to 0.1)
        """
        return -0.1 <= self.score <= 0.1
    
    def get_label(self) -> str:
        """
        Get human-readable sentiment label.
        
        Returns:
            str: 'positive', 'negative', or 'neutral'
        """
        if self.is_positive():
            return "positive"
        elif self.is_negative():
            return "negative"
        else:
            return "neutral"
    
    def is_high_confidence(self) -> bool:
        """
        Check if the sentiment analysis has high confidence.
        
        Returns:
            bool: True if confidence is >= 0.8
        """
        return self.confidence >= 0.8 