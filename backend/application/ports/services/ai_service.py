"""
AI Service Interface

This module defines the interface for AI operations.
This is a "port" in the hexagonal architecture.
"""

from abc import ABC, abstractmethod

from backend.domain.value_objects.sentiment import Sentiment


class AIService(ABC):
    """
    Interface for AI operations.

    This abstract class defines the contract that any AI service
    implementation must follow (e.g., Snowflake Cortex, OpenAI, etc.).
    """

    @abstractmethod
    async def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        Generate a summary of the given text.

        Args:
            text: The text to summarize
            max_length: Maximum length of the summary

        Returns:
            str: The generated summary
        """
        pass

    @abstractmethod
    async def analyze_sentiment(self, text: str) -> Sentiment:
        """
        Analyze sentiment of the given text.

        Args:
            text: The text to analyze

        Returns:
            Sentiment: The sentiment analysis result
        """
        pass

    @abstractmethod
    async def generate_embedding(
        self, text: str, model: str = "default"
    ) -> list[float]:
        """
        Generate vector embedding for the text.

        Args:
            text: The text to embed
            model: The embedding model to use

        Returns:
            List[float]: The embedding vector
        """
        pass

    @abstractmethod
    async def extract_entities(
        self, text: str, entity_types: list[str]
    ) -> dict[str, list[str]]:
        """
        Extract named entities from text.

        Args:
            text: The text to analyze
            entity_types: Types of entities to extract (e.g., PERSON, ORG, MONEY)

        Returns:
            Dict[str, List[str]]: Extracted entities by type
        """
        pass

    @abstractmethod
    async def classify_text(self, text: str, categories: list[str]) -> dict[str, float]:
        """
        Classify text into predefined categories.

        Args:
            text: The text to classify
            categories: List of possible categories

        Returns:
            Dict[str, float]: Category probabilities
        """
        pass

    @abstractmethod
    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        context: str = "",
    ) -> str:
        """
        Generate text completion based on prompt.

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            context: Optional context for the prompt

        Returns:
            str: The generated text
        """
        pass

    @abstractmethod
    async def answer_question(self, question: str, context: str) -> str:
        """
        Answer a question based on provided context.

        Args:
            question: The question to answer
            context: The context containing the answer

        Returns:
            str: The answer to the question
        """
        pass
