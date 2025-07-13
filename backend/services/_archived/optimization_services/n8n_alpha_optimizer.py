"""
N8N Alpha Optimizer - Phase 2
Dynamic alpha tuning for >150ms API calls with dense bias optimization
Adaptive routing for optimal performance under varying loads
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from backend.core.auto_esc_config import get_config_value
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class OptimizationStrategy(Enum):
    DENSE_BIAS = "dense_bias"        # Favor dense embeddings
    SPARSE_BIAS = "sparse_bias"      # Favor sparse embeddings  
    BALANCED = "balanced"            # Even mix
    ADAPTIVE = "adaptive"            # Dynamic based on performance


@dataclass
class APIPerformanceMetrics:
    """Performance metrics for API calls"""
    endpoint: str
    avg_response_time_ms: float
    p95_response_time_ms: float
    success_rate: float
    throughput_qps: float
    error_count: int
    last_updated: datetime
    
    def needs_optimization(self) -> bool:
        """Check if endpoint needs alpha optimization"""
        return (
            self.avg_response_time_ms > 150 or
            self.p95_response_time_ms > 300 or
            self.success_rate < 0.95
        )


@dataclass
class AlphaConfiguration:
    """Alpha configuration for hybrid search optimization"""
    alpha: float                    # 0.0 = pure keyword, 1.0 = pure vector
    strategy: OptimizationStrategy
    performance_score: float
    last_tuned: datetime
    tuning_iterations: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alpha": self.alpha,
            "strategy": self.strategy.value,
            "performance_score": self.performance_score,
            "last_tuned": self.last_tuned.isoformat(),
            "tuning_iterations": self.tuning_iterations
        }


class N8NAlphaOptimizer:
    """
    Dynamic alpha optimizer for n8n workflows
    Optimizes API calls >150ms with intelligent dense/sparse bias
    """
    
    def __init__(self):
        self.performance_cache: Dict[str, APIPerformanceMetrics] = {}
        self.alpha_configs: Dict[str, AlphaConfiguration] = {}
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Default configurations
        self.default_alpha = 0.5  # Balanced start
        self.min_alpha = 0.1      # Minimum vector component
        self.max_alpha = 0.9      # Maximum vector component
        
        # Performance thresholds
        self.target_response_time_ms = 150
        self.target_success_rate = 0.95
        self.optimization_interval_minutes = 5
        
        # Tuning parameters
        self.alpha_step_size = 0.1
        self.performance_window_minutes = 30
        
    async def register_api_call(self, 
                              endpoint: str, 
                              response_time_ms: float, 
                              success: bool,
                              query_type: str = "hybrid") -> None:
        """Register API call performance data"""
        
        if endpoint not in self.performance_cache:
            self.performance_cache[endpoint] = APIPerformanceMetrics(
                endpoint=endpoint,
                avg_response_time_ms=response_time_ms,
                p95_response_time_ms=response_time_ms,
                success_rate=1.0 if success else 0.0,
                throughput_qps=1.0,
                error_count=0 if success else 1,
                last_updated=datetime.utcnow()
            )
        else:
            # Update rolling metrics
            metrics = self.performance_cache[endpoint]
            
            # Exponential moving average for response time
            alpha_ema = 0.1
            metrics.avg_response_time_ms = (
                alpha_ema * response_time_ms + 
                (1 - alpha_ema) * metrics.avg_response_time_ms
            )
            
            # Update P95 (simplified)
            metrics.p95_response_time_ms = max(
                response_time_ms, 
                metrics.p95_response_time_ms * 0.95
            )
            
            # Update success rate
            metrics.success_rate = (
                alpha_ema * (1.0 if success else 0.0) +
                (1 - alpha_ema) * metrics.success_rate
            )
            
            if not success:
                metrics.error_count += 1
                
            metrics.last_updated = datetime.utcnow()
        
        # Trigger optimization if needed
        if self.performance_cache[endpoint].needs_optimization():
            await self.optimize_endpoint(endpoint)
    
    async def optimize_endpoint(self, endpoint: str) -> AlphaConfiguration:
        """Optimize alpha configuration for a specific endpoint"""
        metrics = self.performance_cache.get(endpoint)
        if not metrics:
            logger.warning(f"No metrics found for endpoint: {endpoint}")
            return self._get_default_alpha_config()
        
        logger.info(f"Optimizing endpoint: {endpoint} (avg: {metrics.avg_response_time_ms:.1f}ms)")
        
        current_config = self.alpha_configs.get(endpoint, self._get_default_alpha_config())
        
        # Determine optimization strategy based on current performance
        if metrics.avg_response_time_ms > 200:
            # High latency - try dense bias for better caching
            strategy = OptimizationStrategy.DENSE_BIAS
            target_alpha = min(0.8, current_config.alpha + self.alpha_step_size)
        elif metrics.success_rate < 0.9:
            # High error rate - try sparse bias for simpler processing
            strategy = OptimizationStrategy.SPARSE_BIAS
            target_alpha = max(0.2, current_config.alpha - self.alpha_step_size)
        else:
            # Moderate issues - adaptive approach
            strategy = OptimizationStrategy.ADAPTIVE
            target_alpha = await self._adaptive_alpha_search(endpoint, current_config.alpha)
        
        # Create new configuration
        new_config = AlphaConfiguration(
            alpha=target_alpha,
            strategy=strategy,
            performance_score=self._calculate_performance_score(metrics),
            last_tuned=datetime.utcnow(),
            tuning_iterations=current_config.tuning_iterations + 1
        )
        
        self.alpha_configs[endpoint] = new_config
        
        # Log optimization
        self.optimization_history.append({
            "endpoint": endpoint,
            "timestamp": datetime.utcnow().isoformat(),
            "old_alpha": current_config.alpha,
            "new_alpha": target_alpha,
            "strategy": strategy.value,
            "performance_score": new_config.performance_score,
            "reason": f"avg_latency: {metrics.avg_response_time_ms:.1f}ms"
        })
        
        logger.info(f"Optimized {endpoint}: α={current_config.alpha:.2f}→{target_alpha:.2f} "
                   f"({strategy.value}, score: {new_config.performance_score:.3f})")
        
        return new_config
    
    async def _adaptive_alpha_search(self, endpoint: str, current_alpha: float) -> float:
        """Adaptive alpha search using performance feedback"""
        
        # Test multiple alpha values and predict performance
        test_alphas = [
            max(self.min_alpha, current_alpha - 0.2),
            max(self.min_alpha, current_alpha - 0.1),
            current_alpha,
            min(self.max_alpha, current_alpha + 0.1),
            min(self.max_alpha, current_alpha + 0.2)
        ]
        
        best_alpha = current_alpha
        best_predicted_score = 0.0
        
        for alpha in test_alphas:
            # Predict performance based on historical patterns
            predicted_score = await self._predict_performance_score(endpoint, alpha)
            
            if predicted_score > best_predicted_score:
                best_predicted_score = predicted_score
                best_alpha = alpha
        
        return best_alpha
    
    async def _predict_performance_score(self, endpoint: str, alpha: float) -> float:
        """Predict performance score for given alpha value"""
        
        # Simplified prediction model based on alpha characteristics
        # Dense bias (high alpha) - better for:
        # - Semantic similarity queries
        # - Cached embeddings
        # - Complex reasoning
        
        # Sparse bias (low alpha) - better for:
        # - Exact keyword matches
        # - Simple lookups
        # - High-frequency queries
        
        base_score = 0.7
        
        # Adjust based on endpoint characteristics
        if "search" in endpoint.lower():
            # Search endpoints benefit from balanced approach
            optimal_alpha = 0.6
            alpha_penalty = abs(alpha - optimal_alpha) * 0.5
            predicted_score = base_score - alpha_penalty
        elif "analytics" in endpoint.lower():
            # Analytics endpoints benefit from dense bias
            optimal_alpha = 0.8
            alpha_penalty = abs(alpha - optimal_alpha) * 0.3
            predicted_score = base_score - alpha_penalty
        else:
            # General endpoints - balanced approach
            optimal_alpha = 0.5
            alpha_penalty = abs(alpha - optimal_alpha) * 0.4
            predicted_score = base_score - alpha_penalty
        
        return max(0.1, min(1.0, predicted_score))
    
    def _calculate_performance_score(self, metrics: APIPerformanceMetrics) -> float:
        """Calculate composite performance score"""
        
        # Normalize metrics to 0-1 scale
        latency_score = max(0, 1.0 - (metrics.avg_response_time_ms - 50) / 200)  # 50-250ms range
        success_score = metrics.success_rate
        
        # Weight latency more heavily for our use case
        composite_score = 0.7 * latency_score + 0.3 * success_score
        
        return max(0.0, min(1.0, composite_score))
    
    def _get_default_alpha_config(self) -> AlphaConfiguration:
        """Get default alpha configuration"""
        return AlphaConfiguration(
            alpha=self.default_alpha,
            strategy=OptimizationStrategy.BALANCED,
            performance_score=0.7,
            last_tuned=datetime.utcnow(),
            tuning_iterations=0
        )
    
    async def get_optimal_alpha(self, endpoint: str, query_type: str = "hybrid") -> float:
        """Get optimal alpha value for endpoint"""
        
        config = self.alpha_configs.get(endpoint)
        if not config:
            # Initialize with default
            config = self._get_default_alpha_config()
            self.alpha_configs[endpoint] = config
        
        # Check if configuration is stale
        time_since_tuning = datetime.utcnow() - config.last_tuned
        if time_since_tuning > timedelta(minutes=self.optimization_interval_minutes):
            # Re-optimize if we have recent performance data
            if endpoint in self.performance_cache:
                config = await self.optimize_endpoint(endpoint)
        
        return config.alpha
    
    async def get_n8n_workflow_config(self, workflow_name: str) -> Dict[str, Any]:
        """Generate n8n workflow configuration with optimized alpha values"""
        
        # Common endpoints for n8n workflows
        endpoints = [
            f"{workflow_name}/search",
            f"{workflow_name}/analytics", 
            f"{workflow_name}/synthesis"
        ]
        
        config = {
            "workflow_name": workflow_name,
            "optimized_endpoints": {},
            "global_settings": {
                "performance_monitoring": True,
                "auto_optimization": True,
                "optimization_interval_minutes": self.optimization_interval_minutes
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        for endpoint in endpoints:
            alpha = await self.get_optimal_alpha(endpoint)
            alpha_config = self.alpha_configs.get(endpoint, self._get_default_alpha_config())
            
            config["optimized_endpoints"][endpoint] = {
                "alpha": alpha,
                "strategy": alpha_config.strategy.value,
                "performance_score": alpha_config.performance_score,
                "weaviate_config": {
                    "hybrid_search": {
                        "alpha": alpha,
                        "query": "${query}",
                        "properties": ["content", "metadata"],
                        "limit": 10
                    }
                },
                "fallback_config": {
                    "alpha": self.default_alpha,
                    "timeout_ms": 5000
                }
            }
        
        return config
    
    async def export_n8n_json(self, workflow_name: str) -> Dict[str, Any]:
        """Export optimized n8n workflow JSON"""
        
        config = await self.get_n8n_workflow_config(workflow_name)
        
        # Generate n8n workflow JSON structure
        n8n_workflow = {
            "name": f"Optimized {workflow_name}",
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "url": "={{$node[\"Weaviate Search\"].json[\"endpoint\"]}}",
                        "options": {
                            "timeout": 5000
                        },
                        "bodyParametersUi": {
                            "parameter": [
                                {
                                    "name": "query",
                                    "value": "={{$json[\"query\"]}}"
                                },
                                {
                                    "name": "alpha", 
                                    "value": f"={{$node[\"Alpha Optimizer\"].json[\"alpha\"]}}"
                                }
                            ]
                        }
                    },
                    "name": "Weaviate Search",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [400, 300]
                },
                {
                    "parameters": {
                        "functionCode": f"""
                        // Dynamic alpha optimization
                        const endpoint = items[0].json.endpoint;
                        const responseTime = items[0].json.response_time_ms || 150;
                        
                        // Get optimized alpha from config
                        const config = {json.dumps(config['optimized_endpoints'], indent=2)};
                        const endpointConfig = config[endpoint] || config[Object.keys(config)[0]];
                        
                        let alpha = endpointConfig.alpha;
                        
                        // Dynamic adjustment based on current performance
                        if (responseTime > 200) {{
                            alpha = Math.min(0.9, alpha + 0.1); // Dense bias for slow responses
                        }} else if (responseTime < 100) {{
                            alpha = Math.max(0.1, alpha - 0.05); // Slight sparse bias for fast responses
                        }}
                        
                        return [{{
                            json: {{
                                alpha: alpha,
                                strategy: endpointConfig.strategy,
                                endpoint: endpoint,
                                optimized_at: new Date().toISOString()
                            }}
                        }}];
                        """
                    },
                    "name": "Alpha Optimizer",
                    "type": "n8n-nodes-base.function",
                    "position": [200, 300]
                }
            ],
            "connections": {
                "Alpha Optimizer": {
                    "main": [
                        [
                            {
                                "node": "Weaviate Search",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            "settings": {
                "executionOrder": "v1"
            },
            "staticData": config
        }
        
        return n8n_workflow
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """Generate optimization performance report"""
        
        total_endpoints = len(self.performance_cache)
        optimized_endpoints = len(self.alpha_configs)
        
        # Calculate average improvements
        avg_performance_score = 0.0
        if self.alpha_configs:
            avg_performance_score = sum(
                config.performance_score for config in self.alpha_configs.values()
            ) / len(self.alpha_configs)
        
        # Recent optimizations
        recent_optimizations = [
            opt for opt in self.optimization_history
            if datetime.fromisoformat(opt["timestamp"]) > datetime.utcnow() - timedelta(hours=1)
        ]
        
        report = {
            "summary": {
                "total_endpoints_monitored": total_endpoints,
                "optimized_endpoints": optimized_endpoints,
                "optimization_coverage": optimized_endpoints / max(1, total_endpoints),
                "avg_performance_score": avg_performance_score,
                "recent_optimizations": len(recent_optimizations)
            },
            "performance_metrics": {
                endpoint: {
                    "avg_response_time_ms": metrics.avg_response_time_ms,
                    "success_rate": metrics.success_rate,
                    "needs_optimization": metrics.needs_optimization(),
                    "last_updated": metrics.last_updated.isoformat()
                }
                for endpoint, metrics in self.performance_cache.items()
            },
            "alpha_configurations": {
                endpoint: config.to_dict()
                for endpoint, config in self.alpha_configs.items()
            },
            "recent_optimizations": recent_optimizations[-10:],  # Last 10
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return report


# Global instance for service injection
n8n_optimizer = N8NAlphaOptimizer() 