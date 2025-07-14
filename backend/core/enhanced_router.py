"""
Enhanced Intelligent Router for Sophia AI
"""
import asyncio
import time
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class ModelTier(Enum):
    PREMIUM = "premium"
    FAST = "fast"

@dataclass
class RoutingDecision:
    selected_model: str
    confidence: float
    estimated_cost: float
    estimated_latency: float
    reasoning: str

class EnhancedIntelligentRouter:
    def __init__(self):
        self.model_profiles = {
            "claude-4-sonnet": {
                "tier": ModelTier.PREMIUM,
                "quality_score": 95,
                "latency_p95": 800,
                "cost_per_1k": 0.003,
                "use_cases": ["reasoning", "analysis", "coding"]
            },
            "gemini-2.5-flash": {
                "tier": ModelTier.FAST,
                "quality_score": 85,
                "latency_p95": 300,
                "cost_per_1k": 0.0001,
                "use_cases": ["fast_response", "simple_queries"]
            }
        }
        
    async def route_request(self, prompt: str, context: Dict) -> RoutingDecision:
        """Intelligent routing with <180ms target"""
        start_time = time.time()
        
        # Analyze complexity
        complexity = await self.analyze_complexity(prompt, context)
        
        # Score models
        scores = await self.score_models(complexity, context)
        
        # Select best model
        selected = max(scores, key=lambda x: x["score"])
        
        routing_time = (time.time() - start_time) * 1000
        
        return RoutingDecision(
            selected_model=selected["name"],
            confidence=selected["score"],
            estimated_cost=selected["cost"],
            estimated_latency=selected["latency"],
            reasoning=f"Selected based on complexity {complexity:.2f}"
        )
        
    async def analyze_complexity(self, prompt: str, context: Dict) -> float:
        """Analyze request complexity"""
        complexity = 0.0
        
        if len(prompt.split()) > 100:
            complexity += 0.3
        if any(word in prompt.lower() for word in ["analyze", "explain", "compare"]):
            complexity += 0.4
        if context.get("requires_accuracy"):
            complexity += 0.3
            
        return min(complexity, 1.0)
        
    async def score_models(self, complexity: float, context: Dict) -> List[Dict]:
        """Score available models"""
        scored = []
        
        for name, profile in self.model_profiles.items():
            quality_score = profile["quality_score"] / 100
            latency_score = max(0, (1000 - profile["latency_p95"]) / 1000)
            cost_score = max(0, (0.01 - profile["cost_per_1k"]) / 0.01)
            
            total_score = (quality_score * 0.4 + latency_score * 0.3 + cost_score * 0.3)
            
            if complexity > 0.7 and profile["tier"] == ModelTier.PREMIUM:
                total_score *= 1.2
            elif complexity < 0.3 and profile["tier"] == ModelTier.FAST:
                total_score *= 1.1
                
            scored.append({
                "name": name,
                "score": total_score,
                "cost": complexity * profile["cost_per_1k"],
                "latency": profile["latency_p95"]
            })
            
        return scored
