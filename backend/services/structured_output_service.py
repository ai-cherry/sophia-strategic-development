"""
Structured Output Service for Reliable LLM Responses.

Ensures zero parsing errors and consistent structured outputs
from all LLM interactions using Pydantic models and validation.
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar

import structlog
from pydantic import BaseModel, Field, ValidationError, validator

from backend.services.snowflake_cortex_service import SnowflakeCortexService

logger = structlog.get_logger()

T = TypeVar("T", bound=BaseModel)


class OutputFormat(str, Enum):
    """Supported output formats."""

    JSON = "json"
    PYDANTIC = "pydantic"
    DATAFRAME = "dataframe"
    MARKDOWN_TABLE = "markdown_table"


class StructuredPrompt(BaseModel):
    """Enhanced prompt with structure requirements."""

    base_prompt: str
    output_schema: dict[str, Any]
    examples: list[dict[str, Any]] = Field(default_factory=list)
    validation_rules: list[str] = Field(default_factory=list)
    retry_on_failure: bool = True
    max_retries: int = 3


class ValidationResult(BaseModel):
    """Result of output validation."""

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    cleaned_output: dict[str, Any] | None = None


# Common structured output schemas
class ExecutiveSummary(BaseModel):
    """Executive summary structure."""

    title: str
    key_points: list[str] = Field(min_items=3, max_items=5)
    metrics: dict[str, float | int]
    recommendations: list[str] = Field(min_items=1)
    risk_level: str = Field(regex="^(low|medium|high|critical)$")
    confidence_score: float = Field(ge=0, le=1)

    @validator("key_points")
    def validate_key_points(self, v):
        """Ensure key points are concise."""
        for point in v:
            if len(point) > 200:
                raise ValueError(f"Key point too long: {len(point)} chars")
        return v


class DealAnalysis(BaseModel):
    """Deal analysis structure."""

    deal_id: str
    deal_name: str
    probability: float = Field(ge=0, le=100)
    risk_factors: list[str]
    opportunities: list[str]
    next_steps: list[str]
    estimated_close_date: datetime | None
    competitor_threats: list[str] = Field(default_factory=list)


class CallInsights(BaseModel):
    """Call analysis insights structure."""

    call_id: str
    sentiment_score: float = Field(ge=-1, le=1)
    key_topics: list[str]
    action_items: list[dict[str, str]]
    customer_concerns: list[str]
    positive_signals: list[str]
    follow_up_required: bool
    urgency_level: str = Field(regex="^(low|medium|high|urgent)$")


class StructuredOutputService:
    """
    Ensures reliable structured outputs from LLM responses.

    Features:
    - Zero parsing errors through validation
    - Automatic retry with improved prompts
    - Schema enforcement
    - Output cleaning and normalization
    """

    def __init__(self):
        self.logger = logger.bind(service="structured_output")
        self.cortex = SnowflakeCortexService()

    async def get_structured_output(
        self,
        prompt: str,
        output_class: type[T],
        examples: list[T] | None = None,
        context: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> T:
        """
        Get structured output with guaranteed parsing.

        Args:
            prompt: The prompt to send to LLM
            output_class: Pydantic model class for output structure
            examples: Optional examples of desired output
            context: Additional context for the prompt
            max_retries: Maximum retry attempts

        Returns:
            Validated instance of output_class

        Raises:
            ValueError: If unable to get valid output after retries
        """
        # Build enhanced prompt with structure
        structured_prompt = self._build_structured_prompt(
            prompt, output_class, examples, context
        )

        for attempt in range(max_retries):
            try:
                # Get LLM response
                response = await self._get_llm_response(structured_prompt, attempt)

                # Parse and validate
                parsed = self._parse_response(response, output_class)

                self.logger.info(
                    "Structured output generated successfully",
                    output_class=output_class.__name__,
                    attempt=attempt + 1,
                )

                return parsed

            except (json.JSONDecodeError, ValidationError) as e:
                self.logger.warning(
                    "Failed to parse structured output",
                    error=str(e),
                    attempt=attempt + 1,
                    output_class=output_class.__name__,
                )

                if attempt < max_retries - 1:
                    # Enhance prompt for retry
                    structured_prompt = self._enhance_prompt_for_retry(
                        structured_prompt,
                        str(e),
                        response if "response" in locals() else None,
                    )
                else:
                    raise ValueError(
                        f"Failed to get valid output after {max_retries} attempts: {e}"
                    )

    async def get_executive_summary(
        self, data: dict[str, Any], focus_area: str
    ) -> ExecutiveSummary:
        """
        Generate executive summary with guaranteed structure.

        Args:
            data: Data to summarize
            focus_area: Area of focus for summary

        Returns:
            Structured executive summary
        """
        prompt = f"""
        Create an executive summary for the following {focus_area} data.
        Focus on actionable insights and key metrics.

        Data: {json.dumps(data, indent=2)}

        Provide a structured summary with:
        - Clear title
        - 3-5 key points (each under 200 characters)
        - Relevant metrics
        - Actionable recommendations
        - Risk assessment (low/medium/high/critical)
        - Confidence score (0-1)
        """

        examples = [
            ExecutiveSummary(
                title="Q4 Sales Performance Summary",
                key_points=[
                    "Revenue exceeded target by 15%",
                    "New customer acquisition up 25%",
                    "Enterprise segment showing strong growth",
                ],
                metrics={"revenue": 5200000, "deals_closed": 47, "win_rate": 0.68},
                recommendations=[
                    "Increase investment in enterprise sales team",
                    "Expand partner channel program",
                ],
                risk_level="low",
                confidence_score=0.92,
            )
        ]

        return await self.get_structured_output(
            prompt=prompt,
            output_class=ExecutiveSummary,
            examples=examples,
            context={"focus_area": focus_area},
        )

    async def analyze_deal(self, deal_data: dict[str, Any]) -> DealAnalysis:
        """
        Analyze deal with structured insights.

        Args:
            deal_data: Deal information

        Returns:
            Structured deal analysis
        """
        prompt = f"""
        Analyze the following deal and provide structured insights:

        Deal Data: {json.dumps(deal_data, indent=2)}

        Include:
        - Win probability (0-100)
        - Risk factors
        - Opportunities to accelerate
        - Concrete next steps
        - Competitor threats
        - Estimated close date
        """

        return await self.get_structured_output(
            prompt=prompt,
            output_class=DealAnalysis,
            context={"deal_stage": deal_data.get("stage", "unknown")},
        )

    async def analyze_call(
        self, transcript: str, metadata: dict[str, Any]
    ) -> CallInsights:
        """
        Analyze call with structured insights.

        Args:
            transcript: Call transcript
            metadata: Call metadata

        Returns:
            Structured call insights
        """
        prompt = f"""
        Analyze this sales call and provide structured insights:

        Call Info: {json.dumps(metadata, indent=2)}
        Transcript excerpt: {transcript[:2000]}...

        Extract:
        - Overall sentiment (-1 to 1)
        - Key topics discussed
        - Action items with owners
        - Customer concerns
        - Positive buying signals
        - Follow-up requirements
        - Urgency level (low/medium/high/urgent)
        """

        return await self.get_structured_output(
            prompt=prompt,
            output_class=CallInsights,
            context={"call_duration": metadata.get("duration_seconds", 0)},
        )

    def _build_structured_prompt(
        self,
        base_prompt: str,
        output_class: type[BaseModel],
        examples: list[BaseModel] | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Build prompt with structure requirements."""
        schema = output_class.schema()

        # Remove internal fields
        schema.pop("title", None)
        schema.pop("type", None)

        structured_prompt = f"""
{base_prompt}

IMPORTANT: You must respond with valid JSON that matches this exact schema:
{json.dumps(schema, indent=2)}

Required fields: {', '.join(schema.get('required', []))}
"""

        if examples:
            structured_prompt += "\n\nExamples of valid responses:\n"
            for i, example in enumerate(examples, 1):
                structured_prompt += f"\nExample {i}:\n{example.json(indent=2)}\n"

        if context:
            structured_prompt += f"\n\nAdditional context: {json.dumps(context)}\n"

        structured_prompt += (
            "\n\nRespond ONLY with valid JSON. No additional text or explanation."
        )

        return structured_prompt

    async def _get_llm_response(self, prompt: str, attempt: int) -> str:
        """Get response from LLM with attempt tracking."""
        # Use Cortex for consistency
        response = await self.cortex.complete(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.1 if attempt > 0 else 0.3,  # Lower temperature on retry
        )

        # Clean response
        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        return response.strip()

    def _parse_response(self, response: str, output_class: type[T]) -> T:
        """Parse and validate response."""
        try:
            # Parse JSON
            data = json.loads(response)

            # Validate with Pydantic
            return output_class(**data)

        except json.JSONDecodeError:
            # Try to fix common JSON errors
            fixed_response = self._fix_json_errors(response)
            data = json.loads(fixed_response)
            return output_class(**data)

    def _fix_json_errors(self, response: str) -> str:
        """Attempt to fix common JSON errors."""
        # Remove trailing commas
        import re

        response = re.sub(r",\s*}", "}", response)
        response = re.sub(r",\s*]", "]", response)

        # Fix single quotes
        response = response.replace("'", '"')

        # Ensure proper escaping
        response = response.replace("\\", "\\\\")
        response = response.replace("\n", "\\n")
        response = response.replace("\r", "\\r")
        response = response.replace("\t", "\\t")

        return response

    def _enhance_prompt_for_retry(
        self, original_prompt: str, error: str, failed_response: str | None
    ) -> str:
        """Enhance prompt based on previous failure."""
        enhanced = (
            original_prompt
            + f"""

PREVIOUS ATTEMPT FAILED with error: {error}

Common mistakes to avoid:
- Ensure all JSON keys are in double quotes
- No trailing commas in objects or arrays
- All string values must be in double quotes
- Numbers should not be quoted
- Boolean values must be true/false (lowercase)
- Dates should be ISO format strings
"""
        )

        if failed_response:
            enhanced += f"\n\nYour previous response was:\n{failed_response[:500]}...\n\nPlease fix the JSON syntax errors."

        return enhanced
