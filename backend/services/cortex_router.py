"""
Cortex Router Service

Intelligently routes requests to the most appropriate Snowflake Cortex model
based on intent, complexity, and cost optimization.
"""

from typing import Dict, Any, Optional, Tuple
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available Cortex models with their characteristics"""
    MISTRAL_7B = "mistral-7b"  # Fastest, cheapest, good for classification
    LLAMA3_8B = "llama3-8b"  # Balanced performance and cost
    LLAMA3_70B = "llama3-70b"  # Powerful, good for code generation
    SNOWFLAKE_ARCTIC = "snowflake-arctic"  # Most capable, highest cost
    REKA_CORE = "reka-core"  # Multimodal capabilities


class IntentType(Enum):
    """Types of user intents"""
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    CODE_GENERATION = "code"
    COMPLEX_REASONING = "complex_reasoning"
    DATA_ANALYSIS = "data_analysis"
    GENERAL_QUERY = "general"


class CortexRouter:
    """Routes requests to appropriate Cortex models based on various factors"""
    
    # Model costs per million tokens (approximate)
    MODEL_COSTS = {
        ModelType.MISTRAL_7B: 0.10,
        ModelType.LLAMA3_8B: 0.19,
        ModelType.LLAMA3_70B: 0.80,
        ModelType.SNOWFLAKE_ARCTIC: 2.00,
        ModelType.REKA_CORE: 1.50,
    }
    
    # Model selection rules
    MODEL_SELECTION_RULES = {
        IntentType.CLASSIFICATION: ModelType.MISTRAL_7B,
        IntentType.SUMMARIZATION: ModelType.LLAMA3_8B,
        IntentType.CODE_GENERATION: ModelType.LLAMA3_70B,
        IntentType.COMPLEX_REASONING: ModelType.SNOWFLAKE_ARCTIC,
        IntentType.DATA_ANALYSIS: ModelType.LLAMA3_70B,
        IntentType.GENERAL_QUERY: ModelType.LLAMA3_8B,
    }
    
    # Temperature settings by use case
    TEMPERATURE_MAP = {
        "deterministic": 0.2,  # Facts, data queries
        "balanced": 0.5,       # General queries
        "creative": 0.7,       # Brainstorming, ideation
    }
    
    def __init__(self):
        self.usage_stats: Dict[ModelType, Dict[str, Any]] = {
            model: {"count": 0, "total_cost": 0.0, "total_tokens": 0}
            for model in ModelType
        }
    
    async def route_request(
        self,
        query: str,
        intent: Optional[IntentType] = None,
        complexity: Optional[float] = None,
        max_cost: Optional[float] = None,
        required_capabilities: Optional[list] = None
    ) -> Tuple[ModelType, float, Dict[str, Any]]:
        """
        Route request to appropriate model.
        
        Args:
            query: User query
            intent: Detected intent type
            complexity: Complexity score (0-1)
            max_cost: Maximum cost constraint
            required_capabilities: List of required model capabilities
            
        Returns:
            Tuple of (model, temperature, metadata)
        """
        # Detect intent if not provided
        if intent is None:
            intent = await self._detect_intent(query)
        
        # Calculate complexity if not provided
        if complexity is None:
            complexity = self._calculate_complexity(query)
        
        # Select model based on rules and constraints
        model = self._select_model(intent, complexity, max_cost, required_capabilities)
        
        # Determine temperature
        temperature = self._get_temperature(intent, query)
        
        # Prepare metadata
        metadata = {
            "intent": intent.value,
            "complexity": complexity,
            "estimated_cost": self._estimate_cost(model, query),
            "model_capabilities": self._get_model_capabilities(model),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Update usage statistics
        self._update_stats(model, metadata["estimated_cost"], len(query))
        
        logger.info(
            f"Routed request to {model.value} with temperature {temperature}. "
            f"Intent: {intent.value}, Complexity: {complexity:.2f}"
        )
        
        return model, temperature, metadata
    
    async def _detect_intent(self, query: str) -> IntentType:
        """Detect user intent from query"""
        query_lower = query.lower()
        
        # Simple keyword-based detection (to be enhanced with ML)
        if any(word in query_lower for word in ["classify", "categorize", "type of", "what kind"]):
            return IntentType.CLASSIFICATION
        elif any(word in query_lower for word in ["summarize", "summary", "brief", "overview"]):
            return IntentType.SUMMARIZATION
        elif any(word in query_lower for word in ["code", "function", "implement", "program"]):
            return IntentType.CODE_GENERATION
        elif any(word in query_lower for word in ["analyze", "insights", "trends", "data"]):
            return IntentType.DATA_ANALYSIS
        elif any(word in query_lower for word in ["why", "how does", "explain", "reasoning"]):
            return IntentType.COMPLEX_REASONING
        else:
            return IntentType.GENERAL_QUERY
    
    def _calculate_complexity(self, query: str) -> float:
        """Calculate query complexity (0-1)"""
        # Simple heuristic based on query characteristics
        complexity_factors = {
            "length": min(len(query) / 500, 0.3),  # Longer queries tend to be complex
            "questions": min(query.count("?") * 0.1, 0.2),  # Multiple questions
            "technical_terms": 0.0,  # To be implemented with domain dictionary
            "nested_clauses": min(query.count(",") * 0.05, 0.2),  # Comma-separated clauses
        }
        
        # Check for technical keywords
        technical_keywords = [
            "algorithm", "optimize", "architecture", "implementation",
            "analysis", "correlation", "regression", "forecast"
        ]
        if any(keyword in query.lower() for keyword in technical_keywords):
            complexity_factors["technical_terms"] = 0.3
        
        return min(sum(complexity_factors.values()), 1.0)
    
    def _select_model(
        self,
        intent: IntentType,
        complexity: float,
        max_cost: Optional[float],
        required_capabilities: Optional[list]
    ) -> ModelType:
        """Select appropriate model based on constraints"""
        # Start with rule-based selection
        base_model = self.MODEL_SELECTION_RULES.get(intent, ModelType.LLAMA3_8B)
        
        # Adjust based on complexity
        if complexity < 0.3 and base_model != ModelType.MISTRAL_7B:
            # Simple queries can use smaller model
            return ModelType.MISTRAL_7B
        elif complexity > 0.7:
            # Complex queries need powerful models
            if intent == IntentType.CODE_GENERATION:
                return ModelType.LLAMA3_70B
            else:
                return ModelType.SNOWFLAKE_ARCTIC
        
        # Check cost constraints
        if max_cost is not None:
            affordable_models = [
                model for model, cost in self.MODEL_COSTS.items()
                if cost <= max_cost
            ]
            if base_model not in affordable_models and affordable_models:
                # Downgrade to most capable affordable model
                return max(affordable_models, key=lambda m: self.MODEL_COSTS[m])
        
        # Check required capabilities
        if required_capabilities and "multimodal" in required_capabilities:
            return ModelType.REKA_CORE
        
        return base_model
    
    def _get_temperature(self, intent: IntentType, query: str) -> float:
        """Determine appropriate temperature setting"""
        # Deterministic for data and facts
        if intent in [IntentType.CLASSIFICATION, IntentType.DATA_ANALYSIS]:
            return self.TEMPERATURE_MAP["deterministic"]
        
        # Creative for brainstorming
        creative_keywords = ["ideas", "suggestions", "creative", "innovative", "brainstorm"]
        if any(keyword in query.lower() for keyword in creative_keywords):
            return self.TEMPERATURE_MAP["creative"]
        
        # Default to balanced
        return self.TEMPERATURE_MAP["balanced"]
    
    def _estimate_cost(self, model: ModelType, query: str) -> float:
        """Estimate cost for the query"""
        # Rough token estimation (1 token ≈ 4 characters)
        estimated_tokens = len(query) / 4
        # Assume response is 2x query length
        total_tokens = estimated_tokens * 3
        
        cost_per_million = self.MODEL_COSTS[model]
        return (total_tokens / 1_000_000) * cost_per_million
    
    def _get_model_capabilities(self, model: ModelType) -> list:
        """Get list of model capabilities"""
        capabilities = {
            ModelType.MISTRAL_7B: ["fast", "classification", "simple_queries"],
            ModelType.LLAMA3_8B: ["balanced", "general_purpose", "summarization"],
            ModelType.LLAMA3_70B: ["code_generation", "complex_queries", "analysis"],
            ModelType.SNOWFLAKE_ARCTIC: ["highest_quality", "reasoning", "comprehensive"],
            ModelType.REKA_CORE: ["multimodal", "image_understanding", "comprehensive"],
        }
        return capabilities.get(model, [])
    
    def _update_stats(self, model: ModelType, cost: float, tokens: int):
        """Update usage statistics"""
        stats = self.usage_stats[model]
        stats["count"] += 1
        stats["total_cost"] += cost
        stats["total_tokens"] += tokens
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Get usage statistics report"""
        total_cost = sum(stats["total_cost"] for stats in self.usage_stats.values())
        total_requests = sum(stats["count"] for stats in self.usage_stats.values())
        
        report = {
            "total_cost": total_cost,
            "total_requests": total_requests,
            "by_model": {
                model.value: {
                    "requests": stats["count"],
                    "cost": stats["total_cost"],
                    "average_cost": stats["total_cost"] / max(stats["count"], 1),
                    "percentage": (stats["count"] / max(total_requests, 1)) * 100
                }
                for model, stats in self.usage_stats.items()
            },
            "cost_savings": self._calculate_savings(),
        }
        
        return report
    
    def _calculate_savings(self) -> float:
        """Calculate cost savings from intelligent routing"""
        # Calculate what it would cost if everything used the most expensive model
        total_tokens = sum(stats["total_tokens"] for stats in self.usage_stats.values())
        max_cost = (total_tokens / 1_000_000) * max(self.MODEL_COSTS.values())
        actual_cost = sum(stats["total_cost"] for stats in self.usage_stats.values())
        
        return max_cost - actual_cost 