"""
Configuration schema for LLM Router
Live-reloadable configuration with validation
"""

import json
from pathlib import Path

from pydantic import BaseSettings, Field, validator


class ModelConfig(BaseSettings):
    """Model-specific configuration"""

    name: str
    provider: str
    cost_per_1k_tokens: float
    max_tokens: int
    context_window: int
    strengths: list[str] = Field(default_factory=list)
    use_cases: list[str] = Field(default_factory=list)


class RoutingConfig(BaseSettings):
    """Routing configuration"""

    task_routing: dict[str, list[str]]
    complexity_routing: dict[str, list[str]]
    cost_preference_routing: dict[str, list[str]]

    @validator("task_routing", "complexity_routing", "cost_preference_routing")
    def validate_routing(cls, v):
        """Ensure all routing values are lists of strings"""
        for key, value in v.items():
            if not isinstance(value, list):
                raise ValueError(f"Routing value for {key} must be a list")
            if not all(isinstance(item, str) for item in value):
                raise ValueError(f"All routing items for {key} must be strings")
        return v


class CacheConfig(BaseSettings):
    """Cache configuration"""

    enabled: bool = True
    ttl: int = 3600  # seconds
    semantic_similarity_threshold: float = 0.95
    max_size: int = 1000
    redis_url: str | None = None


class LLMRouterConfig(BaseSettings):
    """Main LLM Router configuration"""

    # Model definitions
    models: dict[str, ModelConfig] = Field(default_factory=dict)

    # Routing rules
    routing: RoutingConfig

    # Cache settings
    cache: CacheConfig = Field(default_factory=CacheConfig)

    # Provider configurations
    portkey_config_path: str = "config/portkey/sophia-ai-config.json"

    # Performance settings
    request_timeout: int = 30  # seconds
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds

    # Cost optimization
    budget_per_request: float | None = None
    budget_per_day: float | None = None

    # Feature flags
    enable_ml_routing: bool = False
    enable_cost_tracking: bool = True
    enable_performance_tracking: bool = True

    class Config:
        env_prefix = "LLM_ROUTER_"
        case_sensitive = False

    @classmethod
    def from_file(
        cls, config_path: str = "config/llm_router.json"
    ) -> "LLMRouterConfig":
        """Load configuration from file with live reload support"""
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            return cls(**data)
        return cls.from_defaults()

    @classmethod
    def from_defaults(cls) -> "LLMRouterConfig":
        """Create default configuration"""
        return cls(
            models={
                "gpt-4o": ModelConfig(
                    name="gpt-4o",
                    provider="openai",
                    cost_per_1k_tokens=2.5,
                    max_tokens=16384,
                    context_window=128000,
                    strengths=["balanced", "code", "analysis"],
                    use_cases=["general", "code_generation", "business_intelligence"],
                ),
                "claude-3-5-sonnet": ModelConfig(
                    name="claude-3-5-sonnet",
                    provider="anthropic",
                    cost_per_1k_tokens=3.0,
                    max_tokens=8192,
                    context_window=200000,
                    strengths=["creative", "complex_reasoning", "architecture"],
                    use_cases=[
                        "architecture_design",
                        "complex_analysis",
                        "creative_writing",
                    ],
                ),
                "deepseek-v3": ModelConfig(
                    name="deepseek-v3",
                    provider="deepseek",
                    cost_per_1k_tokens=0.14,
                    max_tokens=8192,
                    context_window=64000,
                    strengths=["code", "technical", "cost_efficient"],
                    use_cases=["code_generation", "technical_documentation"],
                ),
                "gpt-3.5-turbo": ModelConfig(
                    name="gpt-3.5-turbo",
                    provider="openai",
                    cost_per_1k_tokens=0.5,
                    max_tokens=4096,
                    context_window=16385,
                    strengths=["speed", "cost_efficient", "simple"],
                    use_cases=["chat_conversation", "simple_query"],
                ),
            },
            routing=RoutingConfig(
                task_routing={
                    "architecture_design": ["claude-3-5-sonnet", "gpt-4o"],
                    "code_generation": ["deepseek-v3", "gpt-4o", "claude-3-5-sonnet"],
                    "business_intelligence": ["gpt-4o", "claude-3-5-sonnet"],
                    "chat_conversation": ["gpt-3.5-turbo", "deepseek-v3"],
                },
                complexity_routing={
                    "simple": ["gpt-3.5-turbo", "deepseek-v3"],
                    "moderate": ["deepseek-v3", "gpt-4o"],
                    "complex": ["gpt-4o", "claude-3-5-sonnet"],
                    "architecture": ["claude-3-5-sonnet", "gpt-4o"],
                },
                cost_preference_routing={
                    "budget": ["gpt-3.5-turbo", "deepseek-v3"],
                    "balanced": ["deepseek-v3", "gpt-4o"],
                    "premium": ["claude-3-5-sonnet", "gpt-4o"],
                },
            ),
        )
