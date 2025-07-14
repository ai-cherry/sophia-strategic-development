"""
Enumerations for LLM Router
Frozen enums that define routing categories and options
"""

from enum import Enum


class TaskType(str, Enum):
    """Task types for intelligent routing - frozen for stability"""

    # Data operations (Lambda GPU)
    DATA_ANALYSIS = "data_analysis"
    SQL_GENERATION = "sql_generation"
    EMBEDDINGS = "embeddings"

    # Code operations (Premium models)
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"

    # Business operations (Balanced models)
    BUSINESS_INTELLIGENCE = "business_intelligence"
    DOCUMENT_SUMMARY = "document_summary"
    RESEARCH = "research"

    # Conversational (Cost-effective models)
    CHAT_CONVERSATION = "chat_conversation"
    SIMPLE_QUERY = "simple_query"

    # Creative (Specialized models)
    CREATIVE_WRITING = "creative_writing"
    MARKETING_CONTENT = "marketing_content"


class TaskComplexity(str, Enum):
    """Task complexity levels for model selection"""

    SIMPLE = "simple"  # Quick responses, basic queries
    MODERATE = "moderate"  # Standard development tasks
    COMPLEX = "complex"  # Deep analysis, complex reasoning
    ARCHITECTURE = "architecture"  # System design, strategic planning


class Provider(str, Enum):
    """LLM providers - ordered by preference"""

    SNOWFLAKE = "modern_stack"  # Primary for data operations
    PORTKEY = "portkey"  # Gateway for multiple providers
    OPENROUTER = "openrouter"  # 200+ model access
    OPENAI = "openai"  # Direct OpenAI access
    ANTHROPIC = "anthropic"  # Direct Anthropic access
    LOCAL = "local"  # Local models (future)
